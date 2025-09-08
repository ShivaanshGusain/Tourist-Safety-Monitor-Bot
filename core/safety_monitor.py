from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from core.database import locations_collection, alerts_collection, geofences_collection
from core.alert_manager import AlertManager
from core.geofence_manager import GeofenceManager


class SafetyMonitorBot:
    def __init__(self, redis_client=None):
        """Initialize with managers and collections from core/database.py"""
        # Use the existing database collections
        self.locations_collection = locations_collection
        
        # Initialize managers with proper collections
        self.alert_manager = AlertManager(alerts_collection, redis_client)
        self.geofence_manager = GeofenceManager()
        
        # Track user states
        self.user_geofence_status = {}
        self.redis_client = redis_client
        
    async def initialize(self):
        """Initialize bot and verify connections"""
        try:
            # Test database connection
            self.locations_collection.find_one()
            print("Safety Monitor Bot initialized successfully")
            return True
        except Exception as e:
            print(f" Failed to initialize Safety Monitor Bot: {e}")
            return False
        
    async def process_location_update(self, user_id: str, lat: float, lng: float) -> Dict:
        """Process location update and check geofences"""
        try:
            # Store location
            location_doc = {
                "user_id": user_id,
                "lat": lat,
                "lng": lng,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            self.locations_collection.insert_one(location_doc)
            
            # Get all geofences
            geofences = self.geofence_manager.get_all_geofences()
            alerts_created = []
            user_status = []
            
            # Check each geofence
            for geofence in geofences:
                status = self.geofence_manager.check_geofence_status(
                    lat, lng, geofence=geofence
                )
                
                if "error" not in status:
                    geofence_id = geofence.get("place_id")
                    previous_status = self.user_geofence_status.get(
                        f"{user_id}:{geofence_id}", 
                        None
                    )
                    
                    current_inside = status.get("inside", False)
                    
                    # Check for status changes
                    if previous_status is not None:
                        if previous_status and not current_inside:
                            # User exited geofence
                            alert = self.alert_manager.send_geofence_exit_alert(
                                user_id=user_id,
                                geofence=geofence,
                                current_location={"lat": lat, "lng": lng},
                                distance=status.get("distance_from_center")
                            )
                            if alert:
                                alerts_created.append(alert)
                                
                        elif not previous_status and current_inside:
                            # User entered geofence
                            alert = self.alert_manager.create_alert(
                                user_id=user_id,
                                alert_type="GEOFENCE_ENTRY",
                                severity="LOW",
                                title="Entered Safe Zone",
                                message=f"You have entered {geofence.get('name', 'a safe zone')}",
                                metadata={
                                    "geofence_id": geofence_id,
                                    "geofence_name": geofence.get('name'),
                                    "entry_location": {"lat": lat, "lng": lng}
                                }
                            )
                            alerts_created.append(alert)
                    
                    # Update status
                    self.user_geofence_status[f"{user_id}:{geofence_id}"] = current_inside
                    
                    # Store in Redis if available
                    if self.redis_client:
                        self.redis_client.setex(
                            f"user_status:{user_id}:{geofence_id}",
                            3600,  # 1 hour expiry
                            "inside" if current_inside else "outside"
                        )
                    
                    user_status.append({
                        "geofence_id": geofence_id,
                        "geofence_name": geofence.get("name"),
                        "inside": current_inside,
                        "distance": status.get("distance_from_center")
                    })
            
            return {
                "success": True,
                "user_id": user_id,
                "location": {"lat": lat, "lng": lng},
                "timestamp": location_doc["timestamp"],
                "geofence_status": user_status,
                "alerts_created": len(alerts_created),
                "alerts": alerts_created
            }
            
        except Exception as e:
            print(f" Error processing location update: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def check_user_activity(self, user_id: str, hours: int = 24) -> Dict:
        """Check user's recent activity"""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            recent_locations = list(self.locations_collection.find(
                {
                    "user_id": user_id,
                    "timestamp": {"$gte": cutoff_time.isoformat()}
                },
                {"_id": 0}
            ).sort("timestamp", -1))
            
            if not recent_locations:
                return {
                    "active": False,
                    "last_location": None,
                    "location_count": 0
                }
            
            # Check for movement
            if len(recent_locations) >= 2:
                first_loc = recent_locations[-1]
                last_loc = recent_locations[0]
                
                distance = self._calculate_distance(
                    first_loc["lat"], first_loc["lng"],
                    last_loc["lat"], last_loc["lng"]
                )
                
                movement = distance > 100  # More than 100 meters
            else:
                movement = False
            
            return {
                "active": True,
                "last_location": recent_locations[0],
                "location_count": len(recent_locations),
                "has_movement": movement,
                "hours_checked": hours
            }
            
        except Exception as e:
            print(f" Error checking user activity: {e}")
            return {"error": str(e)}
    
    def _calculate_distance(self, lat1: float, lon1: float, 
                           lat2: float, lon2: float) -> float:
        """Calculate distance between two points in meters"""
        from math import sin, cos, sqrt, atan2, radians
        
        R = 6371000  # Earth radius in meters
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lon = radians(lon2 - lon1)
        
        a = sin(delta_lat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    async def send_check_in_reminder(self, user_id: str) -> Optional[Dict]:
        """Send check-in reminder if user hasn't moved in a while"""
        activity = await self.check_user_activity(user_id, hours=2)
        
        if activity.get("active") and not activity.get("has_movement"):
            alert = self.alert_manager.create_alert(
                user_id=user_id,
                alert_type="NO_MOVEMENT",
                severity="LOW",
                title="Check-in Reminder",
                message="You haven't moved in 2 hours. Are you okay?",
                metadata={
                    "last_location": activity.get("last_location"),
                    "check_in_required": True
                }
            )
            return alert
        
        return None
    
    def get_user_current_geofences(self, user_id: str) -> List[str]:
        """Get list of geofences user is currently inside"""
        current_geofences = []
        
        for key, inside in self.user_geofence_status.items():
            if key.startswith(f"{user_id}:") and inside:
                geofence_id = key.split(":")[1]
                current_geofences.append(geofence_id)
        
        return current_geofences


# Don't create a global instance here - let the API handle initialization