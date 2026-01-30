import asyncio
import sys
import re
import requests
import time
import cv2
import numpy as np
import os
from playwright.async_api import async_playwright

# --- HÀM EMAIL (Giữ nguyên) ---
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

# --- AI XỬ LÝ CAPTCHA VỚI CƠ CHẾ QUÉT NHIỀU SELECTOR ---
async def get_puzzle_distance(page):
    try:
        # Danh sách các class có thể là ảnh captcha (để tránh lỗi khi web đổi giao diện)
        bg_selectors = [".captcha-main-img", ".van-image__img", "[class*='bg-img']", "img[src*='captcha']"]
        slice_selectors = [".captcha-slice-img", ".page-slide-img", "[class*='slice-img']"]
        
        bg_path = "bg.png"
        slice_path = "slice.png"

        # Tìm selector đang hoạt động
        bg_el = None
        for s in bg_selectors:
            if await page.locator(s).count() > 0:
                bg_el = page.locator(s).first
                break
        
        if not bg_el: return 180 # Fallback nếu không tìm thấy ảnh

        await bg_el.screenshot(path=bg_path)
        # Tương tự cho mảnh ghép
        for s in slice_selectors:
            if await page.locator(s).count() > 0:
                await page.locator(s).first.screenshot(path=slice_path)
                break
        
        # Xử lý OpenCV
        img_rgb = cv2.imread(bg_path)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(slice_path, 0)
        
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        _, _, _, max_loc = cv2.minMaxLoc(res)
        
        return max_loc[0]
    except Exception as e:
        print(f"AI Error: {e}")
        return 180

# --- LUỒNG CHÍNH ---
async def main():
    ref_code = sys.argv[1] if len(sys.argv) > 1 else "vsagwtjq63"
    email, mail_token = create_temp_email()
    
    # ĐẢM BẢO FILE LUÔN TỒN TẠI ĐỂ GITHUB KHÔNG BÁO LỖI
    with open("ketqua.png", "w") as f: f.write("") 

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(**p.devices['iPhone 13'])
        page = await context.new_page()
        
        try:
            print(f"--- Đang truy cập mã mời: {ref_code} ---")
            await page.goto(f"https://www.vsphone.com/invite/{ref_code}", timeout=60000)
            await asyncio.sleep(5)
            await page.screenshot(path="ketqua.png") # Chụp ảnh lần 1

            # Điền Form
            inputs = page.locator('input')
            await inputs.nth(0).fill(email)
            await page.get_by_text("Get code").click()
            await asyncio.sleep(3)
            
            # Giải Captcha
            distance = await get_puzzle_distance(page)
            slider = page.locator(".van-slider__button, .page-slide-btn").first
            if await slider.count() > 0:
                box = await slider.bounding_box()
                await page.mouse.move(box['x'] + box['width']/2, box['y'] + box['height']/2)
                await page.mouse.down()
                await page.mouse.move(box['x'] + distance, box['y'] + box['height']/2, steps=15)
                await page.mouse.up()
                print(f"--- Đã kéo mảnh ghép {distance}px ---")
            
            # Nhận OTP
            otp = get_otp_from_mail_tm(mail_token)
            if otp:
                await inputs.nth(1).fill(otp)
                await inputs.nth(2).fill("Pass123456@")
                await page.click('button:has-text("Register")')
                await asyncio.sleep(5)
            
        except Exception as e:
            print(f"Main Error: {e}")
        finally:
            await page.screenshot(path="ketqua.png") # Chụp ảnh cuối cùng
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
