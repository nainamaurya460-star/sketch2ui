def classify_component(box: dict) -> str:
    """
    Bounding box dictionary{'x','y','width','height'} ke basis par UI element type predict karta hai.
    """
    # Example classification logic based on bounding box dimensions
    w = box["width"]
    h = box["height"]
    area = w * h
    aspect_ratio = float(w)/ h if h > 0 else 0.0
    # Rule 1: Checknox / Radio Button / Small Icon
    if 15 <= w <= 45 and 15 <= h <= 45 and 0.8 <= aspect_ratio <= 1.2:
        return "Checkbox / Radio Button / Small Icon"
    # Rule 2: Input text field (wide and slender)
    elif aspect_ratio > 4.0 and h <= 60:
        return "input_field"
    # Rule 3: Button ( medium width and compact height)
    elif 1.5 <= aspect_ratio <= 4.0 and 25 <= h <= 70:
        return "button"
    # Rule 4: Image (large area and balanced aspect ratio)
    elif area > 15000:
        return "Card"
    else:
        return "Container"

def predict_ui_element(bounding_box: list) -> list:
    """
    Har Bounding box ke sath classification label attach karta hai. 
    """
    classified_components = []
    for box in bounding_box:
       label = classify_component(box)
       component = {"label": label, "x": box["x"], "y": box["y"], "width": box["width"], "height": box["height"]}
       classified_components.append(component)
    return classified_components