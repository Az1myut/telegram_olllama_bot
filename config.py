from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    # Telegram (required)
    telegram_bot_token: str

    # GitHub (optional)
    github_personal_access_token: Optional[str] = None
    github_username: Optional[str] = None

    # Zapier MCP (optional)
    zapier_mcp_url: Optional[str] = None

    # Ollama
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_model: str = "llama3.1:8b"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()