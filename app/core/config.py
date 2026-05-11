from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Travel Planner API"
    database_url: str = "sqlite:///./travel_planner.db"
    artic_base_url: str = "https://api.artic.edu/api/v1"
    place_cache_ttl_seconds: int = 3600
    request_timeout_seconds: float = 10.0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
