"""
Configuration Settings for CivicFix Main Backend.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "civicfix"

    CLASSIFICATION_SERVICE_URL: str = "http://localhost:8000"
    DUPLICATE_DETECTION_SERVICE_URL: str = "http://localhost:8001"

    CLASSIFICATION_SERVICE_TIMEOUT: float = 60.0
    DUPLICATE_DETECTION_SERVICE_TIMEOUT: float = 30.0

    AI_HIGH_CONFIDENCE_THRESHOLD: float = 0.85

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
