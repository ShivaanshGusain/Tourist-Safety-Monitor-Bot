from geopy.distance import geodesic
from shapely.geometry import Point, Polygon
from typing import Tuple, List, Dict
import math

def calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """
    Calculate distance between two points in meters
    Args:
        point1: (latitude, longitude)
        point2: (latitude, longitude)
    Returns:
        Distance in meters
    """
    return geodesic(point1, point2).meters

def is_point_in_circle(
    point: Tuple[float, float], 
    center: Tuple[float, float], 
    radius: float
) -> bool:
    """Check if point is within circular geofence"""
    distance = calculate_distance(point, center)
    return distance <= radius

def is_point_in_polygon(
    point: Tuple[float, float], 
    polygon_coords: List[List[float]]
) -> bool:
    """Check if point is within polygon geofence"""
    # Convert to shapely objects
    p = Point(point[1], point[0])  # Note: shapely uses (lng, lat)
    polygon = Polygon([(coord[0], coord[1]) for coord in polygon_coords])
    return polygon.contains(p)

def get_bearing(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """
    Calculate bearing between two points
    Returns bearing in degrees (0-360)
    """
    lat1, lon1 = math.radians(point1[0]), math.radians(point1[1])
    lat2, lon2 = math.radians(point2[0]), math.radians(point2[1])
    
    dlon = lon2 - lon1
    
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    
    bearing = math.atan2(x, y)
    bearing = math.degrees(bearing)
    bearing = (bearing + 360) % 360
    
    return bearing

def estimate_time_to_location(
    current: Tuple[float, float], 
    destination: Tuple[float, float], 
    speed_kmh: float = 5.0  # Average walking speed
) -> Dict[str, float]:
    """
    Estimate time to reach destination
    Returns time in minutes and distance in meters
    """
    distance_m = calculate_distance(current, destination)
    time_hours = distance_m / (speed_kmh * 1000)
    time_minutes = time_hours * 60
    
    return {
        "distance_meters": distance_m,
        "time_minutes": round(time_minutes, 1),
        "time_seconds": round(time_minutes * 60),
        "bearing": get_bearing(current, destination)
    }

def find_nearest_safe_zone(
    current_location: Tuple[float, float],
    geofences: List[Dict]
) -> Dict:
    """Find the nearest safe zone from current location"""
    nearest = None
    min_distance = float('inf')
    
    for geofence in geofences:
        if geofence['type'] == 'circle':
            center = (geofence['center_lat'], geofence['center_lng'])
            distance = calculate_distance(current_location, center)
            
            # Subtract radius to get distance to edge
            distance_to_edge = max(0, distance - geofence['radius'])
            
            if distance_to_edge < min_distance:
                min_distance = distance_to_edge
                nearest = {
                    'geofence': geofence,
                    'distance': distance_to_edge,
                    'center': center,
                    'estimated_time': estimate_time_to_location(
                        current_location, 
                        center
                    )
                }
    
    return nearest