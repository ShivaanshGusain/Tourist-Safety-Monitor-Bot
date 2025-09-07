from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class LocationUpdate(BaseModel):
    user_id: str
    lat: float
    lng: float

# In-memory storage
locations = {}

@router.post("/update")
async def update_location(location: LocationUpdate, background_tasks: BackgroundTasks):
    """Update user location"""
    locations[location.user_id] = {
        "lat": location.lat,
        "lng": location.lng,
        "timestamp": datetime.now()
    }
    
    # In a real app, this would trigger geofence checking
    # background_tasks.add_task(check_geofences, location)
    
    return {"status": "success", "message": "Location updated"}

@router.get("/history/{user_id}")
async def get_location_history(user_id: str):
    """Get user location history"""
    if user_id in locations:
        return {"user_id": user_id, "last_location": locations[user_id]}
    return {"user_id": user_id, "last_location": None}
