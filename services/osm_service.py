import requests
from config import settings

class OSMService:
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org"
        self.headers = {"User-Agent": "TouristSafetyApp/1.0"}
    
    def get_location_details(self, lat, lng):
        """Get place details from OpenStreetMap Nominatim API"""
        url = f"https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": lat,
            "lon": lng,
            "format": "json",
            "zoom": 18  # High detail level
        }
        headers = {"User-Agent": "TouristSafetyApp/1.0"}
        
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        
        return {
            "display_name": data.get("display_name"),
            "address": data.get("address", {}),
            "place_type": data.get("type"),
            "osm_id": data.get("osm_id")
        }