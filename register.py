import asyncio
import sys
import re
import requests
import time
import base64
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

# --- HÀM LẤY HOST API TỪ GITHUB (Theo hướng dẫn trang web) ---
def get_api_host():
    try:
        res = requests.get("https://raw.githubusercontent.com/dacohacotool/host_kk/refs/heads/main/url_serverkey.txt")
        if res.status_code == 200:
            return res.text.strip()
    except:
        return None

# --- HÀM GIẢI CAPTCHA QUA API ---
def solve_puzzle_via_api(image_path):
    host = get_api_host()
    if not host:
        return None
    
    api_url = f"{host}/tiktok/puzzel"
    
    with open(image_path, "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode('utf-8')
    
    payload = {"base64_image": img_base64}
    try:
        response = requests.post(api_url, json=payload, timeout=10)
        result = response.json()
        if result.get("success"):
            return result.get("result") # Trả về số px cần kéo
    except Exception as e:
        print(f"Lỗi API: {e}")
    return None

# --- HÀM EMAIL ---
def create_temp_email():
    try:
        user = f"vsp_{int(time.time())}"
        domain = "pawnwell.com" # Có thể thay bằng api mail.tm nếu cần
        email = f"{user}@{domain}"
        # Giả lập tạo tài khoản (Mail.tm API)
        return email, "dummy_token"
    except: return None, None

async def main():
    ref_code = sys.argv[1] if len(sys.argv) > 1 else "vsagwtjq63"
    email, token = create_temp_email()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(**p.devices['iPhone 13'])
        page = await context.new_page()
        await stealth_async(page)
        
        try:
            print(f"--- Đang truy cập mã mời: {ref_code} ---")
            await page.goto(f"https://www.vsphone.com/invite/{ref_code}")
            await asyncio.sleep(2)

            # Nhập Email
            await page.locator('input').nth(0).fill(email)
            await page.get_by_text("Get code").click()
            await asyncio.sleep(3)
            
            # Chụp ảnh Captcha (Chỉ cần ảnh nền chính)
            captcha_img = page.locator(".captcha-main-img").first
            await captcha_img.screenshot(path="captcha.png")
            
            # Gửi lên API để lấy khoảng cách
            distance = solve_puzzle_via_api("captcha.png")
            
            if distance:
                print(f"--- API trả về khoảng cách: {distance}px ---")
                slider = page.locator(".van-slider__button, .page-slide-btn").first
                box = await slider.bounding_box()
                
                # Kéo slider
                await page.mouse.move(box['x'] + box['width']/2, box['y'] + box['height']/2)
                await page.mouse.down()
                # Thường cần nhân thêm tỷ lệ scale nếu ảnh chụp khác kích thước hiển thị
                # Nếu kéo lệch, hãy thử: distance * (box_width_hien_thi / box_width_anh_chup)
                await page.mouse.move(box['x'] + distance, box['y'] + box['height']/2, steps=20)
                await page.mouse.up()
                print("--- Đã giải xong Captcha ---")
            
            # Tiếp tục các bước nhập OTP...
            
        except Exception as e:
            print(f"Lỗi: {e}")
        finally:
            await page.screenshot(path="ketqua.png")
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
