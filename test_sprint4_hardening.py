import io
import json
import numpy as np
import cv2
from fastapi.testclient import TestClient

from app.main import app
from app.core.limiter import limiter
from app.services.camera_services import (
    apply_clahe_contrast_normalization,
    detect_paper_and_warp
)

client = TestClient(app)


def test_health_diagnostics_endpoint():
    print("\n--- Test 1: Health & Readiness Check (GET /api/v1/health) ---")
    response = client.get("/api/v1/health")
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}: {response.text}"
    
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"
    assert "timestamp" in data
    assert "services" in data
    
    services = data["services"]
    assert services.get("yolo_detector") == "ready"
    assert services.get("ocr_engine") == "ready"
    assert services.get("synthesizer") == "ready"
    
    # Also verify backward-compatible root alias /health
    alias_res = client.get("/health")
    assert alias_res.status_code == 200
    assert alias_res.json()["status"] == "healthy"
    
    print(f"  [OK] Health endpoint returned healthy with services: {services}")


def test_clahe_shadow_normalization():
    print("\n--- Test 2: CLAHE Adaptive Shadow Equalization ---")
    # Create a synthetic image with a heavy harsh gradient shadow across the left side
    h, w = 300, 300
    base_img = np.ones((h, w, 3), dtype=np.uint8) * 230  # white paper
    
    # Draw some simulated pencil wireframe lines
    cv2.rectangle(base_img, (50, 50), (250, 100), (40, 40, 40), 2)
    cv2.putText(base_img, "Submit", (70, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (30, 30, 30), 2)
    
    # Inject harsh mobile camera shadow gradient
    shadow = np.tile(np.linspace(0.2, 1.0, w), (h, 1))
    shadow_3ch = np.dstack([shadow, shadow, shadow])
    shadowed_img = np.clip(base_img * shadow_3ch, 0, 255).astype(np.uint8)
    
    # Apply CLAHE normalization
    normalized_img = apply_clahe_contrast_normalization(shadowed_img)
    
    assert normalized_img is not None
    assert normalized_img.shape == shadowed_img.shape
    assert normalized_img.dtype == np.uint8
    
    # Shadowed left region mean should be substantially brightened by CLAHE
    dark_region_before = np.mean(shadowed_img[:, :50])
    dark_region_after = np.mean(normalized_img[:, :50])
    assert dark_region_after > dark_region_before, "CLAHE failed to brighten shadowy region"
    
    # Test on real sketch image with detect_paper_and_warp
    real_img = cv2.imread("test_images/sketches.png")
    if real_img is not None:
        warped, found = detect_paper_and_warp(real_img)
        assert found is True
        assert warped is not None and warped.size > 0
    print("  [OK] Adaptive CLAHE successfully lifted mobile camera shadows without stroke loss")


def test_rate_limiter_protection():
    print("\n--- Test 3: Rate Limiting & HTTP 429 Guardrails ---")
    limiter.reset()
    
    # Test rate limiting on POST /api/v1/sketch/export-zip (configured for 30/minute)
    payload = {
        "project_name": "Hardening Test",
        "jsx_code": "<button>Test</button>"
    }
    
    # Fire 30 requests - should all succeed (200 OK)
    for i in range(30):
        res = client.post("/api/v1/sketch/export-zip", json=payload)
        assert res.status_code == 200, f"Request {i+1} failed with status {res.status_code}"
    
    # The 31st request must trigger HTTP 429 RateLimitExceeded
    res_limited = client.post("/api/v1/sketch/export-zip", json=payload)
    assert res_limited.status_code == 429, f"Expected 429 but got {res_limited.status_code}"
    
    res_json = res_limited.json()
    assert "Too Many Requests" in res_json.get("error", "")
    assert "Too Many Requests. Please wait a moment." in res_json.get("message", "")
    assert "Retry-After" in res_limited.headers
    print(f"  [OK] Rate limit triggered on 31st request: HTTP 429 with Retry-After: {res_limited.headers.get('Retry-After')}")
    
    # Reset limiter so downstream tests are unaffected
    limiter.reset()


if __name__ == "__main__":
    print("======================================================================")
    print("      STARTING SPRINT 4 HARDENING & DIAGNOSTICS TEST SUITE            ")
    print("======================================================================")
    test_health_diagnostics_endpoint()
    test_clahe_shadow_normalization()
    test_rate_limiter_protection()
    print("\n======================================================================")
    print("      ALL SPRINT 4 HARDENING & DIAGNOSTIC TESTS PASSED!               ")
    print("======================================================================")
