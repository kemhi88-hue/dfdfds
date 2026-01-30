import asyncio
import sys
import os
from playwright.async_api import async_playwright
import playwright_stealth

async def solve_slider(page):
    print("--- Đang xử lý Captcha trượt... ---")
    try:
        # Chờ slider xuất hiện
        slider_selector = ".geetest_slider_button, .slide-btn, [class*='slider']" 
        await page.wait_for_selector(slider_selector, timeout=10000)
        
        slider = page.locator(slider_selector).first
        box = await slider.bounding_box()
        
        start_x = box['x'] + box['width'] / 2
        start_y = box['y'] + box['height'] / 2
        
        distance = 165 # Tọa độ giả định
        
        await page.mouse.move(start_x, start_y)
        await page.mouse.down()
        await page.mouse.move(start_x + distance, start_y, steps=20)
        await page.mouse.up()
        print("--- Đã trượt captcha xong ---")
    except:
        print("--- Không tìm thấy captcha để trượt ---")

async def main():
    if len(sys.argv) < 4: return
    email, password, ref_code = sys.argv[1], sys.argv[2], sys.argv[3]

    async with async_playwright() as p:
        # Thêm các tham số để trình duyệt chạy giống người thật hơn
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            await playwright_stealth.stealth_async(page)
        except: pass

        print(f"--- Truy cập trang đăng ký: {email} ---")
        try:
            # 1. Đi đến trang đăng ký
            await page.goto(f"https://cloud.vsphone.com/register?code={ref_code}", timeout=60000, wait_until="networkidle")

            # 2. Selector linh hoạt: Tìm bất kỳ ô input nào có type là text hoặc email
            print("--- Đang tìm ô nhập liệu... ---")
            email_input = page.locator('input[type="text"], input[type="email"], input[placeholder*="mail"]').first
            pass_input = page.locator('input[type="password"], input[placeholder*="password"]').first

            # Đợi ô email hiển thị
            await email_input.wait_for(state="visible", timeout=15000)
            
            # 3. Điền thông tin
            await email_input.fill(email)
            await pass_input.fill(password)
            print("--- Đã điền xong Email và Pass ---")

            # 4. Nhấn nút đăng ký (tìm theo text cho chắc)
            register_btn = page.locator('button, input[type="button"], .btn').filter(has_text="Register").first
            await register_btn.click()
            
            await asyncio.sleep(3)
            await solve_slider(page)
            
            # Chụp ảnh kết quả cuối cùng
            await asyncio.sleep(5)
            await page.screenshot(path="ketqua.png")
            print("--- Hoàn tất! Đã chụp ảnh ketqua.png ---")

        except Exception as e:
            print(f"❌ LỖI RỒI: {e}")
            # QUAN TRỌNG: Chụp ảnh lúc bị lỗi để xem trang web đang hiện gì
            await page.screenshot(path="ketqua.png")
            print("--- Đã chụp ảnh màn hình lỗi vào ketqua.png ---")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
