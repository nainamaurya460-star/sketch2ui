import cv2
import numpy as np

def process_sketch(image_path):
    # Image read karein
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Image not found at {image_path}")
        return None

    # 1. Grayscale Conversion
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2. Gaussian Blur (Noise hatane ke liye)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 3. Adaptive Thresholding (Shadow aur low-light fix karne ke liye)
    processed = cv2.adaptiveThreshold(
        blurred, 
        255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 
        11, 
        2
    )

    return processed

if __name__ == "__main__":
    # Test sample par test run
    sample_path = "test_samples/sample_shadow.jpg"
    result = process_sketch(sample_path)
    if result is not None:
        cv2.imwrite("test_samples/processed_output.jpg", result)
        print("Success: Adaptive thresholding output saved to 'test_samples/processed_output.jpg'!")