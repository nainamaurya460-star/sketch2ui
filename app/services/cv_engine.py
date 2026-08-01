import cv2
import numpy as np

def preprocess_sketch(image: np.ndarray) -> np.ndarray:
    """
    Applies Gaussian Blur and Adaptive Gaussian Thresholding to remove 
    shadows and clean low-light sketch images.
    Input: np.ndarray (Image in memory)
    Output: np.ndarray (Processed binary image)
    """
    if image is None:
        raise ValueError("Input image array is None")

    # 1. Convert to Grayscale (if image is BGR)
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # 2. Gaussian Blur (Noise reduction)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 3. Adaptive Thresholding (Shadow and lighting fix)
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
    # Test block: Testing purpose only
    test_img = cv2.imread("test_samples/sample_shadow.jpg")
    if test_img is not None:
        result = preprocess_sketch(test_img)
        cv2.imwrite("test_samples/processed_output.jpg", result)
        print("Success: Refactored preprocess_sketch executed successfully!")