"""
Validation Suite for Sprint 1:
Advanced Layout Synthesizer with Horizontal Flex Clustering & Semantic Containers
Location: test_layout_clustering.py
"""
import json
from app.services.heuristic_service import (
    compute_vertical_overlap,
    are_horizontally_aligned_peers,
    cluster_elements_into_rows,
    sanitize_redundant_boxes,
    build_spatial_hierarchy,
    synthesize_layout_code,
)


def test_vertical_overlap_metric():
    print("\n--- Test 1: Vertical Overlap Metric Calculation ---")
    # Box A: y1=100, y2=150, h=50
    # Box B: y1=110, y2=160, h=50
    # inter_y = 150 - 110 = 40. min_h = 50. overlap = 40/50 = 0.8
    box_a = {"y1": 100, "y2": 150, "h": 50, "x1": 50, "x2": 200, "w": 150}
    box_b = {"y1": 110, "y2": 160, "h": 50, "x1": 220, "x2": 370, "w": 150}

    overlap = compute_vertical_overlap(box_a, box_b)
    print(f"Calculated Overlap_y: {overlap:.2f}")
    assert round(overlap, 2) == 0.80, f"Expected 0.80 but got {overlap}"

    # Disjoint boxes (no vertical overlap)
    box_c = {"y1": 200, "y2": 250, "h": 50, "x1": 50, "x2": 200, "w": 150}
    overlap_zero = compute_vertical_overlap(box_a, box_c)
    assert overlap_zero == 0.0, f"Expected 0.0 but got {overlap_zero}"
    print("  [OK] Vertical overlap metric accurately computed")


def test_horizontal_input_clustering():
    print("\n--- Test 2: Side-by-Side Input Fields (First/Last Name) ---")
    detected = [
        {
            "name": "Heading",
            "conf": "96%",
            "box": [20, 40, 60, 440],
            "x1": 40,
            "y1": 20,
            "x2": 440,
            "y2": 60,
        },
        # Input 1: First Name
        {
            "name": "TextBox",
            "conf": "93%",
            "box": [90, 40, 135, 230],
            "x1": 40,
            "y1": 90,
            "x2": 230,
            "y2": 135,
        },
        # Input 2: Last Name (horizontally aligned with Input 1)
        {
            "name": "TextBox",
            "conf": "91%",
            "box": [92, 250, 137, 440],
            "x1": 250,
            "y1": 92,
            "x2": 440,
            "y2": 137,
        },
    ]

    result = synthesize_layout_code(detected, project_name="RegistrationForm")
    jsx = result["jsx"]
    tailwind = result["tailwind"]
    ast = json.loads(result["json"])

    print("Synthesized JSX:")
    print(jsx)

    # 1. Verify responsive flex row container in JSX
    assert '<div className="flex flex-col sm:flex-row items-center gap-4 w-full">' in jsx, (
        "JSX missing responsive flex row container"
    )

    # 2. Verify flex-1 w-full on input fields inside row
    assert 'className="flex-1 w-full' in jsx, "Input field missing flex-1 w-full"

    # 3. Verify semantic First / Last name placeholders
    assert 'placeholder="First name..."' in jsx, "Missing First name placeholder"
    assert 'placeholder="Last name..."' in jsx, "Missing Last name placeholder"

    # 4. Verify Heading remains outside the flex row as full-width block
    assert '<h1 className="text-lg font-bold tracking-tight text-white">' in jsx

    # 5. Verify Tailwind HTML
    assert '<div class="flex flex-col sm:flex-row items-center gap-4 w-full">' in tailwind

    # 6. Verify AST hierarchy
    hierarchy = ast["hierarchy"]
    row_clusters = [n for n in hierarchy if n["name"] == "RowCluster"]
    assert len(row_clusters) == 1, "Expected 1 RowCluster in AST"
    assert len(row_clusters[0]["children"]) == 2, "Expected 2 children inside RowCluster"
    print("  [OK] 2 horizontal inputs successfully clustered into responsive Flexbox row")


def test_action_buttons_clustering():
    print("\n--- Test 3: Side-by-Side Action Buttons (Cancel / Submit) ---")
    detected = [
        # Button 1: Cancel / Secondary
        {
            "name": "Button",
            "conf": "90%",
            "box": [200, 180, 240, 290],
            "x1": 180,
            "y1": 200,
            "x2": 290,
            "y2": 240,
        },
        # Button 2: Submit / Primary
        {
            "name": "Button",
            "conf": "95%",
            "box": [200, 310, 240, 420],
            "x1": 310,
            "y1": 200,
            "x2": 420,
            "y2": 240,
        },
    ]

    result = synthesize_layout_code(detected, project_name="DialogActions")
    jsx = result["jsx"]
    tailwind = result["tailwind"]

    print("Synthesized Action Buttons JSX:")
    print(jsx)

    # 1. Verify action button wrapper
    assert '<div className="flex items-center justify-end gap-3 w-full pt-2">' in jsx, (
        "JSX missing action button flex row container"
    )

    # 2. Verify secondary/outline button (Button 1)
    assert "border border-white/10 hover:bg-white/5 text-zinc-300" in jsx, (
        "Button 1 missing outline/secondary styling"
    )
    assert ">Cancel</button>" in jsx, "Button 1 missing 'Cancel' text"

    # 3. Verify primary cyan button (Button 2)
    assert "bg-cyan-500 hover:bg-cyan-400 text-black" in jsx, (
        "Button 2 missing primary cyan styling"
    )
    assert ">Submit</button>" in jsx, "Button 2 missing 'Submit' text"

    # 4. Verify Tailwind HTML equivalent
    assert '<div class="flex items-center justify-end gap-3 w-full pt-2">' in tailwind
    print("  [OK] Action buttons successfully clustered in right-aligned flex container with primary/secondary hierarchy")


