from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Any
from app.services.heuristic_service import process_ui_pipeline

router = APIRouter()

class BoundingBoxRequest(BaseModel):
    boxes: List[Any]

@router.post("/api/v1/predict", tags=["Prediction Engine"])
async def predict_ui_elements(payload: BoundingBoxRequest):
    try:
        if not payload.boxes:
            raise HTTPException(status_code=400, detail="Bounding boxes list cannot be empty.")
        result = process_ui_pipeline(payload.boxes)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))