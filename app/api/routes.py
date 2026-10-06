from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from typing import List
from app.services.heuristic_service import process_ui_pipeline
app = FastAPI(tittle="Asketch2UI API", description="API for Asketch2UI")
class BoundingBoxRequest(BaseModel):
    boxes: List[List[int]]
@app.post("api/v1/predict")
async def predict_ui_elements(payload: BoundingBoxRequest):
    try:
        if not payload.boxes:
            raise HTTPException(status_code=400, detail="Bounding boxes list cannot be empty.")
        return result
    result = process_ui_pipeline(payload.boxes)
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))