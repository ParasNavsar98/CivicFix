"""
Configuration settings for Duplicate Candidate Detection module.
Implementation Decision (not mandated by SRS): Default weights and thresholds.
SRS mandates that DUPLICATE_SIMILARITY_THRESHOLD must be configurable.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_DIMENSION: int = 384
    VECTOR_TOP_K: int = 10

    # Configurable duplicate similarity / composite thresholds
    DUPLICATE_SIMILARITY_THRESHOLD: float = 0.75
    LOCATION_DISTANCE_THRESHOLD_KM: float = 5.0

    # Configurable multi-factor scoring weights (Must sum to 1.0)
    SEMANTIC_WEIGHT: float = 0.50
    PRIMARY_DOMAIN_WEIGHT: float = 0.15
    SUBCATEGORY_WEIGHT: float = 0.15
    SECONDARY_DOMAIN_WEIGHT: float = 0.10
    LOCATION_WEIGHT: float = 0.10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
