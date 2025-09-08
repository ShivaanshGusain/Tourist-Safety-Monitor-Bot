from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
import certifi
import os
import sys

# Try to import settings - handle different import paths
try:
    from core.config import settings
except ImportError:
    try:
        from config import settings
    except ImportError:
        # If no config module, use environment variables directly
        class Settings:
            mongodb_url = os.getenv("MONGODB_URL")
            mongo_db_name = os.getenv("MONGO_DB_NAME", "tourist_safety")
            redis_url = os.getenv("REDIS_URL")
            

        @property
        def mongodb_uri(self):
            if not self.mongodb_url:
                raise ValueError("MONGODB_URL environment variable is required!")
            return self.mongodb_url
        settings = Settings()


class Database:
    """Singleton database connection manager"""
    client = None
    db = None
    _initialized = False


def get_database():
    """Get MongoDB database instance with proper error handling"""
    if Database.db is None and not Database._initialized:
        Database._initialized = True  # Prevent multiple connection attempts
        
        # Check for MongoDB URL
        mongodb_url = settings.mongodb_url or os.getenv("MONGODB_URL")
        
        if not mongodb_url:
            error_msg = """
            ❌ MONGODB_URL not found!
            
            Please set the MONGODB_URL environment variable:
            - In Render: Add it in the Environment tab
            - Locally: Create a .env file with MONGODB_URL=your_connection_string
            
            The URL should look like:
            mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
            """
            print(error_msg)
            raise ValueError("MONGODB_URL environment variable is required")
        
        # Don't print the actual URL (security)
        if "localhost" in mongodb_url:
            print("⚠️  WARNING: Using localhost MongoDB. This won't work in production!")
        else:
            print("🔄 Connecting to MongoDB Atlas...")
        
        # Try multiple connection methods
        connection_attempts = [
            {
                "name": "Atlas with SSL",
                "url": settings.mongodb_url_with_ssl if hasattr(settings, 'mongodb_url_with_ssl') else mongodb_url,
                "options": {
                    "tls": True,
                    "tlsCAFile": certifi.where(),
                    "serverSelectionTimeoutMS": 10000,
                    "connectTimeoutMS": 20000,
                    "retryWrites": True,
                    "w": "majority"
                }
            },
            {
                "name": "Atlas with relaxed SSL",
                "url": mongodb_url,
                "options": {
                    "tls": True,
                    "tlsAllowInvalidCertificates": True,
                    "serverSelectionTimeoutMS": 10000,
                    "connectTimeoutMS": 20000
                }
            },
            {
                "name": "Direct connection",
                "url": mongodb_url,
                "options": {
                    "serverSelectionTimeoutMS": 10000,
                    "directConnection": True
                }
            }
        ]
        
        last_error = None
        for attempt in connection_attempts:
            try:
                print(f"  Trying {attempt['name']}...")
                Database.client = MongoClient(attempt["url"], **attempt["options"])
                
                # Test the connection
                Database.client.admin.command('ping')
                
                # Get the database
                db_name = settings.mongo_db_name if hasattr(settings, 'mongo_db_name') else os.getenv("MONGO_DB_NAME", "tourist_safety")
                Database.db = Database.client[db_name]
                
                print(f"✅ Connected to MongoDB successfully! Database: {db_name}")
                break
                
            except Exception as e:
                last_error = e
                print(f"  ❌ {attempt['name']} failed: {str(e)[:100]}...")
                continue
        
        if Database.db is None:
            error_msg = f"""
            ❌ Failed to connect to MongoDB after all attempts!
            
            Last error: {last_error}
            
            Troubleshooting:
            1. Check your MONGODB_URL environment variable
            2. Ensure your IP is whitelisted in MongoDB Atlas
            3. Verify your username and password
            4. Check if the cluster is active
            """
            print(error_msg)
            raise ConnectionFailure(f"Could not connect to MongoDB: {last_error}")
    
    return Database.db


def get_collection(name: str):
    """Get a collection from the database"""
    db = get_database()
    if db is None:
        raise ConnectionFailure("Database not initialized")
    return db[name]


# Initialize Redis connection
redis_client = None
redis_url = settings.redis_url if hasattr(settings, 'redis_url') else os.getenv("REDIS_URL")

if redis_url:
    try:
        import redis
        print("🔄 Connecting to Redis...")
        redis_client = redis.from_url(redis_url, decode_responses=True)
        redis_client.ping()
        print("✅ Connected to Redis successfully!")
    except ImportError:
        print("⚠️  Redis package not installed. Install with: pip install redis")
    except Exception as e:
        print(f"⚠️  Redis connection failed: {e}")
        print("   Continuing without caching...")
        redis_client = None


# Initialize collections only when requested
_collections_cache = {}

def _get_or_create_collection(name: str):
    """Lazy load collections"""
    if name not in _collections_cache:
        _collections_cache[name] = get_collection(name)
    return _collections_cache[name]


# Export collections (lazy-loaded)
@property
def locations_collection():
    return _get_or_create_collection("locations")

@property
def geofences_collection():
    return _get_or_create_collection("geofences")

@property
def alerts_collection():
    return _get_or_create_collection("alerts")


# For backward compatibility, create them immediately if possible
try:
    locations_collection = get_collection("locations")
    geofences_collection = get_collection("geofences")
    alerts_collection = get_collection("alerts")
except Exception as e:
    print(f"⚠️  Collections will be initialized on first use: {e}")
    locations_collection = None
    geofences_collection = None
    alerts_collection = None