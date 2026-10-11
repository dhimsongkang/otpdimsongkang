# ═══════════════════════════════════════════════════════════════
#  IVASMS SCRAPER - Monitor OTP dari website ivasms.com
#  ─────────────────────────────────────────────────────────────
#  Disesuaikan dengan arsitektur multi-step AJAX IVASMS:
#  1. GET /portal/sms/received (ambil _token CSRF)
#  2. POST /portal/sms/received/getsms (ambil daftar RANGE aktif hari ini)
#  3. POST /portal/sms/received/getsms/number (ambil daftar nomor per RANGE)
#  4. POST /portal/sms/received/getsms/number/sms (ambil isi SMS detail)
# ═══════════════════════════════════════════════════════════════

import cloudscraper
import json
import logging
import gzip
import re
import time
from datetime import datetime
from bs4 import BeautifulSoup

try:
    import brotli
except ImportError:
    brotli = None

logger = logging.getLogger(__name__)


# ────────────────────────────────────────────
#  COUNTRY DATA - Kode negara + flag emoji
# ────────────────────────────────────────────
COUNTRY_FLAGS = {
    "AF": "🇦🇫", "AL": "🇦🇱", "DZ": "🇩🇿", "AO": "🇦🇴", "AR": "🇦🇷",
    "AM": "🇦🇲", "AU": "🇦🇺", "AT": "🇦🇹", "AZ": "🇦🇿", "BD": "🇧🇩",
    "BY": "🇧🇾", "BE": "🇧🇪", "BJ": "🇧🇯", "BO": "🇧🇴", "BA": "🇧🇦",
    "BW": "🇧🇼", "BR": "🇧🇷", "BN": "🇧🇳", "BG": "🇧🇬", "BF": "🇧🇫",
    "BI": "🇧🇮", "KH": "🇰🇭", "CM": "🇨🇲", "CA": "🇨🇦", "CV": "🇨🇻",
    "CF": "🇨🇫", "TD": "🇹🇩", "CL": "🇨🇱", "CN": "🇨🇳", "CO": "🇨🇴",
    "KM": "🇰🇲", "CG": "🇨🇬", "CD": "🇨🇩", "CR": "🇨🇷", "CI": "🇨🇮",
    "HR": "🇭🇷", "CU": "🇨🇺", "CY": "🇨🇾", "CZ": "🇨🇿", "DK": "🇩🇰",
    "DJ": "🇩🇯", "DO": "🇩🇴", "EC": "🇪🇨", "EG": "🇪🇬", "SV": "🇸🇻",
    "GQ": "🇬🇶", "ER": "🇪🇷", "EE": "🇪🇪", "ET": "🇪🇹", "FJ": "🇫🇯",
    "FI": "🇫🇮", "FR": "🇫🇷", "GA": "🇬🇦", "GM": "🇬🇲", "GE": "🇬🇪",
    "DE": "🇩🇪", "GH": "🇬🇭", "GR": "🇬🇷", "GT": "🇬🇹", "GN": "🇬🇳",
    "GW": "🇬🇼", "GY": "🇬🇾", "HT": "🇭🇹", "HN": "🇭🇳", "HK": "🇭🇰",
    "HU": "🇭🇺", "IS": "🇮🇸", "IN": "🇮🇳", "ID": "🇮🇩", "IR": "🇮🇷",
    "IQ": "🇮🇶", "IE": "🇮🇪", "IL": "🇮🇱", "IT": "🇮🇹", "JM": "🇯🇲",
    "JP": "🇯🇵", "JO": "🇯🇴", "KZ": "🇰🇿", "KE": "🇰🇪", "KR": "🇰🇷",
    "KW": "🇰🇼", "KG": "🇰🇬", "LA": "🇱🇦", "LV": "🇱🇻", "LB": "🇱🇧",
    "LS": "🇱🇸", "LR": "🇱🇷", "LY": "🇱🇾", "LT": "🇱🇹", "LU": "🇱🇺",
    "MO": "🇲🇴", "MK": "🇲🇰", "MG": "🇲🇬", "MW": "🇲🇼", "MY": "🇲🇾",
    "MV": "🇲🇻", "ML": "🇲🇱", "MT": "🇲🇹", "MR": "🇲🇷", "MU": "🇲🇺",
    "MX": "🇲🇽", "MD": "🇲🇩", "MN": "🇲🇳", "ME": "🇲🇪", "MA": "🇲🇦",
    "MZ": "🇲🇿", "MM": "🇲🇲", "NA": "🇳🇦", "NP": "🇳🇵", "NL": "🇳🇱",
    "NZ": "🇳🇿", "NI": "🇳🇮", "NE": "🇳🇪", "NG": "🇳🇬", "NO": "🇳🇴",
    "OM": "🇴🇲", "PK": "🇵🇰", "PS": "🇵🇸", "PA": "🇵🇦", "PG": "🇵🇬",
    "PY": "🇵🇾", "PE": "🇵🇪", "PH": "🇵🇭", "PL": "🇵🇱", "PT": "🇵🇹",
    "PR": "🇵🇷", "QA": "🇶🇦", "RO": "🇷🇴", "RU": "🇷🇺", "RW": "🇷🇼",
    "SA": "🇸🇦", "SN": "🇸🇳", "RS": "🇷🇸", "SC": "🇸🇨", "SL": "🇸🇱",
    "SG": "🇸🇬", "SK": "🇸🇰", "SI": "🇸🇮", "SO": "🇸🇴", "ZA": "🇿🇦",
    "SS": "🇸🇸", "ES": "🇪🇸", "LK": "🇱🇰", "SD": "🇸🇩", "SR": "🇸🇷",
    "SZ": "🇸🇿", "SE": "🇸🇪", "CH": "🇨🇭", "SY": "🇸🇾", "TW": "🇹🇼",
    "TJ": "🇹🇯", "TZ": "🇹🇿", "TH": "🇹🇭", "TL": "🇹🇱", "TG": "🇹🇬",
    "TT": "🇹🇹", "TN": "🇹🇳", "TR": "🇹🇷", "TM": "🇹🇲", "UG": "🇺🇬",
    "UA": "🇺🇦", "AE": "🇦🇪", "GB": "🇬🇧", "US": "🇺🇸", "UY": "🇺🇾",
    "UZ": "🇺🇿", "VE": "🇻🇪", "VN": "🇻🇳", "YE": "🇾🇪", "ZM": "🇿🇲",
    "ZW": "🇿🇼", "ML": "🇲🇱",
}

