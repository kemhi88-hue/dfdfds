import asyncio
import sys
from playwright.async_api import async_playwright
import playwright_stealth

async def solve_slider(page):
    print("--- Đang tìm Captcha trên link mới... ---")
    try:
        # Link mới có thể dùng kiểu captcha khác, thử tìm selector phổ biến
        slider_selector = ".geetest_slider_button, .slide-btn, [class*='slider'], .van-button" 
        await page.wait_for_selector(slider_selector, timeout=10000)
        slider = page.locator(slider_selector).first
        box = await slider.bounding_box()
        
        start_x, start_y = box['x'] + box['width'] / 2, box['y'] + box['height'] / 2
        distance = 165 
        
        await page.mouse.move(start_x, start_y)
        await page.mouse.down()
        await page.mouse.move(start_x + distance, start_y, steps=20)
        await page.mouse.up()
        print("--- Đã xử lý thao tác trượt ---")
    except:
        print("--- Không thấy Captcha hoặc đã tự qua ---")

async def main():
    if len(sys.argv) < 4: return
    email, password, ref_code = sys.argv[1], sys.argv[2], sys.argv[3]

    # Proxy của bạn
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
        
        # Chống bot an toàn
        try:
            if hasattr(playwright_stealth, 'stealth_async'):
                await playwright_stealth.stealth_async(page)
            else:
                await playwright_stealth.stealth(page)
        except: pass

        try:
            # SỬA LINK TẠI ĐÂY
            target_url = f"https://www.vsphone.com/invite/{ref_code}"
            print(f"--- Truy cập link mời mới: {target_url} ---")
            
            await page.goto(target_url, timeout=100000, wait_until="networkidle")
            await asyncio.sleep(10) # Đợi trang render hoàn toàn

            # Tìm kiếm các ô nhập liệu theo thuộc tính chung (vì link mới có thể đổi class)
            # Thường là Email, Password, và nút Gửi mã
            print("--- Đang quét các ô nhập liệu trên trang mới... ---")
            
            # Tự động tìm ô nhập Email/Username
            inputs = await page.query_selector_all('input')
            for i in inputs:
                p_holder = await i.get_attribute('placeholder') or ""
                t_type = await i.get_attribute('type') or ""
                
                if "email" in p_holder.lower() or "account" in p_holder.lower() or t_type == "text":
                    await i.fill(email)
                elif "password" in p_holder.lower() or t_type == "password":
                    await i.fill(password)

            print("--- Đã điền xong form (giả định) ---")
            
            # Thử tìm nút Register hoặc Confirm
            register_btn = page.locator('button, .btn, [class*="submit"]').first
            if await register_btn.is_visible():
                await register_btn.click()
                await asyncio.sleep(3)
                await solve_slider(page)
            
            # Chụp ảnh để xem giao diện link mới trông như thế nào
            await asyncio.sleep(5)
            await page.screenshot(path="ketqua.png", full_page=True)
            print("--- Đã chụp ảnh kết quả ketqua.png ---")

        except Exception as e:
            print(f"--- Lỗi: {e} ---")
            await page.screenshot(path="ketqua.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
