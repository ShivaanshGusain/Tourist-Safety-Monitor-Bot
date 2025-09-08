from fastapi import APIRouter, HTTPException
from typing import Optional
from models import AlertResponse
from core.alert_manager import AlertManager
from core.database import alerts_collection

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

# Initialize alert manager
alert_manager = AlertManager(alerts_collection)

@router.get("/{user_id}")
async def get_user_alerts(user_id: str, limit: Optional[int] = 50):
    """Get alerts for a user"""
    alerts = alert_manager.get_user_alerts(user_id, limit)
    return {"user_id": user_id, "alerts": alerts, "count": len(alerts)}