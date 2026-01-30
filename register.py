import asyncio
import sys
import re
import requests
import time
import os
import ddddocr
from playwright.async_api import async_playwright

# --- HÀM EMAIL ---
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

# --- AI GIẢI CAPTCHA (ddddocr) ---
async def get_distance_with_ai(page):
    try:
        # Chờ ảnh captcha xuất hiện
        await page.wait_for_selector(".captcha-main-img", timeout=15000)
        bg_path, slice_path = "bg.png", "slice.png"
        
        # Chụp ảnh thực tế trên màn hình
        await page.locator(".captcha-main-img").first.screenshot(path=bg_path)
        await page.locator(".captcha-slice-img").first.screenshot(path=slice_path)

        # Khởi tạo mô hình AI
        det = ddddocr.DdddOcr(det=False, show_ad=False)
        with open(slice_path, 'rb') as f: target_bytes = f.read()
        with open(bg_path, 'rb') as f: background_bytes = f.read()
            
        # AI tính toán tọa độ khớp
        res = det.slide_match(target_bytes, background_bytes, simple_target=True)
        distance = res['target'][0]
        print(f"--- AI nhận diện khoảng cách: {distance}px ---")
        return distance
    except Exception as e:
        print(f"AI Error: {e}")
        return 180

# --- LUỒNG CHÍNH ---
async def main():
    ref_code = sys.argv[1] if len(sys.argv) > 1 else "vsagwtjq63"
    email, mail_token = create_temp_email()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        iphone = p.devices['iPhone 13']
        # Ép Viewport về 1280x720 để AI tính toán pixel chuẩn xác 1:1
        context = await browser.new_context(
            **{k: v for k, v in iphone.items() if k != 'viewport'},
            viewport={'width': 1280, 'height': 720}
        )
        
        page = await context.new_page()
        
        try:
            print(f"--- Đang truy cập mã mời: {ref_code} ---")
            await page.goto(f"https://www.vsphone.com/invite/{ref_code}", timeout=60000)
            await asyncio.sleep(5)

            # Điền Email
            inputs = page.locator('input')
            await inputs.nth(0).fill(email)
            
            # Click lấy mã để hiện Captcha
            await page.get_by_text("Get code").click()
            await asyncio.sleep(4)
            
            # Giải Captcha bằng AI
            distance = await get_distance_with_ai(page)
            
            slider = page.locator(".van-slider__button, .page-slide-btn").first
            if await slider.count() > 0:
                box = await slider.bounding_box()
                start_x = box['x'] + box['width'] / 2
                start_y = box['y'] + box['height'] / 2
                
                await page.mouse.move(start_x, start_y)
                await page.mouse.down()
                # Kéo với steps=35 để giả lập tốc độ người dùng thật
                await page.mouse.move(start_x + distance, start_y, steps=35)
                await asyncio.sleep(0.5)
                await page.mouse.up()
                print("--- AI đã thực hiện kéo mảnh ghép thành công ---")
                
            # Đợi và nhận OTP
            otp = get_otp_from_mail_tm(mail_token)
            if otp:
                print(f"--- Đã nhận OTP: {otp} ---")
                await inputs.nth(1).fill(otp)
                await inputs.nth(2).fill("Pass123456@")
                await page.locator('button:has-text("Register")').click()
                print("--- Hoàn tất quá trình đăng ký ---")
                await asyncio.sleep(5)
            else:
                print("--- Lỗi: Không nhận được OTP từ Mail.tm ---")
            
        except Exception as e:
            print(f"Lỗi thực thi: {e}")
        finally:
            # Lưu ảnh kết quả cuối cùng để kiểm tra lỗi
            await page.screenshot(path="ketqua.png")
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
