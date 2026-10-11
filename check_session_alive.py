import asyncio, os
from playwright.async_api import async_playwright

async def check():
    user_data = os.path.abspath('browser_profile')
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=user_data,
            channel='msedge',
            headless=True,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto('https://www.ivasms.com/portal/sms/received', timeout=20000)
        print('Current URL:', page.url)
        print('Page title:', await page.title())
        cookies = await context.cookies('https://www.ivasms.com')
        print('Cookies:')
        for c in cookies:
            print(f"  {c['name']} (expires: {c.get('expires')})")
        
        # Check if login form is present
        login_btn = await page.query_selector('button[type="submit"]')
        if login_btn or '/login' in page.url:
            print('STATUS: Session logged out, redirected to login page!')
        else:
            print('STATUS: Still logged in!')
        await context.close()

if __name__ == '__main__':
    asyncio.run(check())
