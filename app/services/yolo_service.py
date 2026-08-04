# backend/app/services/yolo_service.py
import os
from pathlib import Path
from ultralytics import YOLO
import cv2
import numpy as np

# 1. Dynamic Absolute Pathing: Server kisi bhi directory se chale, file path hamesha correct rahega
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_MODEL_PATH = str(BASE_DIR / "models" / "best.pt")

class YOLOv8Classifier:
    def __init__(self, model_path: str = DEFAULT_MODEL_PATH):
        # Trained model weights load karna
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at: {model_path}")
        self.model = YOLO(model_path)

    def predict_components(self, image_bytes: bytes, confidence_threshold: float = 0.5):
        # 2. Empty/Corrupted Image Validation
        if not image_bytes:
            raise ValueError("Provided image bytes are empty.")

        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Failed to decode image. Invalid image format.")

        # 3. Model Inference with optimal image size (640)
        results = self.model(img, conf=confidence_threshold, imgsz=640)[0]
        
        detected_elements = []
        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            label = self.model.names[class_id]

            detected_elements.append({
                "label": label,
                "confidence": round(confidence, 2),
                "bounding_box": {
                    "x": int(x1),
                    "y": int(y1),
                    "w": int(x2 - x1),
                    "h": int(y2 - y1)
                },
                "source": "yolo_v8"
            })
            
        return detected_elements