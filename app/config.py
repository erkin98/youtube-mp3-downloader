import os
from pathlib import Path
from pydantic import BaseSettings

class Settings(BaseSettings):
    API_KEY: str | None = None
    BASE_PATH: Path = Path(__file__).resolve().parent

    class Config:
        env_file = ".env"

settings = Settings()
