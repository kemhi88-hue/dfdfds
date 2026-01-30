import asyncio
import sys
from playwright.async_api import async_playwright
import playwright_stealth

async def main():
    if len(sys.argv) < 4: return
    email, password, ref_code = sys.argv[1], sys.argv[2], sys.argv[3]

    async with async_playwright() as p:
        # 1. Khởi tạo trình duyệt với các tham số ẩn danh mạnh hơn
        browser = await p.chromium.launch(
            headless=True, 
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox'
            ]
        )
        
        # 2. Giả lập một trình duyệt Chrome thật trên Windows
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        page = await context.new_page()
        
        try:
            # Kích hoạt tính năng tàng hình
            await playwright_stealth.stealth_async(page)
            
            print(f"--- Đang kết nối tới VSPhone (Chế độ chống chặn)... ---")
            
            # 3. Truy cập và đợi cho đến khi mạng rảnh hoàn toàn
            # Tăng timeout lên 120s vì server GitHub tải web VN rất chậm
            await page.goto(
                f"https://cloud.vsphone.com/register?code={ref_code}", 
                timeout=120000, 
                wait_until="domcontentloaded"
            )

            # Đợi thêm một chút để script giao diện chạy
            await asyncio.sleep(10)
            
            # 4. Kiểm tra xem có Form không, nếu không thấy sẽ chụp ảnh báo lỗi
            email_field = page.locator('input[placeholder*="email"], input[type="text"]').first
            
            if await email_field.is_visible(timeout=20000):
                await email_field.fill(email)
                await page.locator('input[type="password"]').first.fill(password)
                print("--- Đã hiện form và điền thông tin thành công! ---")
                
                # Chụp ảnh xác nhận đã điền form
                await page.screenshot(path="ketqua.png")
                
                # Tới đây bạn có thể thêm lệnh Click Register
            else:
                print("--- Vẫn bị màn hình trắng hoặc trang web không tải được nội dung ---")
                await page.screenshot(path="ketqua.png", full_page=True)

        except Exception as e:
            print(f"Lỗi: {e}")
            await page.screenshot(path="ketqua.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
