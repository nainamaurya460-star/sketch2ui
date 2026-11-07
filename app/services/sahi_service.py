"""
Phase 3: Sliced Multi-Scale Inference (SAHI) Engine
Project: Sketch2UI
Location: app/services/sahi_service.py

Hardens YOLOv8 detection against small-element drops (checkboxes, radio buttons,
small icons) and high-resolution wireframes (>800px-1000px) by slicing canvas images
into overlapping 512x512 tiles, performing multi-scale inference, and merging
bounding boxes via Non-Maximum Suppression (NMS, iou_threshold=0.45).
"""

import logging
from typing import List, Dict, Tuple, Any, Optional, Callable
import cv2
import numpy as np

logger = logging.getLogger(__name__)

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


def compute_box_iou(boxA: List[int], boxB: List[int]) -> float:
    """
    Computes Intersection-over-Union (IoU) between two bounding boxes
    in [ymin, xmin, ymax, xmax] format.
    """
    yA = max(boxA[0], boxB[0])
    xA = max(boxA[1], boxB[1])
    yB = min(boxA[2], boxB[2])
    xB = min(boxA[3], boxB[3])

    inter_w = max(0, xB - xA)
    inter_h = max(0, yB - yA)
    inter_area = inter_w * inter_h

    areaA = max(0, boxA[2] - boxA[0]) * max(0, boxA[3] - boxA[1])
    areaB = max(0, boxB[2] - boxB[0]) * max(0, boxB[3] - boxB[1])
    union_area = areaA + areaB - inter_area

    if union_area <= 0:
        return 0.0
    return float(inter_area) / float(union_area)


def apply_sahi_nms(
    detections: List[Dict[str, Any]],
    iou_threshold: float = 0.45,
    cross_class_threshold: float = 0.70
) -> List[Dict[str, Any]]:
    """
    Applies Non-Maximum Suppression (NMS) across sliced multi-scale detections.
    1. Sorts all candidate boxes descending by confidence score.
    2. Suppresses duplicate detections of the same class when IoU >= iou_threshold.
    3. Suppresses heavily conflicting duplicates across classes when IoU >= cross_class_threshold
       (e.g., tile CheckBox vs global Button artifact covering the exact same pixel zone).
    """
    if not detections or len(detections) <= 1:
        return detections

    # Sort candidates by numerical confidence descending
    def get_score(item: Dict[str, Any]) -> float:
        if "confidence" in item:
            try:
                return float(item["confidence"])
            except (ValueError, TypeError):
                pass
        if "conf" in item:
            try:
                return float(str(item["conf"]).replace("%", "")) / 100.0
            except (ValueError, TypeError):
                pass
        return 0.5

    sorted_dets = sorted(detections, key=get_score, reverse=True)
    kept_dets: List[Dict[str, Any]] = []

    for candidate in sorted_dets:
        c_box = candidate["box"]
        c_name = (candidate.get("name") or candidate.get("label", "")).lower()

        suppress = False
        for kept in kept_dets:
            k_box = kept["box"]
            k_name = (kept.get("name") or kept.get("label", "")).lower()

            iou = compute_box_iou(c_box, k_box)

            # Case A: Same class duplicate detection across slice boundaries
            if c_name == k_name and iou >= iou_threshold:
                suppress = True
                break

            # Case B: Cross-class duplicate artifact on near-identical box
            if iou >= cross_class_threshold:
                # If the candidate is a micro-element (checkbox, radiobutton) and kept is a huge box,
                # check containment rather than raw IoU
                area_c = max(1, (c_box[2] - c_box[0]) * (c_box[3] - c_box[1]))
                area_k = max(1, (k_box[2] - k_box[0]) * (k_box[3] - k_box[1]))
                # Only suppress if candidate and kept are similar size (IoU >= cross_class_threshold)
                if min(area_c, area_k) / max(area_c, area_k) >= 0.40:
                    suppress = True
                    break

        if not suppress:
            kept_dets.append(candidate)

    return kept_dets


