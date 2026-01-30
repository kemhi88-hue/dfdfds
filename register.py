import asyncio
import sys
from playwright.async_api import async_playwright
# Import trực tiếp hàm stealth
from playwright_stealth import stealth

async def main():
    # Kiểm tra tham số truyền vào
    if len(sys.argv) < 4:
        print("Lỗi: Thiếu tham số Email, Password hoặc Ref.")
        return

    email = sys.argv[1]
    password = sys.argv[2]
    ref_code = sys.argv[3]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Sử dụng hàm stealth trực tiếp (thay vì stealth_async)
        await stealth(page)

        print(f"--- Đang mở trang đăng ký cho: {email} ---")
        try:
            await page.goto(f"https://cloud.vsphone.com/register?code={ref_code}", timeout=60000)

            # Chờ và điền thông tin
            await page.wait_for_selector('input[placeholder="Please enter your email address"]', timeout=10000)
            await page.fill('input[placeholder="Please enter your email address"]', email)
            await page.fill('input[placeholder="Please enter your login password"]', password)
            
            print("--- Đã điền xong form, đang dừng ở bước Captcha ---")
            
        except Exception as e:
            print(f"Lỗi khi thực hiện thao tác: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
