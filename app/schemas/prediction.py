from typing import List, Optional
from pydantic import BaseModel, Field

class BoundingBoxSchema(BaseModel):
    """
    Bounding Box Coordinates: (x, y, width, height)
    """
    x: int = Field(..., description="Top-left corner X coordinate")
    y: int = Field(..., description="Top-left corner Y coordinate")
    w: int = Field(..., ge=1, description="Width of the element")
    h: int = Field(..., ge=1, description="Height of the element")

class PredictionRequest(BaseModel):
    """
    Request payload sent to classification endpoint
    """
    image_id: Optional[str] = Field(None, description="Unique identifier for the image")
    bounding_boxes: Optional[List[BoundingBoxSchema]] = Field(
        default=None, 
        description="Optional pre-extracted bounding boxes to classify"
    )

class ElementClassification(BaseModel):
    """
    Classification details for an individual detected UI element
    """
    element_id: int = Field(..., description="Unique index for the detected element")
    label: str = Field(..., description="UI element category (e.g., Button, InputBox, Card, Text)")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    bounding_box: BoundingBoxSchema = Field(..., description="Bounding box of the element")
    source: str = Field(..., description="Classification engine used ('YOLO' or 'Heuristic')")

class PredictionResponse(BaseModel):
    """
    Final API Response structure for UI Classification
    """
    success: bool = Field(True, description="Status of the classification request")
    total_elements: int = Field(..., description="Total UI elements classified")
    predictions: List[ElementClassification] = Field(..., description="List of classified UI elements")
    message: str = Field("Classification completed successfully", description="Status message")

def classify_component(box: dict) -> str:
    """
    Bounding box dictionary ke basis par UI element type predict karta hai.
    """
    w = box.get("width", box.get("w", 0))
    h = box.get("height", box.get("h", 0))
    area = w * h
    aspect_ratio = float(w) / h if h > 0 else 0.0
    
    if 15 <= w <= 45 and 15 <= h <= 45 and 0.8 <= aspect_ratio <= 1.2:
        return "Checkbox / Radio Button / Small Icon"
    elif aspect_ratio > 4.0 and h <= 60:
        return "input_field"
    elif 1.5 <= aspect_ratio <= 4.0 and 25 <= h <= 70:
        return "button"
    elif area > 15000:
        return "Card"
    else:
        return "Container"

def predict_ui_element(bounding_box: list) -> list:
    """
    Har Bounding box ke sath classification label attach karta hai. 
    """
    classified_components = []
    for box in bounding_box:
       label = classify_component(box)
       component = {
           "label": label, 
           "x": box.get("x"), 
           "y": box.get("y"), 
           "width": box.get("width", box.get("w")), 
           "height": box.get("height", box.get("h"))
       }
       classified_components.append(component)
    return classified_components