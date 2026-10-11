"""Inspect debug_page.html table structure."""
from bs4 import BeautifulSoup

with open("debug_page.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

tables = soup.find_all("table")
print(f"Total tables: {len(tables)}")
for idx, tbl in enumerate(tables):
    print(f"\n--- Table {idx+1} (id={tbl.get('id')}, class={tbl.get('class')}) ---")
    headers = [th.get_text(strip=True) for th in tbl.find_all("th")]
    print(f"Headers: {headers}")
    rows = tbl.find_all("tr")
    print(f"Total rows: {len(rows)}")
    for r in rows[:6]:
        cols = [td.get_text(strip=True) for td in r.find_all(["td", "th"])]
        print(f"  Row: {cols}")

# Check if there are scripts or ajax data
scripts = soup.find_all("script")
print(f"\nTotal scripts: {len(scripts)}")
for s in scripts:
    text = s.get_text()
    if "sms" in text.lower() or "received" in text.lower() or "datatable" in text.lower() or "ajax" in text.lower():
        print(f"\nRelevant script preview: {text[:500]}...")
