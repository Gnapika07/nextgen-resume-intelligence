from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

# This finds the backend/ folder no matter where you run from
# Path(__file__) = current file (config.py)
# .parent = app/ folder
# .parent.parent = backend/ folder  ← where .env lives
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    max_file_size_mb: int = 10
    upload_dir: str = "uploads"
    max_resumes_per_batch: int = 100
    app_name: str = "NextGen Resume Intelligence System"
    debug: bool = True

    class Config:
        # Use absolute path to find .env — this always works!
        env_file = str(BASE_DIR / ".env")
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()