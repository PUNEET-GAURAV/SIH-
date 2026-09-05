"""DocShield AI — FastAPI Application Entry Point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.database import engine
from backend.models import Base
from backend.utils.middleware import RequestIDMiddleware
from backend.routes import health, auth, screening, officer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("docshield")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle — startup and shutdown."""
    settings = get_settings()
    logger.info(f"Starting {settings.app_name} (env={settings.app_env}, mock_mode={settings.mock_mode})")

    # Create tables (for dev/SQLite; production uses Alembic migrations)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")

    # Ensure upload directory exists
    settings.upload_path.mkdir(parents=True, exist_ok=True)

    # Seed default admin user if no users exist
    from backend.database import SessionLocal
    from backend.models.user import User
    from backend.services.auth_service import AuthService
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            service = AuthService(db)
            service.register_user(
                username="admin",
                email="admin@docshield.local",
                password="admin1234",
                full_name="System Administrator",
                role="admin",
            )
            service.register_user(
                username="officer1",
                email="officer1@docshield.local",
                password="officer1234",
                full_name="Demo Officer",
                role="officer",
            )
            logger.info("Default users created (admin/admin1234, officer1/officer1234)")
    finally:
        db.close()

    yield

    logger.info("Shutting down DocShield AI")


def create_app() -> FastAPI:
    """Application factory."""
    settings = get_settings()

    app = FastAPI(
        title="DocShield AI",
        description="AI-assisted document screening and investigation system",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Middleware
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(screening.router)
    app.include_router(officer.router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
