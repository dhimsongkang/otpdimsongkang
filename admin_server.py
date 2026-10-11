# ═══════════════════════════════════════════════════════════════
#  ADMIN DASHBOARD SERVER - OTP IVA SMS
#  ─────────────────────────────────────────────────────────────
#  Web admin panel untuk mengelola OTP Bot, SMS Log,
#  Auto-Add Numbers, dan konfigurasi.
# ═══════════════════════════════════════════════════════════════

import asyncio
import json
import logging
import os
import re
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, render_template, jsonify, request, redirect, url_for, session

# ────────────────────────────────────────────
#  APP SETUP
# ────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = "otp-iva-sms-admin-secret-2026"

logger = logging.getLogger("admin")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# ────────────────────────────────────────────
#  IN-MEMORY STATE
# ────────────────────────────────────────────

# SMS Log storage (in-memory, loads from bot.log)
sms_log = []

# Bot process reference
bot_process = None
bot_status = {"running": False, "pid": None, "started_at": None}

# Auto-add state
auto_add_state = {
    "running": False,
    "range_name": "",
    "max_add": 0,
    "delay": 60,
    "added": 0,
    "failed": 0,
    "skipped": 0,
    "total_found": 0,
    "current_action": 0,
    "last_message": "",
    "started_at": None,
    "process": None,
}

# IVASMS connection state
ivasms_status = {
    "connected": False,
    "last_check": None,
    "cookies_valid": False,
}

# Admin credentials
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"


# ────────────────────────────────────────────
#  AUTH DECORATOR
# ────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# ────────────────────────────────────────────
#  HELPER FUNCTIONS
# ────────────────────────────────────────────

def load_config():
    """Load current config from config.py"""
    config = {}
    config_path = os.path.join(os.path.dirname(__file__), "config.py")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Parse key-value pairs
        patterns = {
            "BOT_TOKEN": r'BOT_TOKEN\s*=\s*"([^"]*)"',
            "GROUP_CHAT_ID": r'GROUP_CHAT_ID\s*=\s*"([^"]*)"',
            "GROUP_LINK": r'GROUP_LINK\s*=\s*"([^"]*)"',
            "NUMBER_LINK": r'NUMBER_LINK\s*=\s*"([^"]*)"',
            "OWNER_LINK": r'OWNER_LINK\s*=\s*"([^"]*)"',
            "BOT_NAME": r'BOT_NAME\s*=\s*"([^"]*)"',
            "IVASMS_URL": r'IVASMS_URL\s*=\s*"([^"]*)"',
            "IVASMS_EMAIL": r'IVASMS_EMAIL\s*=\s*"([^"]*)"',
            "IVASMS_PASSWORD": r'IVASMS_PASSWORD\s*=\s*"([^"]*)"',
            "POLL_INTERVAL": r'POLL_INTERVAL\s*=\s*(\d+)',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, content)
            if match:
                config[key] = match.group(1)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
    
    return config


def save_config(new_config):
    """Save config changes to config.py"""
    config_path = os.path.join(os.path.dirname(__file__), "config.py")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        replacements = {
            "BOT_TOKEN": (r'(BOT_TOKEN\s*=\s*)"[^"]*"', r'\1"{}"'),
            "GROUP_CHAT_ID": (r'(GROUP_CHAT_ID\s*=\s*)"[^"]*"', r'\1"{}"'),
            "GROUP_LINK": (r'(GROUP_LINK\s*=\s*)"[^"]*"', r'\1"{}"'),
            "NUMBER_LINK": (r'(NUMBER_LINK\s*=\s*)"[^"]*"', r'\1"{}"'),
            "OWNER_LINK": (r'(OWNER_LINK\s*=\s*)"[^"]*"', r'\1"{}"'),
            "BOT_NAME": (r'(BOT_NAME\s*=\s*)"[^"]*"', r'\1"{}"'),
            "IVASMS_EMAIL": (r'(IVASMS_EMAIL\s*=\s*)"[^"]*"', r'\1"{}"'),
            "IVASMS_PASSWORD": (r'(IVASMS_PASSWORD\s*=\s*)"[^"]*"', r'\1"{}"'),
            "POLL_INTERVAL": (r'(POLL_INTERVAL\s*=\s*)\d+', r'\1{}'),
        }
        
        for key, (pattern, replacement) in replacements.items():
            if key in new_config:
                content = re.sub(pattern, replacement.format(new_config[key]), content)
        
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return True
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        return False


