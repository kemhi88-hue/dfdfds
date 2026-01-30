import asyncio
import sys
from playwright.async_api import async_playwright
import playwright_stealth

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
        
        # Cách gọi stealth an toàn cho bản mới nhất
        await playwright_stealth.stealth_async(page)

        print(f"--- Đang mở trang đăng ký cho: {email} ---")
        await page.goto(f"https://cloud.vsphone.com/register?code={ref_code}")

        # Chờ và điền thông tin
        await page.wait_for_selector('input[placeholder="Please enter your email address"]')
        await page.fill('input[placeholder="Please enter your email address"]', email)
        await page.fill('input[placeholder="Please enter your login password"]', password)
        
        print("--- Đã điền xong form, đang dừng ở bước Captcha ---")
        # Giữ trình duyệt 1 lúc để quan sát log nếu cần
        await asyncio.sleep(2)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
