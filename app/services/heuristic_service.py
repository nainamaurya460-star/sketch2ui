def extract_geometry_features(x: int, y: int, w: int, h: int) -> dict:
    """Extracts geometric features from bounding box dimensions."""
    # 1. Bounding box area (w * h)
    area = w * h

    # 2. Aspect ratio (w / h)
    aspect_ratio = float(w) / h if h > 0 else 0.0

     # 3. Center Point Coordinates
    center_x = x +( w // 2)
    center_y = y + (h // 2)

    return {
        "box": [x, y, w, h],
        "area": area,
        "aspect_ratio":  round(aspect_ratio, 2),
        "center": (center_x, center_y)
        
    }