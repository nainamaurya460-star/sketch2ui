from pathlib import Path
from typing import List
import cv2
import numpy as np
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.core.limiter import limiter
from app.services.file_service import read_uploaded_file
from app.services.cv_engine import preprocess_sketch
from app.services.camera_services import detect_paper_and_warp
from app.services.yolo_service import get_yolo_classifier
from app.services.heuristic_service import synthesize_layout_code
from app.services.ocr_service import get_ocr_service
from app.services.export_service import generate_project_zip, sanitize_project_name
from app.schemas.sketch import SketchPredictResponse, ExportZipRequest

router = APIRouter(prefix="/api/v1/sketch", tags=["Sketch Engine"])


ALLOWED_MIME_TYPES = {
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp"
}

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


@router.post("/predict", response_model=SketchPredictResponse)
@limiter.limit("20/minute")
async def predict_sketch(request: Request, file: UploadFile = File(...)):

    """
    End-to-End Prediction Endpoint:
      1. Validates image MIME-type & safe OpenCV BGR decoding.
      2. Step A: Perspective warp detection via camera_services.
      3. Step B: YOLOv8 component inference (app/models/best.pt).
      4. Step C: Spatial hierarchy sorting, container grouping & React + Tailwind code synthesis.
    """
    # 1. Validate image mime-type and extension
    content_type = (file.content_type or "").lower()
    ext = Path(file.filename or "").suffix.lower()

    if content_type not in ALLOWED_MIME_TYPES and ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format ({content_type or ext}). Please upload a PNG, JPEG, or WEBP image."
        )

    # Read bytes safely
    try:
        contents = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read uploaded file: {str(e)}")

    if not contents or len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Convert file bytes to OpenCV BGR numpy array safely
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        raise HTTPException(status_code=400, detail="Invalid or corrupted image file format.")

    # Step A (Perspective Warp): Pass to detect_paper_and_warp(image)
    active_image = image
    try:
        warped_crop, paper_found = detect_paper_and_warp(image)
        if paper_found and warped_crop is not None and warped_crop.size > 0:
            # Check minimum viable dimensions for warped crop
            if warped_crop.shape[0] >= 30 and warped_crop.shape[1] >= 30:
                active_image = warped_crop
    except Exception:
        # Fallback safely to raw image on warp error
        active_image = image

    # Step B (YOLOv8 Detection): Run inference using YOLO('app/models/best.pt')
    classifier = get_yolo_classifier()
    detected_elements = classifier.predict_image(active_image, confidence_threshold=0.25)

    # If warp cropped out elements or yielded zero, try the raw image
    if len(detected_elements) == 0 and active_image is not image:
        raw_detections = classifier.predict_image(image, confidence_threshold=0.25)
        if len(raw_detections) > 0:
            detected_elements = raw_detections

    # Try lower threshold if still zero detections
    if len(detected_elements) == 0:
        detected_elements = classifier.predict_image(active_image, confidence_threshold=0.15)

    # Determine project name from filename
    project_name = "Synthesized Wireframe"
    if file.filename:
        stem = Path(file.filename).stem
        if stem and stem.lower() not in ["image", "untitled", "file", "blob", "sketch", "captured_frame"]:
            clean_name = stem.replace("_", " ").replace("-", " ").strip().title()
            if clean_name:
                project_name = clean_name

    # Step C: Handwritten Text OCR Pipeline (Sprint 2)
    ocr_service = get_ocr_service()
    detected_elements = ocr_service.batch_extract_component_texts(active_image, detected_elements)

    # Step D: Spatial Hierarchy & Layout-to-Code Generator
    generated_code = synthesize_layout_code(detected_elements, project_name=project_name)

    # Format detected elements for response contract:
    # { "name": <str>, "conf": "<int>%", "box": [ymin, xmin, ymax, xmax] }
    response_elements = []
    for item in detected_elements:
        el_dict = {
            "name": item["name"],
            "conf": item["conf"],
            "box": item["box"],
            "color": item.get("color", "bg-cyan-500")
        }
        if item.get("text"):
            el_dict["text"] = item["text"]
        response_elements.append(el_dict)

    return {
        "status": "success",
        "project_name": project_name,
        "elements_count": len(response_elements),
        "detected_elements": response_elements,
        "generated_code": generated_code
    }


@router.post("/process")
async def process_sketch(file: UploadFile = File(...)):
    """
    Legacy contour-based process endpoint for backward compatibility.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    try:
        contents = await file.read()
        image = read_uploaded_file(contents)

        if image is None:
            raise HTTPException(status_code=400, detail="Corrupted or unreadable image file.")

        processed_img = preprocess_sketch(image)

        contours, _ = cv2.findContours(
            processed_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        components = []
        for idx, cnt in enumerate(contours):
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 20 and h > 20:
                components.append({
                    "id": idx + 1,
                    "x": int(x),
                    "y": int(y),
                    "width": int(w),
                    "height": int(h),
                    "type": "detected_element"
                })

        return {
            "status": "success",
            "filename": file.filename,
            "total_elements": len(components),
            "elements": components
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline Error: {str(e)}")


@router.post("/export-zip")
@limiter.limit("30/minute")
async def export_project_zip(request: Request, payload: ExportZipRequest):
    """
    In-Memory Project ZIP Export Endpoint:
      1. Validates presence of synthesized JSX code.
      2. Generates complete Vite + React 19 + Tailwind CSS boilerplate in memory.
      3. Streams ZIP directly with Content-Disposition attachment header.
    """
    if not payload.jsx_code or not payload.jsx_code.strip():
        raise HTTPException(status_code=400, detail="jsx_code cannot be empty.")

    sanitized_name = f"sketch2ui_{sanitize_project_name(payload.project_name)}"
    filename = f"{sanitized_name}.zip"

    try:
        zip_buffer = generate_project_zip(
            project_name=payload.project_name or "Synthesized Wireframe",
            jsx_code=payload.jsx_code
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate project ZIP: {str(e)}")

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )