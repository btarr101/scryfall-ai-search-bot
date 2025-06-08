from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, extra="ignore", env_file=".env")

    DISCORD_TOKEN: str
    GEMINI_API_KEY: str
    OTLP_ENDPOINT: str | None = None
    OTLP_USERNAME: str | None = None
    OTLP_PASSWORD: str | None = None
    OTLP_SERVICE: str = "scryfall-ai-search-dev"


settings = Settings()  # type: ignore