# Prefix -> Country Code
PHONE_PREFIX_TO_COUNTRY = {
    "+1": "US", "+7": "RU", "+20": "EG", "+27": "ZA", "+30": "GR",
    "+31": "NL", "+32": "BE", "+33": "FR", "+34": "ES", "+36": "HU",
    "+39": "IT", "+40": "RO", "+41": "CH", "+43": "AT", "+44": "GB",
    "+45": "DK", "+46": "SE", "+47": "NO", "+48": "PL", "+49": "DE",
    "+51": "PE", "+52": "MX", "+53": "CU", "+54": "AR", "+55": "BR",
    "+56": "CL", "+57": "CO", "+58": "VE", "+60": "MY", "+61": "AU",
    "+62": "ID", "+63": "PH", "+64": "NZ", "+65": "SG", "+66": "TH",
    "+81": "JP", "+82": "KR", "+84": "VN", "+86": "CN", "+90": "TR",
    "+91": "IN", "+92": "PK", "+93": "AF", "+94": "LK", "+95": "MM",
    "+98": "IR", "+211": "SS", "+212": "MA", "+213": "DZ", "+216": "TN",
    "+218": "LY", "+220": "GM", "+221": "SN", "+222": "MR", "+223": "ML",
    "+224": "GN", "+225": "CI", "+226": "BF", "+227": "NE", "+228": "TG",
    "+229": "BJ", "+230": "MU", "+231": "LR", "+232": "SL", "+233": "GH",
    "+234": "NG", "+235": "TD", "+236": "CF", "+237": "CM", "+238": "CV",
    "+239": "ST", "+240": "GQ", "+241": "GA", "+242": "CG", "+243": "CD",
    "+244": "AO", "+245": "GW", "+248": "SC", "+249": "SD", "+250": "RW",
    "+251": "ET", "+252": "SO", "+253": "DJ", "+254": "KE", "+255": "TZ",
    "+256": "UG", "+257": "BI", "+258": "MZ", "+260": "ZM", "+261": "MG",
    "+262": "RE", "+263": "ZW", "+265": "MW", "+266": "LS", "+267": "BW",
    "+268": "SZ", "+269": "KM", "+290": "SH", "+291": "ER",
    "+350": "GI", "+351": "PT", "+352": "LU", "+353": "IE", "+354": "IS",
    "+355": "AL", "+356": "MT", "+357": "CY", "+358": "FI",
    "+370": "LT", "+371": "LV", "+372": "EE", "+373": "MD",
    "+374": "AM", "+375": "BY", "+376": "AD", "+380": "UA", "+381": "RS",
    "+382": "ME", "+383": "XK", "+385": "HR", "+386": "SI", "+387": "BA",
    "+389": "MK", "+420": "CZ", "+421": "SK", "+855": "KH", "+856": "LA",
    "+880": "BD", "+960": "MV", "+961": "LB", "+962": "JO", "+963": "SY",
    "+964": "IQ", "+965": "KW", "+966": "SA", "+967": "YE", "+968": "OM",
    "+970": "PS", "+971": "AE", "+972": "IL", "+973": "BH", "+974": "QA",
    "+975": "BT", "+976": "MN", "+977": "NP", "+992": "TJ", "+993": "TM",
    "+994": "AZ", "+995": "GE", "+996": "KG", "+998": "UZ",
}

