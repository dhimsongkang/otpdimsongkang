"""
Inspect halaman Test Numbers IVASMS untuk memahami DOM structure
"""
import asyncio
import os
import sys

# Use playwright with persistent context to bypass Cloudflare
from playwright.async_api import async_playwright

USER_DATA_DIR = os.path.abspath("browser_profile")


async def inspect():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            channel="msedge",
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-gpu",
                "--window-position=-2000,-2000",
            ]
        )
        page = context.pages[0] if context.pages else await context.new_page()

        print("[*] Navigating to test numbers page...")
        try:
            await page.goto("https://www.ivasms.com/portal/numbers/test", timeout=30000, wait_until="domcontentloaded")
        except Exception as e:
            print(f"[!] Navigation warning: {e}")

        # Wait for Cloudflare
        for _ in range(15):
            t = await page.title()
            if "Just a moment" not in t:
                break
            await asyncio.sleep(1)

        # Check if redirected to login
        if "/login" in page.url:
            print("[!] Redirected to login page. Session expired.")
            await context.close()
            return

        await asyncio.sleep(3)

        # Get the page title
        title = await page.title()
        print(f"[*] Page title: {title}")
        print(f"[*] URL: {page.url}")

        # Get full HTML
        html = await page.content()
        with open("debug_test_numbers.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[*] Saved full HTML to debug_test_numbers.html ({len(html)} bytes)")

        # Look for key elements
        # Forms
        forms = await page.query_selector_all("form")
        print(f"\n[*] Found {len(forms)} forms:")
        for i, form in enumerate(forms):
            action = await form.get_attribute("action")
            method = await form.get_attribute("method")
            form_id = await form.get_attribute("id")
            inner = await form.inner_html()
            print(f"  Form {i}: action={action}, method={method}, id={form_id}")
            print(f"    Inner HTML (first 500 chars): {inner[:500]}")

        # Buttons
        buttons = await page.query_selector_all("button")
        print(f"\n[*] Found {len(buttons)} buttons:")
        for btn in buttons:
            text = await btn.inner_text()
            btn_type = await btn.get_attribute("type")
            btn_class = await btn.get_attribute("class")
            onclick = await btn.get_attribute("onclick")
            data_target = await btn.get_attribute("data-target")
            print(f"  Button: text='{text.strip()}', type={btn_type}, class={btn_class}, onclick={onclick}, data-target={data_target}")

        # Links with "add" in text or href
        links = await page.query_selector_all("a")
        print(f"\n[*] Found {len(links)} links, filtering for 'add' or 'number':")
        for link in links:
            text = (await link.inner_text()).strip().lower()
            href = await link.get_attribute("href") or ""
            if "add" in text or "add" in href or "number" in text.lower() or "test" in href:
                print(f"  Link: text='{text}', href={href}")

        # Select elements
        selects = await page.query_selector_all("select")
        print(f"\n[*] Found {len(selects)} select elements:")
        for sel in selects:
            name = await sel.get_attribute("name")
            sel_id = await sel.get_attribute("id")
            options = await sel.query_selector_all("option")
            option_texts = []
            for opt in options[:20]:  # Limit to first 20
                opt_text = (await opt.inner_text()).strip()
                opt_val = await opt.get_attribute("value")
                option_texts.append(f"{opt_val}='{opt_text}'")
            print(f"  Select: name={name}, id={sel_id}, options={option_texts}")

        # Input elements
        inputs = await page.query_selector_all("input")
        print(f"\n[*] Found {len(inputs)} input elements:")
        for inp in inputs:
            name = await inp.get_attribute("name")
            inp_type = await inp.get_attribute("type")
            inp_val = await inp.get_attribute("value")
            inp_id = await inp.get_attribute("id")
            placeholder = await inp.get_attribute("placeholder")
            print(f"  Input: name={name}, type={inp_type}, value={inp_val[:50] if inp_val else 'None'}, id={inp_id}, placeholder={placeholder}")

        # Tables
        tables = await page.query_selector_all("table")
        print(f"\n[*] Found {len(tables)} tables:")
        for i, table in enumerate(tables):
            table_id = await table.get_attribute("id")
            headers = await table.query_selector_all("th")
            header_texts = [await h.inner_text() for h in headers]
            rows = await table.query_selector_all("tr")
            print(f"  Table {i}: id={table_id}, headers={header_texts}, rows={len(rows)}")
            # Print first 3 rows
            for j, row in enumerate(rows[:4]):
                cells = await row.query_selector_all("td")
                cell_texts = [(await c.inner_text()).strip()[:50] for c in cells]
                if cell_texts:
                    print(f"    Row {j}: {cell_texts}")

        # Modals
        modals = await page.query_selector_all(".modal")
        print(f"\n[*] Found {len(modals)} modals:")
        for modal in modals:
            modal_id = await modal.get_attribute("id")
            modal_html = await modal.inner_html()
            print(f"  Modal: id={modal_id}")
            print(f"    Inner HTML (first 800 chars): {modal_html[:800]}")

        # Look for DataTables or AJAX
        scripts = await page.query_selector_all("script")
        print(f"\n[*] Found {len(scripts)} script tags, searching for relevant JS...")
        for script in scripts:
            src = await script.get_attribute("src")
            content = await script.inner_html()
            if content and ("add" in content.lower() or "number" in content.lower() or "range" in content.lower() or "test" in content.lower() or "ajax" in content.lower()):
                print(f"  Script (src={src}): {content[:1000]}")

        await context.close()
        print("\n[*] Done!")


asyncio.run(inspect())
