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

# --- HÀM EMAIL TỰ ĐỘNG ---
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

# --- AI XỬ LÝ ẢNH ---
async def get_puzzle_distance(page):
    try:
        # Chờ ảnh captcha hiện ra hoàn toàn
        await page.wait_for_selector(".captcha-main-img, .van-image__img", timeout=15000)
        bg_path, slice_path = "bg.png", "slice.png"
        
        # Chụp ảnh nền và mảnh ghép
        await page.locator(".captcha-main-img, .van-image__img").first.screenshot(path=bg_path)
        await page.locator(".captcha-slice-img, .page-slide-img").first.screenshot(path=slice_path)
        
        img_rgb = cv2.imread(bg_path)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(slice_path, 0)
        
        # Dùng OpenCV tìm tọa độ khớp nhất
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        _, _, _, max_loc = cv2.minMaxLoc(res)
        return max_loc[0]
    except Exception as e:
        print(f"AI Error: {e}")
        return 155 # Giá trị mặc định nếu lỗi

# --- MÔ PHỎNG NGƯỜI THẬT ---
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

# --- LUỒNG CHÍNH ---
async def main():
    email_in = sys.argv[1] if len(sys.argv) > 1 else "null"
    password_in = sys.argv[2] if len(sys.argv) > 2 else "Pass123456@"
    ref_code = sys.argv[3] if len(sys.argv) > 3 else "vsagwtjq63"

    email, mail_token = (email_in, None) if email_in != "null" else create_temp_email()

    async with async_playwright() as p:
        # Giả lập thiết bị Mobile để giao diện ổn định
        browser = await p.chromium.launch(headless=True)
        iphone = p.devices['iPhone 13']
        context = await browser.new_context(
            **{k: v for k, v in iphone.items() if k != 'viewport'},
            viewport={'width': 375, 'height': 812}
        )
        page = await context.new_page()
        
        try:
            print(f"--- Truy cập link ref: {ref_code} ---")
            await page.goto(f"https://www.vsphone.com/invite/{ref_code}", timeout=60000)
            await asyncio.sleep(5)

            # Điền Email
            inputs = page.locator('input')
            await inputs.nth(0).wait_for(state="visible")
            await inputs.nth(0).fill(email)
            
            # Nhấn nút lấy mã để hiện Captcha
            print("--- Đang nhấn Get code... ---")
            await page.get_by_text("Get code").click()
            
            # ĐỢI VÀ GIẢI CAPTCHA
            # Tìm selector chính xác của nút trượt
            slider_selector = ".van-slider__button, .page-slide-btn"
            slider = page.locator(slider_selector).first
            
            # Chờ slider xuất hiện (tăng thời gian chờ lên 20s)
            await slider.wait_for(state="visible", timeout=20000)
            
            distance = await get_puzzle_distance(page)
            box = await slider.bounding_box()
            
            if box:
                start_x = box['x'] + box['width'] / 2
                start_y = box['y'] + box['height'] / 2
                
                await page.mouse.move(start_x, start_y)
                await page.mouse.down()
                
                # Sử dụng Trail để mô phỏng kéo tay
                trail = generate_trail(distance)
                for dx, dy in trail:
                    await page.mouse.move(start_x + dx, start_y + dy, steps=2)
                    await asyncio.sleep(0.01)
                
                await page.mouse.up()
                print(f"--- Đã giải captcha (khớp {distance}px) ---")
                await asyncio.sleep(2)
            
            # Nhận và điền OTP
            otp = get_otp_from_mail_tm(mail_token) if mail_token else "123456"
            if otp:
                await inputs.nth(1).fill(otp)
                await inputs.nth(2).fill(password_in)
                await page.locator('button:has-text("Register")').click()
                await asyncio.sleep(5)
                print("--- Đăng ký hoàn tất! ---")
            
        except Exception as e:
            print(f"Lỗi thực thi: {e}")
        finally:
            await page.screenshot(path="ketqua.png")
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
