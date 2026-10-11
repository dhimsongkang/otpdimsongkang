#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════
#  🤖 IVASMS OTP TELEGRAM BOT
#  ─────────────────────────────────────────────────────────────
#  Bot Telegram yang memonitor IVASMS dan mengirim OTP
#  secara real-time ke grup Telegram
#
#  Format pesan seperti di gambar:
#  🇲🇱 ML | 🟢 | +2237🫣4077
#  WhatsApp                    16:30
#  ┌─────────────────┐
#  │     577732       │
#  └─────────────────┘
#  [📁 File]  [✈️ Grup OTP]
# ═══════════════════════════════════════════════════════════════

import asyncio
import logging
import signal
import sys
import os
from datetime import datetime

os.environ["PYTHONIOENCODING"] = "utf-8"
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode

# Local imports
from config import (
    BOT_TOKEN,
    GROUP_CHAT_ID,
    GROUP_LINK,
    NUMBER_LINK,
    OWNER_LINK,
    BOT_NAME,
    IVASMS_URL,
    IVASMS_SMS_ENDPOINT,
    POLL_INTERVAL,
    COOKIES,
)
from ivasms_scraper import IVASMSClient
from cookie_sync import get_fresh_cookies_from_browser

# ────────────────────────────────────────────
#  LOGGING SETUP
# ────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log', encoding='utf-8'),
    ]
)
logger = logging.getLogger("OTPBot")

# Reduce noise from libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
logging.getLogger("cloudscraper").setLevel(logging.WARNING)


# ────────────────────────────────────────────
#  MESSAGE FORMATTER
# ────────────────────────────────────────────
def format_otp_message(sms_data: dict) -> str:
    """
    Format pesan OTP sesuai screenshot:

    🇿🇼 ZW • 💬 2637 ~ 1419 17:12
    🪙 803-146
    """
    flag = sms_data.get("flag", "🏳️")
    country = sms_data.get("country_code", "??")
    platform = sms_data.get("platform", "SMS")
    
    # Platform icon
    p_lower = platform.lower()
    if "whatsapp" in p_lower:
        platform_icon = "🟢"
    elif "telegram" in p_lower:
        platform_icon = "🔵"
    else:
        platform_icon = sms_data.get("platform_emoji", "💬")

    phone_masked = sms_data.get("phone_masked", sms_data.get("phone", "???"))
    otp = sms_data.get("otp", "N/A")

    # Baris 1: [Flag] [CC] • [PlatformIcon] [4 awal ~ 4 akhir]
    line1 = f"{flag} *{country}* • {platform_icon} *{phone_masked}*"

    # Baris 2: OTP (klik untuk salin otomatis / copy-to-clipboard)
    if otp and otp != "N/A":
        line2 = f"🪙 `{otp}`"
    else:
        line2 = f"🪙 `N/A`"

    return f"{line1}\n{line2}"


def create_keyboard(sms_data: dict, number_link: str = "", owner_link: str = "") -> InlineKeyboardMarkup:
    """
    Buat inline keyboard:
    [ 🔴 NUMBER ↗ ]   [ 🧠 OWNER ↗ ]
    """
    num_btn = (
        InlineKeyboardButton("🔴 NUMBER ↗", url=number_link)
        if number_link
        else InlineKeyboardButton("🔴 NUMBER", callback_data="btn_number")
    )

    owner_btn = (
        InlineKeyboardButton("🧠 OWNER ↗", url=owner_link)
        if owner_link
        else InlineKeyboardButton("🧠 OWNER", callback_data="btn_owner")
    )

    buttons = [
        [num_btn, owner_btn]
    ]

    return InlineKeyboardMarkup(buttons)


