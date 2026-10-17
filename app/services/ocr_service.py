"""
Sprint 2: Handwritten Text OCR Pipeline & Dynamic JSX Text Injection
Location: app/services/ocr_service.py
"""
import re
import logging
from typing import List, Dict, Any, Tuple, Optional
import cv2
import numpy as np

from app.utils.cropper import crop_component

logger = logging.getLogger(__name__)

TEXT_RELEVANT_TYPES = {
    "button", "btn", "submit",
    "heading", "title", "header",
    "label",
    "paragraph", "text", "description",
    "textbox", "input_field", "input", "text_box", "textfield",
    "link", "anchor",
    "checkbox", "radiobutton", "radio"
}


class OCRService:
    _instance = None
    _reader = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(OCRService, cls).__new__(cls)
        return cls._instance

    def __init__(self, languages: Optional[List[str]] = None, gpu: bool = False):
        if self._reader is None:
            self._init_reader(languages=languages or ["en"], gpu=gpu)

    def _init_reader(self, languages: List[str], gpu: bool):
        try:
            import easyocr
            # Singleton EasyOCR reader (CPU mode by default for zero-config portability)
            self._reader = easyocr.Reader(languages, gpu=gpu, verbose=False)
            logger.info("EasyOCR Reader successfully initialized (Singleton).")
        except Exception as e:
            logger.warning(f"EasyOCR Reader initialization warning: {e}. Falling back to rule-based parser.")
            self._reader = None

    def warmup(self):
        """Runs a tiny dummy inference to pre-load neural weights into memory."""
        if self._reader is not None:
            try:
                dummy = np.ones((64, 128, 3), dtype=np.uint8) * 255
                self._reader.readtext(dummy)
            except Exception as e:
                logger.debug(f"OCR warmup exception: {e}")

    def clean_extracted_text(self, text: str) -> str:
        """
        Strips punctuation noise, stray dots, scratch marks, and cleans whitespace.
        Preserves characters like question marks for links/labels (e.g., 'Forgot Password?').
        """
        if not text:
            return ""

        # Normalize whitespace
        cleaned = re.sub(r'\s+', ' ', text).strip()

        # Filter out isolated single punctuation symbols
        if re.fullmatch(r'[\W_]+', cleaned):
            return ""

        # Strip framing noise characters from edges (dots, quotes, underscores, dashes, commas, colons, semicolons, tildes, backticks, pipes)
        # We explicitly preserve terminal '?' or '!' (e.g. 'Forgot Password?')
        noise_chars = " ._-|~`'\":;,"
        cleaned = cleaned.lstrip(noise_chars + "?!")
        cleaned = cleaned.rstrip(noise_chars)

        return cleaned.strip()

    def extract_text_from_crop(self, image_crop: np.ndarray) -> Tuple[str, float]:
        """
        Extracts handwritten or printed text from a bounding box crop.
        Preprocesses with grayscale conversion, Otsu binarization to clean paper shadows.
        Returns: (cleaned_text, confidence)
        """
        if image_crop is None or image_crop.size == 0:
            return "", 0.0

        h, w = image_crop.shape[:2]
        if h < 6 or w < 6:
            return "", 0.0

        # Preprocessing: convert to grayscale
        if len(image_crop.shape) == 3:
            gray = cv2.cvtColor(image_crop, cv2.COLOR_BGR2GRAY)
        else:
            gray = image_crop.copy()

        # Upscale small crops so character strokes are legible for OCR
        if h < 40 or w < 100:
            scale_factor = max(2.0, min(3.0, 60.0 / max(1, h)))
            gray = cv2.resize(gray, (0, 0), fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)

        # Clean shadows: Gaussian blur and Otsu thresholding
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        if self._reader is None:
            return "", 0.0

        try:
            # 1. Run recognition on enhanced grayscale
            raw_results = self._reader.readtext(gray, detail=1, paragraph=False)
            if not raw_results:
                # 2. Fallback to Otsu thresholded image
                raw_results = self._reader.readtext(thresh, detail=1, paragraph=False)

            if not raw_results:
                return "", 0.0

            # Filter results with basic probability
            filtered = []
            for item in raw_results:
                if len(item) == 3:
                    bbox, raw_txt, prob = item
                    cleaned = self.clean_extracted_text(raw_txt)
                    if cleaned and prob >= 0.25:
                        x_min = min(pt[0] for pt in bbox) if isinstance(bbox, (list, tuple)) else 0
                        filtered.append((x_min, cleaned, float(prob)))

            if not filtered:
                return "", 0.0

            # Sort tokens left-to-right
            filtered.sort(key=lambda t: t[0])
            combined_text = " ".join(t[1] for t in filtered)
            avg_conf = sum(t[2] for t in filtered) / len(filtered)

            final_text = self.clean_extracted_text(combined_text)
            return final_text, avg_conf

        except Exception as e:
            logger.warning(f"Error during OCR recognition: {e}")
            return "", 0.0

    def batch_extract_component_texts(
        self, image: np.ndarray, detected_elements: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Iterates over text-bearing components, crops their regions, and attaches 'text'.
        """
        if image is None or not detected_elements:
            return detected_elements

        for el in detected_elements:
            # If already provided (e.g. from mock/unit test), retain it
            if el.get("text"):
                continue

            name_lower = el.get("name", "").lower()
            if name_lower not in TEXT_RELEVANT_TYPES:
                el["text"] = None
                el["ocr_conf"] = 0.0
                continue

            # Extract bbox coordinates
            if "x1" in el and "y1" in el:
                x = el["x1"]
                y = el["y1"]
                w = el.get("w", el.get("x2", x) - x)
                h = el.get("h", el.get("y2", y) - y)
                bbox = {"x": x, "y": y, "w": w, "h": h}
            elif "box" in el and len(el["box"]) == 4:
                b = el["box"]
                ymin, xmin, ymax, xmax = int(b[0]), int(b[1]), int(b[2]), int(b[3])
                bbox = {"x": xmin, "y": ymin, "w": max(1, xmax - xmin), "h": max(1, ymax - ymin)}
            else:
                el["text"] = None
                el["ocr_conf"] = 0.0
                continue

            try:
                crop = crop_component(image, bbox)
                text, conf = self.extract_text_from_crop(crop)

                # Honest confidence filter: require >= 0.40 confidence and non-empty text
                if conf >= 0.40 and text:
                    el["text"] = text
                    el["ocr_conf"] = round(conf, 2)
                else:
                    el["text"] = None
                    el["ocr_conf"] = 0.0
            except Exception as e:
                logger.debug(f"Failed to extract text for component {el.get('name')}: {e}")
                el["text"] = None
                el["ocr_conf"] = 0.0

        return detected_elements


_GLOBAL_OCR_SERVICE = None


def get_ocr_service() -> OCRService:
    """Returns the singleton OCRService instance."""
    global _GLOBAL_OCR_SERVICE
    if _GLOBAL_OCR_SERVICE is None:
        _GLOBAL_OCR_SERVICE = OCRService()
    return _GLOBAL_OCR_SERVICE
