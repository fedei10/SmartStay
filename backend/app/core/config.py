from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Application settings."""

    APP_NAME: str
    APP_VERSION: str
    APP_DESCRIPTION: str
    ENVIRONMENT: str = "local"

    GOOGLE_API_KEY: str | None = Field(
        default=None,
        validation_alias=AliasChoices("GOOGLE_API_KEY", "GEMINI_API_KEY"),
    )
    GEMINI_MODEL: str = "gemini-2.5-flash"

    LITEAPI_API_KEY: str | None = Field(
        default=None,
        validation_alias=AliasChoices("LITEAPI_API_KEY", "LITE_API"),
    )
    LITEAPI_ENV: str = "sandbox"
    LITEAPI_MCP_TOOL_NAMES: str = "get_data_hotels"

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def LITEAPI_PAYMENT_PUBLIC_KEY(self) -> str:
        return "sandbox" if self.LITEAPI_ENV == "sandbox" else "live"

    @property
    def LITEAPI_MCP_ALLOWED_TOOLS(self) -> set[str]:
        return {
            tool_name.strip()
            for tool_name in self.LITEAPI_MCP_TOOL_NAMES.split(",")
            if tool_name.strip()
        }


settings = Settings()
