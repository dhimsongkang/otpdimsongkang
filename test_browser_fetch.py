import asyncio, os, json
from playwright.async_api import async_playwright

async def inspect_browser_fetch():
    user_data = os.path.abspath('browser_profile')
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=user_data,
            channel='msedge',
            headless=False,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto('https://www.ivasms.com/portal/sms/received', timeout=30000)
        await asyncio.sleep(4)
        
        # Test GetSMS call directly inside browser context where Cloudflare clearance exists
        result = await page.evaluate('''
            async () => {
                const tokenMatch = document.documentElement.innerHTML.match(/f\\.append\\('_token',\\s*['"]([^'"]+)['"]\\)/) ||
                                   document.documentElement.innerHTML.match(/name=['"]_token['"]\\s+value=['"]([^'"]+)['"]/);
                const token = tokenMatch ? tokenMatch[1] : '';
                const today = new Date().toISOString().split('T')[0];
                const form = new FormData();
                form.append('from', today);
                form.append('to', today);
                form.append('_token', token);
                
                const resp = await fetch('https://www.ivasms.com/portal/sms/received/getsms', {
                    method: 'POST',
                    body: form,
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });
                const text = await resp.text();
                return { status: resp.status, textLen: text.length, snippet: text.substring(0, 500) };
            }
        ''')
        print("Fetch result from inside Edge:", json.dumps(result, indent=2))
        await context.close()

if __name__ == '__main__':
    asyncio.run(inspect_browser_fetch())
