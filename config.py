from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "Tourist Safety Bot"
    
    # MongoDB Configuration
    mongodb_url: Optional[str] = None
    mongo_db_name: str = "tourist_safety"
    
    # Redis Configuration (optional)
    redis_url: Optional[str] = None
    
    # OSM API Configuration
    osm_api_timeout: int = 30
    osm_user_agent: str = "TouristSafetyBot/1.0"
    
    # Application Settings
    alert_cooldown_minutes: int = 5
    geofence_check_interval: int = 60  # seconds
    max_geofence_radius: float = 5000  # meters
    
    # API Configuration
    api_prefix: str = "/api"
    cors_origins: list = ["*"]
    
    # Environment
    environment: str = "development"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False
        

settings = Settings()