import base64
import cv2
import numpy as np

def decode_base64_image(base64_string: str) -> np.ndarray:
    """
    Live Webcam se aayi Base64 image string ko decode karke 
    OpenCV Image Array (NumPy) me convert karta hai.
    """
    if "," in base64_string:
        base64_string = base64_string.split(",")[1]
        
    image_bytes = base64.b64decode(base64_string)
    np_array = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    
    return image


def read_uploaded_file(file_bytes: bytes) -> np.ndarray:
    """
    FastAPI File Upload se aayi byte stream ko 
    OpenCV image array me read karta hai.
    """
    np_array = np.frombuffer(file_bytes, np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    return image