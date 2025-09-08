from pymongo import MongoClient
import certifi
from config import settings

class Database:
    client = None
    db = None

def get_database():
    """Get database instance"""
    if not Database.db:
        try:
            Database.client = MongoClient(
                settings.mongodb_url_with_ssl,
                tls=True,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=10000
            )
            Database.db = Database.client[settings.mongo_db_name]
            print(f"✅ Connected to MongoDB: {settings.mongo_db_name}")
        except:
            # Fallback
            Database.client = MongoClient(
                settings.mongodb_url,
                tls=True,
                tlsAllowInvalidCertificates=True
            )
            Database.db = Database.client[settings.mongo_db_name]
    
    return Database.db

# Initialize collections
def get_collection(name: str):
    db = get_database()
    return db[name]

# Export collections
locations_collection = get_collection("locations")
geofences_collection = get_collection("geofences")
alerts_collection = get_collection("alerts")