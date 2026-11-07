import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_optional
from app.models.user import User
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/projects", tags=["Projects"])


@router.get("", response_model=List[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Returns list of projects belonging to the current user.
    If unauthenticated (Guest Mode), returns unassigned guest projects.
    """
    if current_user:
        projects = (
            db.query(Project)
            .filter(Project.user_id == current_user.id)
            .order_by(Project.updated_at.desc())
            .all()
        )
    else:
        projects = (
            db.query(Project)
            .filter(Project.user_id.is_(None))
            .order_by(Project.updated_at.desc())
            .all()
        )
    return projects


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Creates a new project record.
    Associates with authenticated user if logged in, or leaves user_id=None for Guest Mode.
    """
    user_id = current_user.id if current_user else None
    new_project = Project(
        user_id=user_id,
        title=payload.title or "Untitled Wireframe",
        thumbnail_url=payload.thumbnail_url or "",
        ast_json=payload.ast_json,
        jsx_code=payload.jsx_code or "",
        tailwind_code=payload.tailwind_code or ""
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Retrieves a single project by ID with tenant isolation checks.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found"
        )

    # Tenant isolation guardrail
    if project.user_id is not None:
        if not current_user or current_user.id != project.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this project"
            )

    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Updates an existing project record.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found"
        )

    # Tenant isolation guardrail
    if project.user_id is not None:
        if not current_user or current_user.id != project.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to modify this project"
            )

    if payload.title is not None:
        project.title = payload.title
    if payload.thumbnail_url is not None:
        project.thumbnail_url = payload.thumbnail_url
    if payload.ast_json is not None:
        project.ast_json = payload.ast_json
    if payload.jsx_code is not None:
        project.jsx_code = payload.jsx_code
    if payload.tailwind_code is not None:
        project.tailwind_code = payload.tailwind_code

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_200_OK)
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Deletes an existing project record with tenant validation.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found"
        )

    # Tenant isolation guardrail
    if project.user_id is not None:
        if not current_user or current_user.id != project.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to delete this project"
            )

    db.delete(project)
    db.commit()
    return {
        "status": "success",
        "message": f"Project '{project_id}' deleted successfully",
        "id": project_id
    }
