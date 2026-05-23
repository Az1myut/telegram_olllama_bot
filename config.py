from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    # Telegram (required)
    telegram_bot_token: str

    # GitHub (optional)
    github_personal_access_token: Optional[str] = None
    github_username: Optional[str] = None

    # Email via mcp-server-email (optional)
    email_sender: Optional[str] = None
    email_password: Optional[str] = None
    email_smtp_host: str = "smtp.gmail.com"
    email_smtp_port: int = 587

    # Ollama
    # For local Ollama (with cloud models via `ollama signin`): use localhost
    # For direct Ollama cloud API: set OLLAMA_BASE_URL=https://ollama.com/v1 and OLLAMA_API_KEY
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_model: str = "qwen3.5:cloud"
    ollama_api_key: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()