import asyncio
import sys
from playwright.async_api import async_playwright
# Cách import trực tiếp để tránh lỗi 'module has no attribute'
from playwright_stealth import stealth_async

async def main():
    if len(sys.argv) < 4:
        print("Lỗi: Thiếu tham số truyền vào.")
        return

    email = sys.argv[1]
    password = sys.argv[2]
    ref_code = sys.argv[3]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Thử thực hiện stealth, nếu vẫn lỗi thì bỏ qua để chạy tiếp
        try:
            await stealth_async(page)
        except Exception as e:
            print(f"Lưu ý: Không thể kích hoạt stealth ({e}), vẫn tiếp tục chạy...")

        print(f"--- Đang mở trang đăng ký cho: {email} ---")
        try:
            # Truy cập trang web
            await page.goto(f"https://cloud.vsphone.com/register?code={ref_code}", timeout=60000)

            # Chờ ô nhập liệu (tăng thời gian chờ lên 20s cho chắc chắn)
            await page.wait_for_selector('input[placeholder*="email"]', timeout=20000)
            await page.fill('input[placeholder*="email"]', email)
            await page.fill('input[placeholder*="password"]', password)
            
            print("--- Đã điền xong form thành công! ---")
            
        except Exception as e:
            print(f"Dừng lại tại bước nhập liệu: {e}")
            # Chụp ảnh màn hình lỗi để bạn tự xem web đang hiện gì
            await page.screenshot(path="error_screen.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