def parse_bot_log():
    """Parse bot.log to extract SMS entries"""
    log_path = os.path.join(os.path.dirname(__file__), "bot.log")
    entries = []
    
    if not os.path.exists(log_path):
        return entries
    
    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        
        # Parse OTP messages from log
        for line in lines:
            # Look for SMS forwarded lines
            if "New OTP" in line or "Forwarded" in line or "new SMS" in line.lower():
                timestamp_match = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
                timestamp = timestamp_match.group(1) if timestamp_match else ""
                entries.append({
                    "timestamp": timestamp,
                    "message": line.strip(),
                    "type": "otp"
                })
            elif "Marked" in line and "initial SMS" in line:
                timestamp_match = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
                timestamp = timestamp_match.group(1) if timestamp_match else ""
                entries.append({
                    "timestamp": timestamp,
                    "message": line.strip(),
                    "type": "info"
                })
            elif "ERROR" in line or "error" in line:
                timestamp_match = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
                timestamp = timestamp_match.group(1) if timestamp_match else ""
                entries.append({
                    "timestamp": timestamp,
                    "message": line.strip(),
                    "type": "error"
                })
    except Exception as e:
        logger.error(f"Error parsing bot log: {e}")
    
    return entries[-100:]  # Last 100 entries


def get_log_tail(n=50):
    """Get last N lines from bot.log"""
    log_path = os.path.join(os.path.dirname(__file__), "bot.log")
    if not os.path.exists(log_path):
        return []
    
    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        return [line.strip() for line in lines[-n:]]
    except:
        return []


