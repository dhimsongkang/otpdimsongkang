"""Test scraper parser on real page with correct keys."""
import sys, os
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding='utf-8')

from config import COOKIES, IVASMS_URL
from ivasms_scraper import IVASMSClient
from bot import format_otp_message

client = IVASMSClient(cookies=COOKIES, base_url=IVASMS_URL)
sms_list = client.get_all_sms()
print(f"Total SMS fetched: {len(sms_list)}")
for i, sms in enumerate(sms_list, 1):
    print(f"\n--- SMS #{i} Raw Dict ---")
    print(sms)
    print("\n--- Formatted Telegram Message ---")
    print(format_otp_message(sms))
