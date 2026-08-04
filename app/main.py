from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np

# Services & Schemas Imports
from app.services.cv_engine import preprocess_sketch

app = FastAPI(
    title="ASketch2UI API",
    description="Backend API engine for sketch processing and UI component detection",
    version="1.0.0"
)

# CORS Setup for Frontend Integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health"])
def read_root():
    return {"message": "Welcome to ASketch2UI Backend Engine!"}

@app.post("/api/detect-contours", tags=["Sketch Engine"])
async def detect_contours(file: UploadFile = File(...)):
    """
    Upload a wireframe sketch image to extract bounding boxes for UI components.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid image")

    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image file format")

        # 1. Apply Shalini's preprocess engine
        processed_image = preprocess_sketch(image)

        # 2. Extract contours
        contours, _ = cv2.findContours(
            processed_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        boxes = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            # Filter noise dots
            if w > 15 and h > 15:
                boxes.append({"x": x, "y": y, "width": w, "height": h})

        return {
            "status": "success",
            "total_shapes": len(boxes),
            "bounding_boxes": boxes
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")