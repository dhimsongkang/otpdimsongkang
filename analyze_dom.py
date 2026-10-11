import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
with open('debug_test_numbers.html', 'r', encoding='utf-8') as f:
    html = f.read()

from bs4 import BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Find TerminationDetials function
for script in soup.find_all('script'):
    content = script.string or ''
    if 'TerminationDetials' in content or 'AddTestNumber' in content or 'addtest' in content.lower():
        print('=== Relevant Script ===')
        print(content[:4000])
        print('...\n')

# Find add-related forms or links
print('\n=== ALL forms ===')
for form in soup.find_all('form'):
    print(f'Form action={form.get("action")}, method={form.get("method")}')
    print(f'  Inner HTML: {str(form)[:600]}')
    print()

# Find add number link/button
print('\n=== Search for Add Number pattern ===')
for a in soup.find_all('a'):
    href = a.get('href', '')
    text = a.get_text(strip=True).lower()
    if 'add' in text or 'add' in href:
        print(f'  a: text="{a.get_text(strip=True)}", href={href}, class={a.get("class")}')

for btn in soup.find_all('button'):
    text = btn.get_text(strip=True).lower()
    if 'add' in text or 'new' in text:
        print(f'  btn: text="{btn.get_text(strip=True)}", onclick={btn.get("onclick")}')

# Find modal content for add
print('\n=== Modals ===')
for modal in soup.find_all(class_='modal'):
    mid = modal.get('id', 'no-id')
    modal_text = modal.get_text(strip=True)[:200]
    print(f'  Modal id={mid}: {modal_text}')
    # Show form elements inside modal
    for inp in modal.find_all(['input', 'select', 'textarea']):
        print(f'    Element: {inp.name}, name={inp.get("name")}, id={inp.get("id")}, type={inp.get("type")}')

# Find table IDs
print('\n=== Tables ===')
for t in soup.find_all('table'):
    tid = t.get('id', 'no-id')
    print(f'  Table id={tid}')
