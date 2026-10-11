# ═══════════════════════════════════════════════════════════════
#  AUTO ADD NUMBERS - IVASMS
#  ─────────────────────────────────────────────────────────────
#  Otomatis add number berdasarkan Range Name dari halaman
#  https://www.ivasms.com/portal/numbers/test
#  dengan delay 1 menit per action.
#
#  Menggunakan Playwright persistent browser untuk bypass
#  Cloudflare dan menjaga session tetap valid.
# ═══════════════════════════════════════════════════════════════

import asyncio
import json
import logging
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from playwright.async_api import async_playwright

# ────────────────────────────────────────────
#  KONFIGURASI
# ────────────────────────────────────────────

# Range name yang ingin di-add (case-insensitive search)
# Contoh: "RUSSIA 1", "UZBEKISTAN", "MALAWI", dll.
# Bisa sebagian nama: "RUSSIA" akan cocok dengan RUSSIA 1, RUSSIA 2, dst.
RANGE_NAME = ""  # <-- ISI DI SINI atau via command line

# Jumlah maksimum nomor yang akan di-add (0 = semua yang ditemukan)
MAX_ADD = 0

# Delay antar action (dalam detik). Default: 60 detik (1 menit)
DELAY_SECONDS = 60

# Berapa banyak rows yang di-fetch per batch dari DataTable
BATCH_SIZE = 50

# ────────────────────────────────────────────

USER_DATA_DIR = os.path.abspath("browser_profile")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("auto_add")


async def wait_cloudflare(page, max_wait=30):
    """Tunggu Cloudflare challenge selesai"""
    for _ in range(max_wait):
        title = await page.title()
        if "Just a moment" not in title:
            return True
        await asyncio.sleep(1)
    return False


async def auto_login_if_needed(page, context):
    """Auto-login jika session expired"""
    from config import IVASMS_EMAIL, IVASMS_PASSWORD

    url = page.url
    if "/login" not in url:
        has_login = await page.query_selector("input[name='email']")
        if not has_login:
            return True  # Already logged in

    logger.info("🔑 Session expired, melakukan auto-login...")
    try:
        await page.fill("input[name='email']", IVASMS_EMAIL)
        await page.fill("input[name='password']", IVASMS_PASSWORD)

        remember = await page.query_selector("input[name='remember']")
        if remember and not await remember.is_checked():
            await remember.check()

        await asyncio.sleep(2)

        submit = await page.query_selector("button[type='submit']")
        if submit:
            await submit.click()
        else:
            await page.keyboard.press("Enter")

        for _ in range(15):
            await asyncio.sleep(1)
            if "/portal" in page.url:
                logger.info("🎉 Auto-login berhasil!")
                return True

        logger.error("❌ Auto-login gagal - tidak redirect ke portal")
        return False

    except Exception as e:
        logger.error(f"❌ Error saat auto-login: {e}")
        return False


async def fetch_ranges(page, range_search, start=0, length=50):
    """
    Fetch data ranges dari DataTable API.
    Mengembalikan list of {id, range, test_number, ...}
    """
    result = await page.evaluate("""
        async ([rangeSearch, start, length]) => {
            try {
                const url = new URL('/portal/numbers/test', window.location.origin);
                url.searchParams.set('draw', '1');
                url.searchParams.set('start', start.toString());
                url.searchParams.set('length', length.toString());

                // Columns sesuai DataTable config
                const cols = [
                    {data: 'range', name: 'terminations.range', searchable: true, orderable: true},
                    {data: 'test_number', name: 'terminations.test_number', searchable: true, orderable: true},
                    {data: 'term', name: 'term'},
                    {data: 'A2P', name: 'A2P'},
                    {data: 'Limit_Range', name: 'Limit_Range'},
                    {data: 'limit_did_a2p', name: 'limit_did_a2p'},
                    {data: 'limit_cli_did_a2p', name: 'limit_cli_did_a2p'},
                    {data: 'created_at', name: 'terminations.created_at'},
                    {data: 'action', name: 'action'},
                ];

                cols.forEach((col, i) => {
                    url.searchParams.set(`columns[${i}][data]`, col.data);
                    url.searchParams.set(`columns[${i}][name]`, col.name);
                    if (col.searchable) url.searchParams.set(`columns[${i}][searchable]`, 'true');
                    if (col.orderable) url.searchParams.set(`columns[${i}][orderable]`, 'true');
                });

                // Filter by range name (column 0 search)
                if (rangeSearch) {
                    url.searchParams.set('columns[0][search][value]', rangeSearch);
                }

                url.searchParams.set('order[0][column]', '8');
                url.searchParams.set('order[0][dir]', 'desc');
                url.searchParams.set('search[value]', '');

                const resp = await fetch(url.toString(), {
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'Accept': 'application/json'
                    }
                });

                if (!resp.ok) {
                    return {error: `HTTP ${resp.status}`, data: [], recordsTotal: 0, recordsFiltered: 0};
                }

                return await resp.json();
            } catch(e) {
                return {error: e.message, data: [], recordsTotal: 0, recordsFiltered: 0};
            }
        }
    """, [range_search, start, length])

    return result


