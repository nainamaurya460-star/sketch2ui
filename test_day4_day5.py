import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, 'app'))

from app.services.heuristic_service import process_ui_pipeline

# Mock Bounding Boxes from CV engine parsing
sample_boxes = [
    [20, 30, 250, 60],   # Button
    [20, 100, 320, 45],  # Input / Text
    [20, 160, 420, 300], # Card
    [2, 2, 3, 3]         # Noise (Filtered out)
]

print("--- Testing Day 4 & Day 5 Combined Pipeline ---")
result = process_ui_pipeline(sample_boxes)

print(f"Status: {result['status']}")
print(f"Detected Elements: {result['total_elements']}\n")

for item in result['predictions']:
    print(f"ID: {item['id']} | Label: {item['label']} | Box: {item['box']}")