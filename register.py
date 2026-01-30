import asyncio
import sys
from playwright.async_api import async_playwright
import playwright_stealth

async def solve_slider(page):
    print("--- Đang xử lý Captcha trượt... ---")
    try:
        # Chờ nút gạt xuất hiện
        slider_selector = ".geetest_slider_button" 
        await page.wait_for_selector(slider_selector, timeout=15000)
        
        slider = page.locator(slider_selector)
        box = await slider.bounding_box()
        
        start_x = box['x'] + box['width'] / 2
        start_y = box['y'] + box['height'] / 2
        
        # Khoảng cách trượt thông dụng cho VSPhone
        distance = 165 
        
        await page.mouse.move(start_x, start_y)
        await page.mouse.down()
        
        # Kéo có gia tốc để giả lập người thật
        await page.mouse.move(start_x + distance * 0.7, start_y + 2, steps=10)
        await asyncio.sleep(0.1)
        await page.mouse.move(start_x + distance, start_y, steps=8)
        
        await page.mouse.up()
        print("--- Đã thực hiện xong thao tác trượt. ---")
    except Exception as e:
        print(f"Lỗi Captcha: {e}")

async def main():
    if len(sys.argv) < 4: return
    email, password, ref_code = sys.argv[1], sys.argv[2], sys.argv[3]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 720})
        page = await context.new_page()
        
        # Kích hoạt chế độ ẩn danh (Stealth) an toàn
        try:
            import playwright_stealth
            await playwright_stealth.stealth_async(page)
        except: pass

        print(f"--- Đăng ký tài khoản: {email} ---")
        await page.goto(f"https://cloud.vsphone.com/register?code={ref_code}", timeout=60000)

        # Điền thông tin đăng ký
        await page.wait_for_selector('input[placeholder*="email"]')
        await page.fill('input[placeholder*="email"]', email)
        await page.fill('input[placeholder*="password"]', password)
        
        # Nhấn nút Register để hiện Captcha
        await page.click('button:has-text("Register"), .register-btn')
        
        await asyncio.sleep(3) # Đợi captcha load
        await solve_slider(page)
        
        # Đợi 5s để trang xử lý và chụp ảnh kết quả
        await asyncio.sleep(5)
        await page.screenshot(path="ketqua.png")
        print("--- Đã chụp ảnh kết quả lưu vào ketqua.png ---")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
