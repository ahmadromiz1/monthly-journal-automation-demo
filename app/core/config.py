from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Monthly Journal Automation Demo"
    app_env: str = "development"
    secret_key: str = Field(default="demo-secret-key-change-me", min_length=16)
    demo_username: str = "finance.demo"
    demo_password: str = "demo12345"
    database_url: str = f"sqlite:///{(BASE_DIR / 'storage' / 'monthly_journal.db').as_posix()}"
    upload_dir: Path = BASE_DIR / "storage" / "jobs"
    archive_dir: Path = BASE_DIR / "storage" / "archive"
    sample_input_dir: Path = BASE_DIR / "sample_data" / "input"
    sample_output_dir: Path = BASE_DIR / "sample_data" / "output"
    log_level: str = "INFO"
    warning_threshold: float = 100.0
    enable_inline_worker: bool = False
    worker_poll_seconds: int = 5


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
