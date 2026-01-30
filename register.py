# ... (Giữ nguyên các hàm create_temp_email và get_otp_from_mail_tm) ...

async def main():
    ref_code = sys.argv[1] if len(sys.argv) > 1 else "vsagwtjq63"
    email, mail_token = create_temp_email()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(**p.devices['iPhone 13'])
        page = await context.new_page()
        
        try:
            # Bước 1: Vừa vào trang là chụp ảnh ngay (Ảnh khởi tạo)
            await page.goto(f"https://www.vsphone.com/invite/{ref_code}", timeout=100000, wait_until="commit")
            await asyncio.sleep(5)
            await page.screenshot(path="ketqua.png") 
            print("--- Đã chụp ảnh khởi tạo trang ---")

            # Bước 2: Điền thông tin
            await page.locator('input').nth(0).fill(email)
            await page.get_by_text("Get code").click()
            await asyncio.sleep(3)
            
            # Bước 3: Chụp ảnh Captcha để xem
            await page.screenshot(path="ketqua.png") 
            
            # Giải captcha và điền nốt... (như bản cũ)
            await solve_puzzle_captcha(page)
            
            otp = get_otp_from_mail_tm(mail_token)
            if otp:
                await page.locator('input').nth(1).fill(otp)
                await page.locator('input').nth(2).fill("Password99@")
                await page.click('button:has-text("Register")')
                await asyncio.sleep(5)
                await page.screenshot(path="ketqua.png")

        except Exception as e:
            print(f"Lỗi thực thi: {e}")
        finally:
            # ĐẢM BẢO LUÔN CHỤP ẢNH CUỐI CÙNG TRƯỚC KHI ĐÓNG
            await page.screenshot(path="ketqua.png")
            await browser.close()
