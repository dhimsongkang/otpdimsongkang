# ═══════════════════════════════════════════════════════════════
#  ELITE-SMS CLIENT - Monitor OTP dari https://elite-sms.com/api
# ═══════════════════════════════════════════════════════════════

import logging
import requests
import re
from datetime import datetime
from ivasms_scraper import (
    get_country_from_phone,
    mask_phone_number,
    detect_platform,
    extract_otp,
    COUNTRY_FLAGS
)

logger = logging.getLogger(__name__)


class EliteSMSClient:
    """
    Client resmi untuk konsumsi REST API https://elite-sms.com/api
    Endpoints:
      - GET /data (live OTP feed)
      - GET /numbers (reserved numbers)
      - GET /status (status & totals)
    """

    def __init__(self, api_key: str = "", base_url: str = "https://elite-sms.com/api"):
        self.api_key = api_key.strip()
        self.base_url = base_url.rstrip("/")
        self.seen_ids = set()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        })
        if self.api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "X-API-Key": self.api_key,
            })

    def check_connection(self) -> bool:
        """Cek apakah API Elite-SMS dapat diakses dan online."""
        try:
            url = f"{self.base_url}/status"
            r = self.session.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                return data.get("status") == "ONLINE" or "otp_count" in data
            return False
        except Exception as e:
            logger.error(f"Elite-SMS check connection failed: {e}")
            return False

    def get_all_sms(self, limit: int = 50) -> list:
        """
        Ambil daftar SMS dari endpoint /data dan normalisasi formatnya
        agar kompatibel 100% dengan bot Telegram dan Admin Dashboard.
        """
        all_sms = []
        try:
            url = f"{self.base_url}/data"
            params = {"limit": limit}
            r = self.session.get(url, params=params, timeout=15)
            if r.status_code != 200:
                logger.error(f"Elite-SMS /data returned HTTP {r.status_code}")
                return []

            res_json = r.json()
            items = res_json.get("data", [])
            for item in items:
                phone_num = str(item.get("number", "")).strip()
                service = str(item.get("service", "")).strip()
                message = str(item.get("message", "")).strip()
                time_str = str(item.get("time", "")).strip()
                flag_from_api = item.get("flag", "")

                phone_cc, phone_flag = get_country_from_phone(phone_num)
                final_flag = flag_from_api if flag_from_api else phone_flag

                otp = extract_otp(message)
                platform, p_emoji = detect_platform(service)
                if platform == "SMS":
                    platform, p_emoji = detect_platform(message)

                sms_id = f"elite_{phone_num}_{service}_{otp}_{time_str}"

                all_sms.append({
                    "id": sms_id,
                    "phone": phone_num,
                    "phone_masked": mask_phone_number(phone_num),
                    "sender": service,
                    "message": message,
                    "otp": otp,
                    "platform": platform,
                    "platform_emoji": p_emoji,
                    "country_code": phone_cc,
                    "flag": final_flag,
                    "timestamp": time_str,
                    "revenue": "$0.00",
                    "range_name": item.get("panel", "Elite-SMS"),
                    "source": "Elite-SMS",
                })
        except Exception as e:
            logger.error(f"Error fetching Elite-SMS data: {e}")

        return all_sms

    def get_new_sms(self, limit: int = 50) -> list:
        """Ambil hanya SMS baru yang belum pernah dikirim."""
        all_sms = self.get_all_sms(limit=limit)
        new_sms = []
        for sms in all_sms:
            if sms["id"] not in self.seen_ids:
                self.seen_ids.add(sms["id"])
                new_sms.append(sms)

        if new_sms:
            logger.info(f"Elite-SMS: Found {len(new_sms)} new SMS")
        return new_sms

    def mark_initial_as_seen(self) -> int:
        """Tandai semua SMS yang sudah ada saat startup agar tidak membanjiri grup."""
        all_sms = self.get_all_sms(limit=50)
        for sms in all_sms:
            self.seen_ids.add(sms["id"])
        logger.info(f"Elite-SMS: Marked {len(all_sms)} initial SMS as seen")
        return len(all_sms)
