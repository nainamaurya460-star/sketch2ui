from typing import List, Optional, Tuple
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