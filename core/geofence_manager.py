
from shapely.geometry import Point, Polygon
from geopy.distance import geodesic
from pymongo import MongoClient
import os

class GeofenceManager:   
    def __init__(self):
        # MongoDB setup
        MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
        self.client = MongoClient(MONGO_URL)
        self.db = self.client["tourist_safety"]
        self.geofences_collection = self.db["geofences"]
    
    def create_geofence(self, place_id, center_lat, center_lng, radius_meters):
        geofence = {
            "id": place_id,
            "center": {"lat": center_lat, "lng": center_lng},
            "radius": radius_meters,
            "type": "circle"
        }
        self.geofences_collection.insert_one(geofence)
        return geofence

    def create_polygon_geofence(self, place_id, coordinates):
        """Create polygon geofence for irregular shapes"""
        geofence = {
            "id": place_id,
            "polygon_coords": coordinates,  # Store as list of [lat, lng]
            "type": "polygon"
        }
        self.geofences_collection.insert_one(geofence)
        return geofence

    def get_geofence(self, place_id):
        return self.geofences_collection.find_one({"id": place_id})

    def check_geofence_status(self, user_lat, user_lng, geofence):
        """Check if user is inside or outside geofence"""
        user_point = Point(user_lng, user_lat)
        
        if geofence["type"] == "circle":
            center = (geofence["center"]["lat"], geofence["center"]["lng"])
            user_loc = (user_lat, user_lng)
            distance = geodesic(center, user_loc).meters
            return {
                "inside": distance <= geofence["radius"],
                "distance_from_center": distance
            }
        elif geofence["type"] == "polygon":
            # Reconstruct polygon from stored coordinates
            polygon = Polygon(geofence["polygon_coords"])
            return {
                "inside": polygon.contains(user_point),
                "distance_from_center": None
            }