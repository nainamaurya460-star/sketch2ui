from pydantic import BaseModel, Field
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

# Priority 3 API Contract Schemas
class DetectedElement(BaseModel):
    name: str
    conf: str
    box: List[int]
    color: Optional[str] = None

class GeneratedCode(BaseModel):
    framework: str = "React + Tailwind"
    jsx: str
    tailwind: str
    json_data: str = Field(alias="json", serialization_alias="json")

    model_config = {
        "populate_by_name": True
    }

class SketchPredictResponse(BaseModel):
    status: str = "success"
    project_name: str = "Synthesized Wireframe"
    elements_count: int
    detected_elements: List[DetectedElement]
    generated_code: GeneratedCode

    model_config = {
        "populate_by_name": True
    }

class ExportZipRequest(BaseModel):
    project_name: Optional[str] = "Synthesized Wireframe"
    jsx_code: str