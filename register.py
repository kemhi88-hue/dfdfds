import asyncio
import sys
import cv2
import numpy as np
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

async def solve_captcha(page):
    try:
        # 1. Đợi khung captcha xuất hiện
        await page.wait_for_selector('.geetest_canvas_bg, .captcha_bg', timeout=10000)
        
        # 2. Chụp ảnh màn hình để xử lý
        await page.screenshot(path="captcha.png")
        img = cv2.imread("captcha.png")
        
        # 3. Logic tìm điểm khuyết (giả lập tìm cạnh)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        # Thường khoảng cách trượt của VSPhone nằm trong khoảng này
        # Chúng ta sẽ thử nghiệm kéo một đoạn giả lập để vượt qua lớp bảo vệ
        distance = 160 
        
        # 4. Thực hiện kéo slider giống người thật
        slider = page.locator('.geetest_slider_button, [class*="slider-btn"]')
        box = await slider.bounding_box()
        
        await page.mouse.move(box['x'] + 10, box['y'] + 10)
        await page.mouse.down()
        # Kéo có gia tốc (steps) để lừa hệ thống chống bot
        await page.mouse.move(box['x'] + distance + 5, box['y'] + 12, steps=15)
        await asyncio.sleep(0.3)
        await page.mouse.move(box['x'] + distance, box['y'] + 10, steps=5)
        await page.mouse.up()
        
        print("Đã thực hiện kéo captcha.")
    except Exception as e:
        print(f"Không xử lý được captcha: {e}")

async def main():
    email = sys.argv[1]
    password = sys.argv[2]
    ref_code = sys.argv[3]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 720})
        page = await context.new_page()
        await stealth_async(page)

        print(f"Bắt đầu đăng ký: {email}")
        await page.goto(f"https://cloud.vsphone.com/register?code={ref_code}")

        # Điền form
        await page.wait_for_selector('input[placeholder="Please enter your email address"]')
        await page.fill('input[placeholder="Please enter your email address"]', email)
        await page.fill('input[placeholder="Please enter your login password"]', password)
        
        # Nhấn nút để hiện captcha
        await page.click('button:has-text("Register"), .register-btn')
        
        # Giải Captcha
        await solve_captcha(page)
        
        # Đợi xem có thông báo thành công không và chụp ảnh lại
        await asyncio.sleep(5)
        await page.screenshot(path="result.png")
        print("Đã chụp ảnh kết quả result.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
