import io
import json
import zipfile
from fastapi.testclient import TestClient

from app.main import app
from app.services.export_service import generate_project_zip, sanitize_project_name, sanitize_package_name

client = TestClient(app)

SAMPLE_JSX = """import React from "react";

export default function MobileCheckout() {
  return (
    <div className="w-full max-w-md mx-auto p-6 rounded-3xl bg-[#090b10] border border-white/10 space-y-4">
      <h2 className="text-xl font-bold text-white">Payment Method</h2>
      <div className="flex flex-col sm:flex-row gap-4 w-full">
        <input placeholder="First Name" className="flex-1 w-full p-2.5 rounded-xl bg-white/5 border border-white/10 text-white" />
        <input placeholder="Last Name" className="flex-1 w-full p-2.5 rounded-xl bg-white/5 border border-white/10 text-white" />
      </div>
      <button className="w-full py-3 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-black font-semibold">Pay Now</button>
    </div>
  );
}
"""


def test_sanitize_utilities():
    print("\n--- Test 1: Project Name Sanitization Utilities ---")
    assert sanitize_project_name("Mobile Checkout Wireframe") == "mobile_checkout_wireframe"
    assert sanitize_project_name("Test @ App #123! & More") == "test_app_123_more"
    assert sanitize_project_name("") == "wireframe"
    assert sanitize_project_name("   ") == "wireframe"
    assert sanitize_package_name("My Cool UI") == "sketch2ui-my-cool-ui"
    print("  [OK] Name and package sanitization verified")


def test_generate_project_zip_in_memory():
    print("\n--- Test 2: In-Memory ZIP Generation ---")
    zip_buffer = generate_project_zip("Mobile Checkout Wireframe", SAMPLE_JSX)
    assert isinstance(zip_buffer, io.BytesIO)
    
    # Read the generated ZIP in memory
    zf = zipfile.ZipFile(zip_buffer, mode="r")
    namelist = zf.namelist()
    
    expected_files = [
        "index.html",
        "package.json",
        "vite.config.js",
        "README.md",
        "src/main.jsx",
        "src/index.css",
        "src/App.jsx"
    ]
    
    for f in expected_files:
        assert f in namelist, f"Missing {f} in generated ZIP"
        content = zf.read(f).decode("utf-8")
        assert len(content) > 0, f"File {f} is empty in generated ZIP"
    
    # Verify package.json validity
    pkg_json = json.loads(zf.read("package.json").decode("utf-8"))
    assert pkg_json["name"] == "sketch2ui-mobile-checkout-wireframe"
    assert "react" in pkg_json["dependencies"]
    assert "@tailwindcss/vite" in pkg_json["devDependencies"]
    
    # Verify App.jsx content
    app_jsx = zf.read("src/App.jsx").decode("utf-8")
    assert "MobileCheckout" in app_jsx
    assert "export default" in app_jsx

    # Verify index.html content
    index_html = zf.read("index.html").decode("utf-8")
    assert "<div id=\"root\"></div>" in index_html
    assert "/src/main.jsx" in index_html
    print("  [OK] In-memory ZIP structure and file contents verified")


def test_export_zip_api_endpoint():
    print("\n--- Test 3: FastAPI POST /api/v1/sketch/export-zip ---")
    response = client.post(
        "/api/v1/sketch/export-zip",
        json={
            "project_name": "Mobile Checkout Wireframe",
            "jsx_code": SAMPLE_JSX
        }
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    assert 'filename="sketch2ui_mobile_checkout_wireframe.zip"' in response.headers["content-disposition"]
    
    # Inspect received binary payload
    zip_bytes = io.BytesIO(response.content)
    zf = zipfile.ZipFile(zip_bytes, mode="r")
    assert "package.json" in zf.namelist()
    assert "src/App.jsx" in zf.namelist()
    print("  [OK] Endpoint returned 200 OK with valid application/zip streaming response")


def test_export_zip_raw_jsx_wrapping():
    print("\n--- Test 4: Raw JSX Wrapping & Fallback Default Export ---")
    raw_jsx = '<button className="px-4 py-2 bg-cyan-500">Click Me</button>'
    response = client.post(
        "/api/v1/sketch/export-zip",
        json={
            "project_name": "Simple Button",
            "jsx_code": raw_jsx
        }
    )
    assert response.status_code == 200
    
    zf = zipfile.ZipFile(io.BytesIO(response.content), mode="r")
    app_jsx = zf.read("src/App.jsx").decode("utf-8")
    assert "export default function App()" in app_jsx
    assert 'Click Me' in app_jsx
    print("  [OK] Raw JSX cleanly wrapped into valid App default export")


def test_export_zip_validation_errors():
    print("\n--- Test 5: Validation & Error Handling ---")
    # Empty jsx_code
    response_empty = client.post(
        "/api/v1/sketch/export-zip",
        json={
            "project_name": "Test Project",
            "jsx_code": "   "
        }
    )
    assert response_empty.status_code == 400
    assert "cannot be empty" in response_empty.json()["detail"].lower()
    
    # Missing project_name falls back to default
    response_default_name = client.post(
        "/api/v1/sketch/export-zip",
        json={
            "jsx_code": SAMPLE_JSX
        }
    )
    assert response_default_name.status_code == 200
    assert "sketch2ui_synthesized_wireframe.zip" in response_default_name.headers["content-disposition"]
    print("  [OK] Validation errors and defaults verified")


if __name__ == "__main__":
    print("======================================================================")
    print("       STARTING SKETCH2UI ZIP EXPORT ENGINE TEST SUITE                ")
    print("======================================================================")
    test_sanitize_utilities()
    test_generate_project_zip_in_memory()
    test_export_zip_api_endpoint()
    test_export_zip_raw_jsx_wrapping()
    test_export_zip_validation_errors()
    print("\n======================================================================")
    print("       ALL 5 ZIP EXPORT VALIDATION TESTS PASSED SUCCESSFULLY!         ")
    print("======================================================================")
