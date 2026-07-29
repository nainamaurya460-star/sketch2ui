from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["Health"]
)

@router.get("/")
def health():
    return {
        "status": "success",
        "message": "Sketch2UI Backend is healthy."
    }