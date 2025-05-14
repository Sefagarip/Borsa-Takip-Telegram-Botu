import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import asyncio
import json
import os


# Loglama ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Telegram Bot Token
TOKEN = "BOTFATHER'DAN_ALDIĞINIZ_TOKEN"

# Hisse fiyatı çekme fonksiyonu
async def get_stock_price(symbol):
    def _get_price():
        # Selenium ayarları
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # ChromeDriver'ı otomatik kur
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        try:
            #  hisse senedi sayfasını aç
            url = f"Senin_Web_Scraping_Linkin"
            driver.get(url)

            # Fiyat değerini çek
            price_element = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "span.js-symbol-last"))
            )
            price = price_element.text.strip()
            
            return price, None
        except Exception as e:
            return None, str(e)
        finally:
            driver.quit()
    
    # Selenium işlemini thread pool ile çalıştır (blocking işlem)
    loop = asyncio.get_running_loop()
    price, error = await loop.run_in_executor(None, _get_price)
    
    if price:
        return f"{symbol} için son fiyat: {price}"
    else:
        return f"{symbol} için fiyat bulunamadı. Hata: {error}"

# Bot komutları
async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"Merhaba {user.first_name}! Hisse Fiyatları Botuna hoş geldiniz."
    )
    await show_main_menu(update, context)

async def help_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "Kullanım:\n"
        "- Hisse fiyatını öğrenmek için bir hisse sembolü gönderin (örn. AKBNK)\n"
        "- /start - Ana menüyü göster\n"
        "- /help - Yardım mesajını göster\n"
        "- /menu - Ana menüyü göster\n"
        "- /favoriler - Favori hisselerinizi gösterir\n"
        "- /ekle [SEMBOL] - Favorilere hisse ekle\n"
    )
    await show_main_menu(update, context)

# Kullanıcının favori hisseleri (gerçek uygulamada veritabanında saklanabilir)
favorites = {
    # user_id: [sembol1, sembol2, ...]
}

# Kullanıcının portföyü (JSON dosyasına kaydedilecek)
portfolio = {
    # user_id: {symbol: {'price': alım_fiyatı, 'quantity': adet}, ...}
}

# Portföy dosyası
PORTFOLIO_FILE = "portfolio_data.json"

# Portföyü yükle
def load_portfolio():
    global portfolio
    try:
        if os.path.exists(PORTFOLIO_FILE):
            with open(PORTFOLIO_FILE, "r", encoding="utf-8") as file:
                # JSON'dan string olan kullanıcı ID'leri int'e çevirme
                data = json.load(file)
                portfolio = {int(user_id): user_data for user_id, user_data in data.items()}
            print("Portföy verileri başarıyla yüklendi.")
    except Exception as e:
        print(f"Portföy yüklenirken hata oluştu: {e}")
        portfolio = {}

# Bildirim tercihlerini yükle
def load_notification_preferences():
    global notification_preferences
    try:
        if os.path.exists(NOTIFICATION_PREFS_FILE):
            with open(NOTIFICATION_PREFS_FILE, "r", encoding="utf-8") as file:
                # JSON'dan string olan kullanıcı ID'leri int'e çevirme
                data = json.load(file)
                notification_preferences = {int(user_id): user_data for user_id, user_data in data.items()}
            print("Bildirim tercihleri başarıyla yüklendi.")
    except Exception as e:
        print(f"Bildirim tercihleri yüklenirken hata oluştu: {e}")
        notification_preferences = {}

