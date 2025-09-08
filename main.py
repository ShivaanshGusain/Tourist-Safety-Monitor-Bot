from pymongo import MongoClient
import os
from pydantic import BaseModel

app = FastAPI()

MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://545ohayu_db_user:zcwvKB50xnUHDzvY@cluster0.v8ym989.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
client = MongoClient(MONGO_URL)
db = client["tourist_safety"]
locations_collection = db["locations"]
geofences_collection = db["geofences"]
alerts_collection = db["alerts"]
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
    if geofences_collection.find_one({"place_id": geofence.place_id}):
        raise HTTPException(status_code=400, detail="Geofence already exists")
    geofences_collection.insert_one(geofence.dict())
    return {"status": "created", "geofence": geofence}

@app.get("/api/geofence/list")
async def list_geofences():
    geofences = list(geofences_collection.find({}, {"_id": 0}))
    return {"geofences": geofences}


@app.post("/api/location/update")
async def update_location(location: LocationUpdate):
    # Store location
    locations_collection.insert_one({
        "user_id": location.user_id,
        "lat": location.lat,
        "lng": location.lng,
        "timestamp": datetime.now().isoformat()
    })
    # Check geofences
    geofences = list(geofences_collection.find({}, {"_id": 0}))
    for gf in geofences:
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
            alerts_collection.insert_one(alert)
    return {"status": "success", "message": "Location updated"}

@app.get("/api/alerts/{user_id}")
async def get_alerts(user_id: str):
    user_alerts = list(alerts_collection.find({"user_id": user_id}, {"_id": 0}))
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

'''
from pymongo import MongoClient
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URL)
db = client["tourist_safety"]
locations_collection = db["locations"]
geofences_collection = db["geofences"]
alerts_collection = db["alerts"]


# Changes to make in the existing file - 
@app.post("/api/geofence/create")
async def create_geofence(geofence: GeofenceCreate):
    if geofences_collection.find_one({"place_id": geofence.place_id}):
        raise HTTPException(status_code=400, detail="Geofence already exists")
    geofences_collection.insert_one(geofence.dict())
    return {"status": "created", "geofence": geofence}

@app.get("/api/geofence/list")
async def list_geofences():
    geofences = list(geofences_collection.find({}, {"_id": 0}))
    return {"geofences": geofences}
    
@app.post("/api/location/update")
async def update_location(location: LocationUpdate):
    # Store location
    locations_collection.insert_one({
        "user_id": location.user_id,
        "lat": location.lat,
        "lng": location.lng,
        "timestamp": datetime.now().isoformat()
    })
    # Check geofences
    geofences = list(geofences_collection.find({}, {"_id": 0}))
    for gf in geofences:
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
            alerts_collection.insert_one(alert)
    return {"status": "success", "message": "Location updated"}
    
@app.get("/api/alerts/{user_id}")
async def get_alerts(user_id: str):
    user_alerts = list(alerts_collection.find({"user_id": user_id}, {"_id": 0}))
    return {"user_id": user_id, "alerts": user_alerts, "count": len(user_alerts)}'''





