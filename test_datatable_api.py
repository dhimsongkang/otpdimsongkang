"""
Test DataTable API via Playwright - with proper Cloudflare wait
"""
import asyncio
import json
import sys
import os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.async_api import async_playwright

USER_DATA_DIR = os.path.abspath("browser_profile")


async def test_api():
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
            await page.goto("https://www.ivasms.com/portal/numbers/test", timeout=45000, wait_until="networkidle")
        except Exception as e:
            print(f"[!] Nav warning: {e}")

        # Wait for Cloudflare + page load
        for _ in range(20):
            t = await page.title()
            url = page.url
            print(f"  Title: {t}, URL: {url}")
            if "Just a moment" not in t and "/portal" in url:
                break
            await asyncio.sleep(2)

        await asyncio.sleep(5)

        # Check if we're on the right page
        title = await page.title()
        url = page.url
        print(f"[*] Final page: title='{title}', url={url}")

        if "/login" in url:
            print("[!] Redirected to login. Auto-login needed.")
            await context.close()
            return

        # Wait for DataTable to load
        try:
            await page.wait_for_selector("#TestNumber", timeout=10000)
            print("[*] DataTable found!")
        except:
            print("[!] DataTable not found")

        # Use DataTable API via JS
        result = await page.evaluate("""
            () => {
                try {
                    const dt = window.LaravelDataTables?.TestNumber;
                    if (!dt) return {error: 'DataTable not initialized'};
                    
                    const data = dt.rows().data().toArray();
                    return {
                        total: dt.page.info().recordsTotal,
                        filtered: dt.page.info().recordsDisplay,
                        rows: data.slice(0, 5)
                    };
                } catch(e) {
                    return {error: e.message};
                }
            }
        """)

        print(f"\n[*] DataTable result: {json.dumps(result, indent=2, default=str)[:3000]}")

        # Also try direct fetch with proper CSRF
        csrf = await page.evaluate("() => document.querySelector('meta[name=csrf-token]')?.content || document.querySelector('input[name=_token]')?.value || ''")
        print(f"\n[*] CSRF token: {csrf[:20]}...")

        # Get data via fetch
        api_result = await page.evaluate("""
            async (csrf) => {
                try {
                    const url = new URL('/portal/numbers/test', window.location.origin);
                    url.searchParams.set('draw', '1');
                    url.searchParams.set('start', '0');
                    url.searchParams.set('length', '10');
                    url.searchParams.set('columns[0][data]', 'range');
                    url.searchParams.set('columns[0][name]', 'terminations.range');
                    url.searchParams.set('columns[0][searchable]', 'true');
                    url.searchParams.set('columns[0][orderable]', 'true');
                    url.searchParams.set('columns[1][data]', 'test_number');
                    url.searchParams.set('columns[1][name]', 'terminations.test_number');
                    url.searchParams.set('columns[2][data]', 'term');
                    url.searchParams.set('columns[2][name]', 'term');
                    url.searchParams.set('columns[3][data]', 'A2P');
                    url.searchParams.set('columns[3][name]', 'A2P');
                    url.searchParams.set('columns[4][data]', 'Limit_Range');
                    url.searchParams.set('columns[4][name]', 'Limit_Range');
                    url.searchParams.set('columns[5][data]', 'limit_did_a2p');
                    url.searchParams.set('columns[5][name]', 'limit_did_a2p');
                    url.searchParams.set('columns[6][data]', 'limit_cli_did_a2p');
                    url.searchParams.set('columns[6][name]', 'limit_cli_did_a2p');
                    url.searchParams.set('columns[7][data]', 'created_at');
                    url.searchParams.set('columns[7][name]', 'terminations.created_at');
                    url.searchParams.set('columns[8][data]', 'action');
                    url.searchParams.set('columns[8][name]', 'action');
                    url.searchParams.set('order[0][column]', '8');
                    url.searchParams.set('order[0][dir]', 'desc');
                    url.searchParams.set('search[value]', '');
                    
                    const resp = await fetch(url.toString(), {
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                            'Accept': 'application/json'
                        }
                    });
                    return await resp.json();
                } catch(e) {
                    return {error: e.message};
                }
            }
        """, csrf)

        total = api_result.get('recordsTotal', 'N/A')
        filtered = api_result.get('recordsFiltered', 'N/A')
        data = api_result.get('data', [])
        print(f"\n[*] API: total={total}, filtered={filtered}, rows={len(data)}")

        # Print first few rows
        for i, row in enumerate(data[:5]):
            # Clean the action HTML to extract ID
            action = row.get('action', '')
            # Extract ID from onclick="TerminationDetials('XX')"
            import re
            ids = re.findall(r"TerminationDetials\('(\d+)'\)", action)
            print(f"  Row {i}: range='{row.get('range','')}', test_number='{row.get('test_number','')}', term={row.get('term','')}, rate={row.get('A2P','')}, id={ids[0] if ids else 'N/A'}")

        # Collect unique range names
        all_ranges = set()
        for row in data:
            all_ranges.add(row.get('range', ''))
        print(f"\n[*] Unique range names from first {len(data)} rows: {all_ranges}")

        await context.close()
        print("\n[*] Done!")


asyncio.run(test_api())