# Portföyü kaydet
def save_portfolio():
    try:
        # int olan kullanıcı ID'lerini string'e çevirme (JSON uyumluluğu için)
        data = {str(user_id): user_data for user_id, user_data in portfolio.items()}
        with open(PORTFOLIO_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print("Portföy verileri başarıyla kaydedildi.")
    except Exception as e:
        print(f"Portföy kaydedilirken hata oluştu: {e}")

# Bildirim tercihlerini kaydet
def save_notification_preferences():
    try:
        # int olan kullanıcı ID'lerini string'e çevirme (JSON uyumluluğu için)
        data = {str(user_id): user_data for user_id, user_data in notification_preferences.items()}
        with open(NOTIFICATION_PREFS_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print("Bildirim tercihleri başarıyla kaydedildi.")
    except Exception as e:
        print(f"Bildirim tercihleri kaydedilirken hata oluştu: {e}")
        
# Kullanıcının bildirim tercihlerini ayarla
def set_notification_preference(user_id, enabled=True):
    if user_id not in notification_preferences:
        notification_preferences[user_id] = {"enabled": enabled, "last_notification": None}
    else:
        notification_preferences[user_id]["enabled"] = enabled
    
    save_notification_preferences()
    
    # Scheduled Notifications modülüne bildir
    try:
        from scheduled_notifications import register_user_for_notifications, unregister_user_from_notifications
        if enabled:
            register_user_for_notifications(user_id)
        else:
            unregister_user_from_notifications(user_id)
    except ImportError:
        print("scheduled_notifications modülü yüklenemedi.")

# Kullanıcı durum takibi için
user_states = {}

# Bildirim alma tercihlerini takip eden sözlük
notification_preferences = {}
# Bildirim zamanlarını kaydetmek için dosya
NOTIFICATION_PREFS_FILE = "notification_prefs.json"

class ConversationState:
    IDLE = 0
    WAITING_FOR_STOCK = 1
    WAITING_FOR_PRICE = 2
    WAITING_FOR_QUANTITY = 3

async def add_favorite(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text("Lütfen eklemek istediğiniz hisse sembolünü yazın. Örnek: /ekle AKBNK")
        return
    
    symbol = context.args[0].upper()
    
    if user_id not in favorites:
        favorites[user_id] = []
    
    if symbol in favorites[user_id]:
        await update.message.reply_text(f"{symbol} zaten favorilerinizde.")
    else:
        favorites[user_id].append(symbol)
        await update.message.reply_text(f"{symbol} favorilerinize eklendi.")

async def show_favorites(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    
    if user_id not in favorites or not favorites[user_id]:
        await update.message.reply_text("Henüz favori hisseniz bulunmuyor.")
        return
    
    keyboard = []
    for symbol in favorites[user_id]:
        keyboard.append([InlineKeyboardButton(symbol, callback_data=f"fav_{symbol}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Favori hisseleriniz:", reply_markup=reply_markup)

async def button_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    user_id = update.effective_user.id
    
    # Ana menüyü göster
    if callback_data == "main_menu":
        await show_main_menu_from_callback(query, context)
    
    # Favorileri göster
    elif callback_data == "favorites":
        await show_favorites_from_callback(query, context)
    
    # Belirli bir hisse fiyatını göster
    elif callback_data.startswith("price_"):
        symbol = callback_data[6:]
        price_message = await get_stock_price(symbol)
        
        # Klavye düğmeleri
        keyboard = [
            [InlineKeyboardButton("⭐ Favorilere Ekle", callback_data=f"add_{symbol}")],
            [InlineKeyboardButton("💼 Portföye Ekle", callback_data=f"add_portfolio_{symbol}")],
            [InlineKeyboardButton("⬅️ Geri", callback_data="favorites")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=price_message, reply_markup=reply_markup)
    
    # Favorilere ekle
    elif callback_data.startswith("add_") and not callback_data.startswith("add_portfolio_"):
        symbol = callback_data[4:]
        
        if user_id not in favorites:
            favorites[user_id] = []
            
        if symbol not in favorites[user_id]:
            favorites[user_id].append(symbol)
            await query.edit_message_text(f"{symbol} favorilerinize eklendi!")
            await show_favorites_from_callback(query, context)
        else:
            await query.edit_message_text(f"{symbol} zaten favorilerinizde!")
            await show_favorites_from_callback(query, context)
    
    # Favorilerden çıkar
    elif callback_data.startswith("remove_"):
        symbol = callback_data[7:]
        
        if user_id in favorites and symbol in favorites[user_id]:
            favorites[user_id].remove(symbol)
            await query.edit_message_text(f"{symbol} favorilerinizden çıkarıldı!")
            await show_favorites_from_callback(query, context)
        else:
            await query.edit_message_text(f"{symbol} favorilerinizde bulunamadı!")
            await show_favorites_from_callback(query, context)
    
    # Portföye ekle
    elif callback_data.startswith("add_portfolio_"):
        symbol = callback_data[14:]
        
        user_states[user_id] = ConversationState.WAITING_FOR_PRICE
        context.user_data["current_symbol"] = symbol
        
        await query.edit_message_text(
            f"{symbol} hissesi için alım fiyatını girin (örn: 45.60):"
        )
    
    # Portföyü göster
    elif callback_data == "portfolio":
        await show_portfolio(query, context)
    
    # Portföyden hisse çıkar
    elif callback_data.startswith("remove_portfolio_"):
        symbol = callback_data[17:]
        
        if user_id in portfolio and symbol in portfolio[user_id]:
            del portfolio[user_id][symbol]
            save_portfolio()
            await query.edit_message_text(f"{symbol} portföyünüzden çıkarıldı!")
            await show_portfolio(query, context)
        else:
            await query.edit_message_text(f"{symbol} portföyünüzde bulunamadı!")
            await show_portfolio(query, context)
    
    # Kâr-zarar durumu göster
    elif callback_data == "profit_loss":
        await show_profit_loss(query, context)
    
    # Kullanıcının kendi portföyünü görmesi için
    elif callback_data == "my_portfolio":
        await show_portfolio(query, context)
        
    # Otomatik bildirimleri aç/kapat
    elif callback_data == "toggle_notifications":
        user_enabled = user_id in notification_preferences and notification_preferences[user_id].get("enabled", False)
        set_notification_preference(user_id, not user_enabled)
        
        status = "açık" if not user_enabled else "kapalı"
        await query.edit_message_text(
            f"Otomatik bildirimler {status} duruma getirildi. Hafta içi saat 09:00-18:00 arasında her saat başı bildirim alacaksınız.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Ana Menü", callback_data="main_menu")]])
        )
    
    # Bildirimleri durdur (bildirim içinden gelen)
    elif callback_data == "stop_notifications":
        set_notification_preference(user_id, False)
        await query.edit_message_text(
            "Otomatik bildirimler kapatıldı. İstediğiniz zaman tekrar açabilirsiniz.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Ana Menü", callback_data="main_menu")]])
        )

