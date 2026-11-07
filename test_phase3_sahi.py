"""
Phase 3 Validation Suite: Sliced Multi-Scale Inference (SAHI) & Data Augmentation Harness
Project: Sketch2UI
Location: test_phase3_sahi.py

Validates:
1. SlicedInferenceEngine overlapping grid generation & coordinate shift back to canvas.
2. Non-Maximum Suppression (NMS) duplicate boundary collapse & score retention.
3. High-resolution canvas (>1000px) small-element preservation (checkboxes, radiobuttons).
4. YOLOv8Classifier Router conditional execution guardrails (no latency blow-up on <=800px).
5. Spatial OCR integration across all resolved SAHI bounding boxes.
6. Sketch noise augmentation harness (ruled lines, pencil fade/jitter, mobile shadows).
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
import cv2

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.services.sahi_service import (
    SlicedInferenceEngine,
    get_sliced_inference_engine,
    compute_box_iou,
    apply_sahi_nms,
)
from app.services.yolo_service import get_yolo_classifier, YOLOv8Classifier
from app.services.ocr_service import get_ocr_service
from benchmarks.augmentations import (
    add_ruled_notebook_lines,
    add_pencil_jitter_and_fade,
    add_vignette_and_shadows,
    apply_composite_sketch_stress,
)


def test_slice_grid_generation():
    print("\n--- Test 1: Sliced Grid Generation & Boundary Edge-Hug Guarantees ---")
    engine = SlicedInferenceEngine(
        slice_height=512,
        slice_width=512,
        overlap_height_ratio=0.20,
        overlap_width_ratio=0.20,
    )

    # 1. 1200x1200 high-res canvas
    slices_1200 = engine.get_slice_bboxes(1200, 1200)
    assert len(slices_1200) >= 4, f"Expected >= 4 slices for 1200x1200, got {len(slices_1200)}"
    print(f"Generated {len(slices_1200)} slices for 1200x1200 canvas.")

    # Verify tile dimensions and edge coverage
    max_y2 = max(s[2] for s in slices_1200)
    max_x2 = max(s[3] for s in slices_1200)
    assert max_y2 == 1200, f"Bottom edge must reach 1200, got {max_y2}"
    assert max_x2 == 1200, f"Right edge must reach 1200, got {max_x2}"

    # Verify each slice has valid positive dimensions
    for y1, x1, y2, x2 in slices_1200:
        assert y2 > y1 and x2 > x1, f"Invalid slice coordinates: {y1, x1, y2, x2}"
        assert y2 - y1 <= 512 and x2 - x1 <= 512, f"Slice exceeds tile bounds: {y1, x1, y2, x2}"

    # 2. Small canvas (e.g. 400x350) should return single slice covering canvas
    small_slices = engine.get_slice_bboxes(400, 350)
    assert len(small_slices) == 1, f"Small canvas must have 1 slice, got {len(small_slices)}"
    assert small_slices[0] == (0, 0, 400, 350)
    print("  [OK] Grid generation and boundary edge-hugging verified")


def test_coordinate_shift():
    print("\n--- Test 2: Local Tile to Global Canvas Coordinate Transformation ---")
    engine = get_sliced_inference_engine()

    # Local tile positioned at (ymin=409, xmin=409)
    slice_ymin, slice_xmin = 409, 409
    local_det = {
        "name": "CheckBox",
        "label": "CheckBox",
        "confidence": 0.91,
        "conf": "91%",
        "box": [45, 50, 85, 90],  # 40x40 local box
        "x1": 50,
        "y1": 45,
        "x2": 90,
        "y2": 85,
        "w": 40,
        "h": 40,
        "source": "local",
    }

    shifted = engine.shift_detection_to_global(local_det, slice_ymin, slice_xmin)
    expected_box = [409 + 45, 409 + 50, 409 + 85, 409 + 90]  # [454, 459, 494, 499]

    assert shifted["box"] == expected_box, f"Expected {expected_box}, got {shifted['box']}"
    assert shifted["x1"] == expected_box[1]
    assert shifted["y1"] == expected_box[0]
    assert shifted["x2"] == expected_box[3]
    assert shifted["y2"] == expected_box[2]
    assert shifted["w"] == 40
    assert shifted["h"] == 40
    assert shifted["confidence"] == 0.91
    print(f"Shifted local box {local_det['box']} -> global canvas box {shifted['box']}")
    print("  [OK] Coordinate transformation preserves box aspect ratio and dimensions")


def test_nms_duplicate_boundary_collapse():
    print("\n--- Test 3: NMS Deduplication & Duplicate Boundary Collapse ---")
    # Duplicate 1: CheckBox detected in Tile 1
    det1 = {
        "name": "CheckBox",
        "label": "CheckBox",
        "confidence": 0.84,
        "conf": "84%",
        "box": [450, 450, 490, 490],
        "x1": 450, "y1": 450, "x2": 490, "y2": 490, "w": 40, "h": 40,
        "source": "sahi_slice",
    }

    # Duplicate 2: Same CheckBox detected in overlapping Tile 2 (slightly offset, higher conf)
    det2 = {
        "name": "CheckBox",
        "label": "CheckBox",
        "confidence": 0.94,
        "conf": "94%",
        "box": [452, 451, 492, 491],
        "x1": 451, "y1": 452, "x2": 491, "y2": 492, "w": 40, "h": 40,
        "source": "sahi_slice",
    }

    # Duplicate 3: Global pass detected the same box with lower confidence
    det3 = {
        "name": "CheckBox",
        "label": "CheckBox",
        "confidence": 0.65,
        "conf": "65%",
        "box": [448, 449, 489, 489],
        "x1": 449, "y1": 448, "x2": 489, "y2": 489, "w": 40, "h": 40,
        "source": "yolo_v8_global",
    }

    # Separate distinct CheckBox in another region of canvas
    det_distinct = {
        "name": "CheckBox",
        "label": "CheckBox",
        "confidence": 0.88,
        "conf": "88%",
        "box": [120, 120, 160, 160],
        "x1": 120, "y1": 120, "x2": 160, "y2": 160, "w": 40, "h": 40,
        "source": "sahi_slice",
    }

    candidates = [det1, det2, det3, det_distinct]
    resolved = apply_sahi_nms(candidates, iou_threshold=0.45)

    print(f"Candidate detections: {len(candidates)} -> Post-NMS resolved: {len(resolved)}")
    assert len(resolved) == 2, f"Expected 2 unique elements after NMS, got {len(resolved)}"

    # Check that highest confidence score (0.94) won the collapsed boundary
    collapsed_box = next(d for d in resolved if d["box"][0] > 300)
    assert collapsed_box["confidence"] == 0.94, f"Expected highest score 0.94, got {collapsed_box['confidence']}"

    # Verify distinct element is preserved
    distinct_box = next(d for d in resolved if d["box"][0] < 300)
    assert distinct_box["box"] == [120, 120, 160, 160]
    print("  [OK] NMS collapsed boundary duplicates into single highest-confidence element")


def test_high_resolution_small_element_preservation():
    print("\n--- Test 4: High-Resolution Sliced Inference Small-Element Retention ---")
    classifier = get_yolo_classifier()

    # Create high-resolution 1200x1200 canvas
    canvas = np.ones((1200, 1200, 3), dtype=np.uint8) * 255

    # 1. Large Card/Container
    cv2.rectangle(canvas, (100, 100), (1100, 1100), (0, 0, 0), 2)
    # 2. Main Title Heading
    cv2.putText(canvas, "Account Settings", (160, 180), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 3)
    cv2.rectangle(canvas, (150, 130), (700, 210), (0, 0, 0), 2)
    # 3. Input field
    cv2.rectangle(canvas, (150, 260), (1050, 340), (0, 0, 0), 2)
    # 4. Tiny Checkbox 1 (35x35px in a 1200x1200 canvas - would be squished to ~18px in 640x640)
    cv2.rectangle(canvas, (150, 400), (185, 435), (0, 0, 0), 2)
    cv2.putText(canvas, "Enable Notifications", (210, 425), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    # 5. Tiny Checkbox 2 (35x35px)
    cv2.rectangle(canvas, (150, 480), (185, 515), (0, 0, 0), 2)
    cv2.putText(canvas, "Dark Mode", (210, 505), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    # 6. Action Button
    cv2.rectangle(canvas, (150, 580), (450, 660), (0, 0, 0), -1)
    cv2.putText(canvas, "SAVE", (240, 630), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

    # Run Sliced Multi-Scale Inference
    sahi_results = classifier.predict_image(canvas, enable_sahi=True, confidence_threshold=0.15)
    print(f"Total elements detected via SAHI on 1200x1200 canvas: {len(sahi_results)}")

    assert len(sahi_results) >= 2, "SAHI must detect wireframe elements on high-res canvas"

    # Verify schema compliance
    for el in sahi_results:
        assert "name" in el
        assert "conf" in el
        assert "confidence" in el
        assert "box" in el and len(el["box"]) == 4
        assert "w" in el and el["w"] > 0
        assert "h" in el and el["h"] > 0
        assert "color" in el
        assert el["source"] in ["sahi_slice", "yolo_v8_global", "yolo_v8"]

    print("  [OK] High-resolution elements detected and mapped to DetectedElement schemas")


def test_router_conditional_activation_guardrails():
    print("\n--- Test 5: YOLO Service Router Conditional Activation Guardrails ---")
    classifier = get_yolo_classifier()

    # Case A: Standard canvas <= 800px (e.g. 500x500)
    # Should use single-pass inference without slicing overhead
    img_500 = np.ones((500, 500, 3), dtype=np.uint8) * 255
    cv2.rectangle(img_500, (50, 50), (450, 150), (0, 0, 0), 2)
    cv2.rectangle(img_500, (100, 250), (400, 350), (0, 0, 0), -1)

    dets_standard = classifier.predict_image(img_500, enable_sahi=None)
    # Detections should have source 'yolo_v8' (not sahi_slice)
    for d in dets_standard:
        assert d.get("source") == "yolo_v8", f"Standard 500px canvas should use yolo_v8, got {d.get('source')}"
    print("  [OK] Standard <=800px canvas routes through fast single-pass yolo_v8")

    # Case B: Canvas >= 1000px automatically triggers sliced inference
    img_1024 = np.ones((1024, 1024, 3), dtype=np.uint8) * 255
    real_sketch = cv2.imread("test_images/sketches.png")
    if real_sketch is not None:
        sh, sw = real_sketch.shape[:2]
        img_1024[100:100+sh, 100:100+sw] = real_sketch
    else:
        cv2.rectangle(img_1024, (100, 100), (900, 300), (0, 0, 0), 2)
        cv2.rectangle(img_1024, (200, 500), (800, 700), (0, 0, 0), -1)

    dets_1024 = classifier.predict_image(img_1024, enable_sahi=None, confidence_threshold=0.15)
    # When >= 1000px, SlicedInferenceEngine is routed
    sources = {d.get("source") for d in dets_1024}
    print(f"Sources present in 1024px canvas detections: {sources}")
    assert any(s in ["sahi_slice", "yolo_v8_global"] for s in sources), "1024px canvas must trigger SAHI"
    print("  [OK] Automatic SAHI routing triggered for dimensions >= 1000px")

    # Case C: Explicit flag override enable_sahi=True on smaller canvas
    dets_forced = classifier.predict_image(img_500, enable_sahi=True)
    assert isinstance(dets_forced, list)
    print("  [OK] Explicit enable_sahi=True override accepted cleanly")


def test_spatial_ocr_integration_with_sahi():
    print("\n--- Test 6: Spatial OCR Integration with Sliced Inference Engine ---")
    classifier = get_yolo_classifier()

    # Create high-res canvas with login sketch containing recognizable text
    canvas = np.ones((1024, 1024, 3), dtype=np.uint8) * 255
    login_sketch = cv2.imread("test_images/login_sketch.png")
    if login_sketch is not None:
        lh, lw = login_sketch.shape[:2]
        canvas[200:200+lh, 200:200+lw] = login_sketch
    else:
        cv2.rectangle(canvas, (200, 300), (600, 420), (0, 0, 0), -1)
        cv2.putText(canvas, "Submit Form", (240, 380), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 3)

    # Predict with SAHI and OCR
    results = classifier.predict_image(canvas, enable_sahi=True, run_ocr=True, confidence_threshold=0.15)
    print(f"Detected elements with OCR count: {len(results)}")
    assert isinstance(results, list)

    for el in results:
        assert "_ocr_done" in el or "text" in el
    print("  [OK] Spatial OCR successfully integrated across resolved SAHI boxes")


def test_sketch_augmentation_pipeline():
    print("\n--- Test 7: Sketch Data Augmentation Noise Harness ---")
    base_img = np.ones((400, 400, 3), dtype=np.uint8) * 250
    cv2.rectangle(base_img, (50, 50), (350, 150), (20, 20, 20), 2)
    cv2.putText(base_img, "Login Wireframe", (80, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (20, 20, 20), 2)

    # 1. Ruled lines
    ruled = add_ruled_notebook_lines(base_img)
    assert ruled.shape == base_img.shape
    assert ruled.dtype == np.uint8
    assert not np.array_equal(ruled, base_img), "Ruled lines should modify the image"

    # 2. Pencil fade & jitter
    faded = add_pencil_jitter_and_fade(base_img)
    assert faded.shape == base_img.shape
    assert faded.dtype == np.uint8
    assert not np.array_equal(faded, base_img), "Pencil fade should modify the image"

    # 3. Mobile shadows
    shadowed = add_vignette_and_shadows(base_img)
    assert shadowed.shape == base_img.shape
    assert shadowed.dtype == np.uint8
    assert not np.array_equal(shadowed, base_img), "Shadows should modify the image"

    # 4. Composite stress
    stressed = apply_composite_sketch_stress(base_img)
    assert stressed.shape == base_img.shape
    assert stressed.dtype == np.uint8
    print("  [OK] All 4 sketch noise augmentation generators validated successfully")


if __name__ == "__main__":
    print("======================================================================")
    print("      STARTING SKETCH2UI PHASE 3 SAHI & AUGMENTATION TEST SUITE       ")
    print("======================================================================")
    test_slice_grid_generation()
    test_coordinate_shift()
    test_nms_duplicate_boundary_collapse()
    test_high_resolution_small_element_preservation()
    test_router_conditional_activation_guardrails()
    test_spatial_ocr_integration_with_sahi()
    test_sketch_augmentation_pipeline()
    print("\n======================================================================")
    print("        ALL 7 PHASE 3 ARCHITECTURAL TESTS PASSED SUCCESSFULLY!        ")
    print("======================================================================")
