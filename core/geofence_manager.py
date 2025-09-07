from shapely.geometry import Point, Polygon
from geopy.distance import geodesic

class GeofenceManager:   
    def __init__(self):
        self.active_geofences = {}
    
    def create_geofence(self, place_id, center_lat, center_lng, radius_meters):
        geofence = {
            "id": place_id,
            "center": {"lat": center_lat, "lng": center_lng},
            "radius": radius_meters,
            "type": "circle" 
        }
        self.active_geofences[place_id] = geofence
        return geofence    
    def create_polygon_geofence(self, place_id, coordinates):
        """Create polygon geofence for irregular shapes"""
        geofence = {
            "id": place_id,
            "polygon": Polygon(coordinates),
            "type": "polygon"
        }
        self.active_geofences[place_id] = geofence
        return geofence

    def check_geofence_status(self, user_lat, user_lng, geofence):
        """Check if user is inside or outside geofence"""
        user_point = Point(user_lng, user_lat)
        
        if geofence["type"] == "circle":
            # Calculate distance from center
            center = (geofence["center"]["lat"], geofence["center"]["lng"])
            user_loc = (user_lat, user_lng)
            distance = geodesic(center, user_loc).meters
            
            return {
                "inside": distance <= geofence["radius"],
                "distance_from_center": distance
            }
        
        elif geofence["type"] == "polygon":
            # Check if point is inside polygon
            return {
                "inside": geofence["polygon"].contains(user_point),
                "distance_from_center": None
            }
