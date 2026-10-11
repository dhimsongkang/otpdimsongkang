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

scraper.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36 Edg/155.0.0.0',
    'Accept': 'text/html, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.9',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': IVASMS_URL,
    'Referer': f"{IVASMS_URL}/portal/sms/received",
})

# First GET the page to get a fresh _token
r_page = scraper.get(f"{IVASMS_URL}/portal/sms/received", timeout=15)
print(f"GET page status: {r_page.status_code}")

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
