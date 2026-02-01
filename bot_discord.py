import asyncio
import os
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        print("--- Đang khởi tạo trình duyệt test ---")
        browser = await p.chromium.launch(headless=True)
        # Giả lập User Agent thật để tránh bị Discord chặn
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Lấy Token từ Secret của Repo
        token = os.getenv("DISCORD_TOKEN")
        channel_id = "1464219586386722816"

        try:
            print("--- Đang nạp Token vào hệ thống ---")
            await page.goto("https://discord.com/login")
            # Script nạp token an toàn
            await page.evaluate(f"""
                (token) => {{
                    setInterval(() => {{
                        window.localStorage.setItem("token", `"${{token}}"`);
                    }}, 50);
                }}
            """, token)
            
            print(f"--- Đang truy cập kênh: {channel_id} ---")
            await page.goto(f"https://discord.com/channels/@me/{channel_id}")
            
            # Chờ ô chat load (Slate Editor)
            print("--- Đang chờ ô nhập liệu xuất hiện... ---")
            await page.wait_for_selector('[data-slate-editor="true"]', timeout=30000)
            chat_input = page.locator('[data-slate-editor="true"]')
            
            # Click để lấy focus
            await chat_input.click()
            await asyncio.sleep(1)
            
            print("--- Đang gõ lệnh /bot ---")
            await chat_input.type("/bot", delay=200)
            
            # Đợi menu lệnh hiện lên (Rất quan trọng)
            print("--- Đợi menu Slash Command hiện lên... ---")
            await asyncio.sleep(4) 
            
            print("--- Nhấn TAB để chọn lệnh đầu tiên ---")
            await page.keyboard.press("Tab")
            await asyncio.sleep(1.5)
            
            print("--- Nhấn ENTER lần cuối để gửi ---")
            await page.keyboard.press("Enter")
            
            print("✅ HOÀN THÀNH: Lệnh đã được gửi đi!")
            # Chụp ảnh lại để bạn xem kết quả trong Artifact nếu cần
            await page.screenshot(path="test_result.png")
            
        except Exception as e:
            print(f"❌ LỖI TRONG QUÁ TRÌNH TEST: {e}")
        finally:
            await browser.close()
            print("--- Đã đóng trình duyệt ---")

if __name__ == "__main__":
    asyncio.run(run())
