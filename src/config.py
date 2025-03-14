from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    # Telegram App API
    telegram_app_api_id: int
    telegram_app_api_hash: str
    telegram_app_phone_number: str

    # OpenAI API
    openai_api_key: str
    openai_base_url: str
    openai_model: str

    # Telegram bots
    telegram_bot_token: str
    telegram_logs_bot_token: str

    # Telegram channels for listening
    telegram_channels: list[str] = Field(default_factory=list)

    # Telegram messages fraudulent keywords
    telegram_messages_fraudulent_keywords: list[str] = Field(default_factory=list)

    # Logs
    logs_recepients: list[int] = Field(default_factory=list)

    # Clickhouse
    clickhouse_host: str
    clickhouse_user: str
    clickhouse_password: str
    clickhouse_port: int
    clickhouse_secure: bool

    # Web
    frontend_origin: str

    class Config:
        env_file = Path(__file__).parent / '.env'


settings = Settings()