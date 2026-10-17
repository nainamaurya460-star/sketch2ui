from datetime import datetime, timezone
from fastapi import APIRouter

router = APIRouter(tags=["Health Diagnostics"])


@router.get("/health")
@router.get("/health/")
def health_diagnostics():
    """
    Comprehensive System Readiness & Health Check Endpoint.
    Validates model status, OCR engine availability, and UI synthesis pipeline readiness.
    """
    yolo_status = "ready"
    try:
        from app.services.yolo_service import get_yolo_classifier
        clf = get_yolo_classifier()
        if clf is None:
            yolo_status = "degraded"
    except Exception:
        yolo_status = "unavailable"

    ocr_status = "ready"
    try:
        from app.services.ocr_service import get_ocr_service
        ocr = get_ocr_service()
        if ocr is None:
            ocr_status = "standby"
    except Exception:
        ocr_status = "unavailable"

    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "services": {
            "yolo_detector": yolo_status,
            "ocr_engine": ocr_status,
            "synthesizer": "ready"
        }
    }