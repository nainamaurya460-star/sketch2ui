"""
Phase 3: Automated Sketch Augmentation & Stress Evaluation Harness
Project: Sketch2UI
Location: benchmarks/run_stress_benchmark.py

Evaluates the Sketch2UI detection engine (YOLOv8 + SAHI + OCR) under clean vs.
harsh real-world conditions (notebook lines, graphite fade, camera shadows, composite noise).
Measures mAP@50, Precision, Recall, and Component Recall Retention percentage.
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime, timezone

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cv2
import numpy as np

from app.services.yolo_service import get_yolo_classifier
from app.services.ocr_service import get_ocr_service
from benchmarks.augmentations import (
    add_ruled_notebook_lines,
    add_pencil_jitter_and_fade,
    add_vignette_and_shadows,
    apply_composite_sketch_stress,
)


def compute_iou(boxA: List[int], boxB: List[int]) -> float:
    """Computes IoU between two boxes in [ymin, xmin, ymax, xmax] format."""
    yA = max(boxA[0], boxB[0])
    xA = max(boxA[1], boxB[1])
    yB = min(boxA[2], boxB[2])
    xB = min(boxA[3], boxB[3])

    inter_w = max(0, xB - xA)
    inter_h = max(0, yB - yA)
    inter_area = inter_w * inter_h

    areaA = max(0, boxA[2] - boxA[0]) * max(0, boxA[3] - boxA[1])
    areaB = max(0, boxB[2] - boxB[0]) * max(0, boxB[3] - boxB[1])
    union_area = areaA + areaB - inter_area

    if union_area <= 0:
        return 0.0
    return float(inter_area) / float(union_area)


def evaluate_detection(
    image: np.ndarray,
    expected_components: List[Dict[str, Any]],
    classifier,
    confidence_threshold: float = 0.18,
) -> Dict[str, Any]:
    """Runs prediction on image and evaluates detection metrics against ground truth."""
    pred_elements = classifier.predict_image(
        image, confidence_threshold=confidence_threshold, iou=0.45
    )

    matched_gt = set()
    tp = 0
    ious = []

    # Compatible matching for sketch conventions
    compatible_classes = {
        "button": {"button", "textbox"},
        "textbox": {"button", "textbox"},
        "checkbox": {"checkbox", "radiobutton"},
        "radiobutton": {"checkbox", "radiobutton"},
        "image": {"image", "image_placeholder"},
    }

    for p_elem in pred_elements:
        p_box = p_elem["box"]
        p_name = p_elem["name"].lower()
        best_iou = 0.0
        best_gt_idx = -1

        for g_idx, g_elem in enumerate(expected_components):
            if g_idx in matched_gt:
                continue
            iou = compute_iou(p_box, g_elem["box"])
            if iou > best_iou:
                best_iou = iou
                best_gt_idx = g_idx

        if best_iou >= 0.50 and best_gt_idx >= 0:
            g_name = expected_components[best_gt_idx]["name"].lower()
            allowed = compatible_classes.get(g_name, {g_name})
            if p_name == g_name or p_name in allowed:
                tp += 1
                matched_gt.add(best_gt_idx)
                ious.append(best_iou)

    fp = max(0, len(pred_elements) - tp)
    fn = max(0, len(expected_components) - tp)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    mean_iou_50 = float(np.mean(ious)) if ious else 0.0

    return {
        "total_gt": len(expected_components),
        "total_pred": len(pred_elements),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "mean_iou_50": mean_iou_50,
        "elements": pred_elements,
    }


def run_stress_benchmark() -> Dict[str, Any]:
    """
    Executes benchmark comparison across clean and augmented sketch conditions:
      1. Baseline (Clean)
      2. Notebook Lines
      3. Pencil Fade & Graphite Noise
      4. Mobile Phone Camera Shadows
      5. Full Composite Stress
    """
    root_dir = Path(__file__).resolve().parent.parent
    gt_path = root_dir / "benchmarks" / "dataset" / "ground_truth.json"
    report_path = root_dir / "benchmarks" / "stress_benchmark_report.json"

    if not gt_path.exists():
        raise FileNotFoundError(f"Ground truth dataset not found at: {gt_path}")

    with open(gt_path, "r", encoding="utf-8") as f:
        gt_data = json.load(f)

    classifier = get_yolo_classifier()

    conditions = {
        "baseline_clean": lambda img: img.copy(),
        "notebook_lines": lambda img: add_ruled_notebook_lines(img),
        "pencil_jitter_fade": lambda img: add_pencil_jitter_and_fade(img),
        "mobile_shadows": lambda img: add_vignette_and_shadows(img),
        "composite_stress": lambda img: apply_composite_sketch_stress(img),
    }

    condition_metrics: Dict[str, Dict[str, Any]] = {}

    for cond_name, aug_fn in conditions.items():
        sample_evals = []
        for sample in gt_data["samples"]:
            img_rel = sample["image_path"]
            img_path = root_dir / img_rel
            if not img_path.exists():
                print(f"Warning: sample image {img_path} not found. Skipping.")
                continue

            raw_img = cv2.imread(str(img_path))
            augmented_img = aug_fn(raw_img)
            eval_res = evaluate_detection(
                augmented_img, sample["expected_components"], classifier
            )
            sample_evals.append({
                "sample_id": sample["id"],
                "metrics": eval_res
            })

        # Aggregate across samples for this condition
        total_tp = sum(s["metrics"]["tp"] for s in sample_evals)
        total_fp = sum(s["metrics"]["fp"] for s in sample_evals)
        total_fn = sum(s["metrics"]["fn"] for s in sample_evals)
        total_gt = sum(s["metrics"]["total_gt"] for s in sample_evals)

        prec = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
        rec = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
        f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0

        all_ious = [
            s["metrics"]["mean_iou_50"]
            for s in sample_evals
            if s["metrics"]["mean_iou_50"] > 0
        ]
        map50 = float(np.mean(all_ious)) if all_ious else 0.0

        condition_metrics[cond_name] = {
            "total_samples": len(sample_evals),
            "total_gt": total_gt,
            "total_tp": total_tp,
            "total_fp": total_fp,
            "total_fn": total_fn,
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "mAP_at_50": round(map50, 4),
            "per_sample": sample_evals,
        }

    # Calculate Component Recall Retention relative to clean baseline
    baseline_tp = condition_metrics["baseline_clean"]["total_tp"]
    baseline_rec = condition_metrics["baseline_clean"]["recall"]

    for cond_name, metrics in condition_metrics.items():
        if baseline_tp > 0:
            retention_pct = round((metrics["total_tp"] / baseline_tp) * 100.0, 2)
        else:
            retention_pct = 100.0 if metrics["total_tp"] == 0 else 0.0
        metrics["recall_retention_pct"] = retention_pct

    summary_report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "benchmark_version": "3.0.0-phase3",
        "description": "Stress evaluation comparing clean sketches against notebook lines, graphite fade, and shadows",
        "baseline_summary": {
            "mAP_at_50": condition_metrics["baseline_clean"]["mAP_at_50"],
            "recall": condition_metrics["baseline_clean"]["recall"],
            "f1_score": condition_metrics["baseline_clean"]["f1_score"],
        },
        "conditions": condition_metrics,
    }

    # Save benchmark report to disk
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(summary_report, f, indent=2)

    # Print clean formatted summary table
    print("\n" + "=" * 80)
    print("      SKETCH2UI PHASE 3: STRESS BENCHMARK & AUGMENTATION HARNESS")
    print("=" * 80)
    print(f"{'Condition':<24} | {'mAP@50':<8} | {'Precision':<10} | {'Recall':<8} | {'F1':<8} | {'Recall Ret.%':<12}")
    print("-" * 80)
    for c_name, data in condition_metrics.items():
        print(
            f"{c_name:<24} | "
            f"{data['mAP_at_50']:<8.4f} | "
            f"{data['precision']:<10.4f} | "
            f"{data['recall']:<8.4f} | "
            f"{data['f1_score']:<8.4f} | "
            f"{data['recall_retention_pct']:<10.1f}%"
        )
    print("=" * 80)
    print(f"Report saved to: {report_path.resolve()}\n")

    return summary_report


if __name__ == "__main__":
    run_stress_benchmark()
