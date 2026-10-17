"""
Sprint 2 Validation Suite:
Handwritten Text OCR Pipeline & Dynamic JSX Text Injection
Location: test_ocr_pipeline.py
"""
import cv2
import numpy as np
from app.services.ocr_service import get_ocr_service, OCRService
from app.services.heuristic_service import synthesize_layout_code


def test_ocr_singleton_and_warmup():
    print("\n--- Test 1: OCR Singleton & Latency Guard ---")
    s1 = get_ocr_service()
    s2 = get_ocr_service()
    assert s1 is s2, "OCRService should be a singleton instance"
    assert s1._reader is not None, "OCR reader should be initialized"
    s1.warmup()
    print("  [OK] Singleton instance verified and warmed up")


def test_text_cleaning_and_noise_filtering():
    print("\n--- Test 2: Punctuation Noise & Stray Dot Sanitization ---")
    ocr = get_ocr_service()

    # Stray scratch marks, underlines, and quotes
    assert ocr.clean_extracted_text("__Submit--") == "Submit"
    assert ocr.clean_extracted_text("..Sign In..") == "Sign In"
    assert ocr.clean_extracted_text("'''Email Address'''") == "Email Address"
    # Preserves question mark
    assert ocr.clean_extracted_text("Forgot Password?") == "Forgot Password?"
    # Stray noise characters only
    assert ocr.clean_extracted_text("...") == ""
    assert ocr.clean_extracted_text("---") == ""
    assert ocr.clean_extracted_text(" ,; ") == ""
    print("  [OK] Noise filtering and punctuation stripping verified")


def test_real_crop_ocr_recognition():
    print("\n--- Test 3: OCR Extraction from Synthetic Text Crop ---")
    ocr = get_ocr_service()

    # Create synthetic white image crop with clean handwritten/printed-like text
    crop = np.ones((80, 260, 3), dtype=np.uint8) * 255
    cv2.putText(
        crop, "Sign In", (20, 50),
        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 3, cv2.LINE_AA
    )

    text, conf = ocr.extract_text_from_crop(crop)
    print(f"Recognized text: '{text}', confidence: {conf:.2f}")

    assert "Sign" in text or "In" in text, f"Expected 'Sign In' in '{text}'"
    assert conf >= 0.40, f"Expected confidence >= 0.40, got {conf}"
    print("  [OK] Text successfully recognized from bounding box crop")


def test_batch_extraction_and_confidence_fallback():
    print("\n--- Test 4: Batch Component Text Extraction & Confidence Fallback ---")
    ocr = get_ocr_service()

    # Create synthetic canvas with 2 elements: one with clear text, one with blank/noise
    canvas = np.ones((400, 600, 3), dtype=np.uint8) * 255

    # Button area with text 'Submit'
    cv2.putText(
        canvas, "Submit", (80, 100),
        cv2.FONT_HERSHEY_SIMPLEX, 1.1, (10, 10, 10), 3, cv2.LINE_AA
    )

    detected = [
        # Button with text
        {
            "name": "Button",
            "conf": "95%",
            "x1": 50,
            "y1": 50,
            "w": 220,
            "h": 80,
            "box": [50, 50, 130, 270]
        },
        # Blank input box without text (should fall back cleanly to None)
        {
            "name": "TextBox",
            "conf": "90%",
            "x1": 50,
            "y1": 180,
            "w": 300,
            "h": 60,
            "box": [180, 50, 240, 350]
        },
        # Non-text component (Image) - should NOT run OCR
        {
            "name": "Image",
            "conf": "98%",
            "x1": 50,
            "y1": 260,
            "w": 300,
            "h": 120,
            "box": [260, 50, 380, 350]
        }
    ]

    enriched = ocr.batch_extract_component_texts(canvas, detected)

    # 1. Button got recognized text
    btn_elem = enriched[0]
    print(f"Button text: '{btn_elem.get('text')}', OCR conf: {btn_elem.get('ocr_conf')}")
    assert btn_elem.get("text") is not None
    assert "Submit" in btn_elem["text"]
    assert btn_elem.get("ocr_conf", 0) >= 0.40

    # 2. Blank text box got safe fallback (None)
    txt_elem = enriched[1]
    print(f"Blank input text: '{txt_elem.get('text')}', OCR conf: {txt_elem.get('ocr_conf')}")
    assert txt_elem.get("text") is None
    assert txt_elem.get("ocr_conf") == 0.0

    # 3. Image got skipped
    img_elem = enriched[2]
    assert img_elem.get("text") is None
    print("  [OK] Batch extraction and honest confidence fallback verified")


