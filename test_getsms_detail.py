"""Test fetching messages for a number."""
import sys, re
import cloudscraper
from config import COOKIES, IVASMS_URL

scraper = cloudscraper.create_scraper()
for name, value in COOKIES.items():
    if value:
        scraper.cookies.set(name, value)

scraper.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36 Edg/155.0.0.0',
    'Accept': 'text/html, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': IVASMS_URL,
    'Referer': f"{IVASMS_URL}/portal/sms/received",
})

# Get token
r_page = scraper.get(f"{IVASMS_URL}/portal/sms/received", timeout=15)
token = re.search(r"f\.append\('_token',\s*[\"']([^\"']+)[\"']\)", r_page.text).group(1)

post_data = {
    '_token': token,
    'start': '2026-10-11',
    'end': '2026-10-11',
    'Number': '4915219700147',
    'Range': 'GERMANY 1100'
}

r_sms = scraper.post(f"{IVASMS_URL}/portal/sms/received/getsms/number/sms", data=post_data, timeout=15)
print(f"Status: {r_sms.status_code}")
print("Response content:")
print(r_sms.text)

with open("debug_sms_detail.html", "w", encoding="utf-8") as f:
    f.write(r_sms.text)
