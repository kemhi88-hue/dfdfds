import asyncio
import sys
import requests
import base64
import time
import random
import re
from playwright.async_api import async_playwright
# Sửa lỗi import tại đây
from playwright_stealth import stealth_async 

# --- 1. HÀM LẤY OTP TỪ MAIL.TM ---
def create_mail():
    try:
        domain_list = requests.get("https://api.mail.tm/domains").json()['hydra:member']
        domain = domain_list[0]['domain']
        email = f"vsp_{int(time.time())}{random.randint(10,99)}@{domain}"
        password = "Password123!"
        requests.post("https://api.mail.tm/accounts", json={"address": email, "password": password})
        token = requests.post("https://api.mail.tm/token", json={"address": email, "password": password}).json()['token']
        return email, token
    except: return None, None

def get_otp(token):
    headers = {"Authorization": f"Bearer {token}"}
    for _ in range(12): 
        time.sleep(5)
        try:
            msgs = requests.get("https://api.mail.tm/messages", headers=headers).json()['hydra:member']
            if msgs:
                msg_id = msgs[0]['@id']
                content = requests.get(f"https://api.mail.tm{msg_id}", headers=headers).json()
                body = content.get('text', '') or content.get('intro', '')
                otp = re.findall(r'\b\d{6}\b', body)
                if otp: return otp[0]
        except: pass
    return None

# --- 2. GIẢI CAPTCHA TIKTOK ---
def solve_tiktok_captcha(image_path):
    try:
        # Lấy host API mới nhất
        host = requests.get("https://raw.githubusercontent.com/dacohacotool/host_kk/refs/heads/main/url_serverkey.txt").text.strip()
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        
        res = requests.post(f"{host}/tiktok/puzzel", json={"base64_image": img_b64}, timeout=15).json()
        if res.get("success"): return res.get("result")
    except: pass
    return None

# --- 3. LUỒNG TỰ ĐỘNG ---
async def main():
    ref = sys.argv[1] if len(sys.argv) > 1 else "vsagwtjq63"
    email, mail_token = create_mail()
    if not email: return print("❌ Lỗi tạo Mail")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(**p.devices['iPhone 12'])
        page = await context.new_page()
        
        # SỬA LỖI TẠI ĐÂY: Dùng stealth_async thay vì stealth
        await stealth_async(page)
        
        try:
            print(f"🚀 Bắt đầu: {email} | Ref: {ref}")
            await page.goto(f"https://www.vsphone.com/invite/{ref}")
            await asyncio.sleep(3)

            # Điền Email & Click lấy mã
            await page.locator('input[type="text"]').first.fill(email)
            await page.get_by_text("Get code").click()
            await asyncio.sleep(4)

            # Xử lý Captcha trượt
            captcha_img = page.locator(".captcha-main-img").first
            if await captcha_img.is_visible():
                await captcha_img.screenshot(path="cap.png")
                dist = solve_tiktok_captcha("cap.png")
                
                if dist:
                    print(f"🎯 Khoảng cách: {dist}px")
                    slider = page.locator(".van-slider__button, .page-slide-btn").first
                    box = await slider.bounding_box()
                    
                    # Kéo chuột giả lập người thật
                    sx, sy = box['x'] + box['width']/2, box['y'] + box['height']/2
                    await page.mouse.move(sx, sy)
                    await page.mouse.down()
                    # Kéo mượt với 30 bước di chuyển
                    await page.mouse.move(sx + dist, sy, steps=30)
                    await asyncio.sleep(0.5)
                    await page.mouse.up()
            
            # Đợi mã OTP
            otp = get_otp(mail_token)
            if otp:
                print(f"📩 OTP: {otp}")
                inputs = page.locator('input')
                await inputs.nth(1).fill(otp)
                await inputs.nth(2).fill("Aa123456@")
                await page.locator('button:has-text("Register")').click()
                await asyncio.sleep(5)
                print("✅ ĐĂNG KÝ THÀNH CÔNG!")
            else:
                print("❌ Không lấy được OTP")

        except Exception as e: print(f"❌ Lỗi: {e}")
        finally:
            await page.screenshot(path="ketqua.png")
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
