"""
Script Login Sekali Pakai untuk IVASMS.
Browser akan terbuka, silakan Login ke akun IVASMS Anda.
Setelah berhasil login dan masuk ke Dashboard / SMS Received,
sesi login akan tersimpan otomatis dan tidak perlu login lagi!
"""
import asyncio
import os
import sys

os.environ["PYTHONIOENCODING"] = "utf-8"
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

from playwright.async_api import async_playwright

USER_DATA_DIR = os.path.abspath("browser_profile")

async def main():
    print("=" * 60)
    print("🚀 MEMBUKA BROWSER LOGIN IVASMS")
    print("Silakan LOGIN ke akun IVASMS Anda di jendela browser yang muncul.")
    print("Setelah login sukses dan masuk ke halaman SMS Received,")
    print("tutup browser atau tekan Enter di sini.")
    print("=" * 60)

    async with async_playwright() as p:
        # Buka Firefox / Chromium terlihat (headless=False)
        browser_type = p.firefox
        context = await browser_type.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            args=["--no-sandbox"]
        )
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto("https://www.ivasms.com/login")

        print("\n⏳ Menunggu Anda login di browser...")
        print("💡 Silakan centang Cloudflare dan login dengan email & password Anda di jendela browser yang terbuka.")
        
        # Loop sampai user berada di halaman portal/sms/received atau portal
        while True:
            await asyncio.sleep(2)
            url = page.url
            if "/portal" in url:
                print(f"✅ Login berhasil terdeteksi! (URL: {url})")
                print("Menyimpan sesi login...")
                await page.goto("https://www.ivasms.com/portal/sms/received")
                await asyncio.sleep(3)
                print("🎉 Sesi login tersimpan permanen di folder 'browser_profile'!")
                break
        
        await context.close()

if __name__ == "__main__":
    asyncio.run(main())
