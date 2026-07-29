import cv2
import numpy as np

def preprocess_sketch(image: np.ndarray) -> np.ndarray:
    """
    Raw paper sketch par OpenCV operations apply karta hai:
    1. Grayscale Conversion
    2. Gaussian Blur Noise Reduction
    3. Adaptive Binarization (Pure Black/White separation)
    """
    # 1. Grayscale me convert karo
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 2. Pencil texture aur shadows smooth karne ke liye Gaussian Blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # 3. Adaptive Thresholding (Paper background ko clear white, lines ko clear black karega)
    binary = cv2.adaptiveThreshold(
        blurred, 
        255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 
        11, 
        2
    )
    
    return binary