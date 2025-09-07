from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import math
import uvicorn

app = FastAPI(title="Tourist Safety Monitor Bot API")

# Storage
locations = {}
geofences = {}
alerts = []

# Models
class LocationUpdate(BaseModel):
    user_id: str
    lat: float
    lng: float

class GeofenceCreate(BaseModel):
    name: str
    place_id: str
    center_lat: float
    center_lng: float
    radius: float

# Endpoints
@app.get("/")
def root():
    return {
        "message": "Tourist Safety Monitor Bot API",
        "version": "1.0",
        "docs": "Visit /docs for API documentation"
    }

@app.post("/api/geofence/create")
async def create_geofence(geofence: GeofenceCreate):
    if geofence.place_id in geofences:
        raise HTTPException(status_code=400, detail="Geofence already exists")
    
    geofences[geofence.place_id] = geofence.dict()
    return {"status": "created", "geofence": geofence}

@app.get("/api/geofence/list")
async def list_geofences():
    return {"geofences": list(geofences.values())}

@app.post("/api/location/update")
async def update_location(location: LocationUpdate):
    # Store location
    locations[location.user_id] = {
        "lat": location.lat,
        "lng": location.lng,
        "timestamp": datetime.now().isoformat()
    }
    
    # Check geofences
    for gf_id, gf in geofences.items():
        distance = calculate_distance(
            location.lat, location.lng,
            gf["center_lat"], gf["center_lng"]
        )
        
        if distance > gf["radius"]:
            alert = {
                "user_id": location.user_id,
                "type": "GEOFENCE_EXIT",
                "message": f"User left {gf['name']}",
                "timestamp": datetime.now().isoformat(),
                "geofence": gf["name"],
                "distance": distance
            }
            alerts.append(alert)
    
    return {"status": "success", "message": "Location updated"}

@app.get("/api/alerts/{user_id}")
async def get_alerts(user_id: str):
    user_alerts = [a for a in alerts if a["user_id"] == user_id]
    return {"user_id": user_id, "alerts": user_alerts, "count": len(user_alerts)}

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in meters"""
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi/2)**2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c