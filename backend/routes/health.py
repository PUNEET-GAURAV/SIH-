"""Health check route."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.database import get_db
from backend.config import get_settings
from backend.schemas import APIResponse

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint — verifies app and DB are running."""
    settings = get_settings()
    checks = {"app": "ok", "database": "ok"}

    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        checks["database"] = f"error: {str(e)}"

    all_ok = all(v == "ok" for v in checks.values())

    return APIResponse(
        success=all_ok,
        data={
            "status": "healthy" if all_ok else "degraded",
            "checks": checks,
            "version": "0.1.0",
            "mock_mode": settings.mock_mode,
            "environment": settings.app_env,
        },
    ).model_dump()
