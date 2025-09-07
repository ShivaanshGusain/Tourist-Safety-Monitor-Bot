from sqlalchemy import Column, String, DateTime, Boolean, JSON, Text, Float
from datetime import datetime
import uuid

from database import Base

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(255), nullable=False, index=True)
    alert_type = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=False)
    
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    location_name = Column(String(500), nullable=True)
    
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)
    user_response = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=True)
    
    push_sent = Column(Boolean, default=False)
    sms_sent = Column(Boolean, default=False)
    email_sent = Column(Boolean, default=False)