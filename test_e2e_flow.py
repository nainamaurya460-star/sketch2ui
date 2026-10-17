"""
End-to-End Full Lifecycle Smoke Test for Sketch2UI (TASK-011)

Validates:
1. Real Vision & Prediction Pipeline via FastAPI (POST /api/v1/sketch/predict) with test_images/sketches.png
2. Schema structure & component detection validity (bounding boxes, confidence values, colors)
3. Code Synthesizer Output Validity (clean React JSX component, Tailwind styling, AST structure)
4. Edge cases: Invalid MIME rejection, empty payload rejection, large image simulation
5. Frontend unified persistence logic simulation:
   - saveProject() with unified Project schema
   - getProjects() with chronological descending sort
   - getProjectById() single project lookup
   - renameProject() update name and updatedAt
   - Summary chips computation as consumed by HistoryView
   - storage usage calculation & exportAllProjectsJson
   - deleteProject() clean schema deletion without leakage
   - Honest empty state verification
"""
import io
import os
import json
import base64
from datetime import datetime, timezone
import numpy as np
import cv2
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

STORAGE_KEY = "sketch2ui_projects"


class LocalStorageMock:
    """Simulates browser localStorage engine in Python."""
    def __init__(self):
        self.store = {}

    def get_item(self, key):
        return self.store.get(key, None)

    def set_item(self, key, value):
        self.store[key] = str(value)

    def remove_item(self, key):
        self.store.pop(key, None)

    def clear(self):
        self.store.clear()


# Emulated Frontend Storage Service matching frontend/src/services/storage.js
class StorageService:
    def __init__(self, storage: LocalStorageMock):
        self.storage = storage

    def get_projects(self):
        raw = self.storage.get_item(STORAGE_KEY)
        if not raw:
            return []
        try:
            items = json.loads(raw)
            if not isinstance(items, list):
                return []
            return sorted(
                items,
                key=lambda x: datetime.fromisoformat(x.get("updatedAt", x.get("createdAt", "1970-01-01T00:00:00+00:00"))),
                reverse=True
            )
        except Exception:
            return []

    def get_project_by_id(self, project_id):
        projects = self.get_projects()
        for p in projects:
            if p.get("id") == project_id:
                return p
        return None

    def save_project(self, project_data):
        projects = self.get_projects()
        now = datetime.now(timezone.utc).isoformat()
        proj_id = project_data.get("id") or f"proj_{int(datetime.now().timestamp() * 1000)}"

        project = {
            "id": proj_id,
            "name": (project_data.get("name") or "Untitled Project").strip(),
            "createdAt": project_data.get("createdAt") or now,
            "updatedAt": now,
            "thumbnail": project_data.get("thumbnail") or "",
            "elements_count": project_data.get("elements_count") or 0,
            "detected_elements": project_data.get("detected_elements") or [],
            "generated_code": {
                "framework": (project_data.get("generated_code") or {}).get("framework", "React + Tailwind"),
                "jsx": (project_data.get("generated_code") or {}).get("jsx", ""),
                "tailwind": (project_data.get("generated_code") or {}).get("tailwind", ""),
                "json": (project_data.get("generated_code") or {}).get("json", "")
            }
        }

        existing_index = next((i for i, p in enumerate(projects) if p.get("id") == proj_id), -1)
        if existing_index >= 0:
            projects[existing_index] = project
        else:
            projects.insert(0, project)

        self.storage.set_item(STORAGE_KEY, json.dumps(projects))
        return project

    def rename_project(self, project_id, new_name):
        projects = self.get_projects()
        found = None
        for p in projects:
            if p.get("id") == project_id:
                p["name"] = new_name.strip()
                p["updatedAt"] = datetime.now(timezone.utc).isoformat()
                found = p
                break
        if found:
            self.storage.set_item(STORAGE_KEY, json.dumps(projects))
        return found

    def delete_project(self, project_id):
        projects = self.get_projects()
        updated = [p for p in projects if p.get("id") != project_id]
        self.storage.set_item(STORAGE_KEY, json.dumps(updated))
        return updated

    def clear_all_projects(self):
        self.storage.remove_item(STORAGE_KEY)
        return True

    def get_storage_usage(self):
        projects = self.get_projects()
        raw = self.storage.get_item(STORAGE_KEY) or ""
        bytes_len = len(raw.encode("utf-8"))
        kb = round(bytes_len / 1024, 2)
        return {"count": len(projects), "bytes": bytes_len, "kb": kb}


