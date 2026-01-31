import asyncio
import sys
import re
import requests
import time
import cv2
import numpy as np
import os
import random
from playwright.async_api import async_playwright

# --- HÀM EMAIL ---
def create_temp_email():
    try:
        domain_res = requests.get("https://api.mail.tm/domains").json()
        domain = domain_res['hydra:member'][0]['domain']
        user = f"vsp_{int(time.time())}_{random.randint(100, 999)}"
        email = f"{user}@{domain}"
        requests.post("https://api.mail.tm/accounts", json={"address": email, "password": "Password123"})
        token_res = requests.post("https://api.mail.tm/token", json={"address": email, "password": "Password123"}).json()
        return email, token_res['token']
    except: return None, None

def get_otp_from_mail_tm(token):
    headers = {"Authorization": f"Bearer {token}"}
    for _ in range(15):
        time.sleep(5)
        try:
            msgs = requests.get("https://api.mail.tm/messages", headers=headers).json()
            if msgs['hydra:member']:
                msg_id = msgs['hydra:member'][0]['@id']
                content = requests.get(f"https://api.mail.tm{msg_id}", headers=headers).json()
                body = content.get('text', '') or content.get('intro', '')
                otp = re.findall(r'\b\d{6}\b', body)
                if otp: return otp[0]
        except: pass
    return None

# --- AI & MÔ PHỎNG HÀNH VI ---
def generate_trail(distance):
    trail = []
    current = 0
    mid = distance * 4 / 5
    t = 0.2
    v = 0
    while current < distance:
        a = 2 if current < mid else -3
        v0 = v
        v = v0 + a * t
        move = v0 * t + 0.5 * a * (t ** 2)
        current += move
        trail.append((round(min(current, distance)), random.randint(-2, 2)))
    trail.append((distance, 0))
    return trail

async def get_puzzle_distance(page):
    try:
        await page.wait_for_selector(".captcha-main-img, .van-image__img", timeout=10000)
        bg_path, slice_path = "bg.png", "slice.png"
        
        await page.locator(".captcha-main-img, .van-image__img").first.screenshot(path=bg_path)
        await page.locator(".captcha-slice-img, .page-slide-img").first.screenshot(path=slice_path)
        
        img_rgb = cv2.imread(bg_path)
        template = cv2.imread(slice_path, 0)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        _, _, _, max_loc = cv2.minMaxLoc(res)
        return max_loc[0]
    except: return 150

# --- LUỒNG CHÍNH ---
async def main():
    # Nhận tham số từ GitHub Action 
    email_arg = sys.argv[1] if len(sys.argv) > 1 else None
    password_arg = sys.argv[2] if len(sys.argv) > 2 else "Pass123456@"
    ref_code = sys.argv[3] if len(sys.argv) > 3 else "vsagwtjq63"

    if not email_arg or email_arg == "null":
        email, mail_token = create_temp_email()
    else:
        email, mail_token = email_arg, None

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(**p.devices['iPhone 13'], viewport={'width': 375, 'height': 812})
        page = await context.new_page()
        
        try:
            print(f"--- Đăng ký Ref: {ref_code} cho {email} ---")
            await page.goto(f"https://www.vsphone.com/invite/{ref_code}", timeout=60000)
            await asyncio.sleep(3)

            inputs = page.locator('input')
            await inputs.nth(0).fill(email)
            await page.get_by_text("Get code").click()
            await asyncio.sleep(2)
            
            # Giải Captcha bằng AI
            distance = await get_puzzle_distance(page)
            slider = page.locator(".van-slider__button, .page-slide-btn").first
            box = await slider.bounding_box()
            
            # Kéo với Trail mô phỏng người
            sx, sy = box['x'] + box['width']/2, box['y'] + box['height']/2
            await page.mouse.move(sx, sy)
            await page.mouse.down()
            for dx, dy in generate_trail(distance):
                await page.mouse.move(sx + dx, sy + dy, steps=2)
                await asyncio.sleep(0.01)
            await page.mouse.up()
            
            # Nhập OTP và Pass
            otp = get_otp_from_mail_tm(mail_token) if mail_token else "123456"
            if otp:
                await inputs.nth(1).fill(otp)
                await inputs.nth(2).fill(password_arg)
                await page.locator('button:has-text("Register")').click()
                await asyncio.sleep(5)
                print("--- Đăng ký hoàn tất! ---")
            
        except Exception as e: print(f"Lỗi: {e}")
        finally:
            await page.screenshot(path="ketqua.png")
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
