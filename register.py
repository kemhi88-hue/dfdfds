import asyncio
import sys
import time
import base64
import requests

from playwright.async_api import async_playwright
from playwright_stealth.stealth import stealth   # ✅ CHUẨN cho 1.0.6


# ================== SOLVE TIKTOK PUZZLE (KKTOOL) ==================
def solve_tiktok_captcha(image_path: str):
    try:
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()

        res = requests.post(
            "https://kktool.dacohacotool.workers.dev/tiktok/puzzel",
            json={"base64_image": img_b64},
            timeout=20
        ).json()

        if res.get("success"):
            return int(res.get("result"))
    except Exception as e:
        print("⚠️ Solve captcha error:", e)
