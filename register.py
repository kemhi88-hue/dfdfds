import asyncio
import sys
import re
import requests
import time
from playwright.async_api import async_playwright

# --- HÀM GIẢI CAPTCHA ---
async def solve_puzzle_captcha(page):
    """Xử lý kéo mảnh ghép dựa trên ảnh thực tế"""
    try:
        print("--- Đang phát hiện Captcha ghép hình... ---")
        # Chờ slider xuất hiện (theo giao diện van-ui thường dùng)
        slider_selector = '.van-slider__button, .page-slide-btn, [class*="slider"]'
        await page.wait_for_selector(slider_selector, timeout=10000)
        
        slider = page.locator(slider_selector).first
        box = await slider.bounding_box()
        
        # Điểm bắt đầu (giữa nút trượt)
        start_x = box['x'] + box['width'] / 2
        start_y = box['y'] + box['height'] / 2
        
        # Khoảng cách kéo (Dựa trên ảnh image_2f0fd9.png, thường khoảng 160-200 pixel)
        # Chúng ta sẽ kéo thử 180px, nếu không khớp bạn hãy báo tôi để chỉnh lại
        distance = 180 
        
        print(f"--- Thực hiện kéo slider từ {start_x} đi {distance}px ---")
        await page.mouse.move(start_x, start_y)
        await page.mouse.down()
        
        # Kéo từ từ có gia tốc để giống người thật
        await page.mouse.move(start_x + distance, start_y, steps=25)
        await asyncio.sleep(0.5)
        await page.mouse.up()
        
        print("--- Đã kéo xong Captcha ---")
        await asyncio.sleep(2) # Chờ hệ thống xác nhận
    except Exception as e:
        print(f"--- Không tìm thấy Captcha hoặc lỗi khi kéo: {e} ---")

# --- LUỒNG CHÍNH ---
async def main():
    ref_code = sys.argv[1] if len(sys.argv) > 1 else "vsagwtjq63"
    
    # Tạo email ảo qua Mail.tm
    email, mail_token = create_temp_email() # Sử dụng hàm tạo mail đã viết ở trên
    if not email: return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Bắt buộc dùng iPhone 13 để hiện đúng giao diện Captcha như ảnh
        context = await browser.new_context(**p.devices['iPhone 13'])
        page = await context.new_page()
        
        try:
            await page.goto(f"https://www.vsphone.com/invite/{ref_code}", timeout=100000, wait_until="commit")
            await asyncio.sleep(10)

            # 1. Điền Email vào ô đầu tiên
            await page.locator('input').nth(0).fill(email)
            
            # 2. Bấm Get code để hiện Captcha
            await page.get_by_text("Get code").click()
            await asyncio.sleep(3)
            
            # 3. GIẢI CAPTCHA TẠI ĐÂY
            await solve_puzzle_captcha(page)
            
            # 4. Đợi OTP và điền tiếp các ô còn lại
            otp = get_otp_from_mail_tm(mail_token)
            if otp:
                await page.locator('input').nth(1).fill(otp)
                await page.locator('input').nth(2).fill("Password99@")
                await page.click('button:has-text("Register")')
                print("--- Đã gửi form đăng ký ---")
            
            await asyncio.sleep(5)
            await page.screenshot(path="ketqua.png")
        except Exception as e:
            print(f"Lỗi: {e}")
            await page.screenshot(path="ketqua.png")
        await browser.close()
