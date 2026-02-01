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
            # Truy cập trang chủ để nạp Token trước
            print("--- Đang nạp Token ---")
            await page.goto("https://discord.com/app")
            await page.evaluate(f"localStorage.setItem('token', '\"{token}\"');")
            await asyncio.sleep(2)

            # Truy cập thẳng vào kênh chat
            url = f"https://discord.com/channels/@me/{channel_id}"
            print(f"--- Đang truy cập: {url} ---")
            await page.goto(url, wait_until="networkidle")
            
            # Đợi thêm một chút cho Slate Editor load
            print("--- Đang tìm ô chat (Slate Editor)... ---")
            # Thay đổi selector linh hoạt hơn
            selector = '[data-slate-editor="true"], [role="textbox"]'
            try:
                await page.wait_for_selector(selector, timeout=60000) # Tăng lên 60s
            except:
                print("⚠️ Không tìm thấy selector chuẩn, thử chụp ảnh màn hình lỗi...")
                await page.screenshot(path="error_layout.png")
                raise Exception("Không tìm thấy ô nhập liệu sau 60 giây.")

            chat_input = page.locator(selector).first
            await chat_input.click()
            await asyncio.sleep(1)
            
            print("--- Đang gõ /bot ---")
            await chat_input.type("/bot", delay=200)
            
            await asyncio.sleep(4) 
            print("--- Chọn lệnh (Tab) ---")
            await page.keyboard.press("Tab")
            await asyncio.sleep(2)
            
            print("--- Gửi (Enter) ---")
            await page.keyboard.press("Enter")
            print("✅ THÀNH CÔNG!")
            
        except Exception as e:
            print(f"❌ LỖI: {e}")
            await page.screenshot(path="ketqua.png")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
