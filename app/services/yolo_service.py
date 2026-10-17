# backend/app/services/yolo_service.py
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from ultralytics import YOLO
import cv2
import numpy as np

# 1. Dynamic Absolute Pathing: Server kisi bhi directory se chale, file path hamesha correct rahega
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_MODEL_PATH = str(BASE_DIR / "models" / "best.pt")

COLOR_MAP = {
    "heading": "bg-purple-500",
    "image": "bg-emerald-500",
    "image_placeholder": "bg-emerald-500",
    "textbox": "bg-cyan-500",
    "input_field": "bg-cyan-500",
    "button": "bg-rose-500",
    "checkbox": "bg-amber-500",
    "radiobutton": "bg-orange-500",
    "select": "bg-teal-500",
    "paragraph": "bg-blue-500",
    "label": "bg-indigo-500",
    "link": "bg-pink-500",
    "card": "bg-amber-500",
    "container": "bg-slate-500",
}


class YOLOv8Classifier:
    _instance: Optional["YOLOv8Classifier"] = None

    def __init__(self, model_path: str = DEFAULT_MODEL_PATH):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at: {model_path}")
        self.model = YOLO(model_path)
        self.model_path = model_path

    @classmethod
    def get_instance(cls, model_path: str = DEFAULT_MODEL_PATH) -> "YOLOv8Classifier":
        if cls._instance is None:
            cls._instance = cls(model_path)
        return cls._instance

    def predict_image(
        self, image: np.ndarray, confidence_threshold: float = 0.25
    ) -> List[Dict[str, Any]]:
        """
        Runs YOLO inference on an OpenCV BGR numpy array.
        Extracts detected bounding boxes [x1, y1, x2, y2], class names, and confidence scores.
        """
        if image is None or image.size == 0:
            return []

        # Model Inference with optimal image size (640)
        results = self.model(image, conf=confidence_threshold, imgsz=640)[0]

        detected_elements = []
        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = float(box.conf[0])
            class_id = int(box.cls[0])
            class_name = self.model.names.get(class_id, "Element")

            ymin = int(round(y1))
            xmin = int(round(x1))
            ymax = int(round(y2))
            xmax = int(round(x2))

            detected_elements.append({
                "name": class_name,
                "label": class_name,
                "conf": f"{int(round(conf * 100))}%",
                "confidence": round(conf, 3),
                "box": [ymin, xmin, ymax, xmax],  # [ymin, xmin, ymax, xmax] contract
                "x1": xmin,
                "y1": ymin,
                "x2": xmax,
                "y2": ymax,
                "w": max(1, xmax - xmin),
                "h": max(1, ymax - ymin),
                "color": COLOR_MAP.get(class_name.lower(), "bg-cyan-500"),
                "source": "yolo_v8",
            })

        return detected_elements

    def predict_components(
        self, image_bytes: bytes, confidence_threshold: float = 0.25
    ):
        """
        Validates raw image bytes and executes component detection.
        Maintains backward compatibility with legacy calls.
        """
        if not image_bytes:
            raise ValueError("Provided image bytes are empty.")

        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Failed to decode image. Invalid image format.")

        results = self.predict_image(img, confidence_threshold=confidence_threshold)

        # Legacy dictionary format mapping
        legacy_elements = []
        for item in results:
            legacy_elements.append({
                "label": item["name"],
                "confidence": item["confidence"],
                "bounding_box": {
                    "x": item["x1"],
                    "y": item["y1"],
                    "w": item["w"],
                    "h": item["h"],
                },
                "source": item["source"],
            })

        return legacy_elements


def get_yolo_classifier(model_path: str = DEFAULT_MODEL_PATH) -> YOLOv8Classifier:
    return YOLOv8Classifier.get_instance(model_path)