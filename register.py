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

# --- AI XỬ LÝ CAPTCHA ---
async def get_puzzle_distance(page):
    try:
        # Đợi các ảnh captcha tải xong hoàn toàn
        await page.wait_for_selector(".captcha-main-img, .van-image__img", timeout=10000)
        
        bg_selectors = [".captcha-main-img", ".van-image__img", "img[src*='captcha']"]
        slice_selectors = [".captcha-slice-img", ".page-slide-img", "[class*='slice-img']"]
        
        bg_path = "bg.png"
        slice_path = "slice.png"

        bg_el = None
        for s in bg_selectors:
            if await page.locator(s).count() > 0:
                bg_el = page.locator(s).first
                break
        
        if not bg_el: return 180

        # Chụp ảnh chất lượng cao để OpenCV xử lý chính xác
        await bg_el.screenshot(path=bg_path)
        
        for s in slice_selectors:
            if await page.locator(s).count() > 0:
                await page.locator(s).first.screenshot(path=slice_path)
                break
        
        # Xử lý OpenCV tìm tọa độ khớp nhất
        img_rgb = cv2.imread(bg_path)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(slice_path, 0)
        
        # Sử dụng phương pháp TM_CCOEFF_NORMED để tăng độ chính xác
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        _, _, _, max_loc = cv2.minMaxLoc(res)
        
        # max_loc[0] là khoảng cách x từ cạnh trái ảnh nền đến mảnh ghép
        return max_loc[0]
    except Exception as e:
        print(f"AI Error: {e}")
        return 180

# --- LUỒNG CHÍNH ---
async def main():
    ref_code = sys.argv[1] if len(sys.argv) > 1 else "vsagwtjq63"
    email, mail_token = create_temp_email()
    
    # Tạo file kết quả trống để tránh lỗi GitHub Actions
    with open("ketqua.png", "w") as f: f.write("") 

    async with async_playwright() as p:
        # Khởi tạo trình duyệt
        browser = await p.chromium.launch(headless=True)
        
        # Cấu hình Context: Kết hợp iPhone 13 và cố định Viewport 1280x720
        context = await browser.new_context(
            **p.devices['iPhone 13'],
            viewport={'width': 1280, 'height': 720}
        )
        
        page = await context.new_page()
        
        try:
            print(f"--- Đang truy cập mã mời: {ref_code} ---")
            await page.goto(f"https://www.vsphone.com/invite/{ref_code}", timeout=60000)
            await asyncio.sleep(5)

            # Điền Email
            inputs = page.locator('input')
            if await inputs.count() > 0:
                await inputs.nth(0).fill(email)
                print(f"--- Đã điền email: {email} ---")
                
                # Click lấy mã OTP để hiện Captcha
                get_code_btn = page.get_by_text("Get code")
                await get_code_btn.click()
                await asyncio.sleep(3)
                
                # --- GIẢI CAPTCHA ---
                distance = await get_puzzle_distance(page)
                slider = page.locator(".van-slider__button, .page-slide-btn").first
                
                if await slider.count() > 0:
                    box = await slider.bounding_box()
                    start_x = box['x'] + box['width'] / 2
                    start_y = box['y'] + box['height'] / 2
                    
                    # Di chuyển chuột đến điểm bắt đầu
                    await page.mouse.move(start_x, start_y)
                    await page.mouse.down()
                    
                    # Kéo mảnh ghép với 30 bước (steps) để giả lập tay người kéo chậm
                    # Thêm một chút dao động nhẹ về trục Y để vượt qua bộ lọc bot
                    await page.mouse.move(start_x + distance, start_y + 2, steps=30)
                    await asyncio.sleep(0.5)
                    await page.mouse.up()
                    
                    print(f"--- Đã kéo mảnh ghép {distance}px thành công ---")
                    await asyncio.sleep(2)
            
            # Nhận OTP từ Email
            otp = get_otp_from_mail_tm(mail_token)
            if otp:
                print(f"--- Nhận được OTP: {otp} ---")
                await inputs.nth(1).fill(otp)
                await inputs.nth(2).fill("Pass123456@")
                
                # Nhấn đăng ký
                register_btn = page.locator('button:has-text("Register")')
                await register_btn.click()
                print("--- Đã nhấn nút Register ---")
                await asyncio.sleep(5)
            else:
                print("--- Không nhận được OTP, vui lòng kiểm tra lại dịch vụ mail ---")
            
        except Exception as e:
            print(f"Main Error: {e}")
        finally:
            # Chụp ảnh màn hình kết quả để debug
            await page.screenshot(path="ketqua.png")
            print("--- Đã chụp ảnh kết quả ketqua.png ---")
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
