import asyncio
import os
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        print("--- Đang khởi tạo trình duyệt ---")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        token = os.getenv("DISCORD_TOKEN")
        channel_id = "1464219586386722816"

        try:
            # Bước 1: Truy cập trang chủ Discord trước để khởi tạo localStorage
            print("--- Truy cập Discord App ---")
            await page.goto("https://discord.com/app", wait_until="domcontentloaded")
            
            # Bước 2: Nạp Token
            print("--- Đang nạp Token ---")
            await page.evaluate(f"window.localStorage.setItem('token', '\"{token}\"');")
            await asyncio.sleep(1)

            # Bước 3: Vào thẳng kênh chat
            print(f"--- Đang truy cập kênh: {channel_id} ---")
            await page.goto(f"https://discord.com/channels/@me/{channel_id}", wait_until="networkidle")
            
            # Bước 4: Chờ ô chat và gửi lệnh
            print("--- Đang tìm ô chat... ---")
            selector = '[data-slate-editor="true"], [role="textbox"]'
            await page.wait_for_selector(selector, timeout=60000)
            
            chat_input = page.locator(selector).first
            await chat_input.click()
            await chat_input.type("/bot", delay=200)
            
            print("--- Đợi menu & Gửi ---")
            await asyncio.sleep(4) 
            await page.keyboard.press("Tab")
            await asyncio.sleep(1.5)
            await page.keyboard.press("Enter")
            
            print("✅ THÀNH CÔNG!")
            
        except Exception as e:
            print(f"❌ LỖI: {e}")
            await page.screenshot(path="loi_chi_tiet.png")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
