from pydantic import BaseModel

class LocationUpdate(BaseModel):
    user_id: str
    lat: float
    lng: float

class LocationHistory(BaseModel):
    user_id: str
    lat: float
    lng: float
    timestamp: str