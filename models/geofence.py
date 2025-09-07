# Remove the self-import from geofence.py
from sqlalchemy import Column, String, Float, JSON, DateTime, Boolean
from datetime import datetime
import uuid
from database import Base

class Geofence(Base):
    __tablename__ = "geofences"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    place_id = Column(String(255), unique=True, nullable=False)
    type = Column(String(50), nullable=False)
    center_lat = Column(Float, nullable=True)
    center_lng = Column(Float, nullable=True)
    radius = Column(Float, nullable=True)
    polygon_coords = Column(JSON, nullable=True)
    description = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
