import asyncio
import os
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        print("--- Khởi tạo trình duyệt ---")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        token = os.getenv("DISCORD_TOKEN")
        channel_id = "1464219586386722816"

        try:
            # 1. Truy cập trang login để khởi tạo môi trường
            print("--- Truy cập Discord để nạp môi trường ---")
            await page.goto("https://discord.com/login", wait_until="networkidle")
            
            # 2. Nạp Token với hàm kiểm tra an toàn
            print("--- Đang thực hiện nạp Token ---")
            await page.evaluate(f"""
                (token) => {{
                    function setToken(t) {{
                        localStorage.setItem('token', '"{token}"');
                    }}
                    // Thử nạp ngay lập tức
                    try {{
                        setToken(token);
                    }} catch (e) {{
                        console.error("Chưa nạp được ngay, đang thử lại...");
                    }}
                }}
            """, token)
            
            await asyncio.sleep(2)

            # 3. Chuyển hướng đến kênh chat
            print(f"--- Đang vào kênh: {channel_id} ---")
            await page.goto(f"https://discord.com/channels/@me/{channel_id}", wait_until="networkidle")
            
            # 4. Tìm ô chat và gửi lệnh
            print("--- Đang tìm ô chat... ---")
            # Danh sách các selector có thể có của Discord
            selectors = ['[data-slate-editor="true"]', '[role="textbox"]', '.slateTextArea_ec4baf']
            
            chat_input = None
            for s in selectors:
                try:
                    await page.wait_for_selector(s, timeout=15000)
                    chat_input = page.locator(s).first
                    if chat_input: break
                except: continue

            if not chat_input:
                raise Exception("Không tìm thấy ô nhập liệu! Discord có thể đã thay đổi giao diện hoặc bắt Captcha.")

            await chat_input.click()
            await chat_input.type("/bot", delay=200)
            
            print("--- Đợi menu & Gửi (Tab + Enter) ---")
            await asyncio.sleep(5) # Đợi menu Slash hiện ra
            await page.keyboard.press("Tab")
            await asyncio.sleep(1)
            await page.keyboard.press("Enter")
            
            print("✅ THÀNH CÔNG: Lệnh đã được gửi!")
            
        except Exception as e:
            print(f"❌ LỖI: {e}")
            await page.screenshot(path="loi_debug.png")
        finally:
            await browser.close()
            print("--- Đã đóng trình duyệt ---")

if __name__ == "__main__":
    asyncio.run(run())
