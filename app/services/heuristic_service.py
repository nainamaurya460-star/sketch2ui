"""
Phase 2 - Day 3: Advanced Heuristic Rules Engine
Location: app/services/heuristic_service.py
"""

def extract_geometry_features(x: int, y: int, w: int, h: int) -> dict:
    """Extracts extended geometric properties from bounding box."""
    area = w * h
    perimeter = 2 * (w + h)
    aspect_ratio = float(w) / h if h > 0 else 0.0
    center_x = x + (w // 2)
    center_y = y + (h // 2)

    return {
        "box": [x, y, w, h],
        "area": area,
        "perimeter": perimeter,
        "aspect_ratio": round(aspect_ratio, 2),
        "center": (center_x, center_y)
    }

def classify_component(w: int, h: int) -> str:
    """
    Day 3 Advanced Heuristic Rules:
    Categorizes contours into UI elements based on shape & aspect ratio thresholds.
    """
    area = w * h
    aspect_ratio = float(w) / h if h > 0 else 0.0

    # Filter noise
    if area < 100 or w < 5 or h < 5:
        return "noise"

    # Shape Rules
    if aspect_ratio > 4.0 and h < 45:
        return "text"
    elif 0.6 <= aspect_ratio <= 1.4 and area >= 10000:
        return "card"
    elif 1.5 <= aspect_ratio <= 5.0 and 1000 <= area < 10000:
        return "button"
    else:
        return "container"

def predict_ui_element(boxes: list) -> list:
    """
    Batch processes bounding boxes and returns classified predictions.
    """
    predictions = []
    for box in boxes:
        if len(box) == 4:
            x, y, w, h = box
            features = extract_geometry_features(x, y, w, h)
            label = classify_component(w, h)
            
            # Print for debug
            if label and str(label).lower() != "noise":
                predictions.append({
                    "label": label,
                    "confidence": 0.88,
                    "box": [x, y, w, h],
                    "features": features
                })
    return predictions
"""
Phase 2 - Day 4 & Day 5: ML Pipeline Integration & JSON Response Generation
"""
from app.services.heuristic_service import extract_geometry_features, classify_component

def process_ui_pipeline(bounding_boxes: list) -> dict:
    """
    Day 4 & Day 5 Integration:
    Processes raw boxes, extracts geometry, applies heuristic rules,
    and returns a clean, structured JSON format for Day 6 API/Frontend.
    """
    elements = []
    
    for idx, box in enumerate(bounding_boxes, 1):
        if len(box) == 4:
            x, y, w, h = box
            features = extract_geometry_features(x, y, w, h)
            label = classify_component(w, h)
            
            # Day 4: Noise Filtering
            if label and str(label).lower() != "noise":
                elements.append({
                    "id": f"elem_{idx}",
                    "label": label,
                    "confidence": 0.92,
                    "box": {"x": x, "y": y, "width": w, "height": h},
                    "features": features
                })

    # Day 5: Structured Final JSON Output
    return {
        "status": "success",
        "total_elements": len(elements),
        "predictions": elements
    }