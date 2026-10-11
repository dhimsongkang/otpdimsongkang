# ═══════════════════════════════════════════════════════════════
#  HELPER: Mendapatkan Chat ID Telegram
#  ─────────────────────────────────────────────────────────────
#  Jalankan script ini untuk mengetahui Chat ID grup Anda
#  Usage: python get_chat_id.py
# ═══════════════════════════════════════════════════════════════

import asyncio
from telegram import Bot, Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Print info tentang setiap pesan yang diterima."""
    chat = update.effective_chat
    user = update.effective_user

    print("=" * 50)
    print(f"📨 Pesan diterima!")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"Chat ID    : {chat.id}")
    print(f"Chat Type  : {chat.type}")
    print(f"Chat Title : {chat.title or 'N/A (Private)'}")
    print(f"From User  : {user.first_name} ({user.id})")
    print(f"Message    : {update.message.text}")
    print("=" * 50)
    print()
    print(f"📋 Copy ini ke config.py:")
    print(f'   GROUP_CHAT_ID = "{chat.id}"')
    print()

    await update.message.reply_text(
        f"✅ Chat ID: `{chat.id}`\n"
        f"📝 Type: `{chat.type}`\n\n"
        f"Copy Chat ID ini ke `config.py`",
        parse_mode="Markdown"
    )


def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN belum diisi di config.py!")
        return

    print("=" * 50)
    print("🔍 Chat ID Finder")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("Kirim pesan apapun ke bot atau grup")
    print("untuk mendapatkan Chat ID")
    print("Tekan Ctrl+C untuk berhenti")
    print("=" * 50)

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    app.run_polling()


if __name__ == "__main__":
    main()