def test_nms_sanitizer():
    print("\n--- Test 4: Non-Maximum Suppression (NMS) Sanitizer ---")
    detected = [
        # Valid Primary Button
        {
            "id": "btn_primary",
            "name": "Button",
            "conf": "95%",
            "confidence": 0.95,
            "box": [100, 50, 150, 250],
            "x1": 50,
            "y1": 100,
            "x2": 250,
            "y2": 150,
        },
        # Duplicate low-confidence TextBox 90% contained inside the Button
        {
            "id": "txt_duplicate",
            "name": "TextBox",
            "conf": "38%",
            "confidence": 0.38,
            "box": [105, 60, 145, 240],
            "x1": 60,
            "y1": 105,
            "x2": 240,
            "y2": 145,
        },
        # Independent valid TextBox elsewhere
        {
            "id": "txt_valid",
            "name": "TextBox",
            "conf": "92%",
            "confidence": 0.92,
            "box": [200, 50, 245, 400],
            "x1": 50,
            "y1": 200,
            "x2": 400,
            "y2": 245,
        },
    ]

    hierarchy = build_spatial_hierarchy(detected)
    hierarchy_ids = [el["id"] for el in hierarchy]
    print(f"Elements after NMS sanitization: {hierarchy_ids}")

    assert "btn_primary" in hierarchy_ids, "Valid primary button was erroneously pruned"
    assert "txt_valid" in hierarchy_ids, "Valid independent text box was erroneously pruned"
    assert "txt_duplicate" not in hierarchy_ids, (
        "Duplicate nested low-confidence text box was NOT pruned by NMS"
    )

    result = synthesize_layout_code(detected, project_name="NMSVerification")
    assert "btn_primary" not in result["jsx"]  # IDs are internal
    # Ensure redundant text box is not generated
    assert result["jsx"].count("<input") == 1, (
        f"Expected exactly 1 input in JSX, but found {result['jsx'].count('<input')}"
    )
    print("  [OK] Nested low-confidence duplicate box pruned cleanly by NMS sanitizer")


def test_card_container_with_nested_rows():
    print("\n--- Test 5: Semantic Card Container with Nested Flex Rows ---")
    detected = [
        # Large Card Container
        {
            "id": "card_main",
            "name": "Card",
            "conf": "98%",
            "box": [20, 20, 450, 480],
            "x1": 20,
            "y1": 20,
            "x2": 480,
            "y2": 450,
        },
        # Heading inside card
        {
            "id": "h_card",
            "name": "Heading",
            "conf": "94%",
            "box": [40, 40, 80, 440],
            "x1": 40,
            "y1": 40,
            "x2": 440,
            "y2": 80,
        },
        # 2 Inputs inside card
        {
            "id": "in_1",
            "name": "TextBox",
            "conf": "90%",
            "box": [110, 40, 155, 230],
            "x1": 40,
            "y1": 110,
            "x2": 230,
            "y2": 155,
        },
        {
            "id": "in_2",
            "name": "TextBox",
            "conf": "89%",
            "box": [110, 250, 155, 440],
            "x1": 250,
            "y1": 110,
            "x2": 440,
            "y2": 155,
        },
        # 2 Action Buttons inside card
        {
            "id": "btn_c",
            "name": "Button",
            "conf": "91%",
            "box": [380, 200, 420, 310],
            "x1": 200,
            "y1": 380,
            "x2": 310,
            "y2": 420,
        },
        {
            "id": "btn_s",
            "name": "Button",
            "conf": "93%",
            "box": [380, 330, 420, 440],
            "x1": 330,
            "y1": 380,
            "x2": 440,
            "y2": 420,
        },
    ]

    result = synthesize_layout_code(detected, project_name="ProfileCard")
    jsx = result["jsx"]
    print("Synthesized Nested Card JSX:\n" + jsx)

    # Card container present
    assert "rounded-2xl bg-white/[0.03] border border-white/10" in jsx
    # Nested input flex row present inside card
    assert "flex flex-col sm:flex-row items-center gap-4 w-full" in jsx
    # Nested action buttons row present inside card
    assert "flex items-center justify-end gap-3 w-full pt-2" in jsx
    print("  [OK] Nested flex rows and action buttons rendered seamlessly inside Card container")


if __name__ == "__main__":
    test_vertical_overlap_metric()
    test_horizontal_input_clustering()
    test_action_buttons_clustering()
    test_nms_sanitizer()
    test_card_container_with_nested_rows()
    print("\n======================================================================")
    print("     ALL 5 LAYOUT CLUSTERING & NMS VALIDATION TESTS PASSED!           ")
    print("======================================================================")
