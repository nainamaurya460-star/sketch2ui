# backend/app/services/yolo_service.py
import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from ultralytics import YOLO
import cv2
import numpy as np

from app.services.sahi_service import get_sliced_inference_engine

logger = logging.getLogger(__name__)

# 1. Dynamic Absolute Pathing: Server kisi bhi directory se chale, file path hamesha correct rahega
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_MODEL_PATH = str(BASE_DIR / "models" / "best.pt")

COLOR_MAP = {
    "button": "bg-rose-500",
    "checkbox": "bg-amber-500",
    "heading": "bg-purple-500",
    "image": "bg-emerald-500",
    "image_placeholder": "bg-emerald-500",
    "label": "bg-indigo-500",
    "link": "bg-pink-500",
    "paragraph": "bg-blue-500",
    "radiobutton": "bg-orange-500",
    "select": "bg-teal-500",
    "textbox": "bg-cyan-500",
    "input_field": "bg-cyan-500",
    "card": "bg-amber-500",
    "container": "bg-slate-500",
}

# Canonical 10 YOLOv8 Classes for Sketch2UI
CLASS_NAMES = {
    0: "Button",
    1: "CheckBox",
    2: "Heading",
    3: "Image",
    4: "Label",
    5: "Link",
    6: "Paragraph",
    7: "RadioButton",
    8: "Select",
    9: "TextBox",
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

    def _boxes_to_detected_elements(
        self, boxes, source: str = "yolo_v8"
    ) -> List[Dict[str, Any]]:
        """Maps ultralytics Results.boxes to canonical Sketch2UI DetectedElement dictionary schemas."""
        detected_elements = []
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf_score = float(box.conf[0])
            class_id = int(box.cls[0])
            class_name = self.model.names.get(class_id) or CLASS_NAMES.get(class_id, "Element")

            ymin = int(round(y1))
            xmin = int(round(x1))
            ymax = int(round(y2))
            xmax = int(round(x2))

            detected_elements.append({
                "name": class_name,
                "label": class_name,
                "conf": f"{int(round(conf_score * 100))}%",
                "confidence": round(conf_score, 3),
                "box": [ymin, xmin, ymax, xmax],  # [ymin, xmin, ymax, xmax] contract
                "x1": xmin,
                "y1": ymin,
                "x2": xmax,
                "y2": ymax,
                "w": max(1, xmax - xmin),
                "h": max(1, ymax - ymin),
                "color": COLOR_MAP.get(class_name.lower(), "bg-cyan-500"),
                "source": source,
            })
        return detected_elements

    def predict_image(
        self,
        image: np.ndarray,
        confidence_threshold: float = 0.18,
        iou: float = 0.45,
        enable_sahi: Optional[bool] = None,
        run_ocr: bool = False,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Runs YOLO inference on an OpenCV BGR numpy array.
        Extracts detected bounding boxes [x1, y1, x2, y2], class names, and confidence scores.
        Defaults: conf=0.18, iou=0.45 for sensitive hand-drawn wireframe detection.

        Phase 3 Routing:
          - Sliced inference executes conditionally:
            1. If dimensions exceed 1000px on any side, routes through SlicedInferenceEngine.
            2. If dimensions > 800px and initial confidence density is low, routes through SlicedInferenceEngine.
            3. Can be explicitly commanded via enable_sahi=True/False or kwargs['sahi'].
          - Preserves standard single-pass latency (<800px) with zero performance blow-up.
          - Runs spatial OCR integration across all resolved boxes when requested or routed via SAHI.
        """
        if image is None or image.size == 0:
            return []

        # Flexible kwargs support for conf / iou / confidence_threshold / iou_threshold
        conf = kwargs.get("conf", confidence_threshold)
        iou_val = kwargs.get("iou_threshold", iou)

        h, w = image.shape[:2]
        max_dim = max(h, w)

        # Sliced inference routing evaluation
        sahi_flag = enable_sahi if enable_sahi is not None else kwargs.get("sahi", kwargs.get("sliced", None))

        should_slice = False
        if sahi_flag is True:
            should_slice = True
        elif sahi_flag is False:
            should_slice = False
        elif max_dim >= 1000:
            should_slice = True
        elif max_dim > 800:
            # Check initial pass confidence density to prevent latency blow-up
            fast_results = self.model(image, conf=conf, iou=iou_val, imgsz=640)[0]
            conf_scores = [float(b.conf[0]) for b in fast_results.boxes] if fast_results.boxes else []
            if len(conf_scores) == 0 or np.mean(conf_scores) < 0.35:
                should_slice = True
            else:
                # Initial pass has sufficient confidence density, use fast pass
                detected_elements = self._boxes_to_detected_elements(fast_results.boxes, source="yolo_v8")
                if run_ocr or kwargs.get("run_ocr", False):
                    try:
                        from app.services.ocr_service import get_ocr_service
                        ocr_service = get_ocr_service()
                        detected_elements = ocr_service.batch_extract_component_texts(image, detected_elements)
                        for el in detected_elements:
                            el["_ocr_done"] = True
                    except Exception as ocr_err:
                        logger.warning(f"Spatial OCR integration skipped/failed in fast pass: {ocr_err}")
                return detected_elements

        # --- BRANCH A: Sliced Multi-Scale Inference (SAHI) ---
        if should_slice:
            sahi_engine = get_sliced_inference_engine(iou_threshold=iou_val)

            def slice_predict_raw(tile_img: np.ndarray) -> List[Dict[str, Any]]:
                tile_results = self.model(tile_img, conf=conf, iou=iou_val, imgsz=640)[0]
                return self._boxes_to_detected_elements(tile_results.boxes, source="sahi_slice")

            detected_elements = sahi_engine.infer(
                image=image,
                predict_fn=slice_predict_raw,
                confidence_threshold=conf,
                iou_threshold=iou_val,
                include_global=True,
            )

            # Spatial OCR integration across all resolved boxes
            do_ocr = run_ocr or kwargs.get("run_ocr", True)
            if do_ocr:
                try:
                    from app.services.ocr_service import get_ocr_service
                    ocr_service = get_ocr_service()
                    detected_elements = ocr_service.batch_extract_component_texts(image, detected_elements)
                    for el in detected_elements:
                        el["_ocr_done"] = True
                except Exception as ocr_err:
                    logger.warning(f"Spatial OCR integration skipped/failed in SAHI pass: {ocr_err}")

            return detected_elements

        # --- BRANCH B: Standard Single-Pass Inference (<= 800px) ---
        results = self.model(
            image,
            conf=conf,
            iou=iou_val,
            imgsz=640
        )[0]

        detected_elements = self._boxes_to_detected_elements(results.boxes, source="yolo_v8")

        if run_ocr or kwargs.get("run_ocr", False):
            try:
                from app.services.ocr_service import get_ocr_service
                ocr_service = get_ocr_service()
                detected_elements = ocr_service.batch_extract_component_texts(image, detected_elements)
                for el in detected_elements:
                    el["_ocr_done"] = True
            except Exception as ocr_err:
                logger.warning(f"Spatial OCR integration skipped/failed in standard pass: {ocr_err}")

        return detected_elements

    def predict_components(
        self,
        image_bytes: bytes,
        confidence_threshold: float = 0.18,
        iou: float = 0.45,
        **kwargs
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

        results = self.predict_image(
            img,
            confidence_threshold=confidence_threshold,
            iou=iou,
            **kwargs
        )

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