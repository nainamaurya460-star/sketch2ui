import cv2
import numpy as np
from pathlib import Path


def load_image(image_path: str):
    path_obj = Path(image_path).resolve()

    # Check 1: File exist karti hai ya nahi
    if not path_obj.is_file():
        raise FileNotFoundError(f"File nahi mili: {path_obj}")

    # Check 2: OpenCV se load karo
    image = cv2.imread(str(path_obj))

    # Fallback reading method for Windows paths
    if image is None:
        image = cv2.imdecode(np.fromfile(str(path_obj), dtype=np.uint8), cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError(f"Image corrupt hai ya format Read nahi ho raha: {path_obj}")

    return image


def extract_contours(image: np.ndarray):
    """
    Image me se shapes detect karke filtered bounding boxes nikalta hai (Day 4 Optimization)
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # Noise reduction & thresholding
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )

    # Hierarchy-based contour extraction (RETR_TREE)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    bounding_boxes = []
    img_h, img_w = image.shape[:2]
    max_allowed_area = (img_h * img_w) * 0.95

    for cnt in contours:
        area = cv2.contourArea(cnt)
        x, y, w, h = cv2.boundingRect(cnt)

        # Filtering Rules
        if 100 < area < max_allowed_area and w > 15 and h > 15:
            bounding_boxes.append({
                "x": int(x),
                "y": int(y),
                "width": int(w),
                "height": int(h)
            })

    return bounding_boxes