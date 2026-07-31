from email.mime import image

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
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    bounding_boxes = []
    for cnt in contours:
        if cv2.contourArea(cnt) > 100:
            x, y, w, h = cv2.boundingRect(cnt)
            bounding_boxes.append({"x": int(x), "y": int(y), "width": int(w), "height": int(h)})
            
    return bounding_boxes

def clean_and_blur_image(image_path:str):
    """Image ko read kro(Grayscale mode me)"""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"Image load nahi ho rahi: {image_path}")
        return None
    """Gaussian blur apply karna"""
    #(5,5) kernel size ke saath, jitna bda number utna zyada blur hoga
    blurred_img = cv2.GaussianBlur(img, (5, 5), 0)
    binary = cv2.adaptiveThreshold(blurred_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return binary
def extract_contours(image: np.ndarray):
    """Image me se shapes detect karke filtered bounding boxes nikalta hai"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    bounding_boxes = []
    for cnt in contours:
        if cv2.contourArea(cnt) > 100:
            x, y, w, h = cv2.boundingRect(cnt)
            bounding_boxes.append({"x": int(x), "y": int(y), "width": int(w), "height": int(h)})
            
    return bounding_boxes
def extract_contours(image: np.ndarray):
    """Image me se shapes detect karke filtered bounding boxes nikalta hai"""
    if len(image.shape) == 3:  # Agar image color hai
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    #Noise reduction & thresholding( Day 3 logic)
    
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    # hierarchy-based contour extraction(RETR_TREE)
    contours, hierarchy = cv2.findContours( thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    bounding_boxes = []
    img_h, img_w = image.shape[:2]
    max_allowed_area = (img_h * img_w) * 0.9  # 90% of the image area ignorance
    for cnt in contours:
        area = cv2.contourArea(cnt)
        x, y, w, h = cv2.boundingRect(cnt)
        """ Filtering . 1: Minimum size constraint: width & height > 15px, area > 100px. 2: Maximum size constraint: area < 90% of the image area. 3: Aspect ratio constraint: width/height between 0.2 and 5.0 """
        if 100 < area < max_allowed_area and w > 15 and h > 15:
         bounding_boxes.append({"x": int(x), "y": int(y), "width": int(w), "height": int(h)})
           
    return bounding_boxes