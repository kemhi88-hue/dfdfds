import asyncio
import sys
from playwright.async_api import async_playwright
# Import theo cách này để tránh lỗi module không thể gọi
import playwright_stealth

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
        
        # Gọi chính xác hàm stealth từ module đã import
        await playwright_stealth.stealth_async(page)

        print(f"--- Đang mở trang đăng ký cho: {email} ---")
        try:
            # Tăng timeout lên 60s để tránh lỗi mạng trên GitHub
            await page.goto(f"https://cloud.vsphone.com/register?code={ref_code}", timeout=60000)

            # Chờ ô nhập liệu xuất hiện
            await page.wait_for_selector('input[placeholder="Please enter your email address"]', timeout=15000)
            await page.fill('input[placeholder="Please enter your email address"]', email)
            await page.fill('input[placeholder="Please enter your login password"]', password)
            
            print("--- Đã điền xong form, đang dừng ở bước Captcha ---")
            
        except Exception as e:
            print(f"Lỗi thao tác trên trang: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
