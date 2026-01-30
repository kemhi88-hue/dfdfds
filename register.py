import asyncio
import sys
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

async def main():
    # Nhận dữ liệu từ GitHub Actions gửi sang
    email = sys.argv[1]
    password = sys.argv[2]
    ref_code = sys.argv[3]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True) # Chạy ngầm trên server
        context = await browser.new_context()
        page = await context.new_page()
        await stealth_async(page)

        print(f"Bắt đầu đăng ký cho: {email}")
        await page.goto(f"https://cloud.vsphone.com/register?code={ref_code}")

        # Điền form dựa trên placeholder bạn đã cung cấp
        await page.wait_for_selector('input[placeholder="Please enter your email address"]')
        await page.fill('input[placeholder="Please enter your email address"]', email)
        await page.fill('input[placeholder="Please enter your login password"]', password)
        
        # Phần giải captcha sẽ được thêm tiếp vào đây khi bạn có HTML ảnh
        print("Đã điền xong form, đang xử lý captcha...")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
