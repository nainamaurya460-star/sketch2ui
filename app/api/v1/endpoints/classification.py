from fastapi import APIRouter, HTTPException, status
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.classification import classification_service

router = APIRouter()

@router.post(
    "/classify",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Classify UI elements from sketches",
    description="Endpoint to classify bounding boxes into UI elements using service logic."
)
async def classify_elements(request: PredictionRequest):
    try:
        predictions = classification_service.classify_bounding_boxes(
            bounding_boxes=request.bounding_boxes
        )

        return PredictionResponse(
            success=True,
            total_elements=len(predictions),
            predictions=predictions,
            message="UI elements classified successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Classification failed: {str(e)}"
        )