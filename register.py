import asyncio
import sys
from playwright.async_api import async_playwright
import playwright_stealth

async def solve_slider(page):
    print("--- Đang xử lý Captcha trượt... ---")
    try:
        # Chờ slider xuất hiện
        slider_selector = ".geetest_slider_button, .slide-btn, [class*='slider']" 
        await page.wait_for_selector(slider_selector, timeout=15000)
        
        slider = page.locator(slider_selector).first
        box = await slider.bounding_box()
        
        start_x = box['x'] + box['width'] / 2
        start_y = box['y'] + box['height'] / 2
        
        # Khoảng cách trượt giả định (có thể cần tinh chỉnh sau khi xem ảnh)
        distance = 165 
        
        await page.mouse.move(start_x, start_y)
        await page.mouse.down()
        # Kéo có gia tốc để giống người thật
        await page.mouse.move(start_x + distance * 0.8, start_y + 2, steps=15)
        await asyncio.sleep(0.2)
        await page.mouse.move(start_x + distance, start_y, steps=5)
        await page.mouse.up()
        print("--- Đã thực hiện kéo thanh trượt ---")
    except Exception as e:
        print(f"--- Không tìm thấy captcha hoặc lỗi trượt: {e} ---")

async def main():
    if len(sys.argv) < 4: return
    email, password, ref_code = sys.argv[1], sys.argv[2], sys.argv[3]

    # THÔNG TIN PROXY CỦA BẠN
    proxy_server = "http://103.190.202.92:8080"

    async with async_playwright() as p:
        print(f"--- Đang khởi tạo trình duyệt với Proxy: {proxy_server} ---")
        
        # Chạy trình duyệt qua Proxy để tránh màn hình trắng
        browser = await p.chromium.launch(
            headless=True,
            proxy={"server": proxy_server},
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        page = await context.new_page()
        
        try:
            # Kích hoạt tàng hình chống bot
            await playwright_stealth.stealth_async(page)
            
            print(f"--- Truy cập trang đăng ký VSPhone: {email} ---")
            # Tăng timeout lên 100 giây vì Proxy có thể làm mạng chậm hơn
            await page.goto(f"https://cloud.vsphone.com/register?code={ref_code}", timeout=100000, wait_until="domcontentloaded")

            # Chờ trang tải ổn định
            await asyncio.sleep(10)
            
            # Tìm ô nhập liệu
            email_input = page.locator('input[type="text"], input[type="email"], [placeholder*="email"]').first
            pass_input = page.locator('input[type="password"], [placeholder*="password"]').first

            if await email_input.is_visible(timeout=20000):
                await email_input.fill(email)
                await pass_input.fill(password)
                print("--- Đã hiện trang web và điền xong thông tin! ---")
                
                # Nhấn nút đăng ký để hiện Captcha
                register_btn = page.locator('button, .btn').filter(has_text="Register").first
                await register_btn.click()
                
                await asyncio.sleep(3)
                await solve_slider(page)
                
                # Chụp ảnh kết quả cuối cùng
                await asyncio.sleep(5)
                await page.screenshot(path="ketqua.png")
                print("--- Đã chụp ảnh kết quả thành công ---")
            else:
                print("--- LỖI: Vẫn bị màn hình trắng dù đã dùng Proxy ---")
                await page.screenshot(path="ketqua.png")

        except Exception as e:
            print(f"--- Gặp lỗi trong quá trình chạy: {e} ---")
            await page.screenshot(path="ketqua.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
