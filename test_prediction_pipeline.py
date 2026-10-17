"""
Comprehensive Validation Test for Priority 3:
FastAPI Prediction Endpoint, Vision Pipeline Integration, and React Code Synthesizer
"""
import io
import json
import numpy as np
import cv2
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_endpoint_with_real_sketch():
    print("\n--- Test 1: Real Sketch Image ('test_images/sketches.png') ---")
    with open("test_images/sketches.png", "rb") as img_file:
        response = client.post(
            "/api/v1/sketch/predict",
            files={"file": ("sketches.png", img_file, "image/png")}
        )

    print(f"Status Code: {response.status_code}")
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}: {response.text}"
    
    data = response.json()
    assert data["status"] == "success", "Expected status == success"
    assert "project_name" in data, "Missing project_name in response"
    assert "elements_count" in data, "Missing elements_count in response"
    assert "detected_elements" in data, "Missing detected_elements in response"
    assert "generated_code" in data, "Missing generated_code in response"

    gen_code = data["generated_code"]
    assert gen_code["framework"] == "React + Tailwind", "Expected React + Tailwind framework"
    assert "jsx" in gen_code and len(gen_code["jsx"]) > 0, "JSX code is empty"
    assert "tailwind" in gen_code and len(gen_code["tailwind"]) > 0, "Tailwind code is empty"
    assert "json" in gen_code and len(gen_code["json"]) > 0, "AST JSON is empty"

    # Verify glassmorphic card container in JSX
    assert "rounded-3xl" in gen_code["jsx"]
    assert "bg-[#090b10]/90" in gen_code["jsx"]

    print(f"Project Name: {data['project_name']}")
    print(f"Elements Detected: {data['elements_count']}")
    print(f"First 3 Elements: {data['detected_elements'][:3]}")
    print("JSX Sample:\n" + "\n".join(gen_code["jsx"].splitlines()[:12]))
    print("Test 1 Passed Successfully!")


def test_endpoint_with_synthetic_image():
    print("\n--- Test 2: Synthetic Clean UI Sketch Image ---")
    # Generate clean white background with black wireframe shapes
    img = np.ones((500, 500, 3), dtype=np.uint8) * 255
    # Heading area
    cv2.rectangle(img, (50, 40), (450, 80), (0, 0, 0), 2)
    # Input field
    cv2.rectangle(img, (50, 110), (450, 160), (0, 0, 0), 2)
    # Button
    cv2.rectangle(img, (150, 200), (350, 250), (0, 0, 0), -1)
    # Image box
    cv2.rectangle(img, (50, 280), (450, 440), (0, 0, 0), 2)

    _, encoded_png = cv2.imencode(".png", img)
    img_bytes = encoded_png.tobytes()

    response = client.post(
        "/api/v1/sketch/predict",
        files={"file": ("wireframe_mock.png", io.BytesIO(img_bytes), "image/png")}
    )

    print(f"Status Code: {response.status_code}")
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"
    data = response.json()
    assert data["status"] == "success"
    assert data["project_name"] == "Wireframe Mock"
    print(f"Elements Count: {data['elements_count']}")
    print(f"Generated JSX Lines: {len(data['generated_code']['jsx'].splitlines())}")
    print("Test 2 Passed Successfully!")


def test_invalid_mime_type():
    print("\n--- Test 3: Invalid MIME Type Rejection ---")
    dummy_text = b"not an image"
    response = client.post(
        "/api/v1/sketch/predict",
        files={"file": ("test.txt", io.BytesIO(dummy_text), "text/plain")}
    )
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 400, "Expected 400 for invalid MIME type"
    print(f"Detail: {response.json().get('detail')}")
    print("Test 3 Passed Successfully!")


def test_empty_file():
    print("\n--- Test 4: Empty File Rejection ---")
    response = client.post(
        "/api/v1/sketch/predict",
        files={"file": ("empty.png", io.BytesIO(b""), "image/png")}
    )
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 400, "Expected 400 for empty file"
    print("Test 4 Passed Successfully!")


def test_cors_headers():
    print("\n--- Test 5: CORS Headers for http://localhost:5173 ---")
    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type"
    }
    response = client.options("/api/v1/sketch/predict", headers=headers)
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 200
    allow_origin = response.headers.get("access-control-allow-origin")
    print(f"Access-Control-Allow-Origin: {allow_origin}")
    assert allow_origin in ["http://localhost:5173", "*"]
    print("Test 5 Passed Successfully!")


def test_legacy_routes_intact():
    print("\n--- Test 6: Legacy Working Routes Preserved ---")
    # GET /
    root_res = client.get("/")
    assert root_res.status_code == 200
    assert "message" in root_res.json()

    # POST /api/v1/predict
    payload = {"boxes": [[20, 30, 250, 60], [20, 100, 320, 45]]}
    pred_res = client.post("/api/v1/predict", json=payload)
    assert pred_res.status_code == 200
    assert pred_res.json()["status"] == "success"
    print("All legacy routes verified working!")
    print("Test 6 Passed Successfully!")


if __name__ == "__main__":
    test_endpoint_with_real_sketch()
    test_endpoint_with_synthetic_image()
    test_invalid_mime_type()
    test_empty_file()
    test_cors_headers()
    test_legacy_routes_intact()
    print("\n==============================================")
    print("  ALL 6 VALIDATION TESTS PASSED SUCCESSFULLY! ")
    print("==============================================")
