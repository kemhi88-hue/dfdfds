import asyncio
import sys
from playwright.async_api import async_playwright
import playwright_stealth

async def solve_slider(page):
    print("--- Đang xử lý Captcha trượt... ---")
    try:
        slider_selector = ".geetest_slider_button, .slide-btn, [class*='slider']" 
        await page.wait_for_selector(slider_selector, timeout=15000)
        slider = page.locator(slider_selector).first
        box = await slider.bounding_box()
        start_x, start_y = box['x'] + box['width'] / 2, box['y'] + box['height'] / 2
        distance = 165 
        await page.mouse.move(start_x, start_y)
        await page.mouse.down()
        await page.mouse.move(start_x + distance, start_y, steps=20)
        await page.mouse.up()
        print("--- Đã thực hiện kéo thanh trượt ---")
    except:
        print("--- Không tìm thấy captcha để trượt ---")

async def main():
    if len(sys.argv) < 4: return
    email, password, ref_code = sys.argv[1], sys.argv[2], sys.argv[3]

    # PROXY CỦA BẠN
    proxy_server = "http://103.190.202.92:8080"

    async with async_playwright() as p:
        print(f"--- Đang chạy với Proxy: {proxy_server} ---")
        browser = await p.chromium.launch(
            headless=True,
            proxy={"server": proxy_server},
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # SỬA LỖI TẠI ĐÂY: Kiểm tra hàm trước khi gọi
        try:
            if hasattr(playwright_stealth, 'stealth_async'):
                await playwright_stealth.stealth_async(page)
            else:
                await playwright_stealth.stealth(page)
        except Exception as e:
            print(f"--- Lưu ý: Lỗi ẩn danh ({e}) nhưng vẫn tiếp tục chạy... ---")

        try:
            print(f"--- Truy cập VSPhone: {email} ---")
            await page.goto(f"https://cloud.vsphone.com/register?code={ref_code}", timeout=100000, wait_until="domcontentloaded")
            await asyncio.sleep(10)
            
            # Tìm ô nhập liệu
            email_input = page.locator('input[type="text"], input[type="email"], [placeholder*="email"]').first
            pass_input = page.locator('input[type="password"], [placeholder*="password"]').first

            if await email_input.is_visible(timeout=20000):
                await email_input.fill(email)
                await pass_input.fill(password)
                print("--- Đã hiện trang và điền xong thông tin! ---")
                
                await page.click('button:has-text("Register"), .register-btn')
                await asyncio.sleep(3)
                await solve_slider(page)
                
                await asyncio.sleep(5)
                await page.screenshot(path="ketqua.png")
            else:
                print("--- LỖI: Trang vẫn bị trắng (Có thể Proxy bị chết) ---")
                await page.screenshot(path="ketqua.png")

        except Exception as e:
            print(f"--- Lỗi khi chạy: {e} ---")
            await page.screenshot(path="ketqua.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
