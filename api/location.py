from fastapi import APIRouter, HTTPException
from typing import Optional, List
from models import LocationUpdate
from core.database import locations_collection, alerts_collection, redis_client
from core.safety_monitor import SafetyMonitorBot
from datetime import datetime, timedelta, timezone

router = APIRouter(prefix="/api/location", tags=["locations"])

# Initialize the safety monitor bot with Redis if available
monitor_bot = SafetyMonitorBot(redis_client=redis_client)

@router.post("/update")
async def update_location(location: LocationUpdate):
    """Update user location and check geofences"""
    try:
        # Use the SafetyMonitorBot to process location
        result = await monitor_bot.process_location_update(
            user_id=location.user_id,
            lat=location.lat,
            lng=location.lng
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500, 
                detail=result.get("error", "Failed to process location update")
            )
        
        return {
            "status": "success",
            "user_id": result["user_id"],
            "location": result["location"],
            "timestamp": result["timestamp"],
            "alerts_triggered": result["alerts_created"],
            "geofence_status": result["geofence_status"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{user_id}")
async def get_location_history(
    user_id: str,
    limit: Optional[int] = 100,
    skip: Optional[int] = 0,
    hours: Optional[int] = None
):
    """Get location history for a user"""
    try:
        query = {"user_id": user_id}
        
        # Filter by time if specified
        if hours:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            query["timestamp"] = {"$gte": cutoff_time.isoformat()}
        
        locations = list(
            locations_collection.find(query, {"_id": 0})
            .sort("timestamp", -1)
            .limit(limit)
            .skip(skip)
        )
        
        total_count = locations_collection.count_documents(query)
        
        return {
            "user_id": user_id,
            "locations": locations,
            "count": len(locations),
            "total_count": total_count,
            "limit": limit,
            "skip": skip
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/current/{user_id}")
async def get_current_status(user_id: str):
    """Get user's current location and geofence status"""
    try:
        # Get latest location
        latest_location = locations_collection.find_one(
            {"user_id": user_id},
            {"_id": 0},
            sort=[("timestamp", -1)]
        )
        
        if not latest_location:
            return {
                "user_id": user_id,
                "has_location": False,
                "message": "No location data found for user"
            }
        
        # Get current geofences
        current_geofences = monitor_bot.get_user_current_geofences(user_id)
        
        return {
            "user_id": user_id,
            "has_location": True,
            "last_location": latest_location,
            "current_geofences": current_geofences,
            "is_safe": len(current_geofences) > 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check-activity/{user_id}")
async def check_user_activity(user_id: str, hours: Optional[int] = 24):
    """Check user's recent activity and send reminders if needed"""
    try:
        # Check activity
        activity = await monitor_bot.check_user_activity(user_id, hours)
        
        # Send reminder if needed
        reminder_sent = False
        if activity.get("active") and not activity.get("has_movement"):
            reminder = await monitor_bot.send_check_in_reminder(user_id)
            reminder_sent = bool(reminder)
        
        return {
            "user_id": user_id,
            "activity": activity,
            "reminder_sent": reminder_sent
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-update")
async def batch_location_update(locations: List[LocationUpdate]):
    """Update multiple user locations at once"""
    try:
        results = []
        
        for location in locations:
            try:
                result = await monitor_bot.process_location_update(
                    user_id=location.user_id,
                    lat=location.lat,
                    lng=location.lng
                )
                results.append({
                    "user_id": location.user_id,
                    "success": result.get("success", False),
                    "alerts_created": result.get("alerts_created", 0)
                })
            except Exception as e:
                results.append({
                    "user_id": location.user_id,
                    "success": False,
                    "error": str(e)
                })
        
        success_count = sum(1 for r in results if r.get("success"))
        
        return {
            "total": len(locations),
            "successful": success_count,
            "failed": len(locations) - success_count,
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/history/{user_id}")
async def delete_location_history(
    user_id: str,
    days_old: Optional[int] = None
):
    """Delete location history for a user"""
    try:
        query = {"user_id": user_id}
        
        if days_old:
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days_old)).isoformat()
            query["timestamp"] = {"$lt": cutoff_date}
        
        result = locations_collection.delete_many(query)
        
        return {
            "user_id": user_id,
            "deleted_count": result.deleted_count,
            "message": f"Deleted {result.deleted_count} location records"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Helper endpoint for testing
@router.get("/test")
async def test_location_endpoint():
    """Test endpoint to verify location API is working"""
    return {
        "status": "operational",
        "monitor_bot_initialized": await monitor_bot.initialize(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }