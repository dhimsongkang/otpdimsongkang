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
        # Cari binary Firefox resmi di sistem Linux
        firefox_paths = [
            "/usr/bin/firefox",
            "/usr/lib/firefox/firefox",
            "/usr/bin/firefox-developer-edition",
        ]
        executable_path = None
        for path in firefox_paths:
            if os.path.exists(path):
                executable_path = path
                break

        launch_kwargs = {
            "user_data_dir": USER_DATA_DIR,
            "headless": False,
            "args": ["--no-sandbox"],
            "firefox_user_prefs": {
                "dom.webdriver.enabled": False,
                "useAutomationExtension": False,
            }
        }
        if executable_path:
            print(f"🦊 Menggunakan Firefox Resmi: {executable_path}")
            launch_kwargs["executable_path"] = executable_path
        else:
            print("🦊 Menggunakan Firefox engine bawaan Playwright")

        context = await p.firefox.launch_persistent_context(**launch_kwargs)
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto("https://www.ivasms.com/login")

        print("\n⏳ Menunggu Anda login di browser Firefox...")
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
