import cv2
import numpy as np
from app.services.contour_services import extract_contours

# Fake test image bana rahe hain (White canvas par 2 black boxes)
test_image = np.ones((400, 400, 3), dtype=np.uint8) * 255
cv2.rectangle(test_image, (50, 50), (200, 150), (0, 0, 0), 2)
cv2.rectangle(test_image, (50, 200), (350, 260), (0, 0, 0), 2)

# Contour Logic Test
boxes = extract_contours(test_image)

print("✅ Detected Bounding Boxes:")
for i, box in enumerate(boxes, 1):
    print(f"Shape {i}: {box}")