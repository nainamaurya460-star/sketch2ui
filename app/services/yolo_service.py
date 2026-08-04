# backend/app/services/yolo_service.py
from ultralytics import YOLO
import cv2
import numpy as np

class YOLOv8Classifier:
    def __init__(self, model_path: str = "backend/app/models/best.pt"):
        # Server startup par trained model weights load honge
        self.model = YOLO(model_path)

    def predict_components(self, image_bytes: bytes, confidence_threshold: float = 0.5):
        # Image byte array ko OpenCV format me convert karna
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # YOLOv8 Inference Run
        results = self.model(img, conf=confidence_threshold)[0]
        
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
    