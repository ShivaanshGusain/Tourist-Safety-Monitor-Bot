from datetime import datetime, timezone
from typing import Dict, List, Optional

from shapely.geometry import Point, Polygon
from geopy.distance import geodesic

from core.database import geofences_collection


class GeofenceManager:
    """All CRUD and helper operations for geofences."""

    def __init__(self) -> None:
        # Use the shared collection provided by core/database.py
        self.geofences_collection = geofences_collection

    # ------------------------------------------------------------------ #
    # CREATE
    # ------------------------------------------------------------------ #
    def create_geofence(
        self,
        place_id: str,
        name: str,
        center_lat: float,
        center_lng: float,
        radius_meters: float,
    ) -> Dict:
        """Create a circular geofence."""
        try:
            # Validation
            if radius_meters <= 0:
                return {"error": "Radius must be greater than 0"}
            if not (-90 <= center_lat <= 90 and -180 <= center_lng <= 180):
                return {"error": "Invalid coordinates"}

            if self.geofences_collection.find_one({"place_id": place_id}):
                return {"error": "Geofence already exists"}

            now = datetime.now(timezone.utc).isoformat()

            geofence = {
                "place_id": place_id,
                "name": name,
                "center_lat": center_lat,
                "center_lng": center_lng,
                "radius": radius_meters,
                "type": "circle",
                "created_at": now,
                "updated_at": now,
            }
            result = self.geofences_collection.insert_one(geofence)
            geofence["_id"] = str(result.inserted_id)
            return {"success": True, "geofence": geofence}

        except Exception as exc:
            print(f" Error creating geofence: {exc}")
            return {"error": str(exc)}

    def create_polygon_geofence(
        self,
        place_id: str,
        name: str,
        coordinates: List[List[float]],
    ) -> Dict:
        """Create a polygon geofence (coordinates are [lng, lat])."""
        try:
            if len(coordinates) < 3:
                return {"error": "Polygon requires at least 3 coordinates"}

            # Ensure closed polygon
            if coordinates[0] != coordinates[-1]:
                coordinates.append(coordinates[0])

            polygon = Polygon(coordinates)
            if not polygon.is_valid:
                return {"error": "Invalid polygon shape"}

            if self.geofences_collection.find_one({"place_id": place_id}):
                return {"error": "Geofence already exists"}

            now = datetime.now(timezone.utc).isoformat()

            geofence = {
                "place_id": place_id,
                "name": name,
                "polygon_coords": coordinates,
                "type": "polygon",
                "created_at": now,
                "updated_at": now,
            }
            result = self.geofences_collection.insert_one(geofence)
            geofence["_id"] = str(result.inserted_id)
            return {"success": True, "geofence": geofence}

        except Exception as exc:
            print(f" Error creating polygon geofence: {exc}")
            return {"error": str(exc)}

    # ------------------------------------------------------------------ #
    # READ
    # ------------------------------------------------------------------ #
    def get_geofence(self, place_id: str) -> Optional[Dict]:
        try:
            return self.geofences_collection.find_one(
                {"place_id": place_id}, {"_id": 0}
            )
        except Exception as exc:
            print(f" Error fetching geofence: {exc}")
            return None

    def get_all_geofences(self) -> List[Dict]:
        try:
            return list(self.geofences_collection.find({}, {"_id": 0}))
        except Exception as exc:
            print(f"Error fetching geofences: {exc}")
            return []

    # ------------------------------------------------------------------ #
    # UPDATE
    # ------------------------------------------------------------------ #
    def update_geofence(self, place_id: str, updates: Dict) -> Dict:
        """Update an existing geofence (cannot change place_id/type)."""
        try:
            updates.pop("place_id", None)
            updates.pop("type", None)
            updates["updated_at"] = datetime.now(timezone.utc).isoformat()

            result = self.geofences_collection.update_one(
                {"place_id": place_id}, {"$set": updates}
            )
            if result.modified_count == 0:
                return {"error": "Geofence not found or no changes made"}

            return {"success": True, "geofence": self.get_geofence(place_id)}

        except Exception as exc:
            print(f"Error updating geofence: {exc}")
            return {"error": str(exc)}

    # ------------------------------------------------------------------ #
    # DELETE
    # ------------------------------------------------------------------ #
    def delete_geofence(self, place_id: str) -> Dict:
        try:
            result = self.geofences_collection.delete_one({"place_id": place_id})
            if result.deleted_count == 0:
                return {"error": "Geofence not found"}
            return {"success": True, "message": "Geofence deleted"}

        except Exception as exc:
            print(f"Error deleting geofence: {exc}")
            return {"error": str(exc)}

    # ------------------------------------------------------------------ #
    # CHECK STATUS
    # ------------------------------------------------------------------ #
    def check_geofence_status(
        self,
        user_lat: float,
        user_lng: float,
        *,
        place_id: Optional[str] = None,
        geofence: Optional[Dict] = None,
    ) -> Dict:
        """Return whether the point is inside the geofence."""
        try:
            if geofence is None and place_id:
                geofence = self.get_geofence(place_id)
            if not geofence:
                return {"error": "Geofence not found"}

            if geofence["type"] == "circle":
                return self._check_circle_geofence(user_lat, user_lng, geofence)
            if geofence["type"] == "polygon":
                return self._check_polygon_geofence(user_lat, user_lng, geofence)

            return {"error": "Unknown geofence type"}
        except Exception as exc:
            print(f"Error checking geofence: {exc}")
            return {"error": str(exc)}

    def _check_circle_geofence(
        self, user_lat: float, user_lng: float, geofence: Dict
    ) -> Dict:
        center = (geofence["center_lat"], geofence["center_lng"])
        distance = geodesic(center, (user_lat, user_lng)).meters
        return {
            "inside": distance <= geofence["radius"],
            "distance_from_center": round(distance, 2),
            "radius": geofence["radius"],
            "geofence_name": geofence["name"],
            "geofence_id": geofence["place_id"],
        }

    def _check_polygon_geofence(
        self, user_lat: float, user_lng: float, geofence: Dict
    ) -> Dict:
        point = Point(user_lng, user_lat)  # Shapely uses (lng, lat)
        polygon = Polygon(geofence["polygon_coords"])
        inside = polygon.contains(point)
        distance = None
        if not inside:
            # degrees→meters (rough) : deg * 111_320
            distance = round(point.distance(polygon.boundary) * 111_320, 2)
        return {
            "inside": inside,
            "distance_from_boundary": distance,
            "geofence_name": geofence["name"],
            "geofence_id": geofence["place_id"],
        }

    # ------------------------------------------------------------------ #
    # UTILITIES
    # ------------------------------------------------------------------ #
    def get_nearby_geofences(
        self, lat: float, lng: float, radius_km: float = 5
    ) -> List[Dict]:
        """Return geofences whose centre/boundary is within radius_km."""
        try:
            nearby = []
            for gf in self.get_all_geofences():
                if gf["type"] == "circle":
                    km = geodesic((lat, lng), (gf["center_lat"], gf["center_lng"])).km
                    if km <= radius_km:
                        gf["distance_km"] = round(km, 2)
                        nearby.append(gf)
                else:  # polygon
                    polygon = Polygon(gf["polygon_coords"])
                    if polygon.distance(Point(lng, lat)) * 111 <= radius_km:
                        nearby.append(gf)
            return sorted(nearby, key=lambda x: x.get("distance_km", 0))
        except Exception as exc:
            print(f"Error computing nearby geofences: {exc}")
            return []

    def get_statistics(self) -> Dict:
        """Return simple counts and average radius."""
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": "$type",
                        "count": {"$sum": 1},
                        "avg_radius": {"$avg": "$radius"},
                    }
                }
            ]
            stats = list(self.geofences_collection.aggregate(pipeline))
            total = self.geofences_collection.count_documents({})

            return {
                "total_geofences": total,
                "by_type": {s["_id"]: s["count"] for s in stats},
                "average_radius": next(
                    (s["avg_radius"] for s in stats if s["_id"] == "circle"), 0
                ),
            }
        except Exception as exc:
            print(f"Error getting statistics: {exc}")
            return {"error": str(exc)}