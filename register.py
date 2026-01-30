import asyncio
import sys
import re
import requests
import time
import base64
from playwright.async_api import async_playwright
from playwright_stealth import stealth # Đảm bảo import đúng

# --- API GIẢI CAPTCHA ---
def solve_tiktok_puzzle(image_path):
    try:
        host_res = requests.get("https://raw.githubusercontent.com/dacohacotool/host_kk/refs/heads/main/url_serverkey.txt")
        api_url = f"{host_res.text.strip()}/tiktok/puzzel"
        
        with open(image_path, "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        response = requests.post(api_url, json={"base64_image": img_base64}, timeout=15)
        res_data = response.json()
        if res_data.get("success"):
            return res_data.get("result")
    except: pass
    return None

async def main():
    ref_code = sys.argv[1] if len(sys.argv) > 1 else "vsagwtjq63"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Sử dụng trình duyệt giả lập Mobile để dễ trượt captcha hơn
        context = await browser.new_context(**p.devices['iPhone 12'])
        page = await context.new_page()
        
        # --- FIX LỖI TẠI ĐÂY ---
        # Gọi stealth như một function truyền page vào
        await stealth(page) 
        
        try:
            print(f"--- Đang mở trang web với Ref: {ref_code} ---")
            await page.goto(f"https://www.vsphone.com/invite/{ref_code}", wait_until="networkidle")
            
            # Giả lập thao tác người dùng: Cuộn trang một chút
            await page.mouse.wheel(0, 500)
            await asyncio.sleep(2)

            # Điền mail (Ví dụ dùng mail ngẫu nhiên để test flow)
            email = f"test_{int(time.time())}@gmail.com"
            await page.locator('input[type="text"]').first.fill(email)
            await page.get_by_text("Get code").click()
            
            # Chờ captcha xuất hiện
            await asyncio.sleep(4)
            captcha_el = page.locator(".captcha-main-img").first
            
            if await captcha_el.is_visible():
                # Chụp ảnh để gửi API
                await captcha_el.screenshot(path="captcha_debug.png")
                distance = solve_tiktok_puzzle("captcha_debug.png")
                
                if distance:
                    print(f"--- Khoảng cách tìm được: {distance}px ---")
                    slider = page.locator(".van-slider__button, .page-slide-btn").first
                    sb = await slider.bounding_box()
                    
                    # Tính toán tọa độ kéo (Dòng này cực quan trọng)
                    start_x = sb['x'] + sb['width'] / 2
                    start_y = sb['y'] + sb['height'] / 2
                    
                    # Bắt đầu kéo
                    await page.mouse.move(start_x, start_y)
                    await page.mouse.down()
                    
                    # Kéo có biến thiên vận tốc (giả lập tay người)
                    await page.mouse.move(start_x + distance, start_y, steps=30)
                    await asyncio.sleep(0.5)
                    await page.mouse.up()
                    print("--- Đã kéo xong Captcha ---")
            
            await asyncio.sleep(5)
            await page.screenshot(path="result_final.png")
            print("--- Hoàn tất flow đăng ký ---")

        except Exception as e:
            print(f"Lỗi: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
