import cv2
import numpy as np
import base64

def crop_bounding_box(image: np.ndarray, x: int, y: int, w: int, h: int) -> np.ndarray:
    """
    Original NumPy image matrix me se bounding box coordinates (X, Y, W, H)
    ko safe slicing ke dwara crop karke return karta hai.
    
    :param image: Original OpenCV image array (BGR/Grayscale)
    :param x: Top-Left X coordinate
    :param y: Top-Left Y coordinate
    :param w: Width of the bounding box
    :param h: Height of the bounding box
    :return: Cropped image section (Region of Interest - ROI)
    """
    # 1. Image ki actual height aur width nikalo
    img_h, img_w = image.shape[:2]
    
    # 2. Out-of-bounds array slicing se bachne ke liye safe boundaries calculate karo
    x1 = max(0, x)
    y1 = max(0, y)
    x2 = min(img_w, x + w)
    y2 = min(img_h, y + h)
    
    # 3. NumPy Matrix Slicing [Y_start:Y_end, X_start:X_end]
    cropped_roi = image[y1:y2, x1:x2]
    
    return cropped_roi


def crop_to_base64(image: np.ndarray, x: int, y: int, w: int, h: int) -> str:
    """
    Bounding box ko crop karke direct Base64 string return karta hai,
    taaki frontend/Vision AI ko direct JSON me bheja ja sake.
    """
    cropped_img = crop_bounding_box(image, x, y, w, h)
    
    # Check if cropped image is valid & not empty
    if cropped_img.size == 0:
        return ""
        
    # Image ko memory me PNG format me encode karo
    _, buffer = cv2.imencode('.png', cropped_img)
    
    # Base64 string conversion
    base64_str = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/png;base64,{base64_str}"