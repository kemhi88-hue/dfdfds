import asyncio
import sys
from playwright.async_api import async_playwright
import playwright_stealth

async def main():
    if len(sys.argv) < 4: return
    email, password, ref_code = sys.argv[1], sys.argv[2], sys.argv[3]

    async with async_playwright() as p:
        # BỎ PROXY LỖI - Chạy trực tiếp với cấu hình giả lập thiết bị di động
        browser = await p.chromium.launch(headless=True)
        
        # Giả lập iPhone để vượt qua rào cản firewall của bản /invite/
        context = await browser.new_context(
            **p.devices['iPhone 13'],
            locale='vi-VN',
            timezone_id='Asia/Ho_Chi_Minh'
        )
        page = await context.new_page()
        
        try:
            # Kích hoạt tàng hình
            try:
                import playwright_stealth
                await playwright_stealth.stealth_async(page)
            except: pass

            target_url = f"https://www.vsphone.com/invite/{ref_code}"
            print(f"--- Đang truy cập trực tiếp (không Proxy): {target_url} ---")
            
            # Sử dụng wait_until="commit" để tránh treo khi trang web tải script bên thứ 3 chậm
            await page.goto(target_url, timeout=60000, wait_until="commit")
            
            # Đợi 10 giây cho giao diện mobile render
            await asyncio.sleep(10)
            
            # Chụp ảnh ngay để kiểm tra link mới có hiển thị không
            await page.screenshot(path="ketqua.png")

            # Tìm kiếm các ô nhập liệu (Link /invite thường dùng label hoặc placeholder Tiếng Việt)
            print("--- Đang tìm form đăng ký... ---")
            
            # Điền Email/SĐT
            inputs = await page.query_selector_all('input')
            for i in inputs:
                p_holder = (await i.get_attribute('placeholder') or "").lower()
                if any(x in p_holder for x in ['email', 'phone', 'số điện thoại', 'tài khoản']):
                    await i.fill(email)
                if any(x in p_holder for x in ['password', 'mật khẩu']):
                    await i.fill(password)

            # Tìm nút bấm: Đăng ký, Nhận mã, hoặc Tiếp tục
            btn = page.locator('button, [class*="button"], .van-button').first
            if await btn.is_visible():
                print("--- Đã thấy nút bấm, đang thực hiện click... ---")
                await btn.click()
                await asyncio.sleep(5)
                await page.screenshot(path="ketqua.png")
            else:
                print("--- Không tìm thấy nút bấm trên giao diện này ---")

        except Exception as e:
            print(f"--- Lỗi khi thực hiện: {e} ---")
            await page.screenshot(path="ketqua.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
