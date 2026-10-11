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
    "cf_clearance": "0A8Ozab_6sIz41LgaGBNRIJcoHi0rSl8mrVvvM4zHYY-1791747187-1.2.1.1-YsrEfjRXoFWcrp.BuBUDVA5sfGfR90F94.R6opT3734uNd3wEtpOKUWUiWvBhFqxnIzmePI_EE2k_78yrIS.MgBWmBEvTWRq._cqaCzC58YGZSUxaqCwRmtSW.PKbD4axZNVlAR7_Ec978Xb0gEcJWPvGti.wBgiJxSPQ1bgsacOyh8Dt9R1C5Os_T.cy8mGot2Shq73npjFE8y2HMB7v4yQdMPfpFEG3DEI8FYGwF70_pXcI3PaQOx4nBIzqVQZu2NBzwSRxXLOsfgWdg15c3zrdQPCaDtXP3kK6YHviYCr.rzkrMGn0wfbQKmc1rBKaTgjjJI1i6Y8PFlq7ildjzJ62d7sTi._bXfochGq0KW5VOdfwkPBEOqrEck8AZ1VRiDENSTvGiAUkmKL_r082Mc5TojtCjDjmFnGqEPJdpXzaTYuiaDJBYKNYP1D5gxyd.Edrg78UeNm5cF9JfguGCICnwxrvGN1l0QPXpRXRUEVESs5l_BCu5rYAGTWcBSsMOzp7a2b3f8ZyrAEbOk.Tg",
    "XSRF-TOKEN": "eyJpdiI6IkN0cGlrU0J6SE9vV2lZQ1ZpUmNYemc9PSIsInZhbHVlIjoiTFBkVVRGRmtRVHRET1JMcDAzZEU5dG9jL28zc3F0Q1pMQzJ2WUdDSDhtNlVlUm1neFBCWXdOcXFWMFpMU1pzcjBkdk5ZM2ZqbFNwaHZnYWpWYW0ya1ZUSVR0ZkpjRnNGTWw1K2JnaUszR3BwQnVlRUlHcEYrSFFkdHRJWGNmazEiLCJtYWMiOiJmNDE2MjNlYTcyNzE5M2IzOWY1OGE2MTIwY2ExYTdkZTQ5NDMyMjU3MGRmNWNjYWMwNTU0OGFhYzNhNThlMmM3IiwidGFnIjoiIn0%3D",
    "ivas_sms_session": "eyJpdiI6Im13NjNnTVNvaDFEekxiNnBFRHV6R0E9PSIsInZhbHVlIjoieC9KbFFyczlWNi9BM1UyZ0RGTDhpbTRvcjVJRDZtVS9iMnpHcEJ3ditDUXcxZkwwQ0kzYnBSY1ZCWWtyNzdxUm8rRStkVm9RRnNSaE9veHBNZEorMng0MGN3YXZPTVFTM3RERHg0a0ozenFzdWR2WmVVelFnODhNY05iblNHeHciLCJtYWMiOiI0ODIzZjI5MjZhMDNlMmQ3MTIzMWJlZGY2NmQ5Y2YzNDgzNWZjYWJkMDFkOTVjZjQ2MWExMjA5ODY0YWQyMTc1IiwidGFnIjoiIn0%3D",
}
