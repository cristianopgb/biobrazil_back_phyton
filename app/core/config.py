from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    service_name: str = "coletor-contabil-api"
    environment: str = Field(default="development", alias="ENVIRONMENT")
    frontend_origin: str = Field(alias="FRONTEND_ORIGIN")
    supabase_url: str = Field(alias="SUPABASE_URL")
    supabase_service_role_key: str = Field(alias="SUPABASE_SERVICE_ROLE_KEY")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")


@lru_cache
def get_settings() -> Settings:
    return Settings()
