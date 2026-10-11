"""Verify saved cookies in browser profile."""
import asyncio
import os
from playwright.async_api import async_playwright

async def verify():
    user_data = os.path.abspath("browser_profile")
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=user_data,
            channel="msedge",
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        cookies = await context.cookies("https://www.ivasms.com")
        print(f"Total cookies found: {len(cookies)}")
        for c in cookies:
            print(f"  {c['name']} = {c['value'][:25]}...")
        await context.close()

if __name__ == "__main__":
    asyncio.run(verify())
