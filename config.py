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
#  COOKIES IVASMS (dari browser)
# ────────────────────────────────────────────

COOKIES = {
    "ivas_sms_session": "eyJpdiI6IlI0cml6WEVlcGsyN3U5aW96WVNrZkE9PSIsInZhbHVlIjoiTFhOS0hVeVdpK1E1Z2c0UlZoRzJ4UjM5NmVOZVc2RjA0eVo0QTh6VFQ5MVhZOUhTd2FPVWpROW5JZ1hiZURZT3RFbFRkWWdqRlFIQVZIY0gzZmZrdjV2cW5CVmJUNU9sQ2FCQzgwUllxa1FyaEdZeVh6UU1EZFdSWXNLR2p1YlEiLCJtYWMiOiI3ODllZDRhODc0Y2FkMjA5YTQ1YjAzZTI0ZmE5YWUzZjMxZGI4OTljYzkxZjMxYjgyYTQxNGUyZjFmOGMyYmEzIiwidGFnIjoiIn0=",
    "XSRF-TOKEN": "eyJpdiI6IlRsRUdUcDNHSC96bXdaSVV4S0V5eHc9PSIsInZhbHVlIjoibzlPZEdaeXZSeVphYU1mQ1hESENnTDhwZDc3d205aXgwMzFJWUZYSmtGak5nRTZuVU9pSklZdkRRbWZyT0pQbm9rNDlHbkN3S1JSU2tMaE1zeUdGTTEyN0xSYzhYYTQzMFRSbHZrek91TVd6N01rNHhmUkdPdGpvRlo3cTNUR1QiLCJtYWMiOiI3MDI4YjZhYjZlYzg4MDIwOTA1YzM5ZGI4ZmQ0ZjdkMmMyOWU0NmM0NjM1NWUyMjJiZTI1MzZjOTBjYmNiOTUyIiwidGFnIjoiIn0=",
}
