from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Application configuration using environment variables."""

    # Wazuh API
    wazuh_api_url: str = "https://127.0.0.1:55000"
    wazuh_user: str = "wazuh"
    wazuh_password: str
    wazuh_verify_ssl: bool = False

    # AI Mode: "local" (only vLLM), "external" (only OpenAI), "mixed" (both)
    ai_mode: Literal["local", "external", "mixed"] = "mixed"

    # AI Configuration - vLLM (Local) - Only used if ai_mode is "local" or "mixed"
    vllm_api_url: str = "http://vllm:8000/v1"
    vllm_model: str = "meta-llama/Meta-Llama-3-8B-Instruct"

    # AI Configuration - OpenAI (External) - Only used if ai_mode is "external" or "mixed"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4"
    openai_base_url: str = "https://api.openai.com/v1"

    # App settings
    app_env: Literal["development", "production"] = "development"
    app_port: int = 8000
    log_level: str = "INFO"
    secret_key: str

    # Database (optional)
    database_url: str = "sqlite:///./sca_history.db"

    # Redis (optional)
    redis_url: str | None = None

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
