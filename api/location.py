from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from datetime import datetime
from typing import List
from pydantic import BaseModel
from core.safety_monitor import monitor_bot
from models.location import LocationHistory
from database import get_db

router = APIRouter()

class LocationUpdate(BaseModel):
    user_id: str
    lat: float
    lng: float
    accuracy: float = None
    battery_level: int = None

class LocationResponse(BaseModel):
    status: str
    message: str
    timestamp: datetime

@router.post("/update", response_model=LocationResponse)
async def update_location(
    location: LocationUpdate,
    background_tasks: BackgroundTasks
):
    """Receive location updates from mobile app"""
    try:
        # Process in background to avoid blocking
        background_tasks.add_task(
            monitor_bot.process_location_update,
            location.user_id,
            location.lat,
            location.lng
        )
        
        # Store in database for history
        background_tasks.add_task(
            save_location_history,
            location
        )
        
        return LocationResponse(
            status="success",
            message="Location update received",
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{user_id}")
async def get_location_history(
    user_id: str,
    limit: int = 100,
    db=Depends(get_db)
):
    """Get user's location history"""
    locations = db.query(LocationHistory)\
        .filter(LocationHistory.user_id == user_id)\
        .order_by(LocationHistory.timestamp.desc())\
        .limit(limit)\
        .all()
    
    return {"user_id": user_id, "locations": locations}

async def save_location_history(location: LocationUpdate):
    """Save location to database"""
    # Implementation for saving to database
    pass


'''
from fastapi import APIRouter, BackgroundTasks, HTTPException
from datetime import datetime
from typing import List
from pydantic import BaseModel
from core.safety_monitor import monitor_bot
from pymongo import MongoClient
import os

router = APIRouter()

# MongoDB setup
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URL)
db = client["tourist_safety"]
locations_collection = db["user_locations"]

class LocationUpdate(BaseModel):
    user_id: str
    lat: float
    lng: float
    accuracy: float = None
    battery_level: int = None

class LocationResponse(BaseModel):
    status: str
    message: str
    timestamp: datetime

@router.post("/update", response_model=LocationResponse)
async def update_location(
    location: LocationUpdate,
    background_tasks: BackgroundTasks
):
    """Receive location updates from mobile app"""
    try:
        # Process in background to avoid blocking
        background_tasks.add_task(
            monitor_bot.process_location_update,
            location.user_id,
            location.lat,
            location.lng
        )
        # Store in MongoDB for history
        background_tasks.add_task(
            save_location_history,
            location
        )
        return LocationResponse(
            status="success",
            message="Location update received",
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{user_id}")
async def get_location_history(
    user_id: str,
    limit: int = 100
):
    """Get user's location history"""
    locations = list(
        locations_collection.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("timestamp", -1).limit(limit)
    )
    return {"user_id": user_id, "locations": locations}

async def save_location_history(location: LocationUpdate):
    """Save location to MongoDB"""
    locations_collection.insert_one({
        "user_id": location.user_id,
        "lat": location.lat,
        "lng": location.lng,
        "accuracy": location.accuracy,
        "battery_level": location.battery_level,
        "timestamp": datetime.utcnow()
    })'''