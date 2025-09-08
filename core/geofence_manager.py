from shapely.geometry import Point, Polygon
from geopy.distance import geodesic
from pymongo.errors import DuplicateKeyError, ServerSelectionTimeoutError
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from core.database import geofences_collection


class GeofenceManager:   
    def __init__(self):
        """Initialize with database collection from core/database.py"""
        self.geofences_collection = geofences_collection
    
    def create_geofence(self, place_id: str, name: str, center_lat: float, 
                       center_lng: float, radius_meters: float) -> Dict:
        """Create circular geofence"""
        try:
            # Validate inputs
            if radius_meters <= 0:
                return {"error": "Radius must be greater than 0"}
            
            if not (-90 <= center_lat <= 90) or not (-180 <= center_lng <= 180):
                return {"error": "Invalid coordinates"}
            
            geofence = {
                "place_id": place_id,
                "name": name,
                "center_lat": center_lat,
                "center_lng": center_lng,
                "radius": radius_meters,
                "type": "circle",
                "created_at": datetime.now(timezone.utc)
.isoformat(),
                "updated_at": datetime.now(timezone.utc)
.isoformat()
            }
            
            # Check if already exists
            existing = self.geofences_collection.find_one({"place_id": place_id})
            if existing:
                return {"error": "Geofence already exists", "existing": existing}
            
            result = self.geofences_collection.insert_one(geofence)
            geofence["_id"] = str(result.inserted_id)
            
            return {"success": True, "geofence": geofence}
            
        except Exception as e:
            print(f"❌ Error creating geofence: {e}")
            return {"error": f"Failed to create geofence: {str(e)}"}

    def create_polygon_geofence(self, place_id: str, name: str, 
                               coordinates: List[List[float]]) -> Dict:
        """Create polygon geofence for irregular shapes
        
        Args:
            coordinates: List of [lng, lat] pairs (note: longitude first for Shapely)
        """
        try:
            # Validate coordinates
            if not coordinates or len(coordinates) < 3:
                return {"error": "Polygon requires at least 3 coordinates"}
            
            # Ensure polygon is closed (first and last points are the same)
            if coordinates[0] != coordinates[-1]:
                coordinates.append(coordinates[0])
            
            # Validate polygon
            try:
                polygon = Polygon(coordinates)
                if not polygon.is_valid:
                    return {"error": "Invalid polygon shape"}
            except:
                return {"error": "Invalid coordinates for polygon"}
            
            geofence = {
                "place_id": place_id,
                "name": name,
                "polygon_coords": coordinates,
                "type": "polygon",
                "created_at": datetime.now(timezone.utc)
.isoformat(),
                "updated_at": datetime.now(timezone.utc)
.isoformat()
            }
            
            # Check if already exists
            existing = self.geofences_collection.find_one({"place_id": place_id})
            if existing:
                return {"error": "Geofence already exists", "existing": existing}
            
            result = self.geofences_collection.insert_one(geofence)
            geofence["_id"] = str(result.inserted_id)
            
            return {"success": True, "geofence": geofence}
            
        except Exception as e:
            print(f"❌ Error creating polygon geofence: {e}")
            return {"error": f"Failed to create polygon geofence: {str(e)}"}

    def get_geofence(self, place_id: str) -> Optional[Dict]:
        """Get geofence by place_id"""
        try:
            return self.geofences_collection.find_one(
                {"place_id": place_id}, 
                {"_id": 0}
            )
        except Exception as e:
            print(f"❌ Error getting geofence: {e}")
            return None

    def get_all_geofences(self) -> List[Dict]:
        """Get all geofences"""
        try:
            return list(self.geofences_collection.find({}, {"_id": 0}))
        except Exception as e:
            print(f"❌ Error getting geofences: {e}")
            return []

    def check_geofence_status(self, user_lat: float, user_lng: float, 
                             place_id: str = None, geofence: Dict = None) -> Dict:
        """Check if user is inside or outside geofence"""
        try:
            # Get geofence if not provided
            if not geofence and place_id:
                geofence = self.get_geofence(place_id)
            
            if not geofence:
                return {"error": "Geofence not found"}
            
            if geofence["type"] == "circle":
                return self._check_circle_geofence(user_lat, user_lng, geofence)
                
            elif geofence["type"] == "polygon":
                return self._check_polygon_geofence(user_lat, user_lng, geofence)
            
            return {"error": "Unknown geofence type"}
                
        except Exception as e:
            print(f"❌ Error checking geofence status: {e}")
            return {"error": str(e)}

    def _check_circle_geofence(self, user_lat: float, user_lng: float, 
                              geofence: Dict) -> Dict:
        """Check if user is inside circular geofence"""
        center = (geofence["center_lat"], geofence["center_lng"])
        user_loc = (user_lat, user_lng)
        
        distance = geodesic(center, user_loc).meters
        
        return {
            "inside": distance <= geofence["radius"],
            "distance_from_center": round(distance, 2),
            "radius": geofence["radius"],
            "geofence_name": geofence.get("name", "Unknown"),
            "geofence_id": geofence.get("place_id")
        }

    def _check_polygon_geofence(self, user_lat: float, user_lng: float, 
                               geofence: Dict) -> Dict:
        """Check if user is inside polygon geofence"""
        # Note: Shapely uses (lng, lat) order
        user_point = Point(user_lng, user_lat)
        polygon = Polygon(geofence["polygon_coords"])
        
        # Calculate distance to nearest edge if outside
        distance = None
        if not polygon.contains(user_point):
            distance = round(user_point.distance(polygon.boundary) * 111320, 2)  # Convert to meters (approximate)
        
        return {
            "inside": polygon.contains(user_point),
            "distance_from_boundary": distance,
            "geofence_name": geofence.get("name", "Unknown"),
            "geofence_id": geofence.get("place_id")
        }

    def update_geofence(self, place_id: str, updates: Dict) -> Dict:
        """Update an existing geofence"""
        try:
            # Add update timestamp
            updates["updated_at"] = datetime.now(timezone.utc)
