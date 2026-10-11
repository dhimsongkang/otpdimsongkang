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
        if os.name == "nt":
            print("🌐 Membuka Microsoft Edge bawaan Windows...")
            context = await p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                channel="msedge",
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox"
                ]
            )
        else:
            print("🦊 Membuka Firefox di Linux...")
            context = await p.firefox.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=False,
                args=["--no-sandbox"],
                firefox_user_prefs={"dom.webdriver.enabled": False}
            )

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
                
                # Ekstrak cookies dan perbarui config.py otomatis
                raw_cookies = await context.cookies()
                cookies_dict = {}
                for c in raw_cookies:
                    if "ivasms.com" in c.get("domain", ""):
                        cookies_dict[c["name"]] = c["value"]
                
                if "ivas_sms_session" in cookies_dict:
                    import re
                    cfg_path = os.path.join(os.path.dirname(__file__), "config.py")
                    with open(cfg_path, "r", encoding="utf-8") as f:
                        cfg_text = f.read()
                    cookie_str = "COOKIES = {\n"
                    for k, v in cookies_dict.items():
                        cookie_str += f'    "{k}": "{v}",\n'
                    cookie_str += "}"
                    cfg_text = re.sub(r"COOKIES\s*=\s*\{[^}]*\}", cookie_str, cfg_text)
                    with open(cfg_path, "w", encoding="utf-8") as f:
                        f.write(cfg_text)
                    print("💾 config.py otomatis diperbarui dengan cookies Edge!")

                print("🎉 Sesi login tersimpan permanen di folder 'browser_profile'!")
                break
        
        await context.close()

if __name__ == "__main__":
    asyncio.run(main())
