"""
Sprint Validation Suite for Phase 2:
Hybrid Multimodal Vision-LLM Reasoning Engine & Local CV Fallback Strategy
Location: test_phase2_multimodal.py
"""
import io
import os
import json
import numpy as np
import cv2
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.services.multimodal_service import get_multimodal_service, MultimodalVisionService
from app.services.heuristic_service import synthesize_vlm_ast

client = TestClient(app)

SAMPLE_VLM_AST = {
    "screen_type": "Authentication",
    "theme": "dark_glassmorphic",
    "screen_meta": {
        "title": "Welcome Back",
        "screen_type": "Authentication",
        "theme": "dark_glassmorphic"
    },
    "components": [
        {
            "type": "heading",
            "text": "Sign In to Sketch2UI",
            "level": 1
        },
        {
            "type": "text_input",
            "label": "Email Address",
            "placeholder": "user@example.com",
            "input_type": "email"
        },
        {
            "type": "text_input",
            "label": "Password",
            "placeholder": "••••••••",
            "input_type": "password"
        },
        {
            "type": "row",
            "elements": [
                {
                    "type": "checkbox",
                    "label": "Remember me",
                    "checked": False
                },
                {
                    "type": "link",
                    "text": "Forgot Password?",
                    "href": "#forgot"
                }
            ]
        },
        {
            "type": "button",
            "text": "SIGN IN",
            "variant": "primary"
        }
    ]
}


def _create_synthetic_image_bytes():
    """Generates a dummy test image in PNG format."""
    img = np.ones((400, 400, 3), dtype=np.uint8) * 255
    cv2.rectangle(img, (40, 40), (360, 90), (0, 0, 0), 2)
    cv2.rectangle(img, (40, 110), (360, 160), (0, 0, 0), 2)
    cv2.rectangle(img, (40, 180), (360, 230), (0, 0, 0), -1)
    _, buf = cv2.imencode(".png", img)
    return buf.tobytes()


def test_vlm_ast_to_jsx_synthesis():
    print("\n--- Test 1: VLM AST to Production JSX Synthesizer ---")
    gen = synthesize_vlm_ast(SAMPLE_VLM_AST, project_name="Login Portal")

    assert gen["framework"] == "React + Tailwind"
    jsx = gen["jsx"]
    tailwind = gen["tailwind"]

    # Component declaration
    assert "export default function LoginPortal()" in jsx

    # Heading assertion
    assert "Sign In to Sketch2UI" in jsx
    assert '<h1 className="text-lg font-bold tracking-tight text-white">Sign In to Sketch2UI</h1>' in jsx

    # Separate label + typed input assertions
    assert '<label className="block text-xs font-medium text-zinc-300">Email Address</label>' in jsx
    assert 'type="email"' in jsx
    assert 'placeholder="user@example.com"' in jsx

    assert '<label className="block text-xs font-medium text-zinc-300">Password</label>' in jsx
    assert 'type="password"' in jsx
    assert 'placeholder="••••••••"' in jsx

    # Checkbox + Link row assertion
    assert '<div className="flex items-center justify-between py-1">' in jsx
    assert '<input type="checkbox"' in jsx
    assert "Remember me" in jsx
    assert '<a href="#forgot"' in jsx
    assert "Forgot Password?" in jsx

    # Primary Action Button assertion with exact casing
    assert ">SIGN IN</button>" in jsx
    assert "bg-cyan-500" in jsx

    # Tailwind markup sanity
    assert '<h1 class="text-lg font-bold tracking-tight text-white">Sign In to Sketch2UI</h1>' in tailwind
    assert 'type="email"' in tailwind
    assert 'type="password"' in tailwind
    assert "SIGN IN" in tailwind

    print("  [OK] Synthesized JSX contains separate labels, type='email', type='password', row flexbox, and SIGN IN button.")


def test_ast_to_detected_elements_conversion():
    print("\n--- Test 2: AST to Detected Elements Mapping Contract ---")
    svc = get_multimodal_service()
    elements = svc.ast_to_detected_elements(SAMPLE_VLM_AST)

    assert len(elements) == 6, f"Expected 6 detected elements, got {len(elements)}"

    # Element 0: Heading
    assert elements[0]["name"] == "Heading"
    assert elements[0]["class_name"] == "Heading"
    assert elements[0]["text"] == "Sign In to Sketch2UI"

    # Element 1: Email TextBox
    assert elements[1]["name"] == "TextBox"
    assert elements[1]["label_above"] == "Email Address"
    assert elements[1]["placeholder"] == "user@example.com"
    assert elements[1]["type"] == "email"

    # Element 2: Password TextBox
    assert elements[2]["name"] == "TextBox"
    assert elements[2]["label_above"] == "Password"
    assert elements[2]["placeholder"] == "••••••••"
    assert elements[2]["type"] == "password"

    # Element 3 & 4: Row elements (CheckBox & Link)
    assert elements[3]["name"] == "CheckBox"
    assert elements[3]["text"] == "Remember me"

    assert elements[4]["name"] == "Link"
    assert elements[4]["text"] == "Forgot Password?"

    # Element 5: Primary Action Button
    assert elements[5]["name"] == "Button"
    assert elements[5]["text"] == "SIGN IN"
    assert elements[5]["variant"] == "primary"

    # Check that bounding boxes are valid [ymin, xmin, ymax, xmax]
    for el in elements:
        box = el["box"]
        assert len(box) == 4
        assert box[2] > box[0]
        assert box[3] > box[1]

    print("  [OK] AST detected elements properly mapped with labels, types, and bounding coordinates.")


