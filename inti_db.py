from database import Base, engine

# Import all models to register them with Base
import models.geofence
import models.location
import models.alert

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Database tables created successfully!")