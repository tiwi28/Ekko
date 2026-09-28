"""Application settings loaded from environment variables (and backend/.env)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database (Neon URLs need ?sslmode=require)
    database_url: str
    db_pool_min_size: int = 1
    db_pool_max_size: int = 5

    # Gemini
    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash"

    # Reddit (script-type app credentials from https://www.reddit.com/prefs/apps)
    reddit_client_id: str
    reddit_client_secret: str
    reddit_user_agent: str = "ekko/0.1"

    # Shared secret the GitHub Actions cron sends in the X-Cron-Secret header
    cron_secret: str

    # Auth
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7

    # Comma-separated list of allowed frontend origins
    cors_origins: str = "http://localhost:5173"

    # Pipeline
    digest_size: int = 10

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
