# astra-backend/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # App
    app_name: str = "ASTRA"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # Database — required, no default, crashes if missing
    database_url: str

    # Redis
    redis_url: str = "redis://localhost:6379"

    # JWT — required, no default
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiry: int = 3600  # seconds

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()