def check_bot_running():
    """Check if bot.py is running"""
    global bot_status
    try:
        if bot_process and bot_process.poll() is None:
            bot_status["running"] = True
            bot_status["pid"] = bot_process.pid
        else:
            # Check system processes for bot.py
            if sys.platform == "win32":
                # Cari proses python yang menjalankan bot.py via powershell
                cmd = 'powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like \'*bot.py*\' } | Select-Object -ExpandProperty ProcessId"'
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                out = res.stdout.strip()
                if out:
                    pids = [int(p) for p in out.splitlines() if p.strip().isdigit()]
                    valid_pids = [p for p in pids if p != os.getpid()]
                    if valid_pids:
                        bot_status["running"] = True
                        bot_status["pid"] = valid_pids[0]
                        return bot_status
            else:
                # Linux check
                result = subprocess.run(
                    ["pgrep", "-f", "bot.py"],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0 and result.stdout.strip():
                    pids = result.stdout.strip().splitlines()
                    valid_pids = [int(p) for p in pids if int(p) != os.getpid()]
                    if valid_pids:
                        bot_status["running"] = True
                        bot_status["pid"] = valid_pids[0]
                        return bot_status
            bot_status["running"] = False
            bot_status["pid"] = None
    except:
        pass
    return bot_status


async def check_ivasms_connection():
    """Check IVASMS connection via config cookies and fallback to browser"""
    global ivasms_status
    try:
        from ivasms_scraper import IVASMSClient
        from config import COOKIES, IVASMS_URL
        client = IVASMSClient(COOKIES, IVASMS_URL)
        if client.check_connection():
            ivasms_status["connected"] = True
            ivasms_status["last_check"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ivasms_status["cookies_valid"] = True
            return ivasms_status

        # If not connected, try browser auto-sync
        from cookie_sync import get_fresh_cookies_from_browser
        cookies = await get_fresh_cookies_from_browser()
        if cookies and "ivas_sms_session" in cookies:
            client.update_cookies(cookies)
            ivasms_status["connected"] = client.check_connection()
        else:
            ivasms_status["connected"] = False

        ivasms_status["last_check"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ivasms_status["cookies_valid"] = bool(cookies)
    except Exception as e:
        ivasms_status["connected"] = False
        ivasms_status["last_check"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.error(f"Connection check error: {e}")
    return ivasms_status


# ────────────────────────────────────────────
#  ROUTES - AUTH
# ────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == ADMIN_USER and password == ADMIN_PASS:
            session["logged_in"] = True
            session["username"] = username
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ────────────────────────────────────────────
#  ROUTES - PAGES
# ────────────────────────────────────────────

@app.route("/")
@login_required
def dashboard():
    return render_template("admin.html", page="dashboard")


@app.route("/sms-log")
@login_required
def sms_log_page():
    return render_template("admin.html", page="sms-log")


@app.route("/auto-add")
@login_required
def auto_add_page():
    return render_template("admin.html", page="auto-add")


@app.route("/bot-control")
@login_required
def bot_control_page():
    return render_template("admin.html", page="bot-control")


@app.route("/settings")
@login_required
def settings_page():
    return render_template("admin.html", page="settings")


# ────────────────────────────────────────────
#  API ROUTES
# ────────────────────────────────────────────

@app.route("/api/dashboard")
@login_required
def api_dashboard():
    """Get dashboard stats"""
    config = load_config()
    log_entries = parse_bot_log()
    
    otp_count = sum(1 for e in log_entries if e["type"] == "otp")
    error_count = sum(1 for e in log_entries if e["type"] == "error")
    
    # Check bot running
    check_bot_running()
    
    return jsonify({
        "stats": {
            "otp_received": otp_count,
            "errors": error_count,
            "bot_running": bot_status["running"],
            "ivasms_connected": ivasms_status.get("connected", False),
            "poll_interval": config.get("POLL_INTERVAL", "10"),
            "bot_name": config.get("BOT_NAME", "OTP_BOT"),
        },
        "recent_logs": log_entries[-10:],
        "bot_status": bot_status,
        "ivasms_status": ivasms_status,
    })


@app.route("/api/sms-log")
@login_required
def api_sms_log():
    """Get SMS log entries"""
    entries = parse_bot_log()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 25, type=int)
    
    # Reverse for newest first
    entries.reverse()
    
    total = len(entries)
    start = (page - 1) * per_page
    end = start + per_page
    
    return jsonify({
        "entries": entries[start:end],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
    })


@app.route("/api/logs/tail")
@login_required
def api_logs_tail():
    """Get tail of bot.log"""
    n = request.args.get("n", 50, type=int)
    lines = get_log_tail(n)
    return jsonify({"lines": lines, "count": len(lines)})


@app.route("/api/bot/start", methods=["POST"])
@login_required
def api_bot_start():
    """Start bot.py"""
    global bot_process, bot_status
    
    if bot_process and bot_process.poll() is None:
        return jsonify({"success": False, "message": "Bot sudah berjalan!"})
    
    try:
        bot_process = subprocess.Popen(
            [sys.executable, "bot.py"],
            cwd=os.path.dirname(__file__),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        bot_status = {
            "running": True,
            "pid": bot_process.pid,
            "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        return jsonify({"success": True, "message": "Bot berhasil dijalankan!", "pid": bot_process.pid})
    except Exception as e:
        return jsonify({"success": False, "message": f"Gagal menjalankan bot: {e}"})


@app.route("/api/bot/stop", methods=["POST"])
@login_required
def api_bot_stop():
    """Stop bot.py"""
    global bot_process, bot_status
    
    if bot_process and bot_process.poll() is None:
        bot_process.terminate()
        try:
            bot_process.wait(timeout=5)
        except:
            bot_process.kill()
        bot_status = {"running": False, "pid": None, "started_at": None}
        return jsonify({"success": True, "message": "Bot berhasil dihentikan!"})
    
    return jsonify({"success": False, "message": "Bot tidak sedang berjalan."})


@app.route("/api/bot/status")
@login_required
def api_bot_status():
    """Get bot status"""
    check_bot_running()
    return jsonify(bot_status)


@app.route("/api/ivasms/check", methods=["POST"])
@login_required
def api_ivasms_check():
    """Check IVASMS connection"""
    try:
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(check_ivasms_connection())
        loop.close()
        return jsonify({"success": True, "status": result})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/api/auto-add/start", methods=["POST"])
@login_required
def api_auto_add_start():
    """Start auto-add numbers"""
    global auto_add_state
    
    if auto_add_state["running"]:
        return jsonify({"success": False, "message": "Auto-add sudah berjalan!"})
    
    data = request.json
    range_name = data.get("range_name", "")
    max_add = data.get("max_add", 0)
    delay = data.get("delay", 60)
    
    if not range_name:
        return jsonify({"success": False, "message": "Range name harus diisi!"})
    
    try:
        proc = subprocess.Popen(
            [sys.executable, "auto_add_numbers.py", range_name, str(max_add), str(delay)],
            cwd=os.path.dirname(__file__),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        
        auto_add_state = {
            "running": True,
            "range_name": range_name,
            "max_add": max_add,
            "delay": delay,
            "added": 0,
            "failed": 0,
            "skipped": 0,
            "total_found": 0,
            "current_action": 0,
            "last_message": "Memulai...",
            "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "process": proc,
        }
        
        # Monitor in background thread
        def monitor_auto_add():
            global auto_add_state
            try:
                for line in iter(proc.stdout.readline, b''):
                    decoded = line.decode("utf-8", errors="replace").strip()
                    if decoded:
                        auto_add_state["last_message"] = decoded
                        
                        # Parse stats
                        if "Added=" in decoded:
                            m = re.search(r"Added=(\d+).*Failed=(\d+).*Skipped=(\d+)", decoded)
                            if m:
                                auto_add_state["added"] = int(m.group(1))
                                auto_add_state["failed"] = int(m.group(2))
                                auto_add_state["skipped"] = int(m.group(3))
                        
                        if "Action #" in decoded:
                            m = re.search(r"Action #(\d+)", decoded)
                            if m:
                                auto_add_state["current_action"] = int(m.group(1))
                        
                        if "total records" in decoded:
                            m = re.search(r"(\d+) total records", decoded)
                            if m:
                                auto_add_state["total_found"] = int(m.group(1))
                
                proc.wait()
            except:
                pass
            finally:
                auto_add_state["running"] = False
                auto_add_state["process"] = None
        
        thread = threading.Thread(target=monitor_auto_add, daemon=True)
        thread.start()
        
        return jsonify({"success": True, "message": f"Auto-add dimulai untuk '{range_name}'!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Gagal: {e}"})


@app.route("/api/auto-add/stop", methods=["POST"])
@login_required
def api_auto_add_stop():
    """Stop auto-add"""
    global auto_add_state
    
    proc = auto_add_state.get("process")
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except:
            proc.kill()
    
    auto_add_state["running"] = False
    auto_add_state["process"] = None
    return jsonify({"success": True, "message": "Auto-add dihentikan."})


@app.route("/api/auto-add/status")
@login_required
def api_auto_add_status():
    """Get auto-add status"""
    safe_state = {k: v for k, v in auto_add_state.items() if k != "process"}
    return jsonify(safe_state)


@app.route("/api/config", methods=["GET"])
@login_required
def api_config_get():
    """Get current config"""
    config = load_config()
    # Mask sensitive data
    if "BOT_TOKEN" in config:
        token = config["BOT_TOKEN"]
        config["BOT_TOKEN_MASKED"] = token[:10] + "..." + token[-5:] if len(token) > 15 else token
    if "IVASMS_PASSWORD" in config:
        config["IVASMS_PASSWORD_MASKED"] = "••••••••"
    return jsonify(config)


@app.route("/api/config", methods=["POST"])
@login_required
def api_config_save():
    """Save config changes"""
    data = request.json
    if save_config(data):
        return jsonify({"success": True, "message": "Konfigurasi berhasil disimpan!"})
    return jsonify({"success": False, "message": "Gagal menyimpan konfigurasi."})


# ────────────────────────────────────────────
#  RUN
# ────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("  🌐 OTP IVA SMS - Admin Dashboard")
    print("  📍 http://localhost:5000")
    print(f"  👤 Login: {ADMIN_USER} / {ADMIN_PASS}")
    print("=" * 55)
    app.run(host="0.0.0.0", port=5000, debug=True)
