"""Application configuration loaded from environment and YAML config files."""

import os
from pathlib import Path
from functools import lru_cache
from typing import Any

import yaml
from pydantic_settings import BaseSettings
from pydantic import Field


# Project root directory
ROOT_DIR = Path(__file__).resolve().parent.parent


def load_yaml_config(config_name: str = "default") -> dict[str, Any]:
    """Load a YAML config file from the config/ directory."""
    config_path = ROOT_DIR / "config" / f"{config_name}.yaml"
    if not config_path.exists():
        return {}
    with open(config_path, "r") as f:
        return yaml.safe_load(f) or {}


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Application
    app_name: str = "DocShield AI"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-me-in-production"
    mock_mode: bool = False

    # Database
    database_url: str = "sqlite:///./docshield.db"

    # Auth
    jwt_secret_key: str = "change-me-jwt-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 480

    # File Storage
    upload_dir: str = "./uploads"
    max_file_size_mb: int = 20

    # Model Paths
    model_dir: str = "./models"
    ocr_model_path: str = ""
    face_model_path: str = ""
    forensic_model_path: str = ""

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Logging
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def upload_path(self) -> Path:
        path = Path(self.upload_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def model_path(self) -> Path:
        path = Path(self.model_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


@lru_cache()
def get_pipeline_config() -> dict[str, Any]:
    """Get cached pipeline configuration from YAML."""
    return load_yaml_config("default")
