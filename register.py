import asyncio
import sys
import re
import requests
import time
import os
import ddddocr
from playwright.async_api import async_playwright

# --- HÀM TẠO EMAIL VÀ NHẬN OTP ---
def create_temp_email():
    try:
        domain_res = requests.get("https://api.mail.tm/domains").json()
        domain = domain_res['hydra:member'][0]['domain']
        user = f"vsp_{int(time.time())}"
        email = f"{user}@{domain}"
        requests.post("https://api.mail.tm/accounts", json={"address": email, "password": "Password123"})
        token_res = requests.post("https://api.mail.tm/token", json={"address": email, "password": "Password123"}).json()
        return email, token_res['token']
    except Exception as e:
        print(f"Lỗi tạo mail: {e}")
        return None, None

def get_otp_from_mail_tm(token):
    headers = {"Authorization": f"Bearer {token}"}
    for _ in range(12): # Thử lại trong 60 giây
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

# --- AI GIẢI CAPTCHA ---
async def solve_captcha_ai(page):
    try:
        # Chờ slider và ảnh xuất hiện
        await page.wait_for_selector(".captcha-main-img", timeout=10000)
        
        # Chụp ảnh để AI xử lý
        await page.locator(".captcha-main-img").first.screenshot(path="bg.png")
        await page.locator(".captcha-slice-img").first.screenshot(path="slice.png")

        # Khởi tạo ddddocr
        det = ddddocr.DdddOcr(det=False, show_ad=False)
        with open("slice.png", 'rb') as f: target = f.read()
        with open("bg.png", 'rb') as f: background = f.read()
            
        res = det.slide_match(target, background, simple_target=True)
        distance = res['target'][0]
        print(f"--- AI tìm thấy khoảng cách: {distance}px ---")
        return distance
    except Exception as e:
        print(f"AI giải Captcha thất bại: {e}")
        return 0

# --- CHƯƠNG TRÌNH CHÍNH ---
async def main():
    ref_code = sys.argv[1] if len(sys.argv) > 1 else "vsagwtjq63"
    email, mail_token = create_temp_email()
    
    if not email: return

    async with async_playwright() as p:
        # Chạy trình duyệt ẩn danh
        browser = await p.chromium.launch(headless=True)
        # Giả lập thiết bị di động để tránh bị chặn
        context = await browser.new_context(
            **p.devices['iPhone 13'],
            viewport={'width': 1280, 'height': 720}
        )
        page = await context.new_page()
        
        try:
            print(f"--- Đăng ký với Email: {email} | Ref: {ref_code} ---")
            await page.goto(f"https://www.vsphone.com/invite/{ref_code}")
            await asyncio.sleep(3)

            # Nhập Email
            inputs = page.locator('input')
            await inputs.nth(0).fill(email)
            
            # Click lấy mã OTP
            await page.get_by_text("Get code").click()
            await asyncio.sleep(3)
            
            # Giải Captcha
            distance = await solve_captcha_ai(page)
            if distance > 0:
                slider = page.locator(".van-slider__button, .page-slide-btn").first
                box = await slider.bounding_box()
                await page.mouse.move(box['x'] + box['width']/2, box['y'] + box['height']/2)
                await page.mouse.down()
                # Kéo trượt với giả lập tốc độ người dùng
                await page.mouse.move(box['x'] + box['width']/2 + distance, box['y'] + box['height']/2, steps=25)
                await page.mouse.up()
                print("--- Đã thực hiện kéo Captcha ---")

            # Nhận và nhập OTP
            otp = get_otp_from_mail_tm(mail_token)
            if otp:
                print(f"--- Đã lấy được mã OTP: {otp} ---")
                await inputs.nth(1).fill(otp)
                await inputs.nth(2).fill("Aa123456@") # Mật khẩu mặc định
                await page.locator('button:has-text("Register")').click()
                await asyncio.sleep(5)
                print("--- Đăng ký hoàn tất thành công ---")
            else:
                print("--- Không tìm thấy mã OTP trong hộp thư ---")

        except Exception as e:
            print(f"Lỗi trong quá trình chạy: {e}")
        finally:
            await page.screenshot(path="ketqua.png")
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
