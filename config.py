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

# Interval polling dalam detik (10 detik agar tidak terkena rate limit IVASMS)
POLL_INTERVAL = 10

# ────────────────────────────────────────────
#  COOKIES IVASMS (dari browser)
# ────────────────────────────────────────────

COOKIES = {
    "ivas_sms_session": "eyJpdiI6IlJTZVJOV0p2cjVyVGJEeXh2dmlETGc9PSIsInZhbHVlIjoiamFRV1JZaVYvTWNOejBGLzJnS3FuY085K2puWlE0blU2R1VQS2UyTWJUSTAxNVRvK3AwZUhsYkFrRUZxSHhlMVd6TXREU1dJYy8xTklHZlgwSnVQZkJwOXFOdUMxQXEyWi9MaXg1NDFvRVVOaHlmdkJmMlpIOTlLeHo4QXN0QTAiLCJtYWMiOiJjZmMwZTE2NTBmMjEyNTllMWFjOTFiOTZjMDQ5NTE1NThmNTYyZTg3ZDhmMzc0OGIyOTIwN2ZmYWQ0YTdlYWI1IiwidGFnIjoiIn0=",
    "XSRF-TOKEN": "eyJpdiI6IlJWWDRNc1lQOURoS3lUZDNjeTgzQ0E9PSIsInZhbHVlIjoieEh0UVZVdGJwZlYyamJNeXFuV1JaTEFJbkNtUzhYVitOQW1kV2cvRVdRbGxFbURSeFlxVFcwUGVxSzRJNnRZZXlXek1MeHRYYlp3Vm9rTmN3Ti91NjZhYzJ6UGk4TGwzMUh1WElmRlVkbHFzbk5SVGwxWVN3VklNM1R6YldoNW0iLCJtYWMiOiI2YTJkMTc5ZjlhNTJlMjQzNDI3MjQ1MjBiZDNmMTg4Nzg1NjI4NWU3YjIwMzAwYWZiOTJlNGI1YWJlYzE2ZDc2IiwidGFnIjoiIn0=",
    "cf_clearance": "K0vOHd66brxhqvHcZ9sZGLbfDj.CirJUnGQ_E5kkvqY-1791711956-1.2.1.1-y1E2EIQu8SFyMmaz_uqJswou5_mWdntaolQufI6hjDOf2cEiUffUfopHNE3350Y9.uFdCreUTTuc0iihYGeEx1Q8m74zQd1zc8jZ4yuBRJ7udnT5hjjBnFhziNPiRtL78GrRqgqMIvY1BM4vpwi.IOwAPW36U66UMwvVb23iK.XOIy8dxHuhg8Mn7ha1B.s6_SDw4hC.MMvRugxcRrz9K.kNjHPkG955KhMkHbYfvPmK61PXbonw072cJKdi2M5Y8qdDEjvuh.zEe9L2s162xB3v9dxohql6Ei0q1kKeFtzyt.RpscpoRPFbdR7VUdwP5wX4qhx9ItFO_3plQ5Oc68pTCRoMEcFoXgu8pQWsTikLCALfblMGbYtPF1I3RnoMHCFyopHMH4RL2gKLk.negeZJ0pQZSOFUJxeMWVAnT3eThBSYoky5hDZC5abmZB2iTtWA_O52kLzyIREmBFBPnRO0uyRG1jq1TMiNTjZUFKAyrpcr5eSw2ZXJaF02HO3gWTDqM8Gkd8hg6TiX0PYrYg",
}
