"""Test POST to /portal/sms/received/getsms."""
import sys, os, re
from datetime import datetime
import cloudscraper
from bs4 import BeautifulSoup
from config import COOKIES, IVASMS_URL

scraper = cloudscraper.create_scraper()

for name, value in COOKIES.items():
    if value:
        scraper.cookies.set(name, value)

# Try both common Firefox UAs
test_uas = [
    'Mozilla/5.0 (X11; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0',
    'Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0',
    'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0',
]

for ua in test_uas:
    scraper.headers.update({
        'User-Agent': ua,
        'Accept': 'text/html, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': IVASMS_URL,
        'Referer': f"{IVASMS_URL}/portal/sms/received",
    })
    r_page = scraper.get(f"{IVASMS_URL}/portal/sms/received", timeout=10)
    print(f"[{ua[:35]}...] GET status: {r_page.status_code}")
    if r_page.status_code == 200:
        print(f"✅ BINGO! Cocok dengan UA: {ua}")
        break

# Find _token
token_match = re.search(r"f\.append\('_token',\s*[\"']([^\"']+)[\"']\)", r_page.text)
if not token_match:
    token_match = re.search(r'name=["\']_token["\']\s+value=["\']([^"\']+)["\']', r_page.text)

token = token_match.group(1) if token_match else None
print(f"Extracted _token: {token}")

# Form data
today = datetime.now().strftime("%Y-%m-%d")
post_data = {
    'from': today,
    'to': today,
    '_token': token or ""
}

r_sms = scraper.post(f"{IVASMS_URL}/portal/sms/received/getsms", data=post_data, timeout=15)
print(f"POST getsms status: {r_sms.status_code}")
print(f"Response length: {len(r_sms.text)}")

with open("debug_getsms.html", "w", encoding="utf-8") as f:
    f.write(r_sms.text)

print("Saved to debug_getsms.html")
print("Response preview:")
print(r_sms.text[:1500])
