from pymongo import MongoClient
import certifi
from config import settings

class Database:
    client = None
    db = None

def get_database():
    """Get database instance"""
    if Database.db is None:  # Changed from "if not Database.db:"
        try:
            Database.client = MongoClient(
                settings.mongodb_url_with_ssl,
                tls=True,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=10000
            )
            Database.db = Database.client[settings.mongo_db_name]
            print(f"✅ Connected to MongoDB: {settings.mongo_db_name}")
        except Exception as e:
            print(f" Primary connection failed: {e}")
            # Fallback
            try:
                Database.client = MongoClient(
                    settings.mongodb_url,
                    tls=True,
                    tlsAllowInvalidCertificates=True
                )
                Database.db = Database.client[settings.mongo_db_name]
                print("✅ Connected to MongoDB with relaxed SSL")
            except Exception as e2:
                print(f" Fallback connection also failed: {e2}")
                raise
    
    return Database.db

# Initialize collections
def get_collection(name: str):
    db = get_database()
    return db[name]

# Initialize Redis
redis_client = None
if settings.redis_url:
    try:
        import redis
        redis_client = redis.from_url(settings.redis_url)
        redis_client.ping()
        print("✅ Connected to Redis")
    except Exception as e:
        print(f"⚠️ Redis connection failed: {e}, continuing without cache")
        redis_client = None

# Export collections
locations_collection = get_collection("locations")
geofences_collection = get_collection("geofences")
alerts_collection = get_collection("alerts")