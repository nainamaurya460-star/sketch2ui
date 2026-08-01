from pydantic import BaseModel

class Canvas(BaseModel):
    
    width: float
    height: float
