import asyncio
import sys
from playwright.async_api import async_playwright
# Sửa lỗi import ở đây
from playwright_stealth import stealth_async

async def main():
    if len(sys.argv) < 4:
        print("Thiếu tham số truyền vào!")
        return
        
    email = sys.argv[1]
    password = sys.argv[2]
    ref_code = sys.argv[3]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Cách dùng đúng cho bản stealth mới
        await stealth_async(page)

        print(f"--- Bắt đầu chạy cho email: {email} ---")
        await page.goto(f"https://cloud.vsphone.com/register?code={ref_code}")

        # Điền form
        await page.wait_for_selector('input[placeholder="Please enter your email address"]')
        await page.fill('input[placeholder="Please enter your email address"]', email)
        await page.fill('input[placeholder="Please enter your login password"]', password)
        
        print("--- Đã điền xong thông tin, đang dừng ở bước Captcha ---")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
