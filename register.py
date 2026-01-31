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
        user = f"vsp_{int(time.time())}"
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

# --- AI XỬ LÝ CAPTCHA: TÌM VỊ TRÍ LỖ TRỐNG ---
async def get_puzzle_distance(page):
    try:
        await page.wait_for_selector(".captcha-main-img, .van-image__img", timeout=10000)
        bg_path, slice_path = "bg.png", "slice.png"
        
        await page.locator(".captcha-main-img, .van-image__img").first.screenshot(path=bg_path)
        await page.locator(".captcha-slice-img, .page-slide-img").first.screenshot(path=slice_path)
        
        img_rgb = cv2.imread(bg_path)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(slice_path, 0)
        
        # Tìm vị trí lỗ trống khít nhất
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        _, _, _, max_loc = cv2.minMaxLoc(res)
        
        return max_loc[0] # Trả về tọa độ X cần lấp đầy
    except Exception as e:
        print(f"AI Error: {e}")
        return 160

# --- LUỒNG CHÍNH ---
async def main():
    # Sửa lỗi nhận tham số từ Workflow
    email_in = sys.argv[1] if len(sys.argv) > 1 else "null"
    password_in = sys.argv[2] if len(sys.argv) > 2 else "Pass123456@"
    ref_code = sys.argv[3] if len(sys.argv) > 3 else "vsagwtjq63"

    # Xử lý Email "null"
    if email_in == "null":
        email, mail_token = create_temp_email()
    else:
        email, mail_token = email_in, None

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # Sửa lỗi multiple values for viewport
        iphone = p.devices['iPhone 13']
        context_params = {k: v for k, v in iphone.items() if k != 'viewport'}
        context = await browser.new_context(**context_params, viewport={'width': 375, 'height': 812})
        page = await context.new_page()
        
        try:
            print(f"--- Đăng ký tài khoản: {email} với mã {ref_code} ---")
            await page.goto(f"https://www.vsphone.com/invite/{ref_code}", timeout=60000)
            await asyncio.sleep(5)

            inputs = page.locator('input')
            await inputs.nth(0).fill(email)
            await page.get_by_text("Get code").click()
            
            # 1. Đợi thanh trượt (nút khoanh đỏ) xuất hiện
            slider = page.locator(".van-slider__button, .page-slide-btn").first
            await slider.wait_for(state="visible", timeout=20000)
            
            # 2. AI tính toán khoảng cách
            distance = await get_puzzle_distance(page)
            box = await slider.bounding_box()
            
            if box:
                start_x = box['x'] + box['width'] / 2
                start_y = box['y'] + box['height'] / 2
                
                await page.mouse.move(start_x, start_y)
                await page.mouse.down()
                
                # 3. Kéo mượt mà để lấp đầy nơi trống
                steps = 35
                for i in range(steps):
                    fraction = (i + 1) / steps
                    current_x = start_x + (distance * fraction)
                    # Thêm độ nhiễu Y để mô phỏng người thật
                    await page.mouse.move(current_x, start_y + random.uniform(-1, 1))
                    await asyncio.sleep(0.01)
                
                await asyncio.sleep(0.5) # Dừng lại để hệ thống khớp ảnh
                await page.mouse.up()
                print(f"--- Đã kéo {distance}px để lấp đầy captcha ---")
                await asyncio.sleep(2)
            
            # 4. Nhập OTP và hoàn tất
            otp = get_otp_from_mail_tm(mail_token) if mail_token else None
            if otp:
                await inputs.nth(1).fill(otp)
                await inputs.nth(2).fill(password_in)
                await page.locator('button:has-text("Register")').click()
                await asyncio.sleep(5)
                print("--- Đăng ký thành công! ---")
            
        except Exception as e:
            print(f"Main Error: {e}")
        finally:
            await page.screenshot(path="ketqua.png")
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