COUNTRY_NAME_TO_CODE = {
    "GERMANY": "DE", "FRANCE": "FR", "SPAIN": "ES", "ITALY": "IT",
    "UNITED KINGDOM": "GB", "UK": "GB", "UNITED STATES": "US", "USA": "US",
    "BRAZIL": "BR", "INDIA": "IN", "INDONESIA": "ID", "JAPAN": "JP",
    "SOUTH KOREA": "KR", "KOREA": "KR", "CHINA": "CN", "RUSSIA": "RU",
    "TURKEY": "TR", "NIGERIA": "NG", "EGYPT": "EG", "SOUTH AFRICA": "ZA",
    "KENYA": "KE", "GHANA": "GH", "CAMEROON": "CM", "SENEGAL": "SN",
    "MALI": "ML", "CAMBODIA": "KH", "THAILAND": "TH", "VIETNAM": "VN",
    "MALAYSIA": "MY", "PHILIPPINES": "PH", "SINGAPORE": "SG", "MYANMAR": "MM",
    "PAKISTAN": "PK", "BANGLADESH": "BD", "NEPAL": "NP", "MEXICO": "MX",
    "ARGENTINA": "AR", "COLOMBIA": "CO", "CHILE": "CL", "PERU": "PE",
}


def get_country_from_phone(phone_number: str) -> tuple:
    """Deteksi kode negara dari nomor telepon. Returns (country_code, flag_emoji)."""
    phone = phone_number.strip()
    if not phone.startswith("+"):
        phone = "+" + phone

    for length in [5, 4, 3, 2]:
        prefix = phone[:length]
        if prefix in PHONE_PREFIX_TO_COUNTRY:
            cc = PHONE_PREFIX_TO_COUNTRY[prefix]
            flag = COUNTRY_FLAGS.get(cc, "🏳️")
            return cc, flag

    return "??", "🏳️"


