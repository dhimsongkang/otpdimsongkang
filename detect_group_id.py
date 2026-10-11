"""Detector ID grup otomatis."""
import requests
import json
import time
from config import BOT_TOKEN

print("=" * 60)
print("Sedang menunggu pesan dari grup Telegram...")
print("Silakan buka grup Telegram Anda dan kirim pesan apa saja (misal: 'tes' atau '/id')")
print("=" * 60)

last_update_id = 0

# Get initial updates offset
try:
    init_res = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates", verify=False).json()
    if init_res.get("result"):
        last_update_id = init_res["result"][-1]["update_id"]
except Exception:
    pass

found = False
for _ in range(30):  # wait up to 60 seconds
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={last_update_id + 1}&timeout=5"
        r = requests.get(url, verify=False, timeout=10)
        data = r.json()
        if data.get("ok") and data.get("result"):
            for update in data["result"]:
                last_update_id = update["update_id"]
                chat = None
                if "message" in update:
                    chat = update["message"]["chat"]
                elif "my_chat_member" in update:
                    chat = update["my_chat_member"]["chat"]
                elif "channel_post" in update:
                    chat = update["channel_post"]["chat"]

                if chat:
                    print("\n" + "=" * 50)
                    print(f"BERHASIL MENDAPATKAN CHAT ID!")
                    print(f"Chat ID    : {chat['id']}")
                    print(f"Title      : {chat.get('title', 'Private')}")
                    print(f"Type       : {chat.get('type')}")
                    print("=" * 50)

                    # Update config.py automatically
                    with open("config.py", "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    import re
                    content = re.sub(r'GROUP_CHAT_ID\s*=\s*["\'].*?["\']', f'GROUP_CHAT_ID = "{chat["id"]}"', content)
                    with open("config.py", "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"config.py otomatis terupdate dengan GROUP_CHAT_ID = \"{chat['id']}\"!")
                    found = True
                    break
        if found:
            break
    except Exception as e:
        pass
    time.sleep(1)

if not found:
    print("\nBelum ada pesan terdeteksi dalam 30 detik.")
    print("Pastikan bot di grup punya izin baca pesan atau jadikan bot Admin.")
