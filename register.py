import asyncio
import sys
import re
import requests
import time
from playwright.async_api import async_playwright

# --- HÀM HỖ TRỢ MAIL.TM (MIỄN PHÍ) ---
def create_temp_email():
    """Tạo một tài khoản email ngẫu nhiên trên Mail.tm"""
    try:
        # Lấy domain khả dụng
        domain_res = requests.get("https://api.mail.tm/domains").json()
        domain = domain_res['hydra:member'][0]['domain']
        
        # Tạo user ngẫu nhiên
        user = f"user_{int(time.time())}"
        email = f"{user}@{domain}"
        password = "Password123"
        
        # Đăng ký tài khoản email
        res = requests.post("https://api.mail.tm/accounts", json={"address": email, "password": password})
        if res.status_code == 201:
            # Đăng nhập để lấy Token
            token_res = requests.post("https://api.mail.tm/token", json={"address": email, "password": password}).json()
            return email, token_res['token']
    except Exception as e:
        print(f"Lỗi tạo mail: {e}")
    return None, None

def get_otp_from_mail_tm(token):
    """Đợi và lấy mã OTP từ hộp thư Mail.tm"""
    headers = {"Authorization": f"Bearer {token}"}
    print("--- Đang đợi OTP từ Mail.tm (tối đa 60s)... ---")
    
    for _ in range(12):
        time.sleep(5)
        try:
            msgs = requests.get("https://api.mail.tm/messages", headers=headers).json()
            if msgs['hydra:member']:
                msg_id = msgs['hydra:member'][0]['@id']
                # Lấy nội dung chi tiết thư
                content = requests.get(f"https://api.mail.tm{msg_id}", headers=headers).json()
                body = content.get('text', '') or content.get('intro', '')
                # Tìm mã 6 chữ số
                otp = re.findall(r'\b\d{6}\b', body)
                if otp: return otp[0]
        except: pass
    return None

# --- LUỒNG CHÍNH ---
async def main():
    # Lấy ref_code từ tham số dòng lệnh (ví dụ: vsagwtjq63)
    ref_code = sys.argv[3] if len(sys.argv) > 3 else "default_ref"
    password_acc = "Huhu1211@" # Mật khẩu cho tài khoản VSPhone mới

    # Bước 1: Tạo Email ảo
    email, token = create_temp_email()
    if not email:
        print("Không thể tạo email ảo. Dừng lại.")
        return
    print(f"--- Đã tạo Email thành công: {email} ---")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Giả lập thiết bị để tránh bị chặn IP
        context = await browser.new_context(**p.devices['iPhone 13'])
        page = await context.new_page()
        
        try:
            target_url = f"https://www.vsphone.com/invite/{ref_code}"
            print(f"--- Truy cập link: {target_url} ---")
            await page.goto(target_url, timeout=60000)
            await asyncio.sleep(5)

            # Điền Email
            await page.locator('input[placeholder*="email"]').first.fill(email)
            
            # Bấm "Get code"
            get_code_btn = page.get_by_text("Get code")
            await get_code_btn.click()
            print("--- Đã bấm Get code. Đang check hộp thư... ---")
            
            # Bước 2: Lấy OTP
            otp_code = get_otp_from_mail_tm(token)
            if otp_code:
                print(f"--- Lấy được OTP: {otp_code}. Đang nhập... ---")
                # Điền mã OTP vào ô thứ 2
                await page.locator('input[placeholder*="verification"]').first.fill(otp_code)
                
                # Điền Mật khẩu vào ô thứ 3
                await page.locator('input[type="password"]').first.fill(password_acc)
                
                # Bấm Register
                await page.click('button:has-text("Register")')
                print("--- Đã nhấn Register! Đang kiểm tra kết quả... ---")
                await asyncio.sleep(5)
            else:
                print("--- Quá thời gian chờ OTP. ---")

            # Chụp ảnh kết quả cuối cùng
            await page.screenshot(path="ketqua.png")
            # Lưu lại thông tin tài khoản để bạn biết
            with open("accounts.txt", "a") as f:
                f.write(f"Email: {email} | Pass: {password_acc}\n")

        except Exception as e:
            print(f"Lỗi: {e}")
            await page.screenshot(path="ketqua.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
