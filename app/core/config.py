from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, read from environment variables prefixed with IMS_."""

    model_config = SettingsConfigDict(env_prefix="IMS_", env_file=".env", extra="ignore")

    app_name: str = "Inventory Management System"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://ims:ims@localhost:5432/ims"
    sql_echo: bool = False
    api_prefix: str = "/api"


@lru_cache
def get_settings() -> Settings:
    return Settings()
