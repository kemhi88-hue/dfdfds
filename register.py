import asyncio
import sys
import requests
import base64
import time
import random
import re
from playwright.async_api import async_playwright
# Import theo cách này để tránh lỗi module
import playwright_stealth 

# --- HÀM GIẢI CAPTCHA ---
def solve_tiktok_captcha(image_path):
    try:
        host = requests.get("https://raw.githubusercontent.com/dacohacotool/host_kk/refs/heads/main/url_serverkey.txt").text.strip()
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        res = requests.post(f"{host}/tiktok/puzzel", json={"base64_image": img_b64}, timeout=15).json()
        if res.get("success"): return res.get("result")
    except: return None

# --- LUỒNG CHÍNH ---
async def main():
    ref = sys.argv[1] if len(sys.argv) > 1 else "vsagwtjq63"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(**p.devices['iPhone 12'])
        page = await context.new_page()
        
        # --- CÁCH GỌI STEALTH CHUẨN ĐỂ KHÔNG LỖI ---
        await playwright_stealth.stealth_async(page)
        
        try:
            print(f"🚀 Khởi chạy đăng ký Ref: {ref}")
            await page.goto(f"https://www.vsphone.com/invite/{ref}")
            await asyncio.sleep(3)

            # Điền Mail & Click
            await page.locator('input[type="text"]').first.fill(f"vsp_{int(time.time())}@gmail.com")
            await page.get_by_text("Get code").click()
            await asyncio.sleep(4)

            # Chụp & Giải Captcha
            captcha_img = page.locator(".captcha-main-img").first
            if await captcha_img.is_visible():
                await captcha_img.screenshot(path="cap.png")
                dist = solve_tiktok_captcha("cap.png")
                
                if dist:
                    print(f"🎯 Tọa độ giải được: {dist}px")
                    slider = page.locator(".van-slider__button, .page-slide-btn").first
                    box = await slider.bounding_box()
                    
                    # Kéo chuột
                    sx, sy = box['x'] + box['width']/2, box['y'] + box['height']/2
                    await page.mouse.move(sx, sy)
                    await page.mouse.down()
                    await page.mouse.move(sx + dist, sy, steps=30)
                    await asyncio.sleep(0.5)
                    await page.mouse.up()
                    print("✅ Đã trượt captcha")

            await asyncio.sleep(5)
            await page.screenshot(path="ketqua.png")

        except Exception as e:
            print(f"❌ Lỗi: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
