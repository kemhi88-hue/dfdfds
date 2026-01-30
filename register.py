import asyncio
import sys
from playwright.async_api import async_playwright

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
        
        # Cách gọi stealth an toàn: Thử từng hàm một
        try:
            import playwright_stealth
            # Thử hàm stealth_async, nếu không có thì thử hàm stealth
            if hasattr(playwright_stealth, 'stealth_async'):
                await playwright_stealth.stealth_async(page)
            elif hasattr(playwright_stealth, 'stealth'):
                await playwright_stealth.stealth(page)
        except Exception as e:
            print(f"Bỏ qua bước Stealth do lỗi thư viện: {e}")

        print(f"--- Đang mở trang đăng ký cho: {email} ---")
        try:
            # Truy cập trang web với thời gian chờ 60 giây
            await page.goto(f"https://cloud.vsphone.com/register?code={ref_code}", timeout=60000)

            # Đợi ô nhập liệu xuất hiện (sử dụng selector linh hoạt hơn)
            await page.wait_for_selector('input', timeout=20000)
            
            # Tìm và điền thông tin dựa trên placeholder hoặc type
            inputs = await page.query_selector_all('input')
            for i in inputs:
                placeholder = await i.get_attribute('placeholder')
                if placeholder and 'email' in placeholder.lower():
                    await i.fill(email)
                if placeholder and 'password' in placeholder.lower():
                    await i.fill(password)
            
            print("--- Đã điền xong form thành công! ---")
            
        except Exception as e:
            print(f"Dừng lại tại bước thao tác: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
