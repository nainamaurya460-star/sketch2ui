"""
Unit & Integration Test Suite for Phase 1:
Context-Driven OCR & Spatial Fusion Architecture
Location: test_phase1_ocr_spatial_fusion.py
"""
import numpy as np
import cv2
from app.services.ocr_service import get_ocr_service, extract_full_page_text_tokens
from app.services.heuristic_service import apply_semantic_reclassification, synthesize_layout_code


def test_full_image_spatial_ocr_extraction():
    print("\n--- Test 1: Full-Image Spatial OCR Token Extraction ---")
    ocr = get_ocr_service()

    # Create canvas with printed text tokens
    canvas = np.ones((600, 800, 3), dtype=np.uint8) * 255
    cv2.putText(canvas, "Email Address", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
    cv2.putText(canvas, "user@domain.com", (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)
    cv2.putText(canvas, "Submit", (100, 350), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)

    tokens = extract_full_page_text_tokens(canvas)
    print(f"Extracted {len(tokens)} full-page tokens:")
    for t in tokens:
        print("  ", t)

    assert len(tokens) >= 3, f"Expected at least 3 tokens, got {len(tokens)}"
    
    # Check token schema contract: {"text": str, "box": [ymin, xmin, ymax, xmax], "confidence": float, "center": (cx, cy)}
    for tok in tokens:
        assert "text" in tok and isinstance(tok["text"], str)
        assert "box" in tok and len(tok["box"]) == 4
        assert "confidence" in tok and isinstance(tok["confidence"], float)
        assert "center" in tok and len(tok["center"]) == 2
        ymin, xmin, ymax, xmax = tok["box"]
        cx, cy = tok["center"]
        assert ymin <= ymax
        assert xmin <= xmax
        assert round(cx, 1) == round((xmin + xmax) / 2.0, 1)
        assert round(cy, 1) == round((ymin + ymax) / 2.0, 1)

    all_texts = " ".join(t["text"] for t in tokens)
    assert "Email" in all_texts or "Address" in all_texts
    assert "user@domain.com" in all_texts or "@" in all_texts
    assert "Submit" in all_texts
    print("  [OK] Full-canvas token extraction and schema validation passed")


def test_spatial_proximity_matcher():
    print("\n--- Test 2: Spatial Proximity Matcher (Inside Box & Label Above) ---")
    ocr = get_ocr_service()

    # Synthesize tokens manually to test deterministic geometric proximity matching
    tokens = [
        # Label above input box 1 (delta_y = 20px, horizontal overlap 100%)
        {
            "text": "Email",
            "box": [60, 50, 80, 120],  # ymin=60, xmin=50, ymax=80, xmax=120
            "confidence": 0.98,
            "center": (85.0, 70.0)
        },
        # Inside input box 1
        {
            "text": "user@gmail.com",
            "box": [115, 60, 135, 220],  # ymin=115, xmin=60, ymax=135, xmax=220
            "confidence": 0.95,
            "center": (140.0, 125.0)
        },
        # Label above input box 2 (Password)
        {
            "text": "Password",
            "box": [165, 50, 185, 150],  # ymin=165, xmin=50, ymax=185, xmax=150
            "confidence": 0.96,
            "center": (100.0, 175.0)
        },
        # Inside button box
        {
            "text": "Sign In",
            "box": [295, 80, 325, 170],  # ymin=295, xmin=80, ymax=325, xmax=170
            "confidence": 0.99,
            "center": (125.0, 310.0)
        }
    ]

    elements = [
        # Element 1: Misclassified as Button by YOLO, but has "Email" above and "user@gmail.com" inside
        {
            "name": "Button",
            "conf": "91%",
            "box": [100, 40, 150, 350],  # ymin=100, xmin=40, ymax=150, xmax=350 (h=50, w=310)
            "x1": 40, "y1": 100, "x2": 350, "y2": 150, "w": 310, "h": 50
        },
        # Element 2: Empty box misclassified as Button, but has "Password" label above (delta_y = 200 - 185 = 15px <= 40px)
        {
            "name": "Button",
            "conf": "88%",
            "box": [200, 40, 250, 350],  # ymin=200, xmin=40, ymax=250, xmax=350 (h=50, w=310)
            "x1": 40, "y1": 200, "x2": 350, "y2": 250, "w": 310, "h": 50
        },
        # Element 3: Real Button with "Sign In"
        {
            "name": "Button",
            "conf": "94%",
            "box": [280, 40, 340, 220],  # ymin=280, xmin=40, ymax=340, xmax=220 (h=60, w=180)
            "x1": 40, "y1": 280, "x2": 220, "y2": 340, "w": 180, "h": 60
        }
    ]

    matched = ocr.match_spatial_tokens(elements, tokens)

    # Element 1 verification:
    el1 = matched[0]
    assert el1["text"] == "user@gmail.com", f"Expected 'user@gmail.com', got {el1.get('text')}"
    assert el1["label_above"] == "Email", f"Expected 'Email', got {el1.get('label_above')}"

    # Element 2 verification:
    el2 = matched[1]
    assert el2["text"] is None
    assert el2["label_above"] == "Password", f"Expected 'Password', got {el2.get('label_above')}"

    # Element 3 verification:
    el3 = matched[2]
    assert el3["text"] == "Sign In", f"Expected 'Sign In', got {el3.get('text')}"
    assert el3["label_above"] is None

    print("  [OK] Spatial inside and label-above proximity matching verified")


def test_deterministic_reclassification_and_guardrails():
    print("\n--- Test 3: Deterministic Re-Classification & Keyword Guardrails ---")
    elements = [
        # Button with email text -> MUST reclassify to TextBox
        {
            "name": "Button",
            "conf": "90%",
            "text": "test@domain.com",
            "label_above": "Email Address",
            "box": [100, 40, 150, 350],
            "x1": 40, "y1": 100, "x2": 350, "y2": 150, "w": 310, "h": 50
        },
        # Button with empty text but "Password" label above -> MUST reclassify to TextBox
        {
            "name": "Button",
            "conf": "85%",
            "text": None,
            "label_above": "Password",
            "box": [170, 40, 220, 350],
            "x1": 40, "y1": 170, "x2": 350, "y2": 220, "w": 310, "h": 50
        },
        # Action button "Sign In" -> MUST stay Button, variant='primary'
        {
            "name": "Button",
            "conf": "94%",
            "text": "Sign In",
            "box": [240, 40, 290, 200],
            "x1": 40, "y1": 240, "x2": 200, "y2": 290, "w": 160, "h": 50
        },
        # Standalone title text -> MUST classify as Heading
        {
            "name": "container",
            "conf": "80%",
            "text": "Welcome Back",
            "box": [20, 40, 60, 400],
            "x1": 40, "y1": 20, "x2": 400, "y2": 60, "w": 360, "h": 40
        },
        # Empty elongated horizontal box with h=45, w=250 without text -> Reclassifies to TextBox
        {
            "name": "Button",
            "conf": "70%",
            "text": None,
            "box": [320, 40, 365, 290],
            "x1": 40, "y1": 320, "x2": 290, "y2": 365, "w": 250, "h": 45
        }
    ]

    reclassified = apply_semantic_reclassification(elements)

    # Verify Element 1 (Email)
    assert reclassified[0]["class_name"] == "TextBox"
    assert reclassified[0]["name"] == "TextBox"
    assert reclassified[0]["placeholder"] == "test@domain.com"

    # Verify Element 2 (Password)
    assert reclassified[1]["class_name"] == "TextBox"
    assert reclassified[1]["name"] == "TextBox"
    assert reclassified[1]["placeholder"] == "Password"

    # Verify Element 3 (Button: Sign In)
    assert reclassified[2]["class_name"] == "Button"
    assert reclassified[2]["name"] == "Button"
    assert reclassified[2]["variant"] == "primary"

    # Verify Element 4 (Heading: Welcome Back)
    assert reclassified[3]["class_name"] == "Heading"
    assert reclassified[3]["name"] == "Heading"

    # Verify Element 5 (Elongated empty box)
    assert reclassified[4]["class_name"] == "TextBox"
    assert reclassified[4]["name"] == "TextBox"

    print("  [OK] All deterministic re-classifications and geometric guardrails verified")


def test_synthesized_jsx_with_reclassified_form():
    print("\n--- Test 4: Synthesized JSX Verification for Reclassified Form ---")
    elements = [
        {
            "name": "Heading",
            "text": "Welcome Back",
            "box": [20, 40, 60, 400],
            "x1": 40, "y1": 20, "x2": 400, "y2": 60, "w": 360, "h": 40
        },
        # Misclassified as Button, has email placeholder
        {
            "name": "Button",
            "text": "user@example.com",
            "box": [80, 40, 125, 400],
            "x1": 40, "y1": 80, "x2": 400, "y2": 125, "w": 360, "h": 45
        },
        # Misclassified as Button, has Password label above
        {
            "name": "Button",
            "label_above": "Password",
            "box": [140, 40, 185, 400],
            "x1": 40, "y1": 140, "x2": 400, "y2": 185, "w": 360, "h": 45
        },
        # Primary Action Button
        {
            "name": "Button",
            "text": "Login",
            "box": [200, 40, 245, 240],
            "x1": 40, "y1": 200, "x2": 240, "y2": 245, "w": 200, "h": 45
        }
    ]

    res = synthesize_layout_code(elements, project_name="LoginForm")
    jsx = res["jsx"]
    print("Synthesized JSX:\n" + jsx)

    assert "Welcome Back</h1>" in jsx or "Welcome Back</h2>" in jsx
    assert 'placeholder="user@example.com"' in jsx
    assert 'placeholder="Password"' in jsx
    assert ">Login</button>" in jsx
    print("  [OK] Form JSX correctly synthesized inputs and buttons")


if __name__ == "__main__":
    test_full_image_spatial_ocr_extraction()
    test_spatial_proximity_matcher()
    test_deterministic_reclassification_and_guardrails()
    test_synthesized_jsx_with_reclassified_form()
    print("\n======================================================================")
    print("        ALL PHASE 1 ARCHITECTURAL TESTS PASSED!                       ")
    print("======================================================================")
