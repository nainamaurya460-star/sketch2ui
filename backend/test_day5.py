import sys
import os

# Python path set kar rahe hain
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from app.services.contour_services import load_image, extract_contours
from app.schemas.prediction import predict_ui_element

# 1. Image load kar rahe hain
img = load_image(r"C:\Users\Lenovo\Documents\Asketch2UI\backend\test_images\sketches.png")

# 2. Bounding boxes extract kar rahe hain
boxes = extract_contours(img)

# 3. Components classify kar rahe hain (singular function name)
components = predict_ui_element(boxes)

# 4. Result print kar rahe hain
print("--- Day 5 Classification Results ---")
print(f"Total Components Identified: {len(components)}\n")

for i, comp in enumerate(components[:5], 1):
    print(f"Component {i}: {comp}")