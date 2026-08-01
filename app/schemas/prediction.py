from pydantic import BaseModel
class Prediction(BaseModel):
    label: str
    confidence: float

