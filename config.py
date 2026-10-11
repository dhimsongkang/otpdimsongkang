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
    "_fbp": "fb.1.1791714419383.358375619963314777",
    "cf_clearance": "C9rn_hwJDpsYBLzBbZyMwz0ZYO9VEDKbQnbfto_NwTs-1791743886-1.2.1.1-St.T1Z0bpaUlj1um9IHTuvzVS8SoppQ6rDWqafy_qGdMF.HXjpMdphP6Llj0WEHyu9Z1gUbgiCV8Q0GcOOlQzfzBrQGGlNEYv4Hyb0y5qLoHQJa1nSghFgZNckvgHEewQVPqH1MAV3ZRo2ccy7zxsO2SLl4g3tZlc5RoYXthAQBHf_r2spPIUOgW7gmNj4e.LdF08r_VxlP3SYiH0Y0XdskJkdG4DKJjoYO.mQmpIOm2adVnjAB7voJoK1yz4gow0iqLaV7IVZ92dwFNZbw.u9VIk8K7RoQfikD6kMntA6sUGigtBJAV.S7Ewp2SZQb2Ig9W9.94F82HvTIjBbob_4r18fvy_oFxu2ZPRKY1xh8lKTKiugVPFPoupcKKDIeLev3itkWWZKX6NcjvJDJNkZf7Bn_zTiLR7NiWLAiDIHsZWXUEaT2vJxkKrRAiY3rQGbP3JlgEAvCDy0sPyxazNm4pMjE7KJQshX5jpcFOqGVG81ypgXy21ROXYDqzZuenSptkddwqG9RrL3BcFE7mUQ",
    "XSRF-TOKEN": "eyJpdiI6InhiYjBQeVUvSFhobmNFSHlGa1FoWWc9PSIsInZhbHVlIjoibDdmV2JvZEVvYTZQZXBxN3lTWHlmaHVjYnM5Ky9qbUthNTR2TXBYUURsbmZrMWhpY0xVdVRudWtqVjlEaUFsc1RoWmxUd1E3VkJTYW1aYVBVaHhTbU4zdGxMalR4TklOOElxbHBnWSt3NlRyTmFVeEoybDJtYzJVYW5FelluODgiLCJtYWMiOiI2Zjk2ZjNlZDI2OGQxZGY3NDBhMjAwNTA0NWFhOTI1YzQ2OWQzNjMwMTJkY2U4NTNiZjBkMTE4NTYwM2U4ZmNiIiwidGFnIjoiIn0%3D",
    "ivas_sms_session": "eyJpdiI6InNxNkVuTUR4d0dqMFdpRHJqdFlXYmc9PSIsInZhbHVlIjoiVnFJdlNBVGRhL240Q2pWNzZRem8xbHdIaUxTdG1qZnVLWjBVRHlCbUNlZ2RUZ1NlODI3R0VzbjNXaEEyVXFybWZKdEhweHQ1NDNPb25mYkdMU3Z2ZSswR0tkekdJZzRHZ2sydHhzdnNFU3lNSmFVRTI3K293aXJwWXYwMGRkRGgiLCJtYWMiOiIxZjY5ODlmMDEwZGMzZTRhYjMyMDY1YWU2YWY4M2Y5N2RmNTQwMDIzNzQ5MzZmYmEyYTU3ZGIxZGJiODY3ODVkIiwidGFnIjoiIn0%3D",
}
