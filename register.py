import asyncio
import sys
import requests
import base64
import time
from playwright.async_api import async_playwright
import playwright_stealth # Import module thay vì import hàm lẻ

# --- HÀM GIẢI CAPTCHA ---
def solve_tiktok_captcha(image_path):
    try:
        host_res = requests.get("https://raw.githubusercontent.com/dacohacotool/host_kk/refs/heads/main/url_serverkey.txt")
        host = host_res.text.strip()
        
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
            
        res = requests.post(f"{host}/tiktok/puzzel", json={"base64_image": img_b64}, timeout=15).json()
        if res.get("success"): 
            return res.get("result")
    except Exception as e:
        print(f"⚠️ Lỗi giải mã Captcha: {e}")
        return None

# --- LUỒNG CHÍNH ---
async def main():
    ref = sys.argv[1] if len(sys.argv) > 1 else "vsagwtjq63"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(**p.devices['iPhone 12'])
        page = await context.new_page()
        
        # SỬA LỖI TẠI ĐÂY: Sử dụng hàm stealth() thay vì stealth_async()
        # Thư viện playwright-stealth bản mới nhất dùng chung hàm này cho async page
        await playwright_stealth.stealth(page)
        
        try:
            print(f"🚀 Đang khởi chạy đăng ký với mã Ref: {ref}")
            await page.goto(f"https://www.vsphone.com/invite/{ref}")
            await asyncio.sleep(5)

            email_random = f"vsp_{int(time.time())}@gmail.com"
            await page.locator('input[type="text"]').first.fill(email_random)
            print(f"📩 Đã nhập email: {email_random}")
            
            await page.get_by_text("Get code").click()
            await asyncio.sleep(4)

            captcha_img = page.locator(".captcha-main-img").first
            if await captcha_img.is_visible():
                print("🧩 Phát hiện Captcha, đang xử lý...")
                await captcha_img.screenshot(path="cap.png")
                dist = solve_tiktok_captcha("cap.png")
                
                if dist:
                    print(f"🎯 Khoảng cách trượt: {dist}px")
                    slider = page.locator(".van-slider__button, .page-slide-btn").first
                    box = await slider.bounding_box()
                    
                    if box:
                        sx, sy = box['x'] + box['width']/2, box['y'] + box['height']/2
                        await page.mouse.move(sx, sy)
                        await page.mouse.down()
                        await page.mouse.move(sx + dist, sy, steps=35)
                        await asyncio.sleep(0.5)
                        await page.mouse.up()
                        print("✅ Đã thực hiện trượt Captcha")

            await asyncio.sleep(5)
            await page.screenshot(path="ketqua.png")
            print("📸 Đã lưu ảnh kết quả (ketqua.png)")

        except Exception as e:
            print(f"❌ Lỗi thực thi: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
