import asyncio
import os
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Chạy trình duyệt ẩn
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Lấy Token từ Secret của Repo (DISCORD_TOKEN)
        token = os.getenv("DISCORD_TOKEN")
        channel_id = "1464219586386722816"

        try:
            # 1. Đăng nhập
            await page.goto("https://discord.com/login")
            await page.evaluate(f"localStorage.setItem('token', '\"{token}\"');")
            
            # 2. Vào kênh DM
            await page.goto(f"https://discord.com/channels/@me/{channel_id}")
            
            # 3. Chờ và gõ lệnh (Mô phỏng V8)
            await page.wait_for_selector('[data-slate-editor="true"]', timeout=30000)
            chat_input = page.locator('[data-slate-editor="true"]')
            await chat_input.click()
            await chat_input.type("/bot", delay=150)
            
            # 4. Nhấn Tab để chọn lệnh
            await asyncio.sleep(3)
            await page.keyboard.press("Tab")
            
            # 5. Nhấn Enter để gửi
            await asyncio.sleep(1)
            await page.keyboard.press("Enter")
            print("✅ Đã gửi lệnh /bot thành công!")
            
        except Exception as e:
            print(f"❌ Lỗi: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
