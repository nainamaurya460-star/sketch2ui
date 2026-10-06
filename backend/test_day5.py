import sys
import os

# Relative path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from app.services.contour_services import load_image, extract_contours
from app.services.heuristic_service import predict_ui_element

# Image path check (backend folder aur root folder dono jagah check karega)
candidate_paths = [
    os.path.join(BASE_DIR, "test_images", "sketches.png"),
    os.path.join(BASE_DIR, "backend", "test_images", "sketches.png"),
]

img_path = None
for p in candidate_paths:
    if os.path.exists(p):
        img_path = p
        break

if not img_path:
    print("❌ Error: 'sketches.png' file nahi mili! Kindly check file path in test_images/ folder.")
    sys.exit(1)

print(f"✅ Loading image from: {img_path}")

# 1. Image load kar rahe hain
img = load_image(img_path)

# 2. Bounding boxes extract kar rahe hain
boxes = extract_contours(img)

# 3. Components classify kar rahe hain
components = predict_ui_element(boxes)

# 4. Result print kar rahe hain
print("\n--- Day 5 Classification Results ---")
print(f"Total Components Identified: {len(components)}\n")

for i, comp in enumerate(components[:5], 1):
    print(f"Component {i}: {comp}")