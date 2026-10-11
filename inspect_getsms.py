"""Print the full GetSMS script from debug_page.html."""
from bs4 import BeautifulSoup

with open("debug_page.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

for s in soup.find_all("script"):
    text = s.get_text()
    if "function GetSMS" in text:
        print("=== GetSMS Script ===")
        print(text)
