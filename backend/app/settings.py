from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Financial Statement Intelligence Platform"
    database_url: str = "sqlite:///./financial_intelligence.db"
    frontend_origin: str = "http://localhost:5173"
    llm_provider: str = "auto"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-flash-lite-latest"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
