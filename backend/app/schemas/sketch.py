from pydantic import BaseModel
from typing import List, Optional

class BoundingBox(BaseModel):
    x: int
    y: int
    width: int
    height: int

class ContourDetectionResponse(BaseModel):
    status: str
    total_shapes: int
    bounding_boxes: List[BoundingBox]

class ElementPrediction(BaseModel):
    label: str
    confidence: float
    box: BoundingBox

class SketchProcessResponse(BaseModel):
    status: str
    detected_elements: List[ElementPrediction]