import numpy as np
import cv2
import os
from pathlib import Path

def load_image(image_path: str):
    path_obj = Path(image_path).resolve()
    
    # Check 1: File exist karti hai ya nahi
    if not path_obj.is_file():
        raise FileNotFoundError(f"File nahi mili: {path_obj}")
    
    # Check 2: OpenCV se load karo
    image = cv2.imread(str(path_obj))
    
    # Agar OpenCV read nahi kar pata (path issue in Windows):
    if image is None:
        # Fallback reading method for Windows paths
        image = cv2.imdecode(np.fromfile(str(path_obj), dtype=np.uint8), cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError(f"Image corrupt hai ya format Read nahi ho raha: {path_obj}")
        
    return image
def extract_contours(image: np.ndarray):
    """Image me se shapes detect karke bounding boxes nikalta hai"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    bounding_boxes = []
    for cnt in contours:
        if cv2.contourArea(cnt) > 100:
            x, y, w, h = cv2.boundingRect(cnt)
            bounding_boxes.append({"x": int(x), "y": int(y), "width": int(w), "height": int(h)})
            
    return bounding_boxes