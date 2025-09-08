
from datetime import datetime
from pymongo import MongoClient
import os
from core.alert_manager import AlertManager

class SafetyMonitorBot:
    def __init__(self):
        self.alert_manager = AlertManager()
        # MongoDB setup
        MONGO_URL = env("MONGO_URL", "mongodb+srv://545ohayu_db_user:zcwvKB50xnUHDzvY@cluster0.v8ym989.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        self.client = MongoClient(MONGO_URL)
        self.db = self.client["tourist_safety"]
        self.locations_collection = self.db["user_locations"]
        self.user_geofence_status = {}
        
    async def initialize(self):
        print("Safety Monitor Bot initialized")
        
    async def process_location_update(self, user_id: str, lat: float, lng: float):
        location_doc = {
            "user_id": user_id,
            "lat": lat,
            "lng": lng,
            "timestamp": datetime.utcnow()
        }
        self.locations_collection.insert_one(location_doc)
        print(f"Location updated for user {user_id}: {lat}, {lng}")

# Create global instance
monitor_bot = SafetyMonitorBot()