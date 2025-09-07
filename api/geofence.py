from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter()

class GeofenceCreate(BaseModel):
    name: str
    place_id: str
    center_lat: float
    center_lng: float
    radius: float
    description: str = None

# In-memory storage for now
geofences = {}

@router.post("/create/circle")
async def create_circular_geofence(geofence: GeofenceCreate):
    """Create a circular geofence"""
    if geofence.place_id in geofences:
        raise HTTPException(status_code=400, detail="Geofence already exists")
    
    geofences[geofence.place_id] = geofence.dict()
    return {"status": "created", "geofence": geofence}

@router.get("/list")
async def list_geofences():
    """List all geofences"""
    return {"geofences": list(geofences.values())}

@router.delete("/{geofence_id}")
async def delete_geofence(geofence_id: str):
    """Delete a geofence"""
    if geofence_id not in geofences:
        raise HTTPException(status_code=404, detail="Geofence not found")
    
    del geofences[geofence_id]
    return {"status": "deleted", "geofence_id": geofence_id}