async def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    text = update.message.text.strip().upper()
    
    # Konuşma durumunu kontrol et
    if user_id in user_states:
        user_state = user_states[user_id]['state']
        
        # Hisse sembolü bekleniyor
        if user_state == ConversationState.WAITING_FOR_STOCK:
            user_states[user_id]['data']['symbol'] = text
            user_states[user_id]['state'] = ConversationState.WAITING_FOR_PRICE
            
            keyboard = [[InlineKeyboardButton("İptal", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"{text} hissesinin alım fiyatını TL olarak giriniz (örn. 45.60):",
                reply_markup=reply_markup
            )
            return
        
        # Hisse fiyatı bekleniyor
        elif user_state == ConversationState.WAITING_FOR_PRICE:
            try:
                price = float(text.replace(',', '.'))
                user_states[user_id]['data']['price'] = price
                user_states[user_id]['state'] = ConversationState.WAITING_FOR_QUANTITY
                
                keyboard = [[InlineKeyboardButton("İptal", callback_data="main_menu")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    f"Kaç adet hisse aldığınızı giriniz (örn. 100):",
                    reply_markup=reply_markup
                )
                return
            except ValueError:
                await update.message.reply_text(
                    "Geçerli bir sayı giriniz. Örnek: 45.60"
                )
                return
        
        # Hisse adedi bekleniyor
        elif user_state == ConversationState.WAITING_FOR_QUANTITY:
            try:
                quantity = int(text)
                symbol = user_states[user_id]['data']['symbol']
                price = user_states[user_id]['data']['price']
                
                # Portföye ekle
                if user_id not in portfolio:
                    portfolio[user_id] = {}
                
                portfolio[user_id][symbol] = {
                    'price': price,
                    'quantity': quantity
                }
                
                # Portföyü kaydet
                save_portfolio()
                
                # Kullanıcı durumunu sıfırla
                del user_states[user_id]
                
                await update.message.reply_text(
                    f"{symbol} hissesi portföyünüze eklendi.\n" 
                    f"Alım Fiyatı: {price} TL\n"
                    f"Adet: {quantity}\n"
                    f"Toplam: {price * quantity} TL"
                )
                
                # Ana menüyü göster
                await show_main_menu(update, context)
                return
            except ValueError:
                await update.message.reply_text(
                    "Geçerli bir sayı giriniz. Örnek: 100"
                )
                return
    
    # Özel mesaj kontrolü
    if text == "MENU" or text == "MENÜ":
        await show_main_menu(update, context)
        return
        
    # Hisse sembolü olarak kabul et
    await update.message.reply_text(f"{text} için fiyat alınıyor...")
    result = await get_stock_price(text)
    
    # Sonucu göster ve tekrar menü ekle
    keyboard = [
        [InlineKeyboardButton("Ana Menü", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(result, reply_markup=reply_markup)

# Ana menü fonksiyonu
async def show_main_menu(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    
    # Bildirim durumunu kontrol et
    notification_status = "Kapalı"
    if user_id in notification_preferences and notification_preferences[user_id].get("enabled", False):
        notification_status = "Açık"
    
    keyboard = [
        [InlineKeyboardButton("⭐ Favoriler", callback_data="favorites")],
        [InlineKeyboardButton("💼 Portföyüm", callback_data="portfolio")],
        [InlineKeyboardButton("💰 Kâr/Zarar Durumu", callback_data="profit_loss")],
        [InlineKeyboardButton(f"🔔 Otomatik Bildirimler ({notification_status})", callback_data="toggle_notifications")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Ana Menü",
        reply_markup=reply_markup
    )

# Callback query'den ana menü gösterme
async def show_main_menu_from_callback(query, context: CallbackContext) -> None:
    user_id = query.from_user.id
    
    # Bildirim durumunu kontrol et
    notification_status = "Kapalı"
    if user_id in notification_preferences and notification_preferences[user_id].get("enabled", False):
        notification_status = "Açık"
    
    keyboard = [
        [InlineKeyboardButton("⭐ Favoriler", callback_data="favorites")],
        [InlineKeyboardButton("💼 Portföyüm", callback_data="portfolio")],
        [InlineKeyboardButton("💰 Kâr/Zarar Durumu", callback_data="profit_loss")],
        [InlineKeyboardButton(f"🔔 Otomatik Bildirimler ({notification_status})", callback_data="toggle_notifications")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "Ana Menü",
        reply_markup=reply_markup
    )

# Callback query'den favorileri gösterme
async def show_favorites_from_callback(query, context: CallbackContext) -> None:
    user_id = query.from_user.id
    
    if user_id not in favorites or not favorites[user_id]:
        keyboard = [[InlineKeyboardButton("Ana Menü", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Henüz favori hisseniz bulunmuyor.", reply_markup=reply_markup)
        return
    
    keyboard = []
    for symbol in favorites[user_id]:
        keyboard.append([InlineKeyboardButton(symbol, callback_data=f"fav_{symbol}")])
    
    keyboard.append([InlineKeyboardButton("Ana Menü", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Favori hisseleriniz:", reply_markup=reply_markup)

# Portföy gösterme fonksiyonu
async def show_portfolio(query, context: CallbackContext) -> None:
    user_id = query.from_user.id
    
    if user_id not in portfolio or not portfolio[user_id]:
        keyboard = [[InlineKeyboardButton("Ana Menü", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Henüz portföyünüzde hisse bulunmuyor.", reply_markup=reply_markup)
        return
    
    # Portföy bilgilerini hazırla
    portfolio_text = "📊 PORTFÖYÜNÜZ:\n\n"
    total_investment = 0
    
    for symbol, data in portfolio[user_id].items():
        price = data['price']
        quantity = data['quantity']
        total = price * quantity
        total_investment += total
        
        portfolio_text += f"🔸 {symbol}\n"
        portfolio_text += f"   Alım: {price} TL × {quantity} = {total:.2f} TL\n"
    
    portfolio_text += f"\nToplam Yatırım: {total_investment:.2f} TL"
    
    # Butonları hazırla
    keyboard = []
    # Her hisse için bir silme butonu ekle
    for symbol in portfolio[user_id].keys():
        keyboard.append([InlineKeyboardButton(f"❌ {symbol} Sil", callback_data=f"delete_{symbol}")])
    
    keyboard.append([InlineKeyboardButton("💰 Gelir Durumu", callback_data="profit_loss")])
    keyboard.append([InlineKeyboardButton("Ana Menü", callback_data="main_menu")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(portfolio_text, reply_markup=reply_markup)

# Portföy komutu
async def portfolio_command(update: Update, context: CallbackContext) -> None:
    # Mesaj için özel işleme
    msg = update.message
    keyboard = []
    
    user_id = update.effective_user.id
    if user_id not in portfolio or not portfolio[user_id]:
        keyboard = [[InlineKeyboardButton("Ana Menü", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await msg.reply_text("Henüz portföyünüzde hisse bulunmuyor.", reply_markup=reply_markup)
        return
    
    # Portföy bilgilerini hazırla
    portfolio_text = "📊 PORTFÖYÜNÜZ:\n\n"
    total_investment = 0
    
    for symbol, data in portfolio[user_id].items():
        price = data['price']
        quantity = data['quantity']
        total = price * quantity
        total_investment += total
        
        portfolio_text += f"🔸 {symbol}\n"
        portfolio_text += f"   Alım: {price} TL × {quantity} = {total:.2f} TL\n"
    
    portfolio_text += f"\nToplam Yatırım: {total_investment:.2f} TL"
    
    # Butonları hazırla
    keyboard = []
    # Her hisse için bir silme butonu ekle
    for symbol in portfolio[user_id].keys():
        keyboard.append([InlineKeyboardButton(f"❌ {symbol} Sil", callback_data=f"delete_{symbol}")])
    
    keyboard.append([InlineKeyboardButton("💰 Gelir Durumu", callback_data="profit_loss")])
    keyboard.append([InlineKeyboardButton("Ana Menü", callback_data="main_menu")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await msg.reply_text(portfolio_text, reply_markup=reply_markup)
    
# Gelir durumu komutu
async def profit_loss_command(update: Update, context: CallbackContext) -> None:
    await show_profit_loss(update.callback_query if hasattr(update, 'callback_query') else update.message, context)

# Bildirim ayarları komutu
async def notification_settings_command(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    
    # Kullanıcının mevcut bildirim durumunu kontrol et
    current_status = "kapalı"
    if user_id in notification_preferences and notification_preferences[user_id].get("enabled", False):
        current_status = "açık"
    
    keyboard = [
        [InlineKeyboardButton("🔔 Bildirimleri Aç", callback_data="toggle_notifications")],
        [InlineKeyboardButton("❌ Bildirimleri Kapat", callback_data="stop_notifications")],
        [InlineKeyboardButton("Ana Menü", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Bildirim Ayarları\n\n"
        f"Mevcut durum: {current_status}\n\n"
        f"Bildirimler hafta içi (Pazartesi-Cuma) günleri\n"
        f"saat 09:00-18:00 arasında, her saat başı\n"
        f"otomatik olarak gönderilir.",
        reply_markup=reply_markup
    )

# Kâr-zarar gösterme fonksiyonu
async def show_profit_loss(query, context: CallbackContext) -> None:
    user_id = query.from_user.id
    
    if user_id not in portfolio or not portfolio[user_id]:
        keyboard = [[InlineKeyboardButton("Ana Menü", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Henüz portföyünüzde hisse bulunmuyor.", reply_markup=reply_markup)
        return
    
    await query.edit_message_text("Güncel fiyatlar alınıyor, lütfen bekleyin...")
    
    # Kâr-zarar bilgilerini hazırla
    profit_loss_text = "💰 GELİR DURUMU:\n\n"
    total_investment = 0
    total_current_value = 0
    
    for symbol, data in portfolio[user_id].items():
        buy_price = data['price']
        quantity = data['quantity']
        total_buy = buy_price * quantity
        total_investment += total_buy
        
        # Güncel fiyatı al
        current_price_text = await get_stock_price(symbol)
        # Fiyatı metin içinden çıkar
        try:
            current_price_start = current_price_text.find("son fiyat: ") + len("son fiyat: ")
            current_price_str = current_price_text[current_price_start:].strip()
            # Türkçe formatta sayılar 1.234,56 şeklinde olduğundan önce noktaları kaldırıp sonra virgülü noktaya çeviriyoruz
            current_price = float(current_price_str.replace('.', '').replace(',', '.'))
            
            total_current = current_price * quantity
            total_current_value += total_current
            
            profit_loss = total_current - total_buy
            profit_loss_percent = (profit_loss / total_buy) * 100 if total_buy > 0 else 0
            
            profit_loss_text += f"🔹 {symbol}\n"
            profit_loss_text += f"   Alım: {buy_price} TL × {quantity} = {total_buy:.2f} TL\n"
            profit_loss_text += f"   Güncel: {current_price} TL × {quantity} = {total_current:.2f} TL\n"
            
            if profit_loss >= 0:
                profit_loss_text += f"   Kâr: +{profit_loss:.2f} TL (+{profit_loss_percent:.2f}%)\n\n"
            else:
                profit_loss_text += f"   Zarar: {profit_loss:.2f} TL ({profit_loss_percent:.2f}%)\n\n"
        except Exception as e:
            profit_loss_text += f"🔹 {symbol}\n"
            profit_loss_text += f"   Alım: {buy_price} TL × {quantity} = {total_buy:.2f} TL\n"
            profit_loss_text += f"   Güncel fiyat alınamadı\n\n"
    
    total_profit_loss = total_current_value - total_investment
    total_profit_loss_percent = (total_profit_loss / total_investment) * 100 if total_investment > 0 else 0
    
    profit_loss_text += f"Toplam Yatırım: {total_investment:.2f} TL\n"
    profit_loss_text += f"Güncel Değer: {total_current_value:.2f} TL\n"
    
    if total_profit_loss >= 0:
        profit_loss_text += f"Toplam Kâr: +{total_profit_loss:.2f} TL (+{total_profit_loss_percent:.2f}%)"
    else:
        profit_loss_text += f"Toplam Zarar: {total_profit_loss:.2f} TL ({total_profit_loss_percent:.2f}%)"
    
    keyboard = [
        [InlineKeyboardButton("💼 Portföye Dön", callback_data="my_portfolio")],
        [InlineKeyboardButton("Ana Menü", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(profit_loss_text, reply_markup=reply_markup)

def main() -> None:
    # Portföy verilerini yükle
    load_portfolio()
    
    # Bildirim tercihlerini yükle
    load_notification_preferences()
    
    # Bot uygulamasını oluştur
    application = Application.builder().token(TOKEN).build()

    # Telegram Komut Menüsü için komutları ayarla
    bot_commands = [
        ("start", "Ana menüyü göster"),
        ("help", "Yardım mesajını göster"),
        ("menu", "Ana menüyü göster"),
        ("favoriler", "Favori hisselerinizi listele"),
        ("portfolio", "Portföyünüzü göster"),
        ("gelir", "Kâr-zarar durumunuzu göster"),
        ("bildirimler", "Otomatik bildirim ayarlarını yönet")
    ]
    
    # Uygulama başlatıldığında komutları ayarla (post_init application nesnesini parametre olarak alır)
    async def post_init_setup(app):
        await app.bot.set_my_commands(bot_commands)
    
    # post_init hook'unu ayarla
    application.post_init = post_init_setup
    
    # Komut işleyicileri
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", start))  # menu komutu da ana menüyü göstersin
    application.add_handler(CommandHandler("ekle", add_favorite))
    application.add_handler(CommandHandler("favoriler", show_favorites))
    application.add_handler(CommandHandler("portfolio", portfolio_command))
    application.add_handler(CommandHandler("gelir", profit_loss_command))
    application.add_handler(CommandHandler("bildirimler", notification_settings_command))
    
    # Düğme geri çağrıları
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Metin mesajı işleyicisi
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Bot'u başlat
    application.run_polling()

if __name__ == '__main__':
    main()
