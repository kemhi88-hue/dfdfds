import asyncio
import os
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

async def run():
    async with async_playwright() as p:
        print("--- Khởi tạo trình duyệt (Stealth Mode) ---")
        browser = await p.chromium.launch(headless=True)
        # Tạo context với cấu hình giống người dùng thật nhất
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        # Áp dụng Stealth để ẩn danh bot
        await stealth_async(page)
        
        token = os.getenv("DISCORD_TOKEN")
        channel_id = "1464219586386722816"

        try:
            # 1. Truy cập trang chủ trước
            print("--- Truy cập Discord ---")
            await page.goto("https://discord.com/404", wait_until="domcontentloaded") # Vào trang 404 cho nhẹ để nạp Token
            
            # 2. Nạp Token vào LocalStorage với cơ chế ép buộc
            print("--- Đang nạp Token ---")
            await page.evaluate(f"""
                (t) => {{
                    localStorage.setItem('token', '"{token}"');
                }}
            """, token)
            
            # 3. Truy cập thẳng vào kênh chat
            print(f"--- Đang vào kênh: {channel_id} ---")
            await page.goto(f"https://discord.com/channels/@me/{channel_id}", wait_until="networkidle")
            
            # 4. Chờ ô chat xuất hiện với nhiều Selector dự phòng
            print("--- Đang tìm ô chat... ---")
            chat_selector = '[data-slate-editor="true"]'
            
            # Chờ tối đa 60s và kiểm tra liên tục
            await page.wait_for_selector(chat_selector, timeout=60000)
            
            chat_input = page.locator(chat_selector)
            await chat_input.click()
            await asyncio.sleep(2)
            
            print("--- Đang gõ lệnh /bot ---")
            # Gõ từng phím để giống người thật
            await chat_input.type("/bot", delay=250)
            
            # 5. Kỹ thuật Tab + Enter đặc biệt
            print("--- Chờ menu Slash Command (5s) ---")
            await asyncio.sleep(5) 
            
            print("--- Thực hiện Tab + Enter ---")
            await page.keyboard.press("Tab")
            await asyncio.sleep(1.5)
            await page.keyboard.press("Enter")
            
            print("✅ KẾT THÚC: Lệnh đã được gửi!")
            
        except Exception as e:
            print(f"❌ LỖI: {e}")
            # Chụp ảnh toàn màn hình để debug xem Discord đang hiện gì (Captcha hay trang trắng)
            await page.screenshot(path="loi_chi_tiet.png", full_page=True)
        finally:
            await browser.close()
            print("--- Đã đóng trình duyệt ---")

if __name__ == "__main__":
    asyncio.run(run())
