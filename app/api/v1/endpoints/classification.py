from fastapi import APIRouter, HTTPException, status
from app.schemas.prediction import (
    PredictionRequest, 
    PredictionResponse, 
    ElementClassification, 
    BoundingBoxSchema
)

router = APIRouter()

@router.post(
    "/classify",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Classify UI elements from sketches",
    description="Endpoint to classify bounding boxes into UI elements using YOLO/Heuristic models."
)
async def classify_elements(request: PredictionRequest):
    try:
        mock_predictions = []
        
        if request.bounding_boxes:
            for idx, box in enumerate(request.bounding_boxes):
                mock_predictions.append(
                    ElementClassification(
                        element_id=idx + 1,
                        label="Button",
                        confidence_score=0.95,
                        bounding_box=box,
                        source="Heuristic"
                    )
                )
        else:
            mock_predictions.append(
                ElementClassification(
                    element_id=1,
                    label="InputBox",
                    confidence_score=0.88,
                    bounding_box=BoundingBoxSchema(x=10, y=20, w=150, h=40),
                    source="Heuristic"
                )
            )

        return PredictionResponse(
            success=True,
            total_elements=len(mock_predictions),
            predictions=mock_predictions,
            message="Mock classification route executed successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Classification failed: {str(e)}"
        )