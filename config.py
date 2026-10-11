# ═══════════════════════════════════════════════════════════════
#  IVASMS OTP BOT - KONFIGURASI
#  Isi semua konfigurasi di bawah ini sebelum menjalankan bot
# ═══════════════════════════════════════════════════════════════

# ────────────────────────────────────────────
#  TELEGRAM BOT CONFIG
# ────────────────────────────────────────────

# Token dari @BotFather
BOT_TOKEN = "8773155835:AAGJjiP2soccLPvic0N3zWOYrBpB-qWWGuY"

# Chat ID grup Telegram (gunakan angka negatif untuk grup)
# Jalankan get_chat_id.py untuk mendapatkan Chat ID
GROUP_CHAT_ID = "-1003979578338"

# Link grup OTP (untuk tombol "Grup OTP")
GROUP_LINK = "https://t.me/dimsongotp"

# Link tombol NUMBER dan OWNER (sementara kosong / placeholder link grup lain)
NUMBER_LINK = ""  # Isi link grup/channel untuk tombol NUMBER, contoh: "https://t.me/your_number_group"
OWNER_LINK = ""   # Isi link grup/channel/kontak untuk tombol OWNER, contoh: "https://t.me/your_owner_link"

# Nama bot yang muncul di pesan
BOT_NAME = "OTP_BOT"

# ────────────────────────────────────────────
#  IVASMS CONFIG
# ────────────────────────────────────────────

# URL IVASMS
IVASMS_URL = "https://www.ivasms.com"

# Kredensial akun IVASMS untuk auto-login otomatis
IVASMS_EMAIL = "lesehp60nz@deltajohnsons.com"
IVASMS_PASSWORD = "scorpion998"

# Endpoint halaman SMS Received
IVASMS_SMS_ENDPOINT = "/portal/sms/received"

# YesCaptcha Client Key untuk bypass Cloudflare Turnstile
YESCAPTCHA_KEY = "b2a81640d7b006b1d5c15459ec72366b442af456139860"

# Interval polling dalam detik (10 detik agar tidak terkena rate limit IVASMS)
POLL_INTERVAL = 10

# ────────────────────────────────────────────
#  ELITE-SMS CONFIG (https://elite-sms.com/api)
# ────────────────────────────────────────────
ELITE_SMS_ENABLED = True
ELITE_SMS_URL = "https://elite-sms.com/api"
ELITE_SMS_API_KEY = "d3a3c3c16dd897f09dfa3778a92d04331a33f876"

# ────────────────────────────────────────────
#  COOKIES IVASMS (dari browser)
# ────────────────────────────────────────────

COOKIES = {
    "ivas_sms_session": "eyJpdiI6IlI0cml6WEVlcGsyN3U5aW96WVNrZkE9PSIsInZhbHVlIjoiTFhOS0hVeVdpK1E1Z2c0UlZoRzJ4UjM5NmVOZVc2RjA0eVo0QTh6VFQ5MVhZOUhTd2FPVWpROW5JZ1hiZURZT3RFbFRkWWdqRlFIQVZIY0gzZmZrdjV2cW5CVmJUNU9sQ2FCQzgwUllxa1FyaEdZeVh6UU1EZFdSWXNLR2p1YlEiLCJtYWMiOiI3ODllZDRhODc0Y2FkMjA5YTQ1YjAzZTI0ZmE5YWUzZjMxZGI4OTljYzkxZjMxYjgyYTQxNGUyZjFmOGMyYmEzIiwidGFnIjoiIn0=",
    "XSRF-TOKEN": "eyJpdiI6IlRsRUdUcDNHSC96bXdaSVV4S0V5eHc9PSIsInZhbHVlIjoibzlPZEdaeXZSeVphYU1mQ1hESENnTDhwZDc3d205aXgwMzFJWUZYSmtGak5nRTZuVU9pSklZdkRRbWZyT0pQbm9rNDlHbkN3S1JSU2tMaE1zeUdGTTEyN0xSYzhYYTQzMFRSbHZrek91TVd6N01rNHhmUkdPdGpvRlo3cTNUR1QiLCJtYWMiOiI3MDI4YjZhYjZlYzg4MDIwOTA1YzM5ZGI4ZmQ0ZjdkMmMyOWU0NmM0NjM1NWUyMjJiZTI1MzZjOTBjYmNiOTUyIiwidGFnIjoiIn0=",
    "cf_clearance": "KXp41Bf7OPEIREcc2vq5p6KKb6mfmvVijAUfdn1nfQc-1791735310-1.2.1.1-5mazleGKja.6LwwHnAjNQgrS03k58LyjY5hawfxgYRvdYm1S_2qhcTyEMJkYBnbi5QnDWOdTS5fGETK5U2sOGfOCg42OV9ltVqLUGOVBrk13NP45HhzXooTHiigtD8m4K.5xYAMN4aw37eBzI2XXLwe5S_1kFykVhVGTqxJU5s4mBmPHf7sdmEu1g5LD6HWGDNXo62EZf7ZZiN43f_QNgPJ5oTbYs75m1jviA5pP3PMszjC7k7ozUe6Ziy8lXewJ638NST9_XTLDEOZJJdTeSxXpgrpl5ifaS4ZTIAYlQZ2co6a7a7qvVwOtUl13Nxlp1yYe6A4oSj2RL18uwYOoGRrIYOq7DFnD77EBI202L5xSIPiblJEMBYmOOrwBg4izc60RMCQjsQo4Mzt3uSz01RdHPGAORiELReDXRPLAyREHaT8ORyeZ1Y1QWOtRN4A22H8JLiS25oScCyiU0XpgYWWKU9m0zG_vnygJ1C3W_RrAQ_th67t6lsg7w_vSyS9kppxJ.QG4TK49L4z8lrswOA",
}
