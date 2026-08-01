from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to ASketch2UI Backend"}
from fastapi import FastAPI, UploadFile, File, HTTPException
import cv2
import numpy as np
from app.services.contour_services import extract_contours

app = FastAPI(title="Asketch2UI API")

@app.get("/")
def read_root():
    return {"message": "Asketch2UI Backend is running!"}

@app.post("/api/detect-contours")
async def detect_contours(file: UploadFile = File(...)):
    # 1. Image file content read karo
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise HTTPException(status_code=400, detail="Invalid image file")
        
    # 2. Contour extraction service call karo
    boxes = extract_contours(image)
    
    # 3. JSON format me bounding boxes return karo
    return {
        "status": "success",
        "total_shapes": len(boxes),
        "bounding_boxes": boxes
    }