.isoformat()
            
            # Don't allow changing place_id or type
            updates.pop("place_id", None)
            updates.pop("type", None)
            
            result = self.geofences_collection.update_one(
                {"place_id": place_id},
                {"$set": updates}
            )
            
            if result.modified_count == 0:
                return {"error": "Geofence not found or no changes made"}
            
            updated = self.get_geofence(place_id)
            return {"success": True, "geofence": updated}
            
        except Exception as e:
            print(f"❌ Error updating geofence: {e}")
            return {"error": str(e)}

    def delete_geofence(self, place_id: str) -> Dict:
        """Delete a geofence"""
        try:
            result = self.geofences_collection.delete_one({"place_id": place_id})
            
            if result.deleted_count == 0:
                return {"error": "Geofence not found"}
                
            return {"success": True, "message": "Geofence deleted successfully"}
            
        except Exception as e:
            print(f"❌ Error deleting geofence: {e}")
            return {"error": str(e)}

    def check_multiple_users(self, users_locations: List[Dict], 
                           place_id: str) -> List[Dict]:
        """Check multiple users against a geofence"""
        geofence = self.get_geofence(place_id)
        if not geofence:
            return []
        
        results = []
        for user in users_locations:
            status = self.check_geofence_status(
                user["lat"], 
                user["lng"], 
                geofence=geofence
            )
            status["user_id"] = user.get("user_id")
            results.append(status)
        
        return results

    def get_nearby_geofences(self, lat: float, lng: float, 
                           radius_km: float = 5) -> List[Dict]:
        """Find geofences within a certain radius of a location"""
        try:
            all_geofences = self.get_all_geofences()
            nearby = []
            
            for gf in all_geofences:
                if gf["type"] == "circle":
                    center = (gf["center_lat"], gf["center_lng"])
                    distance = geodesic((lat, lng), center).kilometers
                    
                    if distance <= radius_km:
                        gf["distance_km"] = round(distance, 2)
                        nearby.append(gf)
                        
                elif gf["type"] == "polygon":
                    # Check if point is near polygon (simplified check)
                    polygon = Polygon(gf["polygon_coords"])
                    point = Point(lng, lat)
                    
                    # Very rough approximation
                    if polygon.distance(point) * 111 <= radius_km:  # Convert degrees to km (rough)
                        nearby.append(gf)
            
            return sorted(nearby, key=lambda x: x.get("distance_km", 0))
            
        except Exception as e:
            print(f"❌ Error finding nearby geofences: {e}")
            return []

    def get_statistics(self) -> Dict:
        """Get geofence statistics"""
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": "$type",
                        "count": {"$sum": 1},
                        "avg_radius": {
                            "$avg": {
                                "$cond": [
                                    {"$eq": ["$type", "circle"]},
                                    "$radius",
                                    None
                                ]
                            }
                        }
                    }
                }
            ]
            
            stats = list(self.geofences_collection.aggregate(pipeline))
            total = self.geofences_collection.count_documents({})
            
            return {
                "total_geofences": total,
                "by_type": {s["_id"]: s["count"] for s in stats},
                "average_radius": next((s["avg_radius"] for s in stats 
                                      if s["_id"] == "circle" and s["avg_radius"]), 0)
            }
            
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {"error": str(e)}