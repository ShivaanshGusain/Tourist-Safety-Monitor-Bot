from sqlalchemy import Column, String, Float, DateTime, Integer, Boolean, JSON
from datetime import datetime
import uuid

from database import Base

class LocationHistory(Base):
    __tablename__ = "location_history"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(255), nullable=False, index=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=True)
    altitude = Column(Float, nullable=True)
    speed = Column(Float, nullable=True)
    heading = Column(Float, nullable=True)
    battery_level = Column(Integer, nullable=True)
    
    address = Column(JSON, nullable=True)
    location_type = Column(String(100), nullable=True)
    
    inside_geofence = Column(Boolean, default=True)
    nearest_geofence_id = Column(String(36), nullable=True)
    distance_from_geofence = Column(Float, nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)