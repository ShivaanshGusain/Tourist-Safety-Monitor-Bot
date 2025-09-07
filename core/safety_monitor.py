from datetime import datetime
from typing import Dict
from core.alert_manager import AlertManager

class SafetyMonitorBot:
    def __init__(self):
        self.alert_manager = AlertManager()
        self.user_locations = {}
        self.user_geofence_status = {}
        
    async def initialize(self):
        print("Safety Monitor Bot initialized")
        
    async def process_location_update(self, user_id: str, lat: float, lng: float):
        self.user_locations[user_id] = {
            "lat": lat,
            "lng": lng,
            "timestamp": datetime.now()
        }
        print(f"Location updated for user {user_id}: {lat}, {lng}")

# Create global instance
monitor_bot = SafetyMonitorBot()
