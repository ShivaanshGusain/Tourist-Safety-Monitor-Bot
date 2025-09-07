from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "Tourist Safety Bot"
    database_url: str = "postgresql://postgres:password123@localhost:5432/safety_db"
    redis_url: str = "redis://localhost:6379"
    osm_api_timeout: int = 30
    osm_user_agent: str = "TouristSafetyBot/1.0"
    alert_cooldown_minutes: int = 5
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        # This allows the app to run even if .env is missing
        env_ignore_empty = True

settings = Settings()