# ────────────────────────────────────────────
#  STATISTICS TRACKER
# ────────────────────────────────────────────
class StatsTracker:
    """Track statistik OTP yang sudah dikirim."""

    def __init__(self):
        self.total_sent = 0
        self.start_time = datetime.now()
        self.platform_counts = {}
        self.country_counts = {}

    def record(self, sms_data: dict):
        self.total_sent += 1
        platform = sms_data.get("platform", "Unknown")
        country = sms_data.get("country_code", "??")
        self.platform_counts[platform] = self.platform_counts.get(platform, 0) + 1
        self.country_counts[country] = self.country_counts.get(country, 0) + 1

    def get_summary(self) -> str:
        uptime = datetime.now() - self.start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)

        top_platforms = sorted(self.platform_counts.items(), key=lambda x: -x[1])[:5]
        top_countries = sorted(self.country_counts.items(), key=lambda x: -x[1])[:5]

        platform_text = "\n".join(
            f"  • {name}: *{count}*" for name, count in top_platforms
        ) or "  _Belum ada data_"

        country_text = "\n".join(
            f"  • {code}: *{count}*" for code, count in top_countries
        ) or "  _Belum ada data_"

        return (
            f"📊 *STATISTIK OTP BOT*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⏱ Uptime: `{hours}h {minutes}m {seconds}s`\n"
            f"📨 Total OTP: *{self.total_sent}*\n"
            f"\n"
            f"📱 *Platform:*\n{platform_text}\n"
            f"\n"
            f"🌍 *Negara:*\n{country_text}\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )


# ────────────────────────────────────────────
#  FULL MESSAGE STORAGE (untuk tombol File)
# ────────────────────────────────────────────
# Store last N full messages for callback queries
full_messages = {}
MAX_STORED_MESSAGES = 500


def store_full_message(sms_id: str, message: str):
    """Simpan full message untuk callback query."""
    full_messages[sms_id[:40]] = message
    # Cleanup old messages
    if len(full_messages) > MAX_STORED_MESSAGES:
        oldest_keys = list(full_messages.keys())[:-MAX_STORED_MESSAGES]
        for key in oldest_keys:
            del full_messages[key]


# ────────────────────────────────────────────
#  BOT COMMANDS
# ────────────────────────────────────────────
stats = StatsTracker()


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /start command."""
    welcome_msg = (
        f"🤖 *{BOT_NAME} - OTP Monitor Bot*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"\n"
        f"Bot ini memonitor IVASMS dan mengirim\n"
        f"kode OTP secara *real-time* ke grup.\n"
        f"\n"
        f"📋 *Perintah:*\n"
        f"  /start — Menu utama\n"
        f"  /status — Status koneksi\n"
        f"  /stats — Statistik OTP\n"
        f"  /ping — Cek bot hidup\n"
        f"\n"
        f"⚡ Polling interval: `{POLL_INTERVAL}` detik\n"
        f"🌐 Source: `{IVASMS_URL}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    await update.message.reply_text(welcome_msg, parse_mode=ParseMode.MARKDOWN)


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /status command."""
    global active_client
    await update.message.reply_text("🔄 Checking IVASMS connection...", parse_mode=ParseMode.MARKDOWN)

    if not active_client:
        active_client = IVASMSClient(COOKIES, IVASMS_URL)

    is_connected = active_client.check_connection()

    if not is_connected:
        fresh_c = await get_fresh_cookies_from_browser()
        if fresh_c:
            active_client.update_cookies(fresh_c)
            is_connected = active_client.check_connection()

    if is_connected:
        status_msg = (
            f"✅ *Status: ONLINE*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🌐 IVASMS: Connected\n"
            f"🤖 Bot: Running\n"
            f"⚡ Interval: `{POLL_INTERVAL}s`\n"
            f"📨 Total sent: *{stats.total_sent}*\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
    else:
        status_msg = (
            f"❌ *Status: OFFLINE*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🌐 IVASMS: Disconnected\n"
            f"⚠️ Sesi browser perlu diperbarui\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )

    await update.message.reply_text(status_msg, parse_mode=ParseMode.MARKDOWN)


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /stats command."""
    await update.message.reply_text(stats.get_summary(), parse_mode=ParseMode.MARKDOWN)


async def cmd_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /ping command."""
    await update.message.reply_text(
        f"🏓 *Pong!*\n⏰ `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
        parse_mode=ParseMode.MARKDOWN
    )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk callback dari inline keyboard."""
    query = update.callback_query
    data = query.data or ""
    await query.answer()

    if data == "btn_number":
        await query.answer("Link NUMBER belum diisi.", show_alert=True)
        return

    if data == "btn_owner":
        await query.answer("Link OWNER belum diisi.", show_alert=True)
        return

    if data.startswith("file_"):
        sms_id = data[5:]
        full_msg = full_messages.get(sms_id, "⚠️ Pesan sudah tidak tersedia (expired)")

        # Truncate jika terlalu panjang
        if len(full_msg) > 3000:
            full_msg = full_msg[:3000] + "\n\n... _(truncated)_"

        await query.message.reply_text(
            f"📁 *Full SMS Content:*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"```\n{full_msg}\n```",
            parse_mode=ParseMode.MARKDOWN,
        )


# ────────────────────────────────────────────
#  OTP POLLING LOOP
# ────────────────────────────────────────────
async def poll_otp(bot: Bot, client: IVASMSClient, chat_id: str):
    """Loop utama untuk polling OTP dari IVASMS."""
    logger.info("🚀 OTP polling started")

    consecutive_errors = 0
    max_errors = 10

    while True:
        try:
            # Ambil SMS baru
            new_sms_list = client.get_new_sms()

            for sms_data in new_sms_list:
                try:
                    # Format pesan
                    message = format_otp_message(sms_data)
                    keyboard = create_keyboard(sms_data, NUMBER_LINK, OWNER_LINK)

                    # Simpan full message untuk callback
                    store_full_message(
                        sms_data.get("id", "unknown"),
                        sms_data.get("message", "No message")
                    )

                    # Kirim ke Telegram
                    await bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=keyboard,
                    )

                    # Record stats
                    stats.record(sms_data)

                    logger.info(
                        f"📤 Sent OTP: {sms_data.get('country_code', '??')} | "
                        f"{sms_data.get('platform', 'SMS')} | "
                        f"{sms_data.get('otp', 'N/A')}"
                    )

                    # Delay antar pesan untuk menghindari rate limit
                    await asyncio.sleep(0.5)

                except Exception as e:
                    logger.error(f"❌ Failed to send message: {e}")

            consecutive_errors = 0  # Reset error counter on success

        except Exception as e:
            consecutive_errors += 1
            logger.error(f"❌ Polling error ({consecutive_errors}/{max_errors}): {e}")

            # Otomatis refresh cookie dari browser jika error berulang
            if consecutive_errors == 2:
                logger.info("🔄 Auto-refreshing cookies from background browser...")
                try:
                    fresh_c = await get_fresh_cookies_from_browser()
                    if fresh_c:
                        client.update_cookies(fresh_c)
                        logger.info("✅ Cookies successfully auto-refreshed!")
                        consecutive_errors = 0
                except Exception as sync_e:
                    logger.error(f"Failed auto-refresh: {sync_e}")

            if consecutive_errors >= max_errors:
                logger.critical("🔴 Too many consecutive errors! Pausing for 60s...")
                await asyncio.sleep(60)
                consecutive_errors = 0

        # Wait before next poll
        await asyncio.sleep(POLL_INTERVAL)


# Global client instance
active_client = None

# ────────────────────────────────────────────
#  MAIN APPLICATION
# ────────────────────────────────────────────
async def post_init(application: Application):
    """Called after bot initialization."""
    global active_client
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info(f"🤖 {BOT_NAME} is starting up...")
    logger.info(f"🌐 IVASMS URL: {IVASMS_URL}")
    logger.info(f"⚡ Poll interval: {POLL_INTERVAL}s")
    logger.info(f"📤 Target chat: {GROUP_CHAT_ID}")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # Inisialisasi IVASMS client
    active_client = IVASMSClient(COOKIES, IVASMS_URL)

    # Cek koneksi, jika gagal coba auto-sync dari browser profile
    conn_ok = active_client.check_connection()
    if not conn_ok:
        logger.info("🔄 Checking fresh cookies from browser profile...")
        try:
            fresh_c = await get_fresh_cookies_from_browser()
            if fresh_c:
                active_client.update_cookies(fresh_c)
                conn_ok = active_client.check_connection()
        except Exception as e:
            logger.warning(f"Browser sync skipped: {e}")

    # Selalu jalankan bot jika COOKIES ada di config.py
    if conn_ok or (COOKIES and "ivas_sms_session" in COOKIES):
        if conn_ok:
            logger.info("✅ IVASMS connection verified!")
        else:
            logger.info("⚠️ IVASMS session loaded from config.py! Memulai bot polling...")

        # Mark existing SMS as seen
        try:
            existing_count = active_client.mark_initial_as_seen()
            logger.info(f"📌 Skipping {existing_count} existing SMS")
        except Exception as ex:
            logger.warning(f"Could not fetch initial SMS: {ex}")

        # Kirim pesan startup ke grup
        try:
            startup_msg = (
                f"🟢 *{BOT_NAME} ONLINE*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"⏰ `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n"
                f"⚡ Interval: `{POLL_INTERVAL}s`\n"
                f"📡 Monitoring IVASMS...\n"
                f"━━━━━━━━━━━━━━━━━━━━"
            )
            await application.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text=startup_msg,
                parse_mode=ParseMode.MARKDOWN,
            )
        except Exception as e:
            logger.warning(f"⚠️ Could not send startup message: {e}")

        # Start polling task
        asyncio.create_task(poll_otp(application.bot, active_client, GROUP_CHAT_ID))
    else:
        logger.error("❌ IVASMS connection failed! Check your cookies.")
        logger.error("💡 Update cookies di config.py lalu restart bot.")


def main():
    """Entry point utama."""
    # ──── Validasi konfigurasi ────
    if not BOT_TOKEN:
        print("=" * 50)
        print("❌ ERROR: BOT_TOKEN belum diisi!")
        print("")
        print("Cara mendapatkan Bot Token:")
        print("1. Buka Telegram, cari @BotFather")
        print("2. Kirim /newbot")
        print("3. Ikuti instruksi")
        print("4. Copy token ke config.py")
        print("=" * 50)
        sys.exit(1)

    if not GROUP_CHAT_ID:
        print("=" * 50)
        print("❌ ERROR: GROUP_CHAT_ID belum diisi!")
        print("")
        print("Cara mendapatkan Chat ID:")
        print("1. Tambahkan @userinfobot ke grup")
        print("2. Atau gunakan @getidsbot")
        print("3. Copy chat ID ke config.py")
        print("   (Grup biasanya dimulai dengan -100)")
        print("=" * 50)
        sys.exit(1)

    if not COOKIES:
        print("=" * 50)
        print("❌ ERROR: COOKIES IVASMS belum diisi!")
        print("")
        print("Cara mendapatkan cookies:")
        print("1. Buka https://www.ivasms.com")
        print("2. Login ke akun Anda")
        print("3. Tekan F12 → Application → Cookies")
        print("4. Copy semua cookies ke config.py")
        print("=" * 50)
        sys.exit(1)

    # ──── Build & Run Application ────
    logger.info("🔧 Building application...")

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # Register command handlers
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("ping", cmd_ping))

    # Register callback handler untuk inline buttons
    from telegram.ext import CallbackQueryHandler
    app.add_handler(CallbackQueryHandler(callback_handler))

    # Run the bot
    logger.info("🚀 Starting bot...")
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
