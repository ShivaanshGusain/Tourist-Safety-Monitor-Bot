from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "Tourist Safety Bot"
    
    mongodb_url: Optional[str] = None
    mongo_db_name: str = "tourist_safety"
    
    redis_url: Optional[str] = None
    
    osm_api_timeout: int = 30
    osm_user_agent: str = "TouristSafetyBot/1.0"
    
    alert_cooldown_minutes: int = 5
    geofence_check_interval: int = 60  # seconds
    max_geofence_radius: float = 5000  # meters
    
    api_prefix: str = "/api"
    cors_origins: list = ["*"]
    
    environment: str = "development"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False
        

settings = Settings()