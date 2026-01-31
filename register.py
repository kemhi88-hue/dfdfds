import asyncio
import sys
import time
import base64
import requests

from playwright.async_api import async_playwright
from playwright_stealth import stealth


# ================== GIẢI CAPTCHA TIKTOK (KKTOOL) ==================
def solve_tiktok_captcha(image_path: str):
    """
    Gửi ảnh puzzle lên web_tinh_kktool (KKTool)
    Trả về khoảng kéo slider (px) hoặc None
    """
    try:
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()

        res = requests.post(
            "https://kktool.dacohacotool.workers.dev/tiktok/puzzel",
            json={"base64_image": img_b64},
            timeout=20
        ).json()

        if res.get("success"):
            return int(res.get("result"))
    except Exception as e:
        print("⚠️ Lỗi solve captcha:", e)

    return None


# ================== MAIN ==================
async def main():
    # Ref truyền vào: python register.py xxx xxx REF
    ref = sys.argv[3] if len(sys.argv) > 3 else "vsagwtjq63"
    print("🔗 Ref sử dụng:", ref)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ]
        )

        context = await browser.new_context(
            **p.devices["iPhone 12"],
            locale="en-US"
        )

        page = await context.new_page()

        # ---- STEALTH ----
        await stealth(page)

        try:
            print("🌍 Truy cập link invite...")
            await page.goto(
                f"https://www.vsphone.com/invite/{ref}",
                wait_until="networkidle",
                timeout=60000
            )

            # ---- EMAIL ----
            email_input = page.locator(
                'input[type="text"], input[placeholder*="mail"], input[placeholder*="Email"]'
            ).first

            await email_input.wait_for(state="visible", timeout=20000)

            email = f"vsp_{int(time.time())}@gmail.com"
            await email_input.fill(email)
            print("📧 Email:", email)

            await page.get_by_text("Get code").click()
            await asyncio.sleep(3)

            # ---- CAPTCHA ----
            captcha_img = page.locator(
                ".captcha-main-img, #captcha-verify-image, img[src*='captcha']"
            ).first

            if await captcha_img.is_visible():
                print("🧩 Phát hiện captcha")
                await captcha_img.screenshot(path="cap.png")

                dist = solve_tiktok_captcha("cap.png")
                print("➡️ Khoảng kéo:", dist)

                if dist:
                    slider = page.locator(
                        ".van-slider__button, .page-slide-btn, .secsdk-captcha-drag-icon"
                    ).first

                    box = await slider.bounding_box()
                    if box:
                        sx = box["x"] + box["width"] / 2
                        sy = box["y"] + box["height"] / 2

                        await page.mouse.move(sx, sy)
                        await page.mouse.down()
                        await page.mouse.move(sx + dist, sy, steps=35)
                        await page.mouse.up()

                        print("✅ Đã kéo captcha")
                        await asyncio.sleep(3)

            await page.screenshot(path="result.png")
            print("🎉 Hoàn tất")

        except Exception as e:
            print("❌ Lỗi:", e)
            await page.screenshot(path="error.png")

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
