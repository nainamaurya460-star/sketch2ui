import os
import cv2
import numpy as np

# Folder auto create hoga
os.makedirs("test_samples", exist_ok=True)

# Fake sketch base image
height, width = 600, 800
base_img = np.ones((height, width, 3), dtype=np.uint8) * 255

# UI Layout Lines
cv2.rectangle(base_img, (100, 100), (700, 500), (50, 50, 50), 3)
cv2.rectangle(base_img, (150, 150), (650, 220), (80, 80, 80), 2)
cv2.rectangle(base_img, (150, 260), (350, 320), (30, 30, 30), 2)
cv2.rectangle(base_img, (450, 260), (650, 320), (30, 30, 30), 2)

# 1. Bright Image
cv2.imwrite("test_samples/sample_bright.jpg", base_img)

# 2. Low Light Image
low_light_img = (base_img * 0.4).astype(np.uint8)
cv2.imwrite("test_samples/sample_lowlight.jpg", low_light_img)

# 3. Shadow Image
shadow_img = base_img.copy().astype(np.float32)
shadow_mask = np.ones((height, width), dtype=np.float32)
shadow_mask[150:450, 200:600] = 0.5 
shadow_img = shadow_img * shadow_mask[:, :, np.newaxis]
cv2.imwrite("test_samples/sample_shadow.jpg", shadow_img.astype(np.uint8))

print("Done! Teeno images test_samples folder me ban gayi hain.")