def test_markdown_fence_cleaning():
    print("\n--- Test 3: AST Response Cleaner & Markdown Fence Removal ---")
    svc = get_multimodal_service()

    raw_fenced_json = f"""```json
{json.dumps(SAMPLE_VLM_AST)}
```"""
    parsed = svc._parse_and_validate_ast(raw_fenced_json)
    assert parsed["screen_type"] == "Authentication"
    assert len(parsed["components"]) == 5

    raw_plain_json = json.dumps(SAMPLE_VLM_AST)
    parsed_plain = svc._parse_and_validate_ast(raw_plain_json)
    assert parsed_plain["screen_type"] == "Authentication"
    assert len(parsed_plain["components"]) == 5
    print("  [OK] Markdown fences ```json stripped safely.")


def test_endpoint_with_vlm_enabled():
    print("\n--- Test 4: Endpoint Invocation with VLM Enabled ---")
    img_bytes = _create_synthetic_image_bytes()

    original_key = os.environ.get("GEMINI_API_KEY")
    os.environ["GEMINI_API_KEY"] = "mock_test_key_phase2"

    svc = get_multimodal_service()
    svc.api_key = "mock_test_key_phase2"

    with patch.object(MultimodalVisionService, "analyze_sketch", return_value=SAMPLE_VLM_AST):
        response = client.post(
            "/api/v1/sketch/predict",
            files={"file": ("login_screen.png", img_bytes, "image/png")}
        )

    # Clean up env
    if original_key is not None:
        os.environ["GEMINI_API_KEY"] = original_key
    else:
        os.environ.pop("GEMINI_API_KEY", None)
    svc.api_key = original_key

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()

    assert data["status"] == "success"
    assert data["engine_used"] == "multimodal_vision"
    assert data["project_name"] == "Login Screen"
    assert data["elements_count"] == 6

    jsx = data["generated_code"]["jsx"]
    assert '<input type="email"' in jsx
    assert '<input type="password"' in jsx
    assert ">SIGN IN</button>" in jsx
    print("  [OK] predict endpoint successfully routed to Multimodal Vision reasoning engine.")


def test_endpoint_graceful_fallback_when_api_key_missing():
    print("\n--- Test 5: Graceful Fallback to Local YOLO/OCR Engine when API Key Absent ---")
    img_bytes = _create_synthetic_image_bytes()

    # Clear all potential multimodal API keys
    saved_keys = {}
    for k in ["GEMINI_API_KEY", "VISION_LLM_API_KEY", "MULTIMODAL_API_KEY"]:
        saved_keys[k] = os.environ.pop(k, None)

    svc = get_multimodal_service()
    svc.api_key = None

    response = client.post(
        "/api/v1/sketch/predict",
        files={"file": ("sketch.png", img_bytes, "image/png")}
    )

    # Restore keys
    for k, v in saved_keys.items():
        if v is not None:
            os.environ[k] = v
    svc.api_key = saved_keys.get("GEMINI_API_KEY")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()

    assert data["status"] == "success"
    assert data["engine_used"] == "local_cv_fallback"
    assert "generated_code" in data
    assert "jsx" in data["generated_code"]
    print(f"  [OK] Local CV engine gracefully ran with engine_used='{data['engine_used']}'.")


def test_endpoint_graceful_fallback_on_network_or_api_exception():
    print("\n--- Test 6: Graceful Fallback on VLM Network/API Exception ---")
    img_bytes = _create_synthetic_image_bytes()

    original_key = os.environ.get("GEMINI_API_KEY")
    os.environ["GEMINI_API_KEY"] = "mock_test_key_failing"

    svc = get_multimodal_service()
    svc.api_key = "mock_test_key_failing"

    with patch.object(MultimodalVisionService, "analyze_sketch", side_effect=RuntimeError("Google GenAI 503 Service Unavailable")):
        response = client.post(
            "/api/v1/sketch/predict",
            files={"file": ("sketch.png", img_bytes, "image/png")}
        )

    # Restore key
    if original_key is not None:
        os.environ["GEMINI_API_KEY"] = original_key
    else:
        os.environ.pop("GEMINI_API_KEY", None)
    svc.api_key = original_key

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()

    assert data["status"] == "success"
    assert data["engine_used"] == "local_cv_fallback"
    assert "generated_code" in data
    print("  [OK] Network/API exception caught and seamlessly fallen back to local YOLO + OCR pipeline.")


if __name__ == "__main__":
    test_vlm_ast_to_jsx_synthesis()
    test_ast_to_detected_elements_conversion()
    test_markdown_fence_cleaning()
    test_endpoint_with_vlm_enabled()
    test_endpoint_graceful_fallback_when_api_key_missing()
    test_endpoint_graceful_fallback_on_network_or_api_exception()
    print("\n=======================================================")
    print("  ALL 6 MULTIMODAL VISION TESTS PASSED SUCCESSFULLY!   ")
    print("=======================================================")
