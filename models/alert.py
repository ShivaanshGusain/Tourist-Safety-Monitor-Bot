from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime

class AlertBase(BaseModel):
    user_id: str
    type: str
    severity: str
    title: str
    message: str

class AlertCreate(AlertBase):
    metadata: Optional[Dict] = {}

class Alert(AlertBase):
    alert_id: str
    timestamp: str
    read: bool = False
    acknowledged: bool = False
    metadata: Dict = {}
    
class AlertResponse(BaseModel):
    alert_id: str
    type: str
    severity: str
    user_id: str
    title: str
    message: str
    timestamp: str
    read: bool
    acknowledged: bool
    metadata: Optional[Dict] = {}