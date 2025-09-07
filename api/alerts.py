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
