import sys
import os

# Relative path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, 'app'))

from app.services.contour_services import load_image, extract_contours
from app.services.heuristic_service import predict_ui_element

# 1. Image load kar rahe hain using relative path
img_path = os.path.join(BASE_DIR, "backend", "test_images", "sketches.png")
img = load_image(img_path)

# 2. Bounding boxes extract kar rahe hain
boxes = extract_contours(img)

# 3. Components classify kar rahe hain
components = predict_ui_element(boxes)

# 4. Result print kar rahe hain
print("--- Day 5 Classification Results ---")
print(f"Total Components Identified: {len(components)}\n")

for i, comp in enumerate(components[:5], 1):
    print(f"Component {i}: {comp}")s