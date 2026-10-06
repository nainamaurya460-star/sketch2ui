import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, 'app'))

from app.services.heuristic_service import predict_ui_element

test_boxes = [
    [10, 10, 200, 50],   # button
    [10, 70, 300, 40],   # text/input
    [10, 120, 400, 350], # card
    [10, 480, 250, 20],  # text
    [1, 1, 2, 2]         # noise
]

print("--- Day 3 Advanced Heuristics Test ---")
predictions = predict_ui_element(test_boxes)

for i, pred in enumerate(predictions, 1):
    print(f"{i}. Label: {pred['label']} | Box: {pred['box']} | AR: {pred['features']['aspect_ratio']}")