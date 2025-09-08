from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List

router = APIRouter()

class Alert(BaseModel):
    user_id: str
    alert_type: str
    message: str
    severity: str = "MEDIUM"

# In-memory storage
alerts = []

@router.get("/{user_id}")
async def get_user_alerts(user_id: str):
    """Get alerts for a specific user"""
    user_alerts = [a for a in alerts if a.get("user_id") == user_id]
    return {"user_id": user_id, "alerts": user_alerts}

@router.post("/create")
async def create_alert(alert: Alert):
    """Create a new alert"""
    alert_dict = alert.dict()
    alert_dict["timestamp"] = datetime.now().isoformat()
    alert_dict["id"] = len(alerts) + 1
    alerts.append(alert_dict)
    return {"status": "created", "alert": alert_dict}

@router.delete("/{alert_id}")
async def acknowledge_alert(alert_id: int):
    """Acknowledge and remove an alert"""
    global alerts
    alerts = [a for a in alerts if a.get("id") != alert_id]
    return {"status": "acknowledged", "alert_id": alert_id}
'''
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List
from pymongo import MongoClient
import os

router = APIRouter()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URL)
db = client["tourist_safety"]
alerts_collection = db["alerts"]

class Alert(BaseModel):
    user_id: str
    alert_type: str
    message: str
    severity: str = "MEDIUM"

@router.get("/{user_id}")
async def get_user_alerts(user_id: str):
    """Get alerts for a specific user"""
    user_alerts = list(alerts_collection.find({"user_id": user_id}, {"_id": 0}))
    return {"user_id": user_id, "alerts": user_alerts}

@router.post("/create")
async def create_alert(alert: Alert):
    """Create a new alert"""
    alert_dict = alert.dict()
    alert_dict["timestamp"] = datetime.now().isoformat()
    # Generate a unique id (could use ObjectId, but keeping int for compatibility)
    last_alert = alerts_collection.find_one(sort=[("id", -1)])
    alert_dict["id"] = (last_alert["id"] + 1) if last_alert and "id" in last_alert else 1
    alerts_collection.insert_one(alert_dict)
    return {"status": "created", "alert": alert_dict}

@router.delete("/{alert_id}")
async def acknowledge_alert(alert_id: int):
    """Acknowledge and remove an alert"""
    result = alerts_collection.delete_one({"id": alert_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"status": "acknowledged", "alert_id": alert_id}
    '''