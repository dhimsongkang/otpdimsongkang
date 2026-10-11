# ═══════════════════════════════════════════════════════════════
#  AUTO COOKIE SYNC & AUTO LOGIN
#  ─────────────────────────────────────────────────────────────
#  Otomatis memperbarui cf_clearance dan login ulang jika ter-logout
# ═══════════════════════════════════════════════════════════════

import asyncio
import logging
import os
import aiohttp
from playwright.async_api import async_playwright
from config import IVASMS_EMAIL, IVASMS_PASSWORD, YESCAPTCHA_KEY

logger = logging.getLogger(__name__)
USER_DATA_DIR = os.path.abspath("browser_profile")


async def solve_turnstile(website_url: str, website_key: str) -> str:
    """Solve Cloudflare Turnstile challenge using YesCaptcha API"""
    if not YESCAPTCHA_KEY:
        return ""
    try:
        async with aiohttp.ClientSession() as session:
            # Create task
            task_data = {
                "clientKey": YESCAPTCHA_KEY,
                "task": {
                    "type": "TurnstileTaskProxyless",
                    "websiteURL": website_url,
                    "websiteKey": website_key,
                }
            }
            async with session.post("https://api.yescaptcha.com/createTask", json=task_data, timeout=15) as resp:
                res = await resp.json()
                if res.get("errorId") != 0:
                    logger.error(f"❌ YesCaptcha createTask error: {res.get('errorDescription')}")
                    return ""
                task_id = res.get("taskId")

            logger.info(f"🧩 YesCaptcha Task created: {task_id}, awaiting solution...")

            # Poll result
            for _ in range(30):
                await asyncio.sleep(2)
                async with session.post("https://api.yescaptcha.com/getTaskResult", json={"clientKey": YESCAPTCHA_KEY, "taskId": task_id}, timeout=15) as resp:
                    r = await resp.json()
                    if r.get("status") == "ready":
                        token = r.get("solution", {}).get("token", "")
                        logger.info("🎉 YesCaptcha Turnstile SOLVED!")
                        return token
                    elif r.get("errorId") != 0:
                        logger.error(f"❌ YesCaptcha getTaskResult error: {r.get('errorDescription')}")
                        return ""
    except Exception as e:
        logger.error(f"YesCaptcha error: {e}")
    return ""


async def get_fresh_cookies_from_browser() -> dict:
    """
    Buka session browser Playwright:
    1. Jika session masih valid -> ambil cookies segar (cf_clearance, dsb).
    2. Jika ter-logout (/login) -> otomatis login ulang dengan email & password + centang remember me!
    3. Jika tertahan Cloudflare Turnstile -> otomatis di-solve oleh YesCaptcha!
    """
    cookies_dict = {}
    try:
        async with async_playwright() as p:
            # Firefox configuration - much less restricted by Cloudflare on Linux
            context = await p.firefox.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=os.name != "nt" or os.environ.get("HEADLESS", "false").lower() == "true",
                user_agent="Mozilla/5.0 (X11; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0",
                viewport={"width": 1280, "height": 720},
                firefox_user_prefs={
                    "dom.webdriver.enabled": False,
                    "useAutomationExtension": False,
                    "general.useragent.override": "Mozilla/5.0 (X11; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0"
                }
            )
            page = context.pages[0] if context.pages else await context.new_page()

            # Remove navigator.webdriver flag
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)

            target_url = "https://www.ivasms.com/portal/sms/received"
            try:
                await page.goto(target_url, timeout=45000, wait_until="load")
            except Exception as nav_e:
                logger.warning(f"Browser navigation warning: {nav_e}")

            logger.info(f"Page loaded: {page.url} | Title: {await page.title()}")

            # Tunggu bypass Cloudflare jika muncul 'Just a moment...'
            for i in range(25):
                t = await page.title()
                if "Just a moment" not in t:
                    break

                # Log frame URLs if any
                frame_urls = [f.url for f in page.frames]
                if i == 0:
                    logger.info(f"Frames terdeteksi: {len(page.frames)} frame -> {frame_urls}")

                # Cek apakah ada iframe challenge Cloudflare
                frames = page.frames
                sitekey = None
                for frame in frames:
                    try:
                        if "challenges.cloudflare.com" in frame.url or "turnstile" in frame.url:
                            import re
                            m = re.search(r"sitekey=([^&]+)", frame.url) or re.search(r"k=([^&]+)", frame.url)
                            if m:
                                sitekey = m.group(1)
                                break
                            btn = await frame.query_selector("input[type='checkbox'], #challenge-stage, .ctp-checkbox-label")
                            if btn:
                                logger.info("👆 Menemukan checkbox Cloudflare di frame, mencoba klik...")
                                await btn.click()
                                await asyncio.sleep(2)
                    except:
                        pass

                if not sitekey:
                    # Cek elemen data-sitekey di main page
                    turnstile_container = await page.query_selector("[data-sitekey]")
                    if turnstile_container:
                        sitekey = await turnstile_container.get_attribute("data-sitekey")

                if sitekey and YESCAPTCHA_KEY:
                    logger.info(f"🔍 Turnstile SiteKey terdeteksi: {sitekey}")
                    token = await solve_turnstile(page.url, sitekey)
                    if token:
                        await page.evaluate(f"""
                            const input = document.querySelector('[name="cf-turnstile-response"]') || document.querySelector('input[name*="turnstile"]');
                            if (input) {{ input.value = '{token}'; }}
                            const form = document.querySelector('form#challenge-form') || document.querySelector('form');
                            if (form) {{ form.submit(); }}
                        """)
                        await asyncio.sleep(4)
                        break

                # Coba klik challenge body jika ada
                try:
                    challenge_box = await page.query_selector("#challenge-stage, iframe")
                    if challenge_box:
                        await challenge_box.click()
                except:
                    pass

                logger.info(f"⏳ Cloudflare challenge terdeteksi, menunggu... ({i+1}/25)")
                await asyncio.sleep(1)

            curr_url = page.url
            email_field = await page.query_selector("input[name='email']")
            if "/login" in curr_url or email_field:
                logger.info("🔑 Menjalankan auto-login IVASMS...")
                try:
                    if email_field:
                        await email_field.fill(IVASMS_EMAIL)
                    else:
                        await page.fill("input[name='email']", IVASMS_EMAIL)
                    await page.fill("input[name='password']", IVASMS_PASSWORD)

                    # Centang Remember Me
                    remember_cb = await page.query_selector("input[name='remember']")
                    if remember_cb and not await remember_cb.is_checked():
                        await remember_cb.check()

                    await asyncio.sleep(1)

                    # Submit login
                    submit_btn = await page.query_selector("button[type='submit']")
                    if submit_btn:
                        await submit_btn.click()
                    else:
                        await page.keyboard.press("Enter")

                    # Tunggu sampai berhasil masuk ke dashboard / portal
                    for i in range(20):
                        await asyncio.sleep(1)
                        if "/portal" in page.url:
                            logger.info("🎉 Auto-login BERHASIL masuk ke portal!")
                            break

                    if "/portal/sms/received" not in page.url:
                        await page.goto("https://www.ivasms.com/portal/sms/received", timeout=20000)
                        await asyncio.sleep(2)

                except Exception as login_err:
                    logger.error(f"Error during auto-login: {login_err}")

            raw_cookies = await context.cookies()
            for c in raw_cookies:
                if "ivasms.com" in c.get("domain", ""):
                    cookies_dict[c["name"]] = c["value"]

            logger.info(f"Current final URL: {page.url} | Title: {await page.title()}")
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