def test_dynamic_jsx_text_injection():
    print("\n--- Test 5: Dynamic JSX Text Injection with Fallback ---")
    detected = [
        # Heading with extracted text
        {
            "name": "Heading",
            "conf": "95%",
            "text": "User Authentication",
            "box": [20, 40, 60, 440],
            "x1": 40,
            "y1": 20,
            "x2": 440,
            "y2": 60,
        },
        # TextBox with extracted placeholder
        {
            "name": "TextBox",
            "conf": "92%",
            "text": "yourname@company.com",
            "box": [80, 40, 125, 440],
            "x1": 40,
            "y1": 80,
            "x2": 440,
            "y2": 125,
        },
        # Button with extracted text
        {
            "name": "Button",
            "conf": "94%",
            "text": "Sign In Now",
            "box": [150, 40, 195, 240],
            "x1": 40,
            "y1": 150,
            "x2": 240,
            "y2": 195,
        },
        # Link with extracted text
        {
            "name": "Link",
            "conf": "90%",
            "text": "Forgot Password?",
            "box": [210, 40, 240, 300],
            "x1": 40,
            "y1": 210,
            "x2": 300,
            "y2": 240,
        },
        # Button WITHOUT extracted text (tests semantic fallback)
        {
            "name": "Button",
            "conf": "91%",
            "text": None,
            "box": [260, 40, 305, 200],
            "x1": 40,
            "y1": 260,
            "x2": 200,
            "y2": 305,
        }
    ]

    result = synthesize_layout_code(detected, project_name="AuthScreen")
    jsx = result["jsx"]
    tailwind = result["tailwind"]

    print("Synthesized JSX with Extracted Text:")
    print(jsx)

    # Verify injected heading
    assert "User Authentication" in jsx
    # Verify injected input placeholder
    assert 'placeholder="yourname@company.com"' in jsx
    # Verify injected button text
    assert ">Sign In Now</button>" in jsx
    # Verify injected link text
    assert "Forgot Password? &rarr;</a>" in jsx
    # Verify fallback button text
    assert ">Submit Request</button>" in jsx or ">Get Started</button>" in jsx

    # Verify Tailwind HTML equivalent
    assert "User Authentication" in tailwind
    assert 'placeholder="yourname@company.com"' in tailwind
    assert ">Sign In Now</button>" in tailwind
    print("  [OK] Injected dynamic text and semantic fallbacks verified in JSX and Tailwind")


def test_api_predict_with_ocr():
    print("\n--- Test 6: FastAPI /api/v1/sketch/predict with OCR ---")
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    # Create canvas with 'Register' button
    img = np.ones((400, 500, 3), dtype=np.uint8) * 255
    cv2.putText(
        img, "Register", (100, 150),
        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 3, cv2.LINE_AA
    )
    _, encoded = cv2.imencode(".png", img)

    response = client.post(
        "/api/v1/sketch/predict",
        files={"file": ("register_mock.png", encoded.tobytes(), "image/png")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "detected_elements" in data
    assert "generated_code" in data
    print("  [OK] Full API predict flow with OCR completed successfully")


if __name__ == "__main__":
    test_ocr_singleton_and_warmup()
    test_text_cleaning_and_noise_filtering()
    test_real_crop_ocr_recognition()
    test_batch_extraction_and_confidence_fallback()
    test_dynamic_jsx_text_injection()
    test_api_predict_with_ocr()
    print("\n======================================================================")
    print("        ALL 6 SPRINT 2 OCR VALIDATION TESTS PASSED!                   ")
    print("======================================================================")
