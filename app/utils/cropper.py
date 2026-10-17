"""
Utility module for cropping sub-regions of sketches based on bounding boxes.
"""
from typing import Dict, List, Union
import numpy as np


def crop_component(image: np.ndarray, bbox: Union[Dict[str, int], List[int]]) -> np.ndarray:
    """
    Crops a sub-region from an image given a bounding box.
    Accepts:
      - dict: {'x': ..., 'y': ..., 'width': ..., 'height': ...}
      - list/tuple: [x, y, w, h]
    """
    if image is None:
        raise ValueError("Image cannot be None")

    img_h, img_w = image.shape[:2]

    if isinstance(bbox, dict):
        x = bbox.get("x", 0)
        y = bbox.get("y", 0)
        w = bbox.get("width", bbox.get("w", 0))
        h = bbox.get("height", bbox.get("h", 0))
    elif isinstance(bbox, (list, tuple)) and len(bbox) == 4:
        x, y, w, h = bbox
    else:
        raise ValueError(f"Invalid bounding box format: {bbox}")

    x1 = max(0, int(x))
    y1 = max(0, int(y))
    x2 = min(img_w, int(x + w))
    y2 = min(img_h, int(y + h))

    if x2 <= x1 or y2 <= y1:
        return np.zeros((0, 0, image.shape[2] if len(image.shape) > 2 else 1), dtype=image.dtype)

    return image[y1:y2, x1:x2].copy()
