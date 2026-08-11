import logging
from typing import List, Optional
from app.schemas.prediction import ElementClassification, BoundingBoxSchema

logger = logging.getLogger(__name__)

class ClassificationService:
    def __init__(self, model_path: Optional[str] = None):
        """Day 5: Vision Model Loader Interface"""
        self.model_path = model_path
        self.model = None
        self._load_model()

    def _load_model(self):
        """Loads vision weights if available."""
        if self.model_path:
            try:
                logger.info(f"Loading vision model from {self.model_path}")
            except Exception as e:
                logger.error(f"Failed to load model: {str(e)}")
                self.model = None

    def format_confidence(self, score: float) -> float:
        """Format confidence score to 2 decimal places."""
        return round(score, 2)

    def classify_bounding_boxes(
        self, bounding_boxes: List[BoundingBoxSchema]
    ) -> List[ElementClassification]:
        predictions = []

        if not bounding_boxes:
            predictions.append(
                ElementClassification(
                    element_id=1,
                    label="InputBox",
                    confidence_score=self.format_confidence(0.90),
                    bounding_box=BoundingBoxSchema(x=10, y=20, w=150, h=40),
                    source="Fallback-Heuristic"
                )
            )
            return predictions

        for idx, box in enumerate(bounding_boxes):
            aspect_ratio = box.w / float(box.h) if box.h > 0 else 1.0

            # Aapka Heuristic Logic + New Sidebar Condition
            if aspect_ratio > 3.0:
                label = "InputBox"
                raw_confidence = 0.92345
            elif 0.8 <= aspect_ratio <= 1.2:
                label = "Button"
                raw_confidence = 0.88761
            elif aspect_ratio < 0.5:
                label = "Sidebar"
                raw_confidence = 0.86000
            else:
                label = "Card"
                raw_confidence = 0.85123

            source = "YOLOv8-Engine" if self.model else "Vision-Heuristic"

            predictions.append(
                ElementClassification(
                    element_id=idx + 1,
                    label=label,
                    confidence_score=self.format_confidence(raw_confidence),
                    bounding_box=box,
                    source=source
                )
            )

        return predictions

classification_service = ClassificationService()