import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # DATABASE_URL defaults to the required SQLite path
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:////data/app.db")
    # WEBHOOK_SECRET is required; startup fails if empty
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
