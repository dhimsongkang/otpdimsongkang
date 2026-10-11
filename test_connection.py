"""Debug 403 - test with correct User-Agent."""
import sys, os
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding='utf-8')

import cloudscraper
from config import COOKIES, IVASMS_URL

scraper = cloudscraper.create_scraper()

# Load cookies
for name, value in COOKIES.items():
    if value:
        scraper.cookies.set(name, value)

# Use EXACT same User-Agent as the browser
scraper.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36 Edg/155.0.0.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
})

print("--- Testing with correct User-Agent ---")
r = scraper.get(f"{IVASMS_URL}/portal/sms/received", timeout=15)
print(f"Status: {r.status_code}")
print(f"URL: {r.url}")
print(f"Content length: {len(r.text)}")

if r.status_code == 200:
    # Save for analysis
    with open("debug_page.html", "w", encoding="utf-8") as f:
        f.write(r.text)
    print("SAVED to debug_page.html")
    
    if "SMS Received" in r.text:
        print("SUCCESS - Found SMS Received page!")
    elif "login" in r.text.lower():
        print("REDIRECTED to login - session expired")
    
    # Show title
    import re
    title = re.search(r'<title>(.*?)</title>', r.text)
    if title:
        print(f"Page title: {title.group(1)}")
else:
    print(f"Response: {r.text[:300]}")
