import os
from PIL import Image


def crop_image_by_bbox(image_path: str, bbox: dict, output_path: str) -> str:
  """Crops an image based on bounding box coordinates: bbox = {"x": 100, "y": 150, "w": 200, "h": 100}"""
  if not os.path.exists(image_path):
    raise FileNotFoundError(f"Image not found at: {image_path}")

  with Image.open(image_path) as img:
    left = bbox["x"]
    top = bbox["y"]
    right = bbox["x"] + bbox["w"]
    bottom = bbox["y"] + bbox["h"]

    cropped_img = img.crop((left, top, right, bottom))
    cropped_img.save(output_path)
  return output_path