async def add_number(page, termination_id, csrf_token):
    """
    Add number via AJAX POST ke /portal/numbers/termination/number/add
    Mengembalikan {success, message}
    """
    result = await page.evaluate("""
        async ([id, token]) => {
            try {
                const resp = await fetch('/portal/numbers/termination/number/add', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRF-TOKEN': token,
                        'Accept': 'application/json'
                    },
                    body: `_token=${encodeURIComponent(token)}&id=${encodeURIComponent(id)}`
                });

                const status = resp.status;
                let body;
                try {
                    body = await resp.json();
                } catch(e) {
                    body = {message: await resp.text()};
                }

                return {
                    status: status,
                    success: status >= 200 && status < 300,
                    message: body.message || JSON.stringify(body)
                };
            } catch(e) {
                return {status: 0, success: false, message: e.message};
            }
        }
    """, [str(termination_id), csrf_token])

    return result


async def get_csrf_token(page):
    """Ambil CSRF token dari halaman"""
    token = await page.evaluate("""
        () => {
            const meta = document.querySelector('meta[name="csrf-token"]');
            if (meta) return meta.content;
            const input = document.querySelector('input[name="_token"]');
            if (input) return input.value;
            return '';
        }
    """)
    return token


async def main():
    range_name = RANGE_NAME
    max_add = MAX_ADD
    delay = DELAY_SECONDS

    # Bisa override via command line: python auto_add_numbers.py "RUSSIA 1" 10 60
    if len(sys.argv) >= 2:
        range_name = sys.argv[1]
    if len(sys.argv) >= 3:
        max_add = int(sys.argv[2])
    if len(sys.argv) >= 4:
        delay = int(sys.argv[3])

    if not range_name:
        print("=" * 60)
        print("  AUTO ADD NUMBERS - IVASMS")
        print("=" * 60)
        print()
        print("  Cara penggunaan:")
        print()
        print('  python auto_add_numbers.py "RANGE_NAME" [MAX_ADD] [DELAY]')
        print()
        print("  Contoh:")
        print('    python auto_add_numbers.py "RUSSIA 1"')
        print('    python auto_add_numbers.py "RUSSIA 1" 10')
        print('    python auto_add_numbers.py "RUSSIA 1" 10 60')
        print('    python auto_add_numbers.py "UZBEKISTAN" 0 30')
        print()
        print("  Parameter:")
        print("    RANGE_NAME  : Nama range (case-insensitive, partial match)")
        print("    MAX_ADD     : Maks jumlah add (0 = semua). Default: 0")
        print("    DELAY       : Delay per action dalam detik. Default: 60")
        print()

        # Interactive mode
        range_name = input("  Masukkan Range Name: ").strip()
        if not range_name:
            print("  [!] Range name tidak boleh kosong!")
            return

        max_input = input("  Maks jumlah add (0 = semua) [0]: ").strip()
        max_add = int(max_input) if max_input else 0

        delay_input = input("  Delay per action (detik) [60]: ").strip()
        delay = int(delay_input) if delay_input else 60

    print()
    logger.info("═" * 55)
    logger.info("  AUTO ADD NUMBERS - IVASMS")
    logger.info("═" * 55)
    logger.info(f"  🔍 Range Name : {range_name}")
    logger.info(f"  📊 Max Add    : {'Unlimited' if max_add == 0 else max_add}")
    logger.info(f"  ⏱️  Delay      : {delay} detik")
    logger.info("═" * 55)

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

        # Navigate to test numbers page
        logger.info("🌐 Navigating ke halaman Test Numbers...")
        try:
            await page.goto(
                "https://www.ivasms.com/portal/numbers/test",
                timeout=45000,
                wait_until="domcontentloaded"
            )
        except Exception as e:
            logger.warning(f"Navigation warning: {e}")

        # Wait for Cloudflare
        if not await wait_cloudflare(page, 30):
            logger.error("❌ Cloudflare challenge timeout!")
            await context.close()
            return

        await asyncio.sleep(3)

        # Auto-login if needed
        if not await auto_login_if_needed(page, context):
            await context.close()
            return

        # Make sure we're on the right page
        if "/portal/numbers/test" not in page.url:
            await page.goto(
                "https://www.ivasms.com/portal/numbers/test",
                timeout=30000,
                wait_until="domcontentloaded"
            )
            await asyncio.sleep(3)

        # Get CSRF token
        csrf = await get_csrf_token(page)
        if not csrf:
            logger.error("❌ Gagal mendapatkan CSRF token!")
            await context.close()
            return
        logger.info(f"🔐 CSRF token: {csrf[:20]}...")

        # Fetch matching ranges
        logger.info(f"🔍 Mencari ranges dengan nama '{range_name}'...")

        total_added = 0
        total_failed = 0
        total_skipped = 0
        start = 0
        has_more = True

        while has_more:
            result = await fetch_ranges(page, range_name, start, BATCH_SIZE)

            if 'error' in result and result['error']:
                logger.error(f"❌ API Error: {result['error']}")
                # Try refreshing CSRF
                csrf = await get_csrf_token(page)
                break

            records_total = result.get('recordsFiltered', 0)
            data = result.get('data', [])

            if start == 0:
                logger.info(f"📊 Ditemukan {records_total} total records untuk '{range_name}'")

            if not data:
                logger.info("📭 Tidak ada data lagi.")
                break

            for row in data:
                termination_id = row.get('id')
                row_range = row.get('range', '')
                test_number = row.get('test_number', '')

                if not termination_id:
                    continue

                # Check max
                if max_add > 0 and total_added >= max_add:
                    logger.info(f"✅ Sudah mencapai batas {max_add} add.")
                    has_more = False
                    break

                total_added_and_failed = total_added + total_failed + total_skipped
                logger.info(f"")
                logger.info(f"── Action #{total_added_and_failed + 1} ──")
                logger.info(f"  📋 Range: {row_range}")
                logger.info(f"  📱 Number: {test_number}")
                logger.info(f"  🆔 ID: {termination_id}")

                # Call AddNumbers
                res = await add_number(page, termination_id, csrf)

                if res.get('success'):
                    total_added += 1
                    logger.info(f"  ✅ Berhasil! {res.get('message', '')}")
                else:
                    status = res.get('status', 0)
                    msg = res.get('message', 'Unknown error')

                    if status == 419:
                        # CSRF expired, refresh
                        logger.warning(f"  ⚠️ CSRF expired, refreshing...")
                        await page.reload(wait_until="domcontentloaded")
                        await asyncio.sleep(3)
                        csrf = await get_csrf_token(page)
                        # Retry
                        res = await add_number(page, termination_id, csrf)
                        if res.get('success'):
                            total_added += 1
                            logger.info(f"  ✅ Berhasil setelah refresh! {res.get('message', '')}")
                        else:
                            total_failed += 1
                            logger.error(f"  ❌ Gagal: [{status}] {msg}")
                    elif status == 429:
                        logger.warning(f"  ⚠️ Rate limited! Menunggu 120 detik...")
                        total_skipped += 1
                        await asyncio.sleep(120)
                    elif "already" in msg.lower() or "exist" in msg.lower():
                        total_skipped += 1
                        logger.info(f"  ⏩ Sudah ada: {msg}")
                    else:
                        total_failed += 1
                        logger.error(f"  ❌ Gagal: [{status}] {msg}")

                logger.info(f"  📊 Stats: Added={total_added}, Failed={total_failed}, Skipped={total_skipped}")

                # Delay between actions
                if max_add == 0 or total_added < max_add:
                    if has_more and (data.index(row) < len(data) - 1 or start + BATCH_SIZE < records_total):
                        logger.info(f"  ⏱️ Menunggu {delay} detik sebelum action berikutnya...")
                        await asyncio.sleep(delay)

            # Move to next batch
            start += BATCH_SIZE
            if start >= records_total:
                has_more = False

            if max_add > 0 and total_added >= max_add:
                has_more = False

        # Summary
        logger.info("")
        logger.info("═" * 55)
        logger.info("  📊 RINGKASAN")
        logger.info("═" * 55)
        logger.info(f"  🔍 Range Name : {range_name}")
        logger.info(f"  ✅ Berhasil   : {total_added}")
        logger.info(f"  ❌ Gagal      : {total_failed}")
        logger.info(f"  ⏩ Dilewati   : {total_skipped}")
        logger.info(f"  📊 Total      : {total_added + total_failed + total_skipped}")
        logger.info("═" * 55)

        await context.close()
        logger.info("🏁 Selesai!")


if __name__ == "__main__":
    asyncio.run(main())
