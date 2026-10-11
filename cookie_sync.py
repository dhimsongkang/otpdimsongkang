# ═══════════════════════════════════════════════════════════════
#  AUTO COOKIE SYNC & AUTO LOGIN
#  ─────────────────────────────────────────────────────────────
#  Otomatis memperbarui cf_clearance dan login ulang jika ter-logout
# ═══════════════════════════════════════════════════════════════

import asyncio
import logging
import os
from playwright.async_api import async_playwright
from config import IVASMS_EMAIL, IVASMS_PASSWORD

logger = logging.getLogger(__name__)
USER_DATA_DIR = os.path.abspath("browser_profile")


async def get_fresh_cookies_from_browser() -> dict:
    """
    Buka session browser Edge headless:
    1. Jika session masih valid -> ambil cookies segar (cf_clearance, dsb).
    2. Jika ter-logout (/login) -> otomatis login ulang dengan email & password + centang remember me!
    """
    cookies_dict = {}
    try:
        async with async_playwright() as p:
            # Check environment: on Linux default chromium, on Windows can use msedge/chrome
            launch_kwargs = {
                "user_data_dir": USER_DATA_DIR,
                "headless": os.name != "nt" or os.environ.get("HEADLESS", "false").lower() == "true",
                "args": [
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-gpu",
                ]
            }
            # Only specify channel if available or on Windows
            if os.name == "nt":
                launch_kwargs["channel"] = "msedge"
                launch_kwargs["args"].append("--window-position=-2000,-2000")

            context = await p.chromium.launch_persistent_context(**launch_kwargs)
            page = context.pages[0] if context.pages else await context.new_page()

            # Buka halaman received
            try:
                await page.goto("https://www.ivasms.com/portal/sms/received", timeout=30000, wait_until="domcontentloaded")
            except Exception as nav_e:
                logger.warning(f"Browser navigation warning: {nav_e}")

            # Tunggu bypass Cloudflare jika muncul 'Just a moment...'
            for _ in range(12):
                t = await page.title()
                if "Just a moment" not in t:
                    break
                await asyncio.sleep(1)

            # Cek apakah dialihkan ke halaman login
            curr_url = page.url
            if "/login" in curr_url or await page.query_selector("input[name='email']"):
                logger.info("🔑 Session expired, melakukan auto-login otomatis...")
                try:
                    await page.fill("input[name='email']", IVASMS_EMAIL)
                    await page.fill("input[name='password']", IVASMS_PASSWORD)

                    # Centang Remember Me
                    remember_cb = await page.query_selector("input[name='remember']")
                    if remember_cb and not await remember_cb.is_checked():
                        await remember_cb.check()

                    # Tunggu Cloudflare turnstile menyelesaikan challenge jika ada
                    await asyncio.sleep(2)

                    # Submit login
                    submit_btn = await page.query_selector("button[type='submit']")
                    if submit_btn:
                        await submit_btn.click()
                    else:
                        await page.keyboard.press("Enter")

                    # Tunggu sampai berhasil masuk ke dashboard / portal
                    for _ in range(15):
                        await asyncio.sleep(1)
                        if "/portal" in page.url:
                            logger.info("🎉 Auto-login BERHASIL masuk ke portal!")
                            break

                    # Pastikan berada di halaman sms received
                    if "/portal/sms/received" not in page.url:
                        await page.goto("https://www.ivasms.com/portal/sms/received", timeout=20000)
                        await asyncio.sleep(2)

                except Exception as login_err:
                    logger.error(f"Error during auto-login: {login_err}")

            raw_cookies = await context.cookies("https://www.ivasms.com")
            for c in raw_cookies:
                cookies_dict[c["name"]] = c["value"]

            await context.close()

        logger.info(f"🔄 Auto-synced {len(cookies_dict)} cookies from browser profile!")
    except Exception as e:
        logger.error(f"❌ Failed to auto-sync cookies: {e}")

    return cookies_dict


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s │ %(levelname)-8s │ %(message)s")
    print("🔄 Running cookie sync test...")
    res = asyncio.run(get_fresh_cookies_from_browser())
    print(f"Hasil cookie: {len(res)} cookies ditemukan.")
    if "ivas_sms_session" in res:
        print("✅ Session IVASMS VALID!")
    else:
        print("⚠️ Session belum valid atau perlu login.")
