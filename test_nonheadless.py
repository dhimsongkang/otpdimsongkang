import asyncio, os
from playwright.async_api import async_playwright

async def check():
    user_data = os.path.abspath('browser_profile')
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=user_data,
            channel='msedge',
            headless=False,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto('https://www.ivasms.com/portal/sms/received')
        for i in range(15):
            await asyncio.sleep(1)
            t = await page.title()
            print(f'Second {i}: {t}')
            if 'Just a moment' not in t:
                print('Cleared Cloudflare! Final title:', t)
                break
        cookies = await context.cookies('https://www.ivasms.com')
        for c in cookies:
            print(f"  {c['name']} = {c['value'][:20]}...")
        await context.close()

if __name__ == '__main__':
    asyncio.run(check())
