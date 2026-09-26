"""
Central application configuration.

Every value here is overridable via environment variable (see .env.example).
IMPORTANT: this is the ONLY file that should read os.environ directly for
app-wide settings — everything else should import `settings` from here.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Database ---
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db_name: str = "university_matching"

    # --- Assignment workflow ---
    default_assignment_deadline_hours: int = 48
    default_reminder_window_hours: int = 12

    # --- Auth ---
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    dev_mode: bool = True

    # --- Seeding ---
    seed_on_startup: bool = True

    # --- CORS ---
    cors_origins: str = "http://localhost:5500,http://127.0.0.1:5500"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
