from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")

    DISCORD_TOKEN: str
    GEMINI_API_KEY: str


settings = Settings()  # type: ignore