class SlicedInferenceEngine:
    """
    Sliced Aided Hyper Inference (SAHI) Engine for Sketch2UI.
    Partitions high-resolution wireframe canvases into overlapping tiles,
    executes localized detection passes to capture micro-elements,
    shifts coordinates back to global canvas space, and merges via NMS.
    """

    def __init__(
        self,
        slice_height: int = 512,
        slice_width: int = 512,
        overlap_height_ratio: float = 0.20,
        overlap_width_ratio: float = 0.20,
        iou_threshold: float = 0.45,
    ):
        self.slice_height = slice_height
        self.slice_width = slice_width
        self.overlap_height_ratio = overlap_height_ratio
        self.overlap_width_ratio = overlap_width_ratio
        self.iou_threshold = iou_threshold

    def get_slice_bboxes(
        self, image_height: int, image_width: int
    ) -> List[Tuple[int, int, int, int]]:
        """
        Generates overlapping bounding box grid [ymin, xmin, ymax, xmax]
        covering the full canvas dimensions with boundary edge-hug guarantees.
        """
        if image_height <= self.slice_height and image_width <= self.slice_width:
            return [(0, 0, image_height, image_width)]

        step_h = max(1, int(self.slice_height * (1.0 - self.overlap_height_ratio)))
        step_w = max(1, int(self.slice_width * (1.0 - self.overlap_width_ratio)))

        y_starts = list(range(0, max(1, image_height - self.slice_height + step_h), step_h))
        x_starts = list(range(0, max(1, image_width - self.slice_width + step_w), step_w))

        # Ensure edge coverage
        if y_starts[-1] + self.slice_height < image_height:
            y_starts.append(image_height - self.slice_height)
        if x_starts[-1] + self.slice_width < image_width:
            x_starts.append(image_width - self.slice_width)

        slices = []
        for y1 in y_starts:
            y1 = max(0, min(y1, image_height - 1))
            y2 = min(image_height, y1 + self.slice_height)
            if y2 - y1 < min(self.slice_height, image_height):
                y1 = max(0, y2 - self.slice_height)

            for x1 in x_starts:
                x1 = max(0, min(x1, image_width - 1))
                x2 = min(image_width, x1 + self.slice_width)
                if x2 - x1 < min(self.slice_width, image_width):
                    x1 = max(0, x2 - self.slice_width)

                slices.append((y1, x1, y2, x2))

        # Deduplicate slice windows
        unique_slices: List[Tuple[int, int, int, int]] = []
        seen = set()
        for s in slices:
            if s not in seen:
                seen.add(s)
                unique_slices.append(s)

        return unique_slices

    @staticmethod
    def shift_detection_to_global(
        det: Dict[str, Any], slice_ymin: int, slice_xmin: int
    ) -> Dict[str, Any]:
        """
        Shifts a detection's bounding coordinates from local tile space
        back to absolute global canvas coordinates.
        """
        local_ymin, local_xmin, local_ymax, local_xmax = det["box"]
        g_ymin = int(round(local_ymin + slice_ymin))
        g_xmin = int(round(local_xmin + slice_xmin))
        g_ymax = int(round(local_ymax + slice_ymin))
        g_xmax = int(round(local_xmax + slice_xmin))

        class_name = det.get("name") or det.get("label", "Element")
        conf_score = det.get("confidence", 0.5)

        shifted = dict(det)
        shifted.update({
            "name": class_name,
            "label": class_name,
            "box": [g_ymin, g_xmin, g_ymax, g_xmax],
            "x1": g_xmin,
            "y1": g_ymin,
            "x2": g_xmax,
            "y2": g_ymax,
            "w": max(1, g_xmax - g_xmin),
            "h": max(1, g_ymax - g_ymin),
            "source": det.get("source", "sahi_slice"),
        })
        return shifted

    def infer(
        self,
        image: np.ndarray,
        predict_fn: Callable[[np.ndarray], List[Dict[str, Any]]],
        confidence_threshold: float = 0.18,
        iou_threshold: Optional[float] = None,
        include_global: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Executes sliced multi-scale inference:
          1. Global downsampled full-image pass (captures large layouts/cards).
          2. Tile-by-tile passes across overlapping slices (extracts micro-elements).
          3. Absolute coordinate transformation for all tile boxes.
          4. Non-Maximum Suppression (NMS) deduplication across tile boundaries.
        """
        if image is None or image.size == 0:
            return []

        h, w = image.shape[:2]
        effective_iou = iou_threshold if iou_threshold is not None else self.iou_threshold
        accumulated_detections: List[Dict[str, Any]] = []

        # Step 1: Global full-image pass
        if include_global:
            try:
                global_raw = predict_fn(image)
                for det in global_raw:
                    det_copy = dict(det)
                    det_copy["source"] = "yolo_v8_global"
                    accumulated_detections.append(det_copy)
            except Exception as e:
                logger.warning(f"Global pass in SAHI encountered exception: {e}")

        # Step 2: Slice grid passes
        slice_windows = self.get_slice_bboxes(h, w)
        for y1, x1, y2, x2 in slice_windows:
            tile = image[y1:y2, x1:x2]
            if tile.size == 0:
                continue

            try:
                tile_raw = predict_fn(tile)
                for det in tile_raw:
                    shifted = self.shift_detection_to_global(det, y1, x1)
                    shifted["source"] = "sahi_slice"
                    accumulated_detections.append(shifted)
            except Exception as tile_err:
                logger.warning(f"Slice ({y1},{x1},{y2},{x2}) prediction error: {tile_err}")

        # Step 3: Apply NMS to collapse duplicate boundary detections
        resolved_elements = apply_sahi_nms(
            accumulated_detections,
            iou_threshold=effective_iou,
        )

        return resolved_elements


_GLOBAL_SAHI_ENGINE: Optional[SlicedInferenceEngine] = None


def get_sliced_inference_engine(
    slice_height: int = 512,
    slice_width: int = 512,
    overlap_ratio: float = 0.20,
    iou_threshold: float = 0.45,
) -> SlicedInferenceEngine:
    """Returns or initializes the singleton SlicedInferenceEngine."""
    global _GLOBAL_SAHI_ENGINE
    if _GLOBAL_SAHI_ENGINE is None:
        _GLOBAL_SAHI_ENGINE = SlicedInferenceEngine(
            slice_height=slice_height,
            slice_width=slice_width,
            overlap_height_ratio=overlap_ratio,
            overlap_width_ratio=overlap_ratio,
            iou_threshold=iou_threshold,
        )
    return _GLOBAL_SAHI_ENGINE