def get_country_from_range_name(range_name: str) -> tuple:
    """Parse country dari range name seperti 'GERMANY 1100' -> ('DE', '🇩🇪')."""
    if not range_name:
        return "??", "🏳️"
    name_clean = re.sub(r'\s*\d+\s*$', '', range_name.strip()).upper()
    if name_clean in COUNTRY_NAME_TO_CODE:
        cc = COUNTRY_NAME_TO_CODE[name_clean]
        return cc, COUNTRY_FLAGS.get(cc, "🏳️")
    if name_clean in COUNTRY_FLAGS:
        return name_clean, COUNTRY_FLAGS[name_clean]
    return "??", "🏳️"


def mask_phone_number(phone: str) -> str:
    """
    Format nomor telepon: 4 angka pertama dan 4 angka terakhir.
    Contoh: 263799991419 -> 2637 ~ 1419
    """
    clean = phone.strip()
    prefix = "+" if clean.startswith("+") else ""
    digits = clean.lstrip("+")
    if len(digits) <= 8:
        return clean
    first_4 = digits[:4]
    last_4 = digits[-4:]
    return f"{prefix}{first_4} ~ {last_4}"


def detect_platform(sender_or_message: str) -> tuple:
    """Deteksi platform OTP. Returns (platform_name, emoji)."""
    text_lower = (sender_or_message or "").lower()

    platform_map = {
        "whatsapp": ("WhatsApp", "🟢"),
        "wa ": ("WhatsApp", "🟢"),
        "telegram": ("Telegram", "🔵"),
        "facebook": ("Facebook", "🔵"),
        "fb ": ("Facebook", "🔵"),
        "instagram": ("Instagram", "🟣"),
        "tiktok": ("TikTok", "⚫"),
        "twitter": ("Twitter", "🐦"),
        "x.com": ("Twitter/X", "🐦"),
        "google": ("Google", "🔴"),
        "gmail": ("Google", "🔴"),
        "yahoo": ("Yahoo", "🟣"),
        "microsoft": ("Microsoft", "🔷"),
        "apple": ("Apple", "🍎"),
        "icloud": ("Apple", "🍎"),
        "snapchat": ("Snapchat", "👻"),
        "discord": ("Discord", "💜"),
        "signal": ("Signal", "💬"),
        "viber": ("Viber", "💜"),
        "line": ("LINE", "💚"),
        "wechat": ("WeChat", "💚"),
        "uber": ("Uber", "⬛"),
        "grab": ("Grab", "💚"),
        "gojek": ("Gojek", "💚"),
        "shopee": ("Shopee", "🟠"),
        "lazada": ("Lazada", "🔵"),
        "tokopedia": ("Tokopedia", "💚"),
        "paypal": ("PayPal", "🔵"),
        "binance": ("Binance", "🟡"),
        "amazon": ("Amazon", "📦"),
        "netflix": ("Netflix", "🔴"),
        "spotify": ("Spotify", "💚"),
    }

    for keyword, (name, emoji) in platform_map.items():
        if keyword in text_lower:
            return name, emoji

    return "SMS", "📱"


def extract_otp(message_text: str) -> str:
    """Ekstrak kode OTP dari teks pesan SMS."""
    if not message_text:
        return "N/A"

    # WhatsApp style: 265-192 or 265 192 -> 265192
    wa_match = re.search(r'(?:code|kode|otp|pin)[:\s]+(\d{3}[\-\s]\d{3})', message_text, re.IGNORECASE)
    if wa_match:
        return wa_match.group(1).replace("-", "").replace(" ", "")

    # Common patterns
    patterns = [
        r'(?:code|kode|otp|pin|verify|verification|verifikasi)[:\-\s]+(\d{4,8})',
        r'(\d{4,8})\s*(?:is your|adalah|code|kode|otp)',
        r'(?:^|\s)(\d{6})(?:\s|$|\.|,)',   # 6 digit standalone
        r'(?:^|\s)(\d{4})(?:\s|$|\.|,)',    # 4 digit standalone
        r'(?:^|\s)(\d{5})(?:\s|$|\.|,)',    # 5 digit standalone
        r'(?:^|\s)(\d{8})(?:\s|$|\.|,)',    # 8 digit standalone
    ]

    for pattern in patterns:
        match = re.search(pattern, message_text, re.IGNORECASE)
        if match:
            return match.group(1)

    numbers = re.findall(r'\d{4,8}', message_text)
    if numbers:
        return numbers[0]

    return "N/A"


