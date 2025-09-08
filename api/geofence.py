from fastapi import APIRouter, HTTPException
from models import GeofenceCreate, GeofenceResponse
from core.geofence_manager import GeofenceManager
from core.database import geofences_collection

router = APIRouter(prefix="/api/geofence", tags=["geofences"])

# Initialize geofence manager
geofence_manager = GeofenceManager()

@router.post("/create")
async def create_geofence(geofence: GeofenceCreate):
    """Create a new geofence"""
    result = geofence_manager.create_geofence(
        place_id=geofence.place_id,
        name=geofence.name,
        center_lat=geofence.center_lat,
        center_lng=geofence.center_lng,
        radius_meters=geofence.radius
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.get("/list")
async def list_geofences():
    """List all geofences"""
    geofences = geofence_manager.get_all_geofences()
    return {"geofences": geofences, "count": len(geofences)}