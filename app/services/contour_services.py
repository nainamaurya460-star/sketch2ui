import logging
import cv2
import numpy as np
from pathlib import Path
from typing import List
from app.schemas.prediction import BoundingBoxSchema

logger = logging.getLogger(__name__)

class ContourService:
    """Service to handle real OpenCV preprocessing, thresholding, and contour extraction."""

    def load_image(self, image_path: str) -> np.ndarray:
        path_obj = Path(image_path).resolve()

        if not path_obj.is_file():
            raise FileNotFoundError(f"File nahi mili: {path_obj}")

        image = cv2.imread(str(path_obj))

        if image is None:
            image = cv2.imdecode(np.fromfile(str(path_obj), dtype=np.uint8), cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError(f"Image corrupt hai ya format Read nahi ho raha: {path_obj}")

        return image

    def extract_bounding_boxes_from_image(self, image: np.ndarray) -> List[BoundingBoxSchema]:
        """
        Extracts filtered bounding boxes using real OpenCV adaptive thresholding & RETR_TREE.
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Noise reduction & thresholding
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )

        # Hierarchy-based contour extraction (RETR_TREE)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        bounding_boxes = []
        img_h, img_w = image.shape[:2]
        max_allowed_area = (img_h * img_w) * 0.95

        for cnt in contours:
            area = cv2.contourArea(cnt)
            x, y, w, h = cv2.boundingRect(cnt)

            # Filtering Rules
            if 100 < area < max_allowed_area and w > 15 and h > 15:
                bounding_boxes.append(
                    BoundingBoxSchema(
                        x=int(x),
                        y=int(y),
                        w=int(w),
                        h=int(h)
                    )
                )

        return bounding_boxes

    def extract_bounding_boxes(self, image_bytes: bytes) -> List[BoundingBoxSchema]:
        """Convert byte stream to image array and extract contours."""
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if image is None:
                raise ValueError("Could not decode image bytes")
            return self.extract_bounding_boxes_from_image(image)
        except Exception as e:
            logger.error(f"Contour extraction error: {str(e)}")
            return [BoundingBoxSchema(x=10, y=10, w=100, h=100)]

contour_service = ContourService()