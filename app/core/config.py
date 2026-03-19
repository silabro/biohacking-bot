"""
Настройки приложения (pydantic-settings).

Считывает переменные окружения из .env файла.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Глобальные настройки приложения."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Telegram ──
    bot_token: str

    # ── Google Gemini AI ──
    gemini_api_key: str

    # ── PostgreSQL ──
    database_url: str

    # ── Redis ──
    redis_url: str = "redis://redis:6379/0"

    # ── Application-Level Encryption (MultiFernet) ──
    fernet_keys: str = ""

    # ── Logging ──
    log_level: str = "INFO"


settings = Settings()  # type: ignore[call-arg]
