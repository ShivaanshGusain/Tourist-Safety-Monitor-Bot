from datetime import datetime, timedelta
from typing import Dict, List, Optional
import asyncio

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
        self.active_alerts = {}
        
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
        print(f"Alert generated: {alert}")
        return alert
