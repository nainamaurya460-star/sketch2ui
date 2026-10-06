import sys
import os

sys.path.insert(0, os.path.abspath('.'))

import cv2
import numpy as np
from app.services.camera_services import detect_paper_and_warp
from app.services.cv_engine import preprocess_sketch
from app.services.contour_services import extract_contours

print('--- Testing Full End-to-End Vision Pipeline ---')

# 1. Ek dummy frame banate hain jisme skewed paper aur uske andar drawn boxes hain
frame = np.zeros((600, 800, 3), dtype=np.uint8)

# Paper Polygon
paper_pts = np.array([[100, 80], [700, 120], [650, 540], [80, 500]], np.int32)
cv2.fillPoly(frame, [paper_pts], (255, 255, 255))

# Paper ke upar drawn buttons / text blocks (black color lines)
cv2.rectangle(frame, (200, 180), (350, 240), (0, 0, 0), 2)
cv2.rectangle(frame, (200, 270), (550, 320), (0, 0, 0), 2)

# Step A: Document Warp
warped_img, detected = detect_paper_and_warp(frame)
print(f'1. Paper Detection: {detected}')
assert detected is True, 'Paper detection fail ho gaya!'

# Step B: Preprocess & Thresholding
binary_mask = preprocess_sketch(warped_img)
print(f'2. CV Engine Thresholding Output Shape: {binary_mask.shape}')

# Step C: Extract Contours
boxes = extract_contours(binary_mask)
print(f'3. Extracted UI Component Boxes: {len(boxes)}')
for idx, b in enumerate(boxes):
    print(f'   Box {idx+1}: {b}')

print('--- PIPELINE TEST PASSED SUCCESSFULLY! ---')
