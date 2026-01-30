import asyncio
import sys
import requests
import base64
import time
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async  # Import trực tiếp hàm async

# --- HÀM GIẢI CAPTCHA ---
def solve_tiktok_captcha(image_path):
    try:
        # Lấy URL server giải captcha từ host uy tín
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
    # Nhận mã Ref từ tham số dòng lệnh hoặc mặc định
    ref = sys.argv[1] if len(sys.argv) > 1 else "vsagwtjq63"
    
    async with async_playwright() as p:
        # Chạy ở chế độ không giao diện (headless) trên GitHub Actions
        browser = await p.chromium.launch(headless=True)
        # Giả lập thiết bị iPhone 12 để tránh bị soi
        context = await browser.new_context(**p.devices['iPhone 12'])
        page = await context.new_page()
        
        # Áp dụng Stealth để chống phát hiện bot
        await stealth_async(page)
        
        try:
            print(f"🚀 Đang khởi chạy đăng ký với mã Ref: {ref}")
            await page.goto(f"https://www.vsphone.com/invite/{ref}")
            await asyncio.sleep(5)

            # Điền Mail ngẫu nhiên theo định dạng vsp_timestamp@gmail.com
            email_random = f"vsp_{int(time.time())}@gmail.com"
            await page.locator('input[type="text"]').first.fill(email_random)
            print(f"📩 Đã nhập email: {email_random}")
            
            await page.get_by_text("Get code").click()
            await asyncio.sleep(4)

            # Kiểm tra và xử lý Captcha trượt
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
                        # Di chuyển chuột mượt mô phỏng người thật
                        await page.mouse.move(sx + dist, sy, steps=35)
                        await asyncio.sleep(0.5)
                        await page.mouse.up()
                        print("✅ Đã thực hiện trượt Captcha")
                else:
                    print("❌ Không lấy được tọa độ giải Captcha")

            # Chụp ảnh kết quả cuối cùng để debug
            await asyncio.sleep(5)
            await page.screenshot(path="ketqua.png")
            print("📸 Đã lưu ảnh kết quả (ketqua.png)")

        except Exception as e:
            print(f"❌ Lỗi thực thi: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
