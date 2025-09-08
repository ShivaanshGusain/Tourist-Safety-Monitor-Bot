from pydantic import BaseModel
from typing import Optional

class LocationUpdate(BaseModel):
    user_id: str
    lat: float
    lng: float

class LocationHistory(BaseModel):
    user_id: str
    lat: float
    lng: float
    timestamp: str