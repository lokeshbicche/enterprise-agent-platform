"""Application settings loaded from the environment or a local .env file."""

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Required credentials and service configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    postgres_dsn: str = Field(min_length=1)
    openai_api_key: SecretStr
    api_bearer_token: SecretStr = Field(min_length=32)
    model_name: str = "openai:gpt-4o-mini"
    deep_agent_model_name: str = "openai:gpt-4o-mini"
    postgres_pool_min_size: int = Field(default=1, ge=1)
    postgres_pool_max_size: int = Field(default=10, ge=1)

    @model_validator(mode="after")
    def pool_max_must_cover_min(self) -> "Settings":
        if self.postgres_pool_max_size < self.postgres_pool_min_size:
            raise ValueError("POSTGRES_POOL_MAX_SIZE must be >= POSTGRES_POOL_MIN_SIZE.")
        return self
