import asyncio
import sys
import re
import requests
import time
import base64
from playwright.async_api import async_playwright
from playwright_stealth import stealth  # Sửa từ stealth_async thành stealth

# --- LẤY URL API GIẢI CAPTCHA ---
def get_api_url():
    try:
        host_res = requests.get("https://raw.githubusercontent.com/dacohacotool/host_kk/refs/heads/main/url_serverkey.txt")
        if host_res.status_code == 200:
            return f"{host_res.text.strip()}/tiktok/puzzel"
    except: return None

def solve_tiktok_puzzle(image_path):
    api_url = get_api_url()
    if not api_url: return None
    
    with open(image_path, "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode('utf-8')
    
    try:
        response = requests.post(api_url, json={"base64_image": img_base64}, timeout=15)
        res_data = response.json()
        if res_data.get("success"):
            return res_data.get("result")
    except: pass
    return None

# --- CHƯƠNG TRÌNH CHÍNH ---
async def main():
    ref_code = sys.argv[1] if len(sys.argv) > 1 else "vsagwtjq63"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(**p.devices['iPhone 13'])
        page = await context.new_page()
        
        # SỬA LỖI TẠI ĐÂY: Dùng stealth(page) thay cho stealth_async
        await stealth(page)
        
        try:
            print(f"--- Đăng ký Ref: {ref_code} ---")
            await page.goto(f"https://www.vsphone.com/invite/{ref_code}")
            await asyncio.sleep(3)

            # 1. Nhập Email (Dùng mail giả lập để test)
            email = f"user_{int(time.time())}@gmail.com"
            await page.locator('input[type="text"]').first.fill(email)
            
            # 2. Click lấy code để hiện Captcha
            await page.get_by_text("Get code").click()
            await asyncio.sleep(4)
            
            # 3. Chụp ảnh captcha
            captcha_el = page.locator(".captcha-main-img").first
            if await captcha_el.is_visible():
                await captcha_el.screenshot(path="captcha.png")
                
                # 4. Giải bằng API dacohacotool
                distance = solve_tiktok_puzzle("captcha.png")
                
                if distance:
                    print(f"--- Khoảng cách nhận diện: {distance}px ---")
                    slider = page.locator(".van-slider__button, .page-slide-btn").first
                    box = await slider.bounding_box()
                    
                    # Kéo slider mượt mà
                    await page.mouse.move(box['x'] + box['width']/2, box['y'] + box['height']/2)
                    await page.mouse.down()
                    # TikTok thường cần kéo distance * tỉ lệ màn hình, thử nghiệm distance chuẩn:
                    await page.mouse.move(box['x'] + distance, box['y'] + box['height']/2, steps=25)
                    await page.mouse.up()
                    print("--- Đã thực hiện giải captcha ---")
            
            await asyncio.sleep(5)
            await page.screenshot(path="ketqua.png")

        except Exception as e:
            print(f"Lỗi thực thi: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
