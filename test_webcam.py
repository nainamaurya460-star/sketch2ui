import sys
import os

sys.path.insert(0, os.path.abspath('.'))

import cv2
import numpy as np
from app.services.camera_services import detect_paper_and_warp

print('--- Testing Paper Scanner Service ---')

frame = np.zeros((600, 800, 3), dtype=np.uint8)
pts = np.array([[150, 100], [650, 140], [600, 520], [120, 480]], np.int32)
cv2.fillPoly(frame, [pts], (255, 255, 255))

warped_img, detected = detect_paper_and_warp(frame)

print(f'Paper Detected: {detected}')
print(f'Original Frame Shape: {frame.shape}')
print(f'Warped Output Shape: {warped_img.shape}')

assert detected is True, 'Paper detection failed!'
assert warped_img.shape[0] > 0 and warped_img.shape[1] > 0, 'Invalid warp output!'

print('--- TEST PASSED: Camera Service working properly! ---')