class IVASMSClient:
    """
    Client untuk scraping SMS dari IVASMS menggunakan multi-tier AJAX:
    /portal/sms/received/getsms -> /getsms/number -> /getsms/number/sms
    """

    def __init__(self, cookies: dict | list, base_url: str = "https://www.ivasms.com"):
        self.scraper = cloudscraper.create_scraper()
        self.base_url = base_url.rstrip("/")
        self.csrf_token = None
        self.seen_ids = set()
        self._setup_headers()
        self._load_cookies(cookies)

    def _setup_headers(self):
        self.scraper.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36 Edg/155.0.0.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Referer': f'{self.base_url}/portal/sms/received',
        })

    def update_cookies(self, cookies: dict | list):
        """Update/refresh cookies pada session aktif."""
        self._load_cookies(cookies)
        self.csrf_token = None
        logger.info("Cookies updated in scraper session")

    def _load_cookies(self, cookies):
        if isinstance(cookies, dict):
            for name, value in cookies.items():
                if value:
                    self.scraper.cookies.set(name, value)
        elif isinstance(cookies, list):
            for cookie in cookies:
                if 'name' in cookie and 'value' in cookie:
                    self.scraper.cookies.set(cookie['name'], cookie['value'])
        logger.info(f"Loaded {len(self.scraper.cookies)} cookies")

    def _refresh_csrf_token(self) -> str:
        """Mengambil CSRF token terbaru dari halaman received."""
        try:
            url = f"{self.base_url}/portal/sms/received"
            res = self.scraper.get(url, timeout=15)
            if res.status_code == 200:
                match = re.search(r"f\.append\('_token',\s*[\"']([^\"']+)[\"']\)", res.text)
                if not match:
                    match = re.search(r'name=["\']_token["\']\s+value=["\']([^"\']+)["\']', res.text)
                if match:
                    self.csrf_token = match.group(1)
                    return self.csrf_token
        except Exception as e:
            logger.error(f"Failed to refresh CSRF token: {e}")
        return self.csrf_token or ""

    def get_all_sms(self, date_str: str = None) -> list:
        """
        Ambil semua SMS hari ini secara rekursif melalui endpoint AJAX IVASMS.
        """
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")

        if not self.csrf_token:
            self._refresh_csrf_token()

        all_sms = []
        ajax_headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': self.base_url,
            'Referer': f"{self.base_url}/portal/sms/received",
            'Accept': 'text/html, */*; q=0.01',
        }

        # Step 1: POST /portal/sms/received/getsms
        getsms_url = f"{self.base_url}/portal/sms/received/getsms"
        data = {
            'from': date_str,
            'to': date_str,
            '_token': self.csrf_token or "",
        }

        try:
            r = self.scraper.post(getsms_url, data=data, headers=ajax_headers, timeout=15)
            if r.status_code != 200:
                logger.warning(f"getsms returned {r.status_code}, refreshing token...")
                self._refresh_csrf_token()
                data['_token'] = self.csrf_token or ""
                r = self.scraper.post(getsms_url, data=data, headers=ajax_headers, timeout=15)
                if r.status_code != 200:
                    return []

            # Parse Range entries from getsms response
            # Format: toggleRange('GERMANY 1100', 'GERMANY_1100')
            ranges = re.findall(r"toggleRange\(['\"]([^'\"]+)['\"],\s*['\"]([^'\"]+)['\"]\)", r.text)
            logger.debug(f"Found ranges: {ranges}")

            for range_id, safe_name in ranges:
                c_code, flag = get_country_from_range_name(range_id)

                # Step 2: POST /portal/sms/received/getsms/number
                num_url = f"{self.base_url}/portal/sms/received/getsms/number"
                num_data = {
                    '_token': self.csrf_token or "",
                    'start': date_str,
                    'end': date_str,
                    'range': range_id,
                }
                r_num = self.scraper.post(num_url, data=num_data, headers=ajax_headers, timeout=15)
                if r_num.status_code != 200:
                    continue

                # Parse numbers from getsms/number response
                # Format: toggleNum...('4915219700147', '4915219700147_333134757')
                numbers = re.findall(r"toggleNum[A-Za-z0-9]*\(['\"]([^'\"]+)['\"],\s*['\"]([^'\"]+)['\"]\)", r_num.text)
                logger.debug(f"Found numbers for range {range_id}: {numbers}")

                for phone_num, num_safe in numbers:
                    phone_cc, phone_flag = get_country_from_phone(phone_num)
                    final_cc = phone_cc if phone_cc != "??" else c_code
                    final_flag = phone_flag if phone_flag != "🏳️" else flag

                    # Step 3: POST /portal/sms/received/getsms/number/sms
                    sms_url = f"{self.base_url}/portal/sms/received/getsms/number/sms"
                    sms_data = {
                        '_token': self.csrf_token or "",
                        'start': date_str,
                        'end': date_str,
                        'Number': phone_num,
                        'Range': range_id,
                    }
                    r_sms = self.scraper.post(sms_url, data=sms_data, headers=ajax_headers, timeout=15)
                    if r_sms.status_code != 200:
                        continue

                    # Parse SMS table rows
                    soup = BeautifulSoup(r_sms.text, 'html.parser')
                    table = soup.find('table')
                    if not table:
                        continue

                    tbody = table.find('tbody') or table
                    for tr in tbody.find_all('tr'):
                        tds = tr.find_all('td')
                        if len(tds) < 3:
                            continue

                        sender = tds[0].get_text(strip=True)
                        msg_div = tds[1].find('div', class_='msg-text')
                        message = msg_div.get_text(strip=True) if msg_div else tds[1].get_text(strip=True)
                        time_cell = tds[2].get_text(strip=True)
                        rev_cell = tds[3].get_text(strip=True) if len(tds) > 3 else "$0.00"

                        otp = extract_otp(message)
                        platform, p_emoji = detect_platform(sender)
                        if platform == "SMS":
                            platform, p_emoji = detect_platform(message)

                        sms_id = f"{phone_num}_{sender}_{otp}_{time_cell}"

                        all_sms.append({
                            "id": sms_id,
                            "phone": phone_num,
                            "phone_masked": mask_phone_number(phone_num),
                            "sender": sender,
                            "message": message,
                            "otp": otp,
                            "platform": platform,
                            "platform_emoji": p_emoji,
                            "country_code": final_cc,
                            "flag": final_flag,
                            "timestamp": time_cell,
                            "revenue": rev_cell,
                            "range_name": range_id,
                        })

        except Exception as e:
            logger.error(f"Error fetching SMS data: {e}")

        return all_sms

    def get_new_sms(self, date_str: str = None) -> list:
        """Ambil SMS baru yang belum pernah dikirim."""
        all_sms = self.get_all_sms(date_str)
        new_sms = []
        for sms in all_sms:
            if sms["id"] not in self.seen_ids:
                self.seen_ids.add(sms["id"])
                new_sms.append(sms)

        if new_sms:
            logger.info(f"Found {len(new_sms)} new SMS")
        return new_sms

    def mark_initial_as_seen(self):
        """Tandai semua SMS lama saat bot startup."""
        all_sms = self.get_all_sms()
        for sms in all_sms:
            self.seen_ids.add(sms["id"])
        logger.info(f"Marked {len(all_sms)} initial SMS as seen")
        return len(all_sms)

    def check_connection(self) -> bool:
        """Verifikasi session cookie masih valid."""
        try:
            r = self.scraper.get(f"{self.base_url}/portal/sms/received", timeout=15)
            if r.status_code == 200 and "login" not in r.url.lower():
                return True
            return False
        except Exception:
            return False
