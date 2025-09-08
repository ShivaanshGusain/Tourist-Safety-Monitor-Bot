
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient
import os


router = APIRouter()

class GeofenceCreate(BaseModel):
    name: str
    place_id: str
    center_lat: float
    center_lng: float
    radius: float
    description: str = None

# MongoDB connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URL)
db = client["tourist_safety"]
geofences_collection = db["geofences"]

@router.post("/create/circle")
async def create_circular_geofence(geofence: GeofenceCreate):
    """Create a circular geofence"""
    if geofences_collection.find_one({"place_id": geofence.place_id}):
        raise HTTPException(status_code=400, detail="Geofence already exists")
    
    geofences_collection.insert_one(geofence.dict())
    return {"status": "created", "geofence": geofence}

@router.get("/list")
async def list_geofences():
    """List all geofences"""
    geofences = list(geofences_collection.find({}, {"_id": 0}))
    return {"geofences": geofences}

@router.delete("/{geofence_id}")
async def delete_geofence(geofence_id: str):
    """Delete a geofence"""
    result = geofences_collection.delete_one({"place_id": geofence_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Geofence not found")
    return {"status": "deleted", "geofence_id": geofence_id}