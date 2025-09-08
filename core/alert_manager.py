from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from pymongo.collection import Collection

# Alert enums
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
    LONG_STAY = "LONG_STAY"
    NO_MOVEMENT = "NO_MOVEMENT"

class AlertManager:
    def __init__(self, alerts_collection: Collection, redis_client=None):
        """Initialize with existing database connection"""
        self.alerts_collection = alerts_collection
        self.redis_client = redis_client
        self.cooldown_minutes = 5
        
    def create_alert(self, user_id: str, alert_type: str, severity: str, 
                    title: str, message: str, metadata: Dict = None) -> Dict:
        """Create a new alert"""
        alert = {
            "alert_id": f"alert_{user_id}_{datetime.now(timezone.utc).timestamp()}",
            "type": alert_type,
            "severity": severity,
            "user_id": user_id,
            "title": title,
            "message": message,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "read": False,
            "acknowledged": False
        }
        
        self.alerts_collection.insert_one(alert)
        return alert

    def check_cooldown(self, user_id: str, geofence_id: str) -> bool:
        """Check if alert is in cooldown period"""
        if not self.redis_client:
            return False
            
        cooldown_key = f"alert_cooldown:{user_id}:{geofence_id}"
        return bool(self.redis_client.get(cooldown_key))

    def set_cooldown(self, user_id: str, geofence_id: str, minutes: int = None):
        """Set alert cooldown"""
        if not self.redis_client:
            return
            
        minutes = minutes or self.cooldown_minutes
        cooldown_key = f"alert_cooldown:{user_id}:{geofence_id}"
        self.redis_client.setex(cooldown_key, minutes * 60, "1")

    def send_geofence_exit_alert(self, user_id: str, geofence: Dict, 
                                 current_location: Dict, distance: float = None) -> Optional[Dict]:
        """Send geofence exit alert with cooldown check"""
        geofence_id = geofence.get('place_id', 'unknown')
        
        # Check cooldown
        if self.check_cooldown(user_id, geofence_id):
            return None
        
        alert = self.create_alert(
            user_id=user_id,
            alert_type=AlertType.GEOFENCE_EXIT,
            severity=AlertSeverity.MEDIUM,
            title="Safety Alert: Left Safe Zone",
            message=f"You have left {geofence.get('name', 'the safe zone')}",
            metadata={
                "geofence_id": geofence_id,
                "geofence_name": geofence.get('name'),
                "exit_location": current_location,
                "distance_from_center": distance
            }
        )
        
        # Set cooldown
        self.set_cooldown(user_id, geofence_id)
        
        return alert

    def send_sos_alert(self, user_id: str, location: Dict, message: str = None) -> Dict:
        """Send SOS alert"""
        return self.create_alert(
            user_id=user_id,
            alert_type=AlertType.SOS,
            severity=AlertSeverity.CRITICAL,
            title="🆘 SOS ALERT",
            message=message or "Emergency SOS activated",
            metadata={
                "location": location,
                "requires_immediate_action": True
            }
        )

    def get_user_alerts(self, user_id: str, limit: int = 50, 
                       unread_only: bool = False) -> List[Dict]:
        """Get alerts for user"""
        query = {"user_id": user_id}
        if unread_only:
            query["read"] = False
            
        return list(self.alerts_collection.find(
            query, 
            {"_id": 0}
        ).sort("timestamp", -1).limit(limit))

    def mark_alert_read(self, alert_id: str) -> bool:
        """Mark alert as read"""
        result = self.alerts_collection.update_one(
            {"alert_id": alert_id},
            {"$set": {"read": True, "read_at": datetime.now(timezone.utc).isoformat()}}
        )
        return result.modified_count > 0

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str = None) -> bool:
        """Acknowledge alert"""
        result = self.alerts_collection.update_one(
            {"alert_id": alert_id},
            {"$set": {
                "acknowledged": True,
                "acknowledged_at": datetime.now(timezone.utc).isoformat(),
                "acknowledged_by": acknowledged_by
            }}
        )
        return result.modified_count > 0

    def delete_old_alerts(self, days: int = 30) -> int:
        """Delete alerts older than specified days"""
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        result = self.alerts_collection.delete_many({
            "timestamp": {"$lt": cutoff_date}
        })
        return result.deleted_count

    def get_alert_statistics(self, user_id: str = None) -> Dict:
        """Get alert statistics"""
        match_query = {"user_id": user_id} if user_id else {}
        
        pipeline = [
            {"$match": match_query},
            {"$group": {
                "_id": {
                    "type": "$type",
                    "severity": "$severity"
                },
                "count": {"$sum": 1}
            }}
        ]
        
        stats = list(self.alerts_collection.aggregate(pipeline))
        
        # Process stats
        by_type = {}
        by_severity = {}
        
        for stat in stats:
            type_name = stat["_id"]["type"]
            severity = stat["_id"]["severity"]
            count = stat["count"]
            
            by_type[type_name] = by_type.get(type_name, 0) + count
            by_severity[severity] = by_severity.get(severity, 0) + count
        
        return {
            "by_type": by_type,
            "by_severity": by_severity,
            "total": sum(s["count"] for s in stats),
            "user_id": user_id
        }