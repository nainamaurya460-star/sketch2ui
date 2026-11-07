from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    title: Optional[str] = "Untitled Wireframe"
    thumbnail_url: Optional[str] = ""
    ast_json: Optional[Any] = None
    jsx_code: Optional[str] = ""
    tailwind_code: Optional[str] = ""


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    thumbnail_url: Optional[str] = None
    ast_json: Optional[Any] = None
    jsx_code: Optional[str] = None
    tailwind_code: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    title: str
    thumbnail_url: Optional[str] = ""
    ast_json: Optional[Any] = None
    jsx_code: Optional[str] = ""
    tailwind_code: Optional[str] = ""
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
