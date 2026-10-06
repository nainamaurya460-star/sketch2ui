from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.file_service import read_uploaded_file
from app.services.cv_engine import preprocess_sketch
import cv2

router = APIRouter()

@router.post("/process")
async def process_sketch(file: UploadFile = File(...)):
    """
    Processes an uploaded sketch image and returns detected component bounding boxes.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    try:
        # 1. Read bytes to image
        contents = await file.read()
        image = read_uploaded_file(contents)

        if image is None:
            raise HTTPException(status_code=400, detail="Corrupted or unreadable image file.")

        # 2. Preprocess image (Noise removal & adaptive thresholding)
        processed_img = preprocess_sketch(image)

        # 3. Extract bounding boxes using contours
        contours, _ = cv2.findContours(
            processed_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        components = []
        for idx, cnt in enumerate(contours):
            x, y, w, h = cv2.boundingRect(cnt)
            # Filter noise specs
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