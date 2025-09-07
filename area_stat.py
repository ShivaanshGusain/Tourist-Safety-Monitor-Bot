from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

@dataclass
class AreaStats:
    """Statistics for a geographical area identified by geohash"""
    geohash: str
    total_incidents: int = 0
    recent_incidents: int = 0  # Last 24 hours
    safety_score: float = 1.0  # 0-1, where 1 is safest
    last_incident: Optional[datetime] = None
    incident_types: dict = None  # Count by type
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.incident_types is None:
            self.incident_types = {}
        if self.last_updated is None:
            self.last_updated = datetime.now()
    
    def add_incident(self, incident_type: str):
        """Record a new incident in this area"""
        self.total_incidents += 1
        self.recent_incidents += 1
        self.last_incident = datetime.now()
        
        # Track incident types
        if incident_type not in self.incident_types:
            self.incident_types[incident_type] = 0
        self.incident_types[incident_type] += 1
        
        # Recalculate safety score
        self.update_safety_score()
        
    def update_safety_score(self):
        """Calculate safety score based on incidents"""
        # Simple algorithm: more incidents = lower score
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
        """Convert to dictionary for JSON serialization"""
        return {
            "geohash": self.geohash,
            "total_incidents": self.total_incidents,
            "recent_incidents": self.recent_incidents,
            "safety_score": self.safety_score,
            "last_incident": self.last_incident.isoformat() if self.last_incident else None,
            "incident_types": self.incident_types,
            "last_updated": self.last_updated.isoformat()
        }