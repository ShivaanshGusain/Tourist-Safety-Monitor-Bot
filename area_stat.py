from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
from pymongo import MongoClient
import os

MONGO_URL = os.getenv("MONGO_URL", "mmongodb+srv://545ohayu_db_user:zcwvKB50xnUHDzvY@cluster0.v8ym989.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
client = MongoClient(MONGO_URL)
db = client["tourist_safety"]
area_stats_collection = db["area_stats"]

@dataclass
class AreaStats:
    geohash: str
    total_incidents: int = 0
    recent_incidents: int = 0
    safety_score: float = 1.0
    last_incident: Optional[datetime] = None
    incident_types: dict = None
    last_updated: datetime = None

    def __post_init__(self):
        if self.incident_types is None:
            self.incident_types = {}
        if self.last_updated is None:
            self.last_updated = datetime.now()

    def add_incident(self, incident_type: str):
        self.total_incidents += 1
        self.recent_incidents += 1
        self.last_incident = datetime.now()
        if incident_type not in self.incident_types:
            self.incident_types[incident_type] = 0
        self.incident_types[incident_type] += 1
        self.update_safety_score()
        self.last_updated = datetime.now()
        self.save_to_db()

    def update_safety_score(self):
        if self.recent_incidents == 0:
            self.safety_score = 1.0
        elif self.recent_incidents < 3:
            self.safety_score = 0.8
        elif self.recent_incidents < 5:
            self.safety_score = 0.6
        elif self.recent_incidents < 10:
            self.safety_score = 0.4
        else:
            self.safety_score = 0.2

    def to_dict(self):
        return {
            "geohash": self.geohash,
            "total_incidents": self.total_incidents,
            "recent_incidents": self.recent_incidents,
            "safety_score": self.safety_score,
            "last_incident": self.last_incident.isoformat() if self.last_incident else None,
            "incident_types": self.incident_types,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        }

    def save_to_db(self):
        """Upsert this area's stats in MongoDB"""
        area_stats_collection.update_one(
            {"geohash": self.geohash},
            {"$set": self.to_dict()},
            upsert=True
        )

    @staticmethod
    def load_from_db(geohash: str):
        doc = area_stats_collection.find_one({"geohash": geohash})
        if doc:
            doc["last_incident"] = datetime.fromisoformat(doc["last_incident"]) if doc.get("last_incident") else None
            doc["last_updated"] = datetime.fromisoformat(doc["last_updated"]) if doc.get("last_updated") else None
            return AreaStats(**doc)
        return None
