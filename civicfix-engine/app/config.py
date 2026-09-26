"""
Unified Configuration for civicfix-engine.
Consolidates configuration settings for Classification, Duplicate Detection,
University Matching, and Database access.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Server Configuration ---
    APP_TITLE: str = "CivicFix Integrated AI Engine & Capability Portal"
    APP_VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # --- Database Configuration ---
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "civicfix"

    # --- Feature 1: Classification Engine Settings ---
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gemma3:4b"
    LLM_TIMEOUT_SECONDS: float = 60.0
    LLM_MAX_RETRIES: int = 3
    AI_HIGH_CONFIDENCE_THRESHOLD: float = 0.85
    AI_REVIEW_THRESHOLD: float = 0.60

    # --- Feature 2: Duplicate Detection Engine Settings ---
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_DIMENSION: int = 384
    VECTOR_TOP_K: int = 10
    DUPLICATE_SIMILARITY_THRESHOLD: float = 0.75
    STRONG_CANDIDATE_THRESHOLD: float = 0.85
    SEMANTIC_STRONG_THRESHOLD: float = 0.82
    SEMANTIC_CANDIDATE_THRESHOLD: float = 0.70
    LOCATION_DISTANCE_THRESHOLD_KM: float = 5.0

    # Multi-factor weights for duplicate scoring
    SEMANTIC_WEIGHT: float = 0.50
    PRIMARY_DOMAIN_WEIGHT: float = 0.15
    SUBCATEGORY_WEIGHT: float = 0.15
    SECONDARY_DOMAIN_WEIGHT: float = 0.10
    LOCATION_WEIGHT: float = 0.10
    SCORING_VERSION: str = "duplicate-v2"

    # --- Feature 3: University Matching Settings ---
    DEFAULT_ASSIGNMENT_DEADLINE_HOURS: int = 48
    DEFAULT_REMINDER_WINDOW_HOURS: int = 12
    DEV_MODE: bool = True
    SEED_ON_STARTUP: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