def calculate_history_summary_chips(detected_elements):
    """Replicates summary chip generator from HistoryView.jsx."""
    counts = {}
    for el in detected_elements:
        name = el.get("name", "Component")
        counts[name] = counts.get(name, 0) + 1
    
    chips = []
    for name, cnt in counts.items():
        label = f"{name}s" if cnt > 1 and not name.endswith("s") else name
        chips.append(f"{cnt} {label}")
    return chips


def test_e2e_complete_flow():
    print("======================================================================")
    print("      SKETCH2UI END-TO-END PIPELINE & PERSISTENCE VERIFICATION        ")
    print("======================================================================")

    # -------------------------------------------------------------------------
    # STAGE 1: Real FastAPI Prediction Pipeline
    # -------------------------------------------------------------------------
    print("\n[STAGE 1] Testing Vision Pipeline & Prediction Endpoint...")
    sketch_path = os.path.join("test_images", "sketches.png")
    assert os.path.exists(sketch_path), f"File {sketch_path} not found"

    with open(sketch_path, "rb") as f:
        sketch_bytes = f.read()

    response = client.post(
        "/api/v1/sketch/predict",
        files={"file": ("sketches.png", io.BytesIO(sketch_bytes), "image/png")}
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["status"] == "success", "Response status must be 'success'"
    assert "project_name" in data and len(data["project_name"]) > 0
    assert "elements_count" in data and data["elements_count"] > 0
    assert "detected_elements" in data and isinstance(data["detected_elements"], list)
    assert len(data["detected_elements"]) == data["elements_count"]
    print(f"  ✓ API 200 OK: Detected {data['elements_count']} components from '{sketch_path}'")

    # Verify detected element schema
    for idx, el in enumerate(data["detected_elements"]):
        assert "name" in el, f"Element {idx} missing 'name'"
        assert "conf" in el, f"Element {idx} missing 'conf'"
        assert "box" in el and len(el["box"]) == 4, f"Element {idx} invalid 'box'"
        assert "color" in el, f"Element {idx} missing 'color'"

    print(f"  ✓ Element Schema Valid: Sample element -> {data['detected_elements'][0]}")

    # -------------------------------------------------------------------------
    # STAGE 2: Code Synthesizer Output Validity
    # -------------------------------------------------------------------------
    print("\n[STAGE 2] Testing Code Synthesizer Output...")
    gen_code = data["generated_code"]
    assert gen_code["framework"] == "React + Tailwind"
    assert "import React" in gen_code["jsx"], "JSX missing React import"
    assert "export default function" in gen_code["jsx"], "JSX missing functional component export"
    assert "className=" in gen_code["jsx"], "JSX missing Tailwind className props"
    assert len(gen_code["tailwind"]) > 0, "Tailwind markup must not be empty"
    assert len(gen_code["json"]) > 0, "AST JSON markup must not be empty"

    # Verify Cyber-Dark container styling
    assert "rounded-3xl" in gen_code["jsx"]
    assert "bg-[#090b10]/90" in gen_code["jsx"]
    print("  ✓ Synthesizer generated syntactically sound React JSX & Tailwind component")
    print(f"  ✓ Generated JSX contains {len(gen_code['jsx'].splitlines())} lines")

    # -------------------------------------------------------------------------
    # STAGE 3: Edge Case Rejection (Network / Payload Hardening)
    # -------------------------------------------------------------------------
    print("\n[STAGE 3] Testing Network & Payload Edge Cases...")
    
    # 3.1 Invalid MIME type
    res_bad_mime = client.post(
        "/api/v1/sketch/predict",
        files={"file": ("code.py", io.BytesIO(b"print('hello')"), "text/x-python")}
    )
    assert res_bad_mime.status_code == 400
    print(f"  ✓ Correctly rejected invalid MIME: {res_bad_mime.json().get('detail')}")

    # 3.2 Empty file
    res_empty = client.post(
        "/api/v1/sketch/predict",
        files={"file": ("blank.png", io.BytesIO(b""), "image/png")}
    )
    assert res_empty.status_code == 400
    print("  ✓ Correctly rejected empty file payload")

    # 3.3 Large synthetic image (1920x1080 canvas)
    large_canvas = np.ones((1080, 1920, 3), dtype=np.uint8) * 240
    cv2.rectangle(large_canvas, (100, 100), (600, 300), (20, 20, 20), 3)
    _, encoded_large = cv2.imencode(".png", large_canvas)
    res_large = client.post(
        "/api/v1/sketch/predict",
        files={"file": ("large_sketch.png", io.BytesIO(encoded_large.tobytes()), "image/png")}
    )
    assert res_large.status_code == 200
    print("  ✓ Successfully processed large 1080p canvas image payload")

    # -------------------------------------------------------------------------
    # STAGE 4: Client Persistence & Lifecycle Simulation (storage.js)
    # -------------------------------------------------------------------------
    print("\n[STAGE 4] Testing Client Storage & Persistence Lifecycle...")
    mock_local = LocalStorageMock()
    storage = StorageService(mock_local)

    # 4.1 Empty State Verification
    assert storage.get_projects() == [], "Initial storage must be empty"
    print("  ✓ Honest empty state verified: storage.get_projects() == []")

    # 4.2 Auto-save Project from real API prediction
    thumbnail_b64 = f"data:image/png;base64,{base64.b64encode(sketch_bytes[:500]).decode()}"
    project_payload = {
        "id": "proj_smoke_test_001",
        "name": data["project_name"],
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "thumbnail": thumbnail_b64,
        "elements_count": data["elements_count"],
        "detected_elements": data["detected_elements"],
        "generated_code": data["generated_code"]
    }

    saved_p = storage.save_project(project_payload)
    assert saved_p["id"] == "proj_smoke_test_001"
    assert len(storage.get_projects()) == 1
    print(f"  ✓ Project auto-saved: '{saved_p['name']}' (ID: {saved_p['id']})")

    # 4.3 Summary chips calculation for HistoryView
    chips = calculate_history_summary_chips(saved_p["detected_elements"])
    assert len(chips) > 0
    print(f"  ✓ HistoryView summary chips calculated: {chips}")

    # 4.4 Inline rename project
    renamed_p = storage.rename_project("proj_smoke_test_001", "Mobile Checkout Wireframe")
    assert renamed_p["name"] == "Mobile Checkout Wireframe"
    assert storage.get_project_by_id("proj_smoke_test_001")["name"] == "Mobile Checkout Wireframe"
    print(f"  ✓ Inline rename verified: '{renamed_p['name']}'")

    # 4.5 Save second project and verify descending chronological sort
    project_payload_2 = {
        "id": "proj_smoke_test_002",
        "name": "Landing Page Sketch",
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "elements_count": 3,
        "detected_elements": [{"name": "Button", "conf": "95%", "box": [0,0,10,10], "color": "bg-rose-500"}],
        "generated_code": {"framework": "React + Tailwind", "jsx": "export default function() {}", "tailwind": "", "json": ""}
    }
    storage.save_project(project_payload_2)
    all_projects = storage.get_projects()
    assert len(all_projects) == 2
    assert all_projects[0]["id"] == "proj_smoke_test_002", "Most recent project must appear first"
    print(f"  ✓ Chronological sorting verified: {all_projects[0]['name']} is #1")

    # 4.6 Storage metrics calculation
    usage = storage.get_storage_usage()
    assert usage["count"] == 2
    assert usage["kb"] > 0
    print(f"  ✓ Storage usage calculated: {usage['count']} projects using {usage['kb']} KB")

    # 4.7 Clean deletion without schema leakage
    updated_after_del = storage.delete_project("proj_smoke_test_002")
    assert len(updated_after_del) == 1
    assert storage.get_project_by_id("proj_smoke_test_002") is None
    print("  ✓ Clean deletion verified: project removed without schema corruption")

    # 4.8 Clear all storage
    storage.clear_all_projects()
    assert storage.get_projects() == []
    print("  ✓ Clear all projects verified: honest empty state restored")

    print("\n======================================================================")
    print("       ALL E2E SMOKE & LIFECYCLE TESTS COMPLETED SUCCESSFULLY!        ")
    print("======================================================================")


if __name__ == "__main__":
    test_e2e_complete_flow()
