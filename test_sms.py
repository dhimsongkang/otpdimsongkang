import sys
import logging
from datetime import datetime, timezone, timedelta
from config import COOKIES, IVASMS_URL, GROUP_CHAT_ID
from ivasms_scraper import IVASMSClient, format_otp_message

logging.basicConfig(level=logging.INFO, format="%(asctime)s │ %(levelname)-8s │ %(message)s")
logger = logging.getLogger("TestScraper")

def main():
    print("=" * 60)
    print("🔍 TESTING SCRAPER & CEK SMS DI IVASMS")
    print("=" * 60)

    client = IVASMSClient(COOKIES, IVASMS_URL)
    
    print("\n1. Memeriksa koneksi IVASMS...")
    if not client.check_connection():
        print("❌ Sesi cookies IVASMS expired atau belum login!")
        print("💡 Coba jalankan: python cookie_sync.py")
        return
    print("✅ Sesi IVASMS VALID!")

    utc_now = datetime.now(timezone.utc)
    utc_yesterday = (utc_now - timedelta(days=1)).strftime("%Y-%m-%d")
    local_today = datetime.now().strftime("%Y-%m-%d")

    print(f"\n2. Mengambil SMS dengan rentang tanggal:")
    print(f"   Dari : {utc_yesterday} (UTC)")
    print(f"   Sampai: {local_today} (Lokal)")

    sms_list = client.get_all_sms()
    print(f"\n3. Total SMS ditemukan: {len(sms_list)}")

    if not sms_list:
        print("ℹ️ Belum ada SMS yang masuk dalam rentang tanggal ini.")
    else:
        print("\n📋 5 SMS Terakhir yang ditemukan:")
        print("-" * 60)
        for i, sms in enumerate(sms_list[:5], 1):
            print(f"[{i}] Nomor   : {sms.get('phone')}")
            print(f"    Sender  : {sms.get('sender')}")
            print(f"    Waktu   : {sms.get('timestamp')}")
            print(f"    OTP     : {sms.get('otp')}")
            print(f"    Pesan   : {sms.get('message')[:70]}...")
            print("-" * 60)

    print("\n✅ Selesai cek IVASMS!")

    # 4. Cek Elite-SMS
    print("\n" + "=" * 60)
    print("🔍 TESTING ELITE-SMS (https://elite-sms.com/api)")
    print("=" * 60)
    try:
        from config import ELITE_SMS_ENABLED, ELITE_SMS_URL, ELITE_SMS_API_KEY
        from elite_sms_client import EliteSMSClient

        if not ELITE_SMS_ENABLED or not ELITE_SMS_API_KEY:
            print("⚠️ Elite-SMS tidak diaktifkan di config.py")
        else:
            elite_client = EliteSMSClient(ELITE_SMS_API_KEY, ELITE_SMS_URL)
            print("1. Memeriksa koneksi Elite-SMS API...")
            if elite_client.check_connection():
                print("✅ Koneksi Elite-SMS VALID (ONLINE)!")
            else:
                print("⚠️ Status Elite-SMS belum ONLINE atau respon tidak sesuai.")

            print("2. Mengambil live OTP feed dari Elite-SMS...")
            elite_sms_list = elite_client.get_all_sms(limit=10)
            print(f"3. Total SMS ditemukan: {len(elite_sms_list)}")
            if elite_sms_list:
                print("\n📋 SMS Terakhir dari Elite-SMS:")
                print("-" * 60)
                for i, sms in enumerate(elite_sms_list[:5], 1):
                    print(f"[{i}] Nomor   : {sms.get('phone')} ({sms.get('flag')} {sms.get('country_code')})")
                    print(f"    Service : {sms.get('sender')}")
                    print(f"    Waktu   : {sms.get('timestamp')}")
                    print(f"    OTP     : {sms.get('otp')}")
                    print(f"    Pesan   : {sms.get('message')[:70]}...")
                    print("-" * 60)
    except Exception as e:
        print(f"❌ Error testing Elite-SMS: {e}")

    print("\n✅ Seluruh pengujian selesai!")

if __name__ == "__main__":
    main()
