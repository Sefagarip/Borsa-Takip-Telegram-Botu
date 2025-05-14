# 🇹🇷 | 🇬🇧 Choose Your Language / Dil Seçin

- [English](#english)
- [Türkçe](#turkish)

<a name="english"></a>

****************************************************************************
* ____  _     _     _____     _ _                          ____        _   *
*| __ )(_)___| |_  |  ___|__ | | | _____      _____ _ __  | __ )  ___ | |_ *
*|  _ \| / __| __| | |_ / _ \| | |/ _ \ \ /\ / / _ \ '__| |  _ \ / _ \| __|*
*| |_) | \__ \ |_  |  _| (_) | | | (_) \ V  V /  __/ |    | |_) | (_) | |_ *
*|____/|_|___/\__| |_|  \___/|_|_|\___/ \_/\_/ \___|_|    |____/ \___/ \__|*
****************************************************************************

# BIST Stock Tracker Bot for Telegram

Track Borsa Istanbul (BIST) stocks, manage your portfolio, and receive market data directly through Telegram.

## 🔍 Features

- **Stock Price Tracking**: Get real-time prices for any BIST stock
- **Favorite Stocks**: Add frequently checked stocks to your favorites
- **Portfolio Management**: Track and manage your purchased stocks
- **Profit-Loss Analysis**: View profit or loss status of your portfolio
- **User-Friendly Interface**: Button-based menus for easy navigation
- **Data Storage**: Your portfolio information and notification preferences are stored locally

## 📋 Requirements

- Python 3.7 or higher
- Telegram account
- Telegram Bot Token obtained through BotFather

## 📦 Required Libraries

```
python-telegram-bot>=20.0
selenium
webdriver-manager
```

## 🔧 Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/bist-telegram-bot.git
   cd bist-telegram-bot
   ```

2. Install required libraries:
   ```
   pip install -r requirements.txt
   ```

3. Set your Telegram Bot Token in `telegram_bot.py`:
   ```python
   TOKEN = "YOUR_TOKEN_FROM_BOTFATHER"
   ```
4. Set your web scraping link in `telegram_bot.py`:
   ```python
   url = "YOUR_WEB_SCRAPING_LINK"
   ```

5. Run the bot:
   ```
   python telegram_bot.py
   ```

## 🤖 Bot Commands

| Command | Description |
|---------|-------------|
| /start | Shows the main menu |
| /help | Displays help message |
| /menu | Shows the main menu |
| /favoriler | Lists your favorite stocks |
| /ekle [SYMBOL] | Adds a stock to favorites |
| /portfolio | Shows your portfolio |
| /gelir | Shows profit-loss status |
| /bildirimler | Manages automatic notification settings |

## 💼 Creating a Portfolio

Follow these steps to add stocks to your portfolio:
1. Select "Portfolio Management" from the main menu
2. Click the "Add Stock" button
3. When the bot asks for a stock symbol (e.g., AKBNK, THYAO, TUPRS), send the symbol you want
4. Enter the purchase price of the stock
5. Finally, specify the quantity/lot amount you bought

## 🆕 Updates

New features will be continuously added. Coming soon:
- Price alerts
- Market news integration
- Stock charts

## 📄 License

This project is licensed under the MIT License. See the 'LICENSE' file for details.

---

<a name="turkish"></a>

********************************************************************
* ____  _     _     _____     _    _         ____        _         *
*| __ )(_)___| |_  |_   _|_ _| | _(_)_ __   | __ )  ___ | |_ _   _ *
*|  _ \| / __| __|   | |/ _` | |/ / | '_ \  |  _ \ / _ \| __| | | |*
*| |_) | \__ \ |_    | | (_| |   <| | |_) | | |_) | (_) | |_| |_| |*
*|____/|_|___/\__|   |_|\__,_|_|\_\_| .__/  |____/ \___/ \__|\__,_|*
*                                   |_|                            *
********************************************************************

# BorsaTakip Telegram Botu

Borsa İstanbul (BIST) hisse senetlerini takip etmek, portföy yönetmek ve piyasa verilerini Telegram üzerinden almak için kullanabileceğiniz bir bot.

## 🔍 Özellikler

- **Hisse Fiyatı Takibi**: Herhangi bir BIST hissesinin anlık fiyatını öğrenme
- **Favori Hisseler**: Sık takip ettiğiniz hisseleri favorilerinize ekleme
- **Portföy Yönetimi**: Satın aldığınız hisseleri yönetme ve takip etme
- **Kâr-Zarar Analizi**: Portföyünüzdeki kâr veya zarar durumunu görüntüleme
- **Arayüz Menüleri**: Kullanıcı dostu düğme tabanlı menüler
- **Veri Saklama**: Portföy bilgileriniz ve bildirim tercihleriniz yerel olarak saklanır

## 📋 Gereksinimler

- Python 3.7 veya üzeri
- Telegram hesabı
- BotFather üzerinden alınmış bir Telegram Bot Token'ı

## 📦 Gerekli Kütüphaneler

```
python-telegram-bot>=20.0
selenium
webdriver-manager
```

## 🔧 Kurulum

1. Repo'yu klonlayın:
   ```
   git clone https://github.com/kullaniciadi/borsatakip-telegram-bot.git
   cd borsatakip-telegram-bot
   ```

2. Gerekli kütüphaneleri yükleyin:
   ```
   pip install -r requirements.txt
   ```

3. `telegram_bot.py` dosyasında Telegram Bot Token'ınızı ayarlayın:
   ```python
   TOKEN = "BOTFATHER'DAN_ALDIĞINIZ_TOKEN"
   ```
4. web scraping için web sitesinin linkini girin:
   ```python
   url = "Senin_Web_Scraping_Linkin"
   ```

5. Bot'u çalıştırın:
   ```
   python telegram_bot.py
   ```

## 🤖 Bot Komutları

| Komut | Açıklama |
|-------|----------|
| /start | Ana menüyü gösterir |
| /help | Yardım mesajını gösterir |
| /menu | Ana menüyü gösterir |
| /favoriler | Favori hisselerinizi listeler |
| /ekle [SEMBOL] | Favorilere hisse ekler |
| /portfolio | Portföyünüzü gösterir |
| /gelir | Kâr-zarar durumunuzu gösterir |
| /bildirimler | Otomatik bildirim ayarlarını yönetir |

## 💼 Portföy Oluşturma

Hisse almak için aşağıdaki adımları takip edin:
1. Ana menüden "Portföy Yönetimi" seçeneğini seçin
2. "Hisse Ekle" düğmesine tıklayın
3. Bot size hisse sembolünü sorduğunda (örn. AKBNK, THYAO, TUPRS) istediğiniz hissenin sembolünü gönderin
4. Daha sonra hisse alım fiyatını girin
5. Son olarak aldığınız adet/lot miktarını belirtin

## 🆕 Güncellemeler

Sürekli yeni özellikler eklenmeye devam edilecek. Yakında gelecek özellikler:
- Fiyat alarmları 
- Piyasa haberleri entegrasyonu
- Hisse grafikleri

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için 'LICENSE' dosyasına bakın.

---

⭐ Projeyi beğendiyseniz yıldız vermeyi unutmayın!
