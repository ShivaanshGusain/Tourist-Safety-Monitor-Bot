from pydantic import BaseModel
from typing import List, Optional

class GeofenceCreate(BaseModel):
    name: str
    place_id: str
    center_lat: float
    center_lng: float
    radius: float

class PolygonGeofenceCreate(BaseModel):
    name: str
    place_id: str
    coordinates: List[List[float]]

    class Config:
        schema_extra = {
            "example": {
                "name": "Central Park",
                "place_id": "park_001",
                "coordinates": [
                    [-73.9814, 40.7681],
                    [-73.9580, 40.7681],
                    [-73.9580, 40.8005],
                    [-73.9814, 40.8005],
                    [-73.9814, 40.7681]  # Close the polygon
                ]
            }
        }


class GeofenceResponse(BaseModel):
    place_id: str
    name: str
    type: str
    center_lat: Optional[float] = None
    center_lng: Optional[float] = None
    radius: Optional[float] = None
    polygon_coords: Optional[List[List[float]]] = None
    created_at: str
    updated_at: Optional[str] = None