from pydantic import (BaseModel):
class Component(BaseModel):
    id: int
    name: str
    x: float
    y: float
    width: float
    height: float