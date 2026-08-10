from typing import List
from app.schemas.prediction import ElementClassification, BoundingBoxSchema

class ClassificationService:
    def __init__(self):
        # Future expansion for YOLO model initialization
        pass

    def format_confidence(self, score: float) -> float:
        """Day 4 Refinement: Format confidence score to 2 decimal places."""
        return round(score, 2)

    def classify_bounding_boxes(
        self, bounding_boxes: List[BoundingBoxSchema]
    ) -> List[ElementClassification]:
        predictions = []

        if not bounding_boxes:
            # Fallback heuristic prediction if no boxes provided
            predictions.append(
                ElementClassification(
                    element_id=1,
                    label="InputBox",
                    confidence_score=self.format_confidence(0.90),
                    bounding_box=BoundingBoxSchema(x=10, y=20, w=150, h=40),
                    source="Heuristic"
                )
            )
            return predictions

        for idx, box in enumerate(bounding_boxes):
            # Simple heuristic classification based on aspect ratio
            aspect_ratio = box.w / float(box.h) if box.h > 0 else 1.0
            
            if aspect_ratio > 3.0:
                label = "InputBox"
                raw_confidence = 0.92345
            elif 0.8 <= aspect_ratio <= 1.2:
                label = "Button"
                raw_confidence = 0.88761
            else:
                label = "Card"
                raw_confidence = 0.85123

            predictions.append(
                ElementClassification(
                    element_id=idx + 1,
                    label=label,
                    confidence_score=self.format_confidence(raw_confidence),
                    bounding_box=box,
                    source="Heuristic"
                )
            )

        return predictions

classification_service = ClassificationService()