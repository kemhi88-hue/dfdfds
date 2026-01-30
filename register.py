import cv2
import numpy as np

async def get_puzzle_distance(page):
    """Sử dụng OpenCV để tính toán khoảng cách cần kéo"""
    # 1. Chụp ảnh captcha thực tế từ màn hình
    captcha_box = await page.locator('.captcha-main-image').bounding_box() # Selector có thể thay đổi tùy giao diện
    await page.locator('.captcha-main-image').screenshot(path="background.png")
    await page.locator('.captcha-slice-image').screenshot(path="slice.png")

    # 2. Đọc ảnh bằng OpenCV
    bg_img = cv2.imread("background.png", 0) # Chuyển ảnh xám
    slice_img = cv2.imread("slice.png", 0)

    # 3. Tìm vị trí khớp nhất
    res = cv2.matchTemplate(bg_img, slice_img, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    # Tọa độ X của điểm khớp chính là khoảng cách cần kéo
    distance = max_loc[0] 
    return distance

async def solve_puzzle_captcha(page):
    try:
        print("--- AI đang phân tích vị trí mảnh ghép... ---")
        distance = await get_puzzle_distance(page)
        
        slider = page.locator('.van-slider__button').first
        box = await slider.bounding_box()
        start_x = box['x'] + box['width'] / 2
        start_y = box['y'] + box['height'] / 2

        # Kéo với khoảng cách AI vừa tìm được
        await page.mouse.move(start_x, start_y)
        await page.mouse.down()
        # Thêm một chút dao động ngẫu nhiên để giống người thật
        await page.mouse.move(start_x + distance + 5, start_y, steps=20)
        await asyncio.sleep(0.2)
        await page.mouse.move(start_x + distance, start_y, steps=10)
        await page.mouse.up()
        print(f"--- AI đã kéo thành công: {distance}px ---")
    except Exception as e:
        print(f"Lỗi AI: {e}")
