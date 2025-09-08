from pydantic import BaseModel
from typing import List, Optional

class GeofenceCreate(BaseModel):
    name: str
    place_id: str
    center_lat: float
    center_lng: float
    radius: float

class GeofenceResponse(BaseModel):
    place_id: str
    name: str
    type: str
    center_lat: Optional[float] = None
    center_lng: Optional[float] = None
    radius: Optional[float] = None
    created_at: str