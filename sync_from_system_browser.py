# ═══════════════════════════════════════════════════════════════
#  AUTO EXTRACT COOKIES FROM FIREFOX / CACHY BROWSER
# ═══════════════════════════════════════════════════════════════
import glob
import os
import re
import shutil
import sqlite3
import sys

def get_firefox_cookies():
    """Extract cookies from Firefox or Cachy-Browser profiles on Linux or Windows"""
    cookies_found = {}
    
    # Path profil Firefox & Cachy-browser di Linux & Windows
    potential_paths = [
        os.path.expanduser("~/.mozilla/firefox/*"),
        os.path.expanduser("~/.cachy-browser/*"),
        os.path.expanduser("~/.cachy/browser/*"),
        os.path.expanduser("~/.librewolf/*"),
        os.path.expanduser("~/.config/cachy-browser/*"),
        os.path.expanduser("~/.config/librewolf/*"),
        os.path.expanduser("~/.config/google-chrome/*"),
        os.path.expanduser("~/.config/chromium/*"),
    ]
    
    db_paths = []
    # 1. Cek folder profil yang umum
    for p in potential_paths:
        for profile in glob.glob(p):
            for filename in ["cookies.sqlite", "Cookies"]:
                cookie_db = os.path.join(profile, filename)
                if os.path.exists(cookie_db):
                    db_paths.append(cookie_db)

    # 2. Jika belum ketemu, lakukan pencarian otomatis di folder ~/.mozilla & ~/.cachy
    if not db_paths:
        for root_dir in [os.path.expanduser("~/.mozilla"), os.path.expanduser("~/.cachy"), os.path.expanduser("~/.config")]:
            if os.path.exists(root_dir):
                for root, dirs, files in os.walk(root_dir):
                    if "cookies.sqlite" in files:
                        db_paths.append(os.path.join(root, "cookies.sqlite"))

    if not db_paths:
        print("❌ Tidak ditemukan file database cookies browser di home folder.")
        print("💡 Tips: Pastikan browser tempat Anda login sudah dibuka setidaknya sekali.")
        return {}

    temp_db = "temp_cookies.sqlite"
    for db in db_paths:
        try:
            # Copy agar tidak locked jika browser sedang terbuka
            shutil.copy2(db, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT name, value FROM moz_cookies WHERE host LIKE '%ivasms.com%'")
            rows = cursor.fetchall()
            for name, val in rows:
                cookies_found[name] = val
            conn.close()
            if os.path.exists(temp_db):
                os.remove(temp_db)
            if "ivas_sms_session" in cookies_found:
                print(f"✅ Berhasil mengekstrak {len(cookies_found)} cookie IVASMS dari: {db}")
                break
        except Exception as e:
            if os.path.exists(temp_db):
                try: os.remove(temp_db)
                except: pass
            continue

    return cookies_found

def update_config_file(cookies):
    """Update config.py with the extracted cookies"""
    if not cookies:
        print("⚠️ Tidak ada cookie yang diekstrak.")
        return False
        
    config_path = os.path.join(os.path.dirname(__file__), "config.py")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()

        cookie_str = "COOKIES = {\n"
        for k, v in cookies.items():
            cookie_str += f'    "{k}": "{v}",\n'
        cookie_str += "}"

        pattern = r"COOKIES\s*=\s*\{[^}]*\}"
        if re.search(pattern, content):
            new_content = re.sub(pattern, cookie_str, content)
        else:
            new_content = content + "\n\n" + cookie_str

        with open(config_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        print("🎉 config.py BERHASIL DIUPDATE OTOMATIS DENGAN COOKIE TERBARU!")
        return True
    except Exception as e:
        print(f"❌ Gagal update config.py: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Mencari cookie login IVASMS dari browser sistem...")
    cookies = get_firefox_cookies()
    if cookies and "ivas_sms_session" in cookies:
        update_config_file(cookies)
        print("\n🚀 Anda sekarang bisa langsung jalankan:")
        print("   ./venv/bin/python bot.py")
        print("   atau ./venv/bin/python admin_server.py")
    else:
        print("⚠️ Cookie ivas_sms_session belum ditemukan. Pastikan Anda sudah login ke ivasms.com di browser.")
