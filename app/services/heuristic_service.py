"""
Phase 2 & Priority 3: Heuristic Rules Engine & Semantic Layout-to-Code Synthesizer
Location: app/services/heuristic_service.py
"""
import json
from typing import List, Dict, Any, Tuple, Optional


def normalize_bounding_box(box):
    """
    Normalizes a bounding box into (x, y, w, h) ints regardless of input format.
    Supports:
      - dict: {'x': ..., 'y': ..., 'width': ..., 'height': ...} or {'x': ..., 'y': ..., 'w': ..., 'h': ...}
      - list/tuple: [x, y, w, h] or [ymin, xmin, ymax, xmax]
    Returns (x, y, w, h) as tuple of ints, or None if invalid.
    """
    if isinstance(box, dict):
        x = box.get("x", 0)
        y = box.get("y", 0)
        w = box.get("width", box.get("w", 0))
        h = box.get("height", box.get("h", 0))
        return int(x), int(y), int(w), int(h)
    elif isinstance(box, (list, tuple)) and len(box) == 4:
        try:
            return int(box[0]), int(box[1]), int(box[2]), int(box[3])
        except (ValueError, TypeError):
            return None
    return None


def extract_geometry_features(x: int, y: int, w: int, h: int) -> dict:
    """Extracts extended geometric properties from bounding box."""
    area = w * h
    perimeter = 2 * (w + h)
    aspect_ratio = float(w) / h if h > 0 else 0.0
    center_x = x + (w // 2)
    center_y = y + (h // 2)

    return {
        "box": [x, y, w, h],
        "area": area,
        "perimeter": perimeter,
        "aspect_ratio": round(aspect_ratio, 2),
        "center": (center_x, center_y)
    }


def classify_component(w: int, h: int) -> str:
    """
    Day 3 Advanced Heuristic Rules:
    Categorizes contours into UI elements based on shape & aspect ratio thresholds.
    """
    area = w * h
    aspect_ratio = float(w) / h if h > 0 else 0.0

    # Filter noise
    if area < 100 or w < 5 or h < 5:
        return "noise"

    # Shape Rules
    if aspect_ratio > 4.0 and h < 45:
        return "text"
    elif 0.6 <= aspect_ratio <= 1.4 and area >= 10000:
        return "card"
    elif 1.5 <= aspect_ratio <= 5.0 and 1000 <= area < 10000:
        return "button"
    else:
        return "container"


def predict_ui_element(boxes: list) -> list:
    """
    Batch processes bounding boxes and returns classified predictions.
    Accepts both coordinate lists [x, y, w, h] and dictionaries {'x', 'y', 'width', 'height'}.
    """
    predictions = []
    for box in boxes:
        coords = normalize_bounding_box(box)
        if coords is not None:
            x, y, w, h = coords
            features = extract_geometry_features(x, y, w, h)
            label = classify_component(w, h)
            
            if label and str(label).lower() != "noise":
                predictions.append({
                    "label": label,
                    "confidence": 0.88,
                    "box": [x, y, w, h],
                    "features": features
                })
    return predictions


def process_ui_pipeline(bounding_boxes: list) -> dict:
    """
    Day 4 & Day 5 Integration:
    Processes raw boxes (dicts or lists), extracts geometry, applies heuristic rules,
    and returns a clean, structured JSON format for Day 6 API/Frontend.
    """
    elements = []
    
    for idx, box in enumerate(bounding_boxes, 1):
        coords = normalize_bounding_box(box)
        if coords is not None:
            x, y, w, h = coords
            features = extract_geometry_features(x, y, w, h)
            label = classify_component(w, h)
            
            # Noise Filtering
            if label and str(label).lower() != "noise":
                elements.append({
                    "id": f"elem_{idx}",
                    "label": label,
                    "confidence": 0.92,
                    "box": {"x": x, "y": y, "width": w, "height": h},
                    "features": features
                })

    return {
        "status": "success",
        "total_elements": len(elements),
        "predictions": elements
    }


# ==============================================================================
# PRIORITY 3: SPATIAL HIERARCHY & LAYOUT-TO-CODE SYNTHESIZER
# ==============================================================================

def _parse_confidence(conf_val: Any) -> float:
    """Parses confidence into a float between 0.0 and 1.0."""
    if isinstance(conf_val, (int, float)):
        val = float(conf_val)
        return val / 100.0 if val > 1.0 else val
    if isinstance(conf_val, str):
        cleaned = conf_val.strip().rstrip("%")
        try:
            val = float(cleaned)
            return val / 100.0 if val > 1.0 else val
        except ValueError:
            return 0.5
    return 0.5


def _normalize_detected_element(raw_elem: Dict[str, Any], idx: int) -> Dict[str, Any]:
    """Normalizes an element into a consistent spatial node format."""
    name = raw_elem.get("name") or raw_elem.get("label", "TextBox")
    conf = raw_elem.get("conf") or f"{int(round(raw_elem.get('confidence', 0.9) * 100))}%"
    conf_score = _parse_confidence(raw_elem.get("confidence") or raw_elem.get("conf") or 0.88)
    
    # Extract coordinates
    if "box" in raw_elem and isinstance(raw_elem["box"], (list, tuple)) and len(raw_elem["box"]) == 4:
        # [ymin, xmin, ymax, xmax] format from prediction contract or [x, y, w, h]
        b = raw_elem["box"]
        if "x1" in raw_elem and "y1" in raw_elem:
            x1, y1, x2, y2 = raw_elem["x1"], raw_elem["y1"], raw_elem["x2"], raw_elem["y2"]
        else:
            # Assume [ymin, xmin, ymax, xmax]
            y1, x1, y2, x2 = int(b[0]), int(b[1]), int(b[2]), int(b[3])
    elif "bounding_box" in raw_elem:
        bb = raw_elem["bounding_box"]
        x1 = bb.get("x", 0)
        y1 = bb.get("y", 0)
        x2 = x1 + bb.get("w", bb.get("width", 50))
        y2 = y1 + bb.get("h", bb.get("height", 30))
    else:
        x1 = raw_elem.get("x1", raw_elem.get("x", 0))
        y1 = raw_elem.get("y1", raw_elem.get("y", 0))
        x2 = raw_elem.get("x2", x1 + raw_elem.get("w", raw_elem.get("width", 100)))
        y2 = raw_elem.get("y2", y1 + raw_elem.get("h", raw_elem.get("height", 40)))

    w = max(1, x2 - x1)
    h = max(1, y2 - y1)
    area = w * h

    return {
        "id": raw_elem.get("id", f"node_{idx}"),
        "name": name,
        "conf": conf,
        "conf_score": conf_score,
        "x1": int(x1),
        "y1": int(y1),
        "x2": int(x2),
        "y2": int(y2),
        "w": int(w),
        "h": int(h),
        "area": int(area),
        "color": raw_elem.get("color", "bg-cyan-500"),
        "text": raw_elem.get("text"),
        "children": []
    }


def sanitize_redundant_boxes(elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Task 3: Non-Maximum Suppression (NMS) Sanitizer.
    Before clustering, filter out nested duplicate bounding boxes:
    If a low-confidence bounding box is >= 75% contained inside another bounding box
    of the same or conflicting type (e.g., duplicate TextBox inside Button), prune the redundant child box.
    """
    if not elements or len(elements) <= 1:
        return elements

    container_types = {"card", "container"}
    pruned_ids = set()

    for i, a in enumerate(elements):
        if a["id"] in pruned_ids:
            continue
        a_name = a["name"].lower()
        if a_name in container_types:
            continue

        for j, b in enumerate(elements):
            if i == j or b["id"] in pruned_ids:
                continue
            b_name = b["name"].lower()
            if b_name in container_types:
                continue

            # Compute intersection area
            ix1 = max(a["x1"], b["x1"])
            iy1 = max(a["y1"], b["y1"])
            ix2 = min(a["x2"], b["x2"])
            iy2 = min(a["y2"], b["y2"])
            iw = max(0, ix2 - ix1)
            ih = max(0, iy2 - iy1)
            inter_area = iw * ih

            if inter_area <= 0:
                continue

            area_a = max(1, a["area"])
            area_b = max(1, b["area"])
            containment_b_in_a = inter_area / area_b
            containment_a_in_b = inter_area / area_a

            conf_a = a.get("conf_score", 0.5)
            conf_b = b.get("conf_score", 0.5)

            # Case 1: B is >= 75% contained inside A
            if containment_b_in_a >= 0.75:
                if conf_b < conf_a or (conf_b == conf_a and area_b <= area_a):
                    pruned_ids.add(b["id"])
                elif conf_a < conf_b and containment_a_in_b >= 0.75:
                    pruned_ids.add(a["id"])
                    break

            # Case 2: A is >= 75% contained inside B
            elif containment_a_in_b >= 0.75:
                if conf_a < conf_b or (conf_a == conf_b and area_a <= area_b):
                    pruned_ids.add(a["id"])
                    break
                elif conf_b < conf_a and containment_b_in_a >= 0.75:
                    pruned_ids.add(b["id"])

    return [el for el in elements if el["id"] not in pruned_ids]


def compute_vertical_overlap(a: Dict[str, Any], b: Dict[str, Any]) -> float:
    """
    Computes vertical intersection ratio between bounding boxes A and B:
    Overlap_y = (min(y2_A, y2_B) - max(y1_A, y1_B)) / min(h_A, h_B)
    """
    y1_a, y2_a, h_a = a["y1"], a["y2"], a["h"]
    y1_b, y2_b, h_b = b["y1"], b["y2"], b["h"]

    inter_y = min(y2_a, y2_b) - max(y1_a, y1_b)
    if inter_y <= 0:
        return 0.0

    min_h = min(h_a, h_b)
    if min_h <= 0:
        return 0.0

    return inter_y / float(min_h)


def are_horizontally_aligned_peers(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    """
    Checks if elements A and B can form a horizontal RowCluster:
      1. Neither is a standalone type (Heading, Image) or a container with enclosed children.
      2. Overlap_y >= 0.5 (50% or more vertical overlap).
      3. Height ratio is balanced (min_h / max_h >= 0.35).
      4. They are not overlapping on the X axis (inter_x <= tolerance).
    """
    standalone_types = {"heading", "header", "title", "image", "img", "image_placeholder", "photo"}
    if a["name"].lower() in standalone_types or b["name"].lower() in standalone_types:
        return False

    if a.get("children") or b.get("children"):
        return False

    overlap_y = compute_vertical_overlap(a, b)
    if overlap_y < 0.5:
        return False

    min_h = min(a["h"], b["h"])
    max_h = max(a["h"], b["h"])
    if max_h > 0 and (min_h / float(max_h)) < 0.35:
        return False

    ix1 = max(a["x1"], b["x1"])
    ix2 = min(a["x2"], b["x2"])
    inter_x = ix2 - ix1
    min_w = min(a["w"], b["w"])
    x_tolerance = max(15, int(0.15 * min_w))
    if inter_x > x_tolerance:
        return False

    return True


def cluster_elements_into_rows(elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Task 1: Spatial Clustering Algorithm.
    Groups horizontally aligned elements into a single horizontal row (RowCluster).
    Sorts elements within RowCluster from left to right by their x1 coordinate.
    If elements do not share vertical overlap with peers, keeps them as independent block items.
    """
    if not elements:
        return []
    if len(elements) == 1:
        return elements

    items = list(elements)
    n = len(items)

    adj = {i: [] for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            if are_horizontally_aligned_peers(items[i], items[j]):
                adj[i].append(j)
                adj[j].append(i)

    visited = set()
    clusters = []

    for i in range(n):
        if i in visited:
            continue

        comp = []
        queue = [i]
        visited.add(i)

        while queue:
            curr = queue.pop(0)
            comp.append(curr)
            for neighbor in adj[curr]:
                if neighbor not in visited:
                    # Consistency check: neighbor must not overlap on X with any node in comp
                    neigh_el = items[neighbor]
                    has_x_conflict = False
                    for existing_idx in comp:
                        ex_el = items[existing_idx]
                        ix1 = max(neigh_el["x1"], ex_el["x1"])
                        ix2 = min(neigh_el["x2"], ex_el["x2"])
                        inter_x = ix2 - ix1
                        min_w = min(neigh_el["w"], ex_el["w"])
                        if inter_x > max(15, int(0.15 * min_w)):
                            has_x_conflict = True
                            break
                    if not has_x_conflict:
                        visited.add(neighbor)
                        queue.append(neighbor)

        cluster_elements = [items[idx] for idx in comp]
        cluster_elements.sort(key=lambda el: el["x1"])

        if len(cluster_elements) >= 2:
            is_all_buttons = all(el["name"].lower() in ["button", "btn", "submit"] for el in cluster_elements)
            row_y1 = min(el["y1"] for el in cluster_elements)
            row_x1 = min(el["x1"] for el in cluster_elements)
            row_y2 = max(el["y2"] for el in cluster_elements)
            row_x2 = max(el["x2"] for el in cluster_elements)

            clusters.append({
                "type": "row_cluster",
                "is_row": True,
                "is_buttons": is_all_buttons,
                "elements": cluster_elements,
                "y1": row_y1,
                "x1": row_x1,
                "y2": row_y2,
                "x2": row_x2,
                "w": max(1, row_x2 - row_x1),
                "h": max(1, row_y2 - row_y1),
                "area": max(1, (row_x2 - row_x1) * (row_y2 - row_y1)),
                "name": "RowCluster",
                "conf": "100%",
                "children": []
            })
        else:
            clusters.append(cluster_elements[0])

    clusters.sort(key=lambda c: (c["y1"], c["x1"]))
    return clusters


def _is_enclosed(parent: Dict[str, Any], child: Dict[str, Any], margin: int = 15) -> bool:
    """Returns True if child lies inside parent with margin tolerance and parent is larger."""
    if parent["id"] == child["id"]:
        return False
    if parent["area"] <= child["area"] * 1.25:
        return False
    
    return (
        parent["x1"] - margin <= child["x1"] and
        parent["y1"] - margin <= child["y1"] and
        child["x2"] <= parent["x2"] + margin and
        child["y2"] <= parent["y2"] + margin
    )


def build_spatial_hierarchy(elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    1. Normalizes elements into spatial nodes.
    2. NMS Sanitizer: Prunes nested duplicate bounding boxes before clustering.
    3. Spatial Sort: Sorts components primarily by vertical coordinate (y1), then horizontal (x1).
    4. Container Grouping: Groups child elements that lie inside card/container bounding boxes.
    """
    normalized = [_normalize_detected_element(el, i + 1) for i, el in enumerate(elements)]
    if not normalized:
        return []

    # Apply Task 3 NMS Sanitizer
    sanitized = sanitize_redundant_boxes(normalized)

    # Sort all by y1, then x1
    sanitized.sort(key=lambda item: (item["y1"], item["x1"]))

    # Identify container candidates (explicit card/container or large bounding boxes)
    container_types = {"card", "container"}
    
    # Check parent-child enclosure
    child_ids = set()
    for parent in sanitized:
        p_name = parent["name"].lower()
        is_container_candidate = (p_name in container_types) or (parent["area"] > 25000 and parent["w"] > 180 and parent["h"] > 120)
        
        if is_container_candidate:
            for child in sanitized:
                if child["id"] not in child_ids and _is_enclosed(parent, child):
                    parent["children"].append(child)
                    child_ids.add(child["id"])

    # Root elements are those not enclosed as children of another container
    root_elements = [el for el in sanitized if el["id"] not in child_ids]
    
    # Sort children of each container spatially as well
    for el in root_elements:
        if el["children"]:
            el["children"].sort(key=lambda c: (c["y1"], c["x1"]))

    root_elements.sort(key=lambda r: (r["y1"], r["x1"]))
    return root_elements


def _render_element_markup(
    elem: Dict[str, Any],
    ctx_counts: Dict[str, int],
    is_jsx: bool = True,
    in_row: bool = False,
    is_secondary_btn: bool = False,
    placeholder_override: Optional[str] = None
) -> str:
    """
    Synthesizes clean, responsive React JSX and Tailwind CSS markup:
      - Button -> primary cyan or secondary outline
      - TextBox / input_field -> w-full or flex-1 w-full in row
      - Heading -> <h2 className="...">...</h2>
      - Paragraph / Label -> <p className="...">...</p>
      - Image -> <div className="...">Image Placeholder</div>
      - CheckBox, RadioButton, Select, Link
    """
    name_lower = elem["name"].lower().replace("-", "_").replace(" ", "_")
    count = ctx_counts.get(name_lower, 0) + 1
    ctx_counts[name_lower] = count

    attr = "className" if is_jsx else "class"

    # 1. Heading
    if name_lower in ["heading", "title", "header"]:
        extracted_text = elem.get("text")
        if extracted_text and extracted_text.strip():
            text = extracted_text.strip()
        else:
            heading_texts = [
                "Synthesized Wireframe",
                "Account Settings",
                "Project Overview",
                "Component Details",
                "Dashboard Analytics"
            ]
            text = heading_texts[(count - 1) % len(heading_texts)]
        return f'<{ "h2" if count > 1 else "h1" } {attr}="text-lg font-bold tracking-tight text-white">{text}</{ "h2" if count > 1 else "h1" }>'

    # 2. Button
    elif name_lower in ["button", "btn", "submit"]:
        extracted_text = elem.get("text")
        if is_secondary_btn:
            sec_count = ctx_counts.get("sec_btn", 0) + 1
            ctx_counts["sec_btn"] = sec_count
            if extracted_text and extracted_text.strip():
                text = extracted_text.strip()
            else:
                sec_texts = ["Cancel", "Reset", "Previous", "Dismiss"]
                text = sec_texts[(sec_count - 1) % len(sec_texts)]
            return (
                f'<button {attr}="px-4 py-2.5 rounded-xl border border-white/10 hover:bg-white/5 text-zinc-300 '
                f'font-semibold text-xs transition-all cursor-pointer">{text}</button>'
            )
        else:
            if extracted_text and extracted_text.strip():
                text = extracted_text.strip()
            elif in_row:
                prim_count = ctx_counts.get("prim_btn", 0) + 1
                ctx_counts["prim_btn"] = prim_count
                btn_texts = ["Submit", "Save Changes", "Confirm Action", "Explore More", "Get Started"]
                text = btn_texts[(prim_count - 1) % len(btn_texts)]
            else:
                btn_texts = ["Get Started", "Submit Request", "Save Changes", "Confirm Action", "Explore More"]
                text = btn_texts[(count - 1) % len(btn_texts)]
            return (
                f'<button {attr}="px-4 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-black '
                f'font-semibold text-xs shadow-lg shadow-cyan-500/20 transition-all cursor-pointer">{text}</button>'
            )

    # 3. TextBox / input_field
    elif name_lower in ["textbox", "input_field", "input", "text_box", "textfield"]:
        extracted_text = elem.get("text")
        if extracted_text and extracted_text.strip():
            placeholder = extracted_text.strip()
        elif placeholder_override:
            placeholder = placeholder_override
        else:
            placeholders = [
                "Enter your email address...",
                "Enter full name...",
                "Search components or files...",
                "Type your response...",
                "Enter password..."
            ]
            placeholder = placeholders[(count - 1) % len(placeholders)]
        input_type = "password" if "password" in placeholder.lower() else "text"
        width_cls = "flex-1 w-full" if in_row else "w-full"
        return (
            f'<input type="{input_type}" placeholder="{placeholder}" '
            f'{attr}="{width_cls} px-3.5 py-2.5 rounded-xl bg-white/5 border border-white/10 '
            f'text-white text-xs placeholder-zinc-500 focus:outline-none focus:border-cyan-500/50" />'
        )

    # 4. Paragraph / Label
    elif name_lower in ["paragraph", "label", "text", "description"]:
        extracted_text = elem.get("text")
        if name_lower == "label":
            if extracted_text and extracted_text.strip():
                text = extracted_text.strip()
            else:
                labels = ["Email Address", "Full Name", "Project Title", "Category Option", "Preferences"]
                text = labels[(count - 1) % len(labels)]
            return f'<label {attr}="block text-xs font-medium text-zinc-300">{text}</label>'
        else:
            if extracted_text and extracted_text.strip():
                text = extracted_text.strip()
            else:
                paragraphs = [
                    "Turn your hand-drawn wireframes into production-ready UI components instantly.",
                    "Review the synthesized layout hierarchy and export clean Tailwind CSS code.",
                    "Responsive container dynamically optimized for mobile, tablet, and desktop views."
                ]
                text = paragraphs[(count - 1) % len(paragraphs)]
            return f'<p {attr}="text-xs text-zinc-400 leading-relaxed">{text}</p>'

    # 5. Image
    elif name_lower in ["image", "img", "image_placeholder", "photo"]:
        return (
            f'<div {attr}="w-full aspect-video rounded-xl bg-white/5 border border-dashed '
            f'border-white/10 flex items-center justify-center text-zinc-500 text-xs font-mono">Image Placeholder</div>'
        )

    # 6. CheckBox
    elif name_lower in ["checkbox", "check_box"]:
        extracted_text = elem.get("text")
        if extracted_text and extracted_text.strip():
            text = extracted_text.strip()
        else:
            checkbox_labels = [
                "Remember preference on this device",
                "Enable automated layout synchronization",
                "I agree to the terms of service"
            ]
            text = checkbox_labels[(count - 1) % len(checkbox_labels)]
        return (
            f'<label {attr}="flex items-center gap-2.5 text-xs text-zinc-300 cursor-pointer">\n'
            f'  <input type="checkbox" {attr}="w-4 h-4 rounded bg-white/5 border-white/10 text-cyan-500 focus:ring-0 cursor-pointer" />\n'
            f'  <span>{text}</span>\n'
            f'</label>'
        )

    # 7. RadioButton
    elif name_lower in ["radiobutton", "radio_button", "radio"]:
        extracted_text = elem.get("text")
        if extracted_text and extracted_text.strip():
            text = extracted_text.strip()
        else:
            radio_labels = ["Standard Option", "Pro Tier Workflow", "Enterprise Architecture"]
            text = radio_labels[(count - 1) % len(radio_labels)]
        return (
            f'<label {attr}="flex items-center gap-2.5 text-xs text-zinc-300 cursor-pointer">\n'
            f'  <input type="radio" name="wireframe_radio_group" {attr}="w-4 h-4 bg-white/5 border-white/10 text-cyan-500 focus:ring-0 cursor-pointer" />\n'
            f'  <span>{text}</span>\n'
            f'</label>'
        )

    # 8. Select / Dropdown
    elif name_lower in ["select", "dropdown"]:
        extracted_text = elem.get("text")
        first_opt = extracted_text.strip() if (extracted_text and extracted_text.strip()) else "Select an option..."
        width_cls = "flex-1 w-full" if in_row else "w-full"
        return (
            f'<select {attr}="{width_cls} px-3.5 py-2.5 rounded-xl bg-white/5 border border-white/10 '
            f'text-white text-xs focus:outline-none focus:border-cyan-500/50 cursor-pointer">\n'
            f'  <option {attr}="bg-[#090b10] text-white">{first_opt}</option>\n'
            f'  <option {attr}="bg-[#090b10] text-white">Default Configuration</option>\n'
            f'  <option {attr}="bg-[#090b10] text-white">Production Mode</option>\n'
            f'</select>'
        )

    # 9. Link
    elif name_lower in ["link", "anchor"]:
        extracted_text = elem.get("text")
        link_text = extracted_text.strip() if (extracted_text and extracted_text.strip()) else "Explore Documentation"
        return f'<a href="#details" {attr}="text-xs text-cyan-400 hover:text-cyan-300 underline underline-offset-2 transition-colors">{link_text} &rarr;</a>'

    # Fallback element
    else:
        capitalized = elem["name"].replace("_", " ").title()
        return (
            f'<div {attr}="p-3 rounded-xl bg-white/[0.02] border border-white/5 text-xs text-zinc-300 flex items-center justify-between">\n'
            f'  <span>{capitalized} Component</span>\n'
            f'  <span {attr}="font-mono text-[10px] text-cyan-400">{elem["conf"]}</span>\n'
            f'</div>'
        )


def _render_tree(
    nodes: List[Dict[str, Any]],
    ctx_counts: Dict[str, int],
    is_jsx: bool = True,
    indent_level: int = 3
) -> List[str]:
    """Recursively converts hierarchical nodes into indented markup lines."""
    lines = []
    pad = "  " * indent_level
    child_pad = "  " * (indent_level + 1)
    attr = "className" if is_jsx else "class"

    clustered_items = cluster_elements_into_rows(nodes)

    for item in clustered_items:
        # Multi-element RowCluster
        if item.get("is_row") and item.get("elements"):
            row_elements = item["elements"]
            if item.get("is_buttons"):
                # Action buttons side-by-side
                lines.append(f'{pad}<div {attr}="flex items-center justify-end gap-3 w-full pt-2">')
                num_btns = len(row_elements)
                for b_idx, btn in enumerate(row_elements):
                    is_sec = (b_idx < num_btns - 1)
                    btn_markup = _render_element_markup(
                        btn, ctx_counts, is_jsx=is_jsx, in_row=True, is_secondary_btn=is_sec
                    )
                    for m_line in btn_markup.split("\n"):
                        lines.append(f"{child_pad}{m_line}")
                lines.append(f"{pad}</div>")
            else:
                # Responsive flex row (e.g. inputs, mixed controls)
                lines.append(f'{pad}<div {attr}="flex flex-col sm:flex-row items-center gap-4 w-full">')
                textbox_indices = [
                    idx for idx, el in enumerate(row_elements)
                    if el["name"].lower() in ["textbox", "input_field", "input", "text_box", "textfield"]
                ]
                for r_idx, elem in enumerate(row_elements):
                    placeholder_override = None
                    if len(textbox_indices) == 2 and r_idx in textbox_indices:
                        if r_idx == textbox_indices[0]:
                            placeholder_override = "First name..."
                        elif r_idx == textbox_indices[1]:
                            placeholder_override = "Last name..."

                    elem_markup = _render_element_markup(
                        elem,
                        ctx_counts,
                        is_jsx=is_jsx,
                        in_row=True,
                        placeholder_override=placeholder_override
                    )
                    for m_line in elem_markup.split("\n"):
                        lines.append(f"{child_pad}{m_line}")
                lines.append(f"{pad}</div>")

        elif item.get("children"):
            # Render as container wrapping its children
            lines.append(f'{pad}<div {attr}="p-5 rounded-2xl bg-white/[0.03] border border-white/10 shadow-lg space-y-3">')
            c_name = item["name"].lower()
            if c_name not in ["card", "container"]:
                header_line = _render_element_markup(item, ctx_counts, is_jsx=is_jsx, in_row=False)
                lines.append(f"{pad}  {header_line}")
            child_lines = _render_tree(item["children"], ctx_counts, is_jsx=is_jsx, indent_level=indent_level + 1)
            lines.extend(child_lines)
            lines.append(f"{pad}</div>")

        else:
            # Standalone element
            elem_markup = _render_element_markup(item, ctx_counts, is_jsx=is_jsx, in_row=False)
            for m_line in elem_markup.split("\n"):
                lines.append(f"{pad}{m_line}")

    return lines


def _build_ast(nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Builds clean AST dictionary for JSON export."""
    clustered_items = cluster_elements_into_rows(nodes)
    ast_list = []
    for item in clustered_items:
        if item.get("is_row") and item.get("elements"):
            cluster_ast = {
                "name": "RowCluster",
                "conf": "100%",
                "box": [item["y1"], item["x1"], item["y2"], item["x2"]],
                "dimensions": {"width": item["w"], "height": item["h"]},
                "cluster_type": "buttons" if item.get("is_buttons") else "flex_row",
                "children": []
            }
            for child in item["elements"]:
                child_dict = {
                    "name": child["name"],
                    "conf": child["conf"],
                    "box": [child["y1"], child["x1"], child["y2"], child["x2"]],
                    "dimensions": {"width": child["w"], "height": child["h"]},
                }
                if child.get("text"):
                    child_dict["text"] = child["text"]
                cluster_ast["children"].append(child_dict)
            ast_list.append(cluster_ast)
        else:
            node_ast = {
                "name": item["name"],
                "conf": item["conf"],
                "box": [item["y1"], item["x1"], item["y2"], item["x2"]],
                "dimensions": {"width": item["w"], "height": item["h"]},
            }
            if item.get("text"):
                node_ast["text"] = item["text"]
            if item.get("children"):
                node_ast["children"] = _build_ast(item["children"])
            ast_list.append(node_ast)
    return ast_list


def synthesize_layout_code(
    detected_elements: List[Dict[str, Any]],
    project_name: str = "Synthesized Wireframe"
) -> Dict[str, str]:
    """
    Transforms detected elements into:
      1. Clean React JSX string wrapped in glassmorphic card container.
      2. Semantic HTML + Tailwind CSS string.
      3. AST JSON string.
    """
    hierarchy = build_spatial_hierarchy(detected_elements)

    # Safe fallback if empty detections
    if not hierarchy:
        jsx_empty = (
            'import React from "react";\n\n'
            f'export default function {project_name.replace(" ", "")}() {{\n'
            '  return (\n'
            '    <div className="w-full max-w-md mx-auto p-6 rounded-3xl bg-[#090b10]/90 border border-white/10 backdrop-blur-2xl shadow-2xl space-y-4">\n'
            f'      <h2 className="text-lg font-bold tracking-tight text-white">{project_name}</h2>\n'
            '      <p className="text-xs text-zinc-400 leading-relaxed">No distinct elements detected. Showing base template.</p>\n'
            '      <input type="text" placeholder="Enter text..." className="w-full px-3.5 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-xs placeholder-zinc-500 focus:outline-none focus:border-cyan-500/50" />\n'
            '      <button className="px-4 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-black font-semibold text-xs shadow-lg shadow-cyan-500/20 transition-all cursor-pointer">Submit</button>\n'
            '    </div>\n'
            '  );\n'
            '}'
        )
        tailwind_empty = (
            f'<div class="w-full max-w-md mx-auto p-6 rounded-3xl bg-[#090b10]/90 border border-white/10 backdrop-blur-2xl shadow-2xl space-y-4">\n'
            f'  <h2 class="text-lg font-bold tracking-tight text-white">{project_name}</h2>\n'
            f'  <p class="text-xs text-zinc-400 leading-relaxed">No distinct elements detected. Showing base template.</p>\n'
            f'  <input type="text" placeholder="Enter text..." class="w-full px-3.5 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-xs placeholder-zinc-500 focus:outline-none focus:border-cyan-500/50" />\n'
            f'  <button class="px-4 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-black font-semibold text-xs shadow-lg shadow-cyan-500/20 transition-all cursor-pointer">Submit</button>\n'
            f'</div>'
        )
        json_empty = json.dumps({
            "framework": "React + Tailwind",
            "project_name": project_name,
            "elements_count": 0,
            "elements": []
        }, indent=2)

        return {
            "framework": "React + Tailwind",
            "jsx": jsx_empty,
            "tailwind": tailwind_empty,
            "json": json_empty
        }

    # Render JSX
    ctx_jsx: Dict[str, int] = {}
    jsx_body_lines = _render_tree(hierarchy, ctx_jsx, is_jsx=True, indent_level=3)
    jsx_content = "\n".join(jsx_body_lines)

    comp_name = "".join(c for c in project_name.title() if c.isalnum()) or "SynthesizedWireframe"
    jsx_full = (
        'import React from "react";\n\n'
        f'export default function {comp_name}() {{\n'
        '  return (\n'
        '    <div className="w-full max-w-md mx-auto p-6 rounded-3xl bg-[#090b10]/90 border border-white/10 backdrop-blur-2xl shadow-2xl space-y-4">\n'
        f'{jsx_content}\n'
        '    </div>\n'
        '  );\n'
        '}'
    )

    # Render Tailwind HTML
    ctx_tw: Dict[str, int] = {}
    tw_body_lines = _render_tree(hierarchy, ctx_tw, is_jsx=False, indent_level=1)
    tw_content = "\n".join(tw_body_lines)
    tailwind_full = (
        '<div class="w-full max-w-md mx-auto p-6 rounded-3xl bg-[#090b10]/90 border border-white/10 backdrop-blur-2xl shadow-2xl space-y-4">\n'
        f'{tw_content}\n'
        '</div>'
    )

    # Build Layout AST
    ast_elements = _build_ast(hierarchy)
    layout_ast = {
        "framework": "React + Tailwind",
        "project_name": project_name,
        "container": "GlassmorphicCard",
        "elements_count": len(detected_elements),
        "hierarchy": ast_elements
    }

    return {
        "framework": "React + Tailwind",
        "jsx": jsx_full,
        "tailwind": tailwind_full,
        "json": json.dumps(layout_ast, indent=2)
    }