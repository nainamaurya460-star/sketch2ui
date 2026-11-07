"""
Phase 1: Context-Driven Spatial OCR Pipeline & Text Fusion Architecture
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


def _parse_confidence(val: Any) -> float:
    if val is None:
        return 0.5
    if isinstance(val, (int, float)):
        return float(val) if val <= 1.0 else float(val) / 100.0
    if isinstance(val, str):
        cleaned = val.replace("%", "").strip()
        try:
            num = float(cleaned)
            return num / 100.0 if num > 1.0 else num
        except ValueError:
            return 0.5
    return 0.5


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
        Preserves characters like question marks for links/labels (e.g., 'Forgot Password?'),
        and email/password symbols like '@' and '*'.
        """
        if not text:
            return ""

        # Normalize whitespace
        cleaned = re.sub(r'\s+', ' ', text).strip()

        # Check for noise-only punctuation strings, while preserving symbols like '@', '*', '?', '!'
        if re.fullmatch(r'[\W_]+', cleaned):
            if any(sym in cleaned for sym in ["@", "*", "?", "!"]):
                pass
            else:
                return ""

        # Strip framing noise characters from edges (dots, quotes, underscores, dashes, commas, colons, semicolons, tildes, backticks, pipes)
        # We explicitly preserve terminal '?' or '!' (e.g. 'Forgot Password?') and email '@', '*'
        noise_chars = " ._-|~`'\":;,"
        cleaned = cleaned.lstrip(noise_chars)
        cleaned = cleaned.rstrip(noise_chars)

        return cleaned.strip()

    def extract_full_page_text_tokens(self, image_np: np.ndarray) -> List[Dict[str, Any]]:
        """
        Task 1.1: Full-Image Spatial OCR Extraction
        Runs EasyOCR across the entire normalized canvas.
        For each detected token, extracts:
          {"text": str, "box": [ymin, xmin, ymax, xmax], "confidence": float, "center": (cx, cy)}
        Applies clean sanitization (strips stray punctuation, preserves email/password symbols).
        """
        if image_np is None or image_np.size == 0 or self._reader is None:
            return []

        try:
            # 1. Inference on full uncropped normalized canvas
            raw_results = self._reader.readtext(image_np, detail=1, paragraph=False)
            if not raw_results:
                # Fallback to enhanced Otsu thresholded canvas if faint pencil handwriting
                if len(image_np.shape) == 3:
                    gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
                else:
                    gray = image_np.copy()
                blurred = cv2.GaussianBlur(gray, (3, 3), 0)
                _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                raw_results = self._reader.readtext(thresh, detail=1, paragraph=False)

            tokens: List[Dict[str, Any]] = []
            for item in raw_results:
                if len(item) == 3:
                    bbox, raw_txt, prob = item
                    cleaned = self.clean_extracted_text(raw_txt)
                    if cleaned and float(prob) >= 0.20:
                        xs = [pt[0] for pt in bbox]
                        ys = [pt[1] for pt in bbox]
                        xmin = int(round(min(xs)))
                        xmax = int(round(max(xs)))
                        ymin = int(round(min(ys)))
                        ymax = int(round(max(ys)))
                        cx = float((xmin + xmax) / 2.0)
                        cy = float((ymin + ymax) / 2.0)
                        tokens.append({
                            "text": cleaned,
                            "box": [ymin, xmin, ymax, xmax],
                            "confidence": round(float(prob), 3),
                            "center": (cx, cy)
                        })

            return tokens
        except Exception as e:
            logger.warning(f"Error during full-page OCR extraction: {e}")
            return []

    def match_spatial_tokens(
        self,
        detected_elements: List[Dict[str, Any]],
        tokens: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Task 1.2: Spatial Proximity Matcher
        For each YOLO-detected component bounding box:
          - Checks for tokens falling inside the box boundary.
          - Checks for label tokens located immediately above the box (delta_y <= 40px and horizontal overlap >= 40%).
          - Assigns matched text directly:
            element['text'] = matched_text
            element['label_above'] = label_text
        """
        if not detected_elements:
            return []

        for el in detected_elements:
            name_lower = (el.get("name") or el.get("label", "")).lower()

            # Skip non-text components (e.g. Image) unless text was pre-assigned
            if name_lower in ["image", "image_placeholder"] and not el.get("text"):
                el["text"] = None
                el["ocr_conf"] = 0.0
                el["label_above"] = None
                continue

            # Extract box coordinates in [ymin, xmin, ymax, xmax]
            e_ymin, e_xmin, e_ymax, e_xmax = 0, 0, 0, 0
            if "box" in el and isinstance(el["box"], (list, tuple)) and len(el["box"]) == 4:
                b = el["box"]
                e_ymin, e_xmin, e_ymax, e_xmax = int(b[0]), int(b[1]), int(b[2]), int(b[3])
            elif "y1" in el and "x1" in el:
                e_ymin = int(el["y1"])
                e_xmin = int(el["x1"])
                e_ymax = int(el.get("y2", e_ymin + el.get("h", 0)))
                e_xmax = int(el.get("x2", e_xmin + el.get("w", 0)))
            else:
                continue

            e_w = max(1, e_xmax - e_xmin)
            e_h = max(1, e_ymax - e_ymin)

            inside_tokens = []
            above_tokens = []

            for tok in tokens:
                t_ymin, t_xmin, t_ymax, t_xmax = tok["box"]
                t_cx, t_cy = tok["center"]
                t_w = max(1, t_xmax - t_xmin)
                t_h = max(1, t_ymax - t_ymin)

                # 1. Inside box check:
                # Center point is inside box (with 5px tolerance) OR area overlap >= 50%
                inter_xmin = max(e_xmin, t_xmin)
                inter_ymin = max(e_ymin, t_ymin)
                inter_xmax = min(e_xmax, t_xmax)
                inter_ymax = min(e_ymax, t_ymax)
                inter_w = max(0, inter_xmax - inter_xmin)
                inter_h = max(0, inter_ymax - inter_ymin)
                inter_area = inter_w * inter_h
                token_area = t_w * t_h

                is_inside = (
                    (e_xmin - 5 <= t_cx <= e_xmax + 5 and e_ymin - 5 <= t_cy <= e_ymax + 5)
                    or (token_area > 0 and (inter_area / float(token_area)) >= 0.50)
                )

                if is_inside:
                    inside_tokens.append(tok)
                else:
                    # 2. Label token immediately above box check:
                    # delta_y <= 40px and horizontal overlap >= 40%
                    # delta_y = e_ymin - t_ymax
                    delta_y = e_ymin - t_ymax
                    h_overlap = max(0, min(e_xmax, t_xmax) - max(e_xmin, t_xmin))
                    h_overlap_ratio = (h_overlap / float(t_w)) if t_w > 0 else 0.0

                    if -5 <= delta_y <= 40 and h_overlap_ratio >= 0.40:
                        above_tokens.append(tok)

            # Assign matched inside text
            if inside_tokens:
                inside_tokens.sort(key=lambda t: (t["center"][1] // 15, t["center"][0]))
                matched_text = " ".join(t["text"] for t in inside_tokens).strip()
                el["text"] = matched_text
                el["ocr_conf"] = max(t["confidence"] for t in inside_tokens)
            else:
                if not el.get("text"):
                    el["text"] = None
                    el["ocr_conf"] = 0.0

            # Assign matched label_above text
            if above_tokens:
                above_tokens.sort(key=lambda t: t["center"][0])
                label_text = " ".join(t["text"] for t in above_tokens).strip()
                el["label_above"] = label_text
            else:
                if "label_above" not in el:
                    el["label_above"] = None

        return detected_elements

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
        Text-First Spatial OCR Pipeline:
        1. Runs EasyOCR across the entire uncropped normalized canvas.
        2. Spatially fuses text tokens into component bounding boxes and detects labels above.
        3. Preserves existing mocked/injected text and filters non-text components.
        """
        if image is None or not detected_elements:
            return detected_elements

        # Step 1: Extract full page tokens
        tokens = self.extract_full_page_text_tokens(image)

        # Step 2: Spatial proximity matching
        self.match_spatial_tokens(detected_elements, tokens)

        # Step 3: Clean up and validate non-text components
        for el in detected_elements:
            name_lower = (el.get("name") or el.get("label", "")).lower()
            if name_lower not in TEXT_RELEVANT_TYPES:
                el["text"] = None
                el["ocr_conf"] = 0.0

        return detected_elements

    def reclassify_elements(
        self, detected_elements: List[Dict[str, Any]], image: Optional[np.ndarray] = None
    ) -> List[Dict[str, Any]]:
        """Applies heuristic semantic re-classification based on extracted OCR texts and shape cues."""
        from app.services.heuristic_service import apply_semantic_reclassification
        return apply_semantic_reclassification(detected_elements, image)


def extract_full_page_text_tokens(image_np: np.ndarray) -> List[Dict[str, Any]]:
    """Module-level helper for full-page spatial OCR extraction."""
    return get_ocr_service().extract_full_page_text_tokens(image_np)


_GLOBAL_OCR_SERVICE = None


def get_ocr_service() -> OCRService:
    """Returns the singleton OCRService instance."""
    global _GLOBAL_OCR_SERVICE
    if _GLOBAL_OCR_SERVICE is None:
        _GLOBAL_OCR_SERVICE = OCRService()
    return _GLOBAL_OCR_SERVICE
