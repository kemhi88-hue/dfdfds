import asyncio
import sys
import requests
import base64
import time
from playwright.async_api import async_playwright
import playwright_stealth

# --- HÀM GIẢI CAPTCHA ---
def solve_tiktok_captcha(image_path):
    try:
        host_res = requests.get("https://raw.githubusercontent.com/dacohacotool/host_kk/refs/heads/main/url_serverkey.txt")
        host = host_res.text.strip()
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        res = requests.post(f"{host}/tiktok/puzzel", json={"base64_image": img_b64}, timeout=15).json()
        if res.get("success"): return res.get("result")
    except: return None

# --- LUỒNG CHÍNH ---
async def main():
    # Nhận mã Ref từ tham số thứ 3 (theo log của bạn: fg fgfg vsagwtjq63)
    ref = sys.argv[3] if len(sys.argv) > 3 else "vsagwtjq63"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Sử dụng User Agent của iPhone để giảm tỉ lệ bị chặn
        context = await browser.new_context(**p.devices['iPhone 12'])
        page = await context.new_page()
        
        # Kích hoạt chế độ ẩn danh
        await playwright_stealth.stealth(page)
        
        try:
            print(f"🚀 Truy cập link Ref: {ref}")
            await page.goto(f"https://www.vsphone.com/invite/{ref}", wait_until="networkidle")
            
            # Sửa lỗi: Dùng selector tổng quát hơn cho ô nhập email
            # Thử tìm input type="text" đầu tiên nếu không thấy placeholder "email"
            email_input = page.locator('input[type="text"], input[placeholder*="mail"], input[placeholder*="Email"]').first
            
            print("⏳ Đang chờ ô nhập email xuất hiện...")
            await email_input.wait_for(state="visible", timeout=15000)
            
            email_val = f"vsp_{int(time.time())}@gmail.com"
            await email_input.fill(email_val)
            print(f"✅ Đã điền Email: {email_val}")

            # Click nút lấy mã
            await page.get_by_text("Get code").click()
            await asyncio.sleep(5)

            # Xử lý Captcha trượt
            captcha_img = page.locator(".captcha-main-img, #captcha-verify-image").first
            if await captcha_img.is_visible():
                print("🧩 Phát hiện Captcha...")
                await captcha_img.screenshot(path="cap.png")
                dist = solve_tiktok_captcha("cap.png")
                
                if dist:
                    slider = page.locator(".van-slider__button, .page-slide-btn, .secsdk-captcha-drag-icon").first
                    box = await slider.bounding_box()
                    if box:
                        sx, sy = box['x'] + box['width']/2, box['y'] + box['height']/2
                        await page.mouse.move(sx, sy)
                        await page.mouse.down()
                        await page.mouse.move(sx + dist, sy, steps=30)
                        await page.mouse.up()
                        print("🎯 Đã trượt captcha")

            await asyncio.sleep(5)
            await page.screenshot(path="ketqua.png")

        except Exception as e:
            print(f"❌ Lỗi: {e}")
            await page.screenshot(path="error_debug.png")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
