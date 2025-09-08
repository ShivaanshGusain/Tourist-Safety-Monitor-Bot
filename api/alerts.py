from fastapi import APIRouter, HTTPException
from typing import Optional, List
try:
    from models.alert import AlertResponse
except ImportError:
    # Fallback if models aren't set up yet
    from pydantic import BaseModel
    class AlertResponse(BaseModel):
        alert_id: str
        type: str
        severity: str
        user_id: str
        title: str
        message: str
        timestamp: str

from core.alert_manager import AlertManager
from core.database import alerts_collection, redis_client

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

# Initialize alert manager
alert_manager = AlertManager(alerts_collection, redis_client)

@router.get("/{user_id}")
async def get_user_alerts(user_id: str, limit: Optional[int] = 50):
    """Get alerts for a user"""
    alerts = alert_manager.get_user_alerts(user_id, limit)
    return {"user_id": user_id, "alerts": alerts, "count": len(alerts)}