"""
Phase 3: Sketch Data Augmentation Harness
Project: Sketch2UI
Location: benchmarks/augmentations.py

Automated synthetic and physical noise generators for stress-testing and benchmarking
the local YOLOv8 detection engine and OCR pipelines under realistic, imperfect conditions:
1. Ruled and grid notebook paper lines.
2. Pencil stroke jitter, graphite grain, and faint contrast fading.
3. Mobile phone camera angle shadows and vignette lighting falloffs.
"""

from typing import Tuple, Optional
import cv2
import numpy as np


def add_ruled_notebook_lines(
    img_np: np.ndarray,
    line_spacing: int = 32,
    line_color: Tuple[int, int, int] = (210, 210, 230),  # Soft notebook blue/gray in BGR
    line_thickness: int = 1,
    margin_x: Optional[int] = 55,
    margin_color: Tuple[int, int, int] = (190, 190, 245),  # Soft pink/red margin line in BGR
    grid: bool = False
) -> np.ndarray:
    """
    Simulates school notebook lined or grid paper behind hand-drawn sketches.
    Blends the notebook lines onto the paper background while preserving existing sketch strokes.
    """
    if img_np is None or img_np.size == 0:
        return img_np

    canvas = img_np.copy()
    h, w = canvas.shape[:2]

    # Create empty overlay for ruled lines
    lines_overlay = np.full((h, w, 3), 255, dtype=np.uint8)

    # Draw horizontal ruled lines
    for y in range(line_spacing, h, line_spacing):
        cv2.line(lines_overlay, (0, y), (w, y), line_color, line_thickness, cv2.LINE_AA)

    # Optional grid lines (vertical)
    if grid:
        for x in range(line_spacing, w, line_spacing):
            cv2.line(lines_overlay, (x, 0), (x, h), line_color, line_thickness, cv2.LINE_AA)

    # Optional vertical left notebook margin
    if margin_x is not None and 0 < margin_x < w:
        cv2.line(lines_overlay, (margin_x, 0), (margin_x, h), margin_color, line_thickness + 1, cv2.LINE_AA)

    # Blend overlay behind drawings: where sketch canvas is light (paper), blend lines overlay
    # Dark strokes are kept dark via cv2.min or multiplicative blending
    gray_canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY) if canvas.ndim == 3 else canvas
    # Mask of paper background (> 120 intensity)
    paper_mask = (gray_canvas > 110).astype(np.float32) / 255.0
    paper_mask_3c = np.repeat(paper_mask[:, :, np.newaxis], 3, axis=2)

    # Multiplicative blend on paper regions
    blended = (canvas.astype(np.float32) * (lines_overlay.astype(np.float32) / 255.0))
    result = canvas.astype(np.float32) * (1.0 - paper_mask_3c) + blended * paper_mask_3c
    return np.clip(result, 0, 255).astype(np.uint8)


def add_pencil_jitter_and_fade(
    img_np: np.ndarray,
    fade_factor: float = 0.55,
    jitter_sigma: float = 0.8,
    contrast_reduction: float = 0.72
) -> np.ndarray:
    """
    Simulates faint graphite strokes, low contrast, and rough paper texture noise.
    Lifts deep blacks towards washed-out gray and injects subtle graphite grain.
    """
    if img_np is None or img_np.size == 0:
        return img_np

    img_float = img_np.astype(np.float32)

    # 1. Contrast reduction and baseline lift (fade dark strokes toward gray)
    # Target gray level for black strokes
    black_lift = 255.0 * (1.0 - contrast_reduction) * (1.0 - fade_factor * 0.4)
    faded = img_float * contrast_reduction + black_lift

    # 2. Add graphite texture / Gaussian paper grain noise
    noise = np.random.normal(0, jitter_sigma * 7.5, img_np.shape).astype(np.float32)
    faded = faded + noise

    # 3. Subtle hand jitter: blend with a 1px slightly shifted copy
    kernel = np.array([[0.05, 0.0, 0.0],
                       [0.0,  0.90, 0.05],
                       [0.0,  0.0,  0.0]], dtype=np.float32)
    faded = cv2.filter2D(faded, -1, kernel)

    return np.clip(faded, 0, 255).astype(np.uint8)


def add_vignette_and_shadows(
    img_np: np.ndarray,
    intensity: float = 0.55,
    shadow_angle: float = 45.0
) -> np.ndarray:
    """
    Simulates mobile phone camera angle shadows and radial vignette falloff.
    Emulates real handheld photo capture where user's hand or phone casts an oblique shadow.
    """
    if img_np is None or img_np.size == 0:
        return img_np

    h, w = img_np.shape[:2]
    img_float = img_np.astype(np.float32)

    # 1. Radial camera lens vignette falloff from center
    y_coords = np.linspace(-1.0, 1.0, h, dtype=np.float32)
    x_coords = np.linspace(-1.0, 1.0, w, dtype=np.float32)
    x_grid, y_grid = np.meshgrid(x_coords, y_coords)
    radius = np.sqrt(x_grid ** 2 + y_grid ** 2)
    vignette = 1.0 - (radius / np.sqrt(2.0)) * (intensity * 0.35)
    vignette = np.clip(vignette, 0.55, 1.0)

    # 2. Handheld directional shadow gradient
    rad = np.radians(shadow_angle)
    # Directional projection
    grad = np.cos(rad) * x_grid + np.sin(rad) * y_grid
    # Normalize grad to [0, 1]
    grad_norm = (grad - grad.min()) / max(1e-5, (grad.max() - grad.min()))
    # Hand shadow covers approximately one half with smooth sigmoid/cosine transition
    shadow_factor = 1.0 - (1.0 - grad_norm) * (intensity * 0.45)
    shadow_factor = np.clip(shadow_factor, 0.50, 1.0)

    # Combined illumination mask
    illum_mask = (vignette * shadow_factor)[:, :, np.newaxis]
    illum_mask = np.repeat(illum_mask, 3, axis=2)

    shadowed = img_float * illum_mask
    return np.clip(shadowed, 0, 255).astype(np.uint8)


def apply_composite_sketch_stress(img_np: np.ndarray) -> np.ndarray:
    """
    Applies the full composite stress pipeline:
      Notebook Lines -> Pencil Fade & Jitter -> Mobile Phone Shadow
    Simulates high-difficulty production capture conditions.
    """
    if img_np is None or img_np.size == 0:
        return img_np

    step1 = add_ruled_notebook_lines(img_np)
    step2 = add_pencil_jitter_and_fade(step1)
    step3 = add_vignette_and_shadows(step2)
    return step3
