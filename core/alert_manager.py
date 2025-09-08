
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import asyncio
from pymongo import MongoClient
import os

# Define alert types here instead of importing
class AlertSeverity:
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AlertType:
    GEOFENCE_EXIT = "GEOFENCE_EXIT"
    GEOFENCE_ENTRY = "GEOFENCE_ENTRY"
    UNSAFE_AREA = "UNSAFE_AREA"
    SOS = "SOS"

class AlertManager:
    def __init__(self):
        self.alert_cooldowns = {}
        # MongoDB setup
        MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
        self.client = MongoClient(MONGO_URL)
        self.db = self.client["tourist_safety"]
        self.alerts_collection = self.db["alerts"]
        
    async def send_exit_alert(self, user_id: str, geofence: Dict, current_location: Dict):
        alert = {
            "id": f"alert_{datetime.now().timestamp()}",
            "type": AlertType.GEOFENCE_EXIT,
            "severity": AlertSeverity.MEDIUM,
            "user_id": user_id,
            "title": "Safety Alert: Left Safe Zone",
            "message": f"You have left {geofence.get('name', 'the safe zone')}",
            "timestamp": datetime.now().isoformat()
        }
        self.alerts_collection.insert_one(alert)
        print(f"Alert generated: {alert}")
        return alert

    def get_alerts_for_user(self, user_id: str) -> List[Dict]:
        return list(self.alerts_collection.find({"user_id": user_id}, {"_id": 0}))