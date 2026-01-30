import asyncio
import sys
import requests
import base64
import time
import random
from playwright.async_api import async_playwright
from playwright_stealth import stealth

# --- 1. LẤY URL API MỚI NHẤT ---
def get_api_url():
    try:
        host = requests.get("https://raw.githubusercontent.com/dacohacotool/host_kk/refs/heads/main/url_serverkey.txt", timeout=5).text.strip()
        return f"{host}/tiktok/puzzel"
    except Exception as e:
        print(f"❌ Lỗi lấy host API: {e}")
        return None

# --- 2. GIẢI CAPTCHA QUA API TIKTOK PUZZLE ---
def solve_captcha(image_path):
    api_url = get_api_url()
    if not api_url: return None
    
    with open(image_path, "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode('utf-8')
    
    try:
        response = requests.post(api_url, json={"base64_image": img_base64}, timeout=15)
        data = response.json()
        if data.get("success"):
            return data.get("result") # Trả về số pixel cần kéo
    except Exception as e:
        print(f"❌ Lỗi gọi API giải captcha: {e}")
    return None

# --- 3. HÀM KÉO CHUỘT KIỂU NGƯỜI THẬT (QUAN TRỌNG) ---
async def human_slide(page, slider_element, distance):
    box = await slider_element.bounding_box()
    start_x = box['x'] + box['width'] / 2
    start_y = box['y'] + box['height'] / 2
    
    await page.mouse.move(start_x, start_y)
    await page.mouse.down()
    
    # Chia nhỏ quãng đường để giả lập tay người rung và vận tốc thay đổi
    steps = 25
    current_x = start_x
    for i in range(steps):
        # Thuật toán: Nhanh lúc đầu, chậm dần khi về đích + rung nhẹ trục Y
        fraction = i / steps
        target_x = start_x + (distance * fraction)
        # Tạo độ rung ngẫu nhiên
        jitter_y = start_y + random.uniform(-2, 2)
        await page.mouse.move(target_x, jitter_y)
        await asyncio.sleep(random.uniform(0.01, 0.02))
        
    await asyncio.sleep(0.3) # Dừng lại một chút ở đích trước khi thả
    await page.mouse.up()

# --- 4. LUỒNG CHÍNH ---
async def main():
    ref_code = sys.argv[1] if len(sys.argv) > 1 else "vsagwtjq63"
    
    async with async_playwright() as p:
        # Chạy ẩn danh (headless=True)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(**p.devices['iPhone 12'])
        page = await context.new_page()
        
        # FIX LỖI: Gọi stealth đúng cách
        await stealth(page)
        
        try:
            print(f"🚀 Đang mở trang web với Ref: {ref_code}")
            await page.goto(f"https://www.vsphone.com/invite/{ref_code}", wait_until="networkidle")
            
            # Điền email giả lập để test
            await page.locator('input[type="text"]').first.fill(f"user_{int(time.time())}@gmail.com")
            await page.get_by_text("Get code").click()
            
            # Đợi captcha xuất hiện
            print("⏳ Đang chờ Captcha...")
            captcha_img = page.locator(".captcha-main-img").first
            await captcha_img.wait_for(state="visible", timeout=10000)
            
            # Chụp ảnh khung captcha
            await captcha_img.screenshot(path="captcha.png")
            
            # Gửi lên API giải
            distance = solve_captcha("captcha.png")
            
            if distance:
                print(f"✅ API trả về: {distance}px. Bắt đầu kéo...")
                slider_btn = page.locator(".van-slider__button, .page-slide-btn").first
                
                # Thực hiện kéo kiểu người thật
                await human_slide(page, slider_btn, distance)
                print("🏁 Đã trượt xong!")
            else:
                print("❌ API không giải được captcha này.")
            
            # Đợi 5s xem kết quả
            await asyncio.sleep(5)
            await page.screenshot(path="ketqua.png")
            
        except Exception as e:
            print(f"❌ Lỗi hệ thống: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
