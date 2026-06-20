from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

class Database:
    def __init__(self):
        self.client = None
        self.db = None

db_instance = Database()

async def connect_to_mongo():
    try:
        print("🔄 Connecting to MongoDB...")
        print(f"Database Name: {settings.DB_NAME}")

        db_instance.client = AsyncIOMotorClient(settings.MONGO_URI)

        # Test connection
        await db_instance.client.admin.command("ping")

        db_instance.db = db_instance.client[settings.DB_NAME]

        print("✅ MongoDB Connected Successfully")
        print(f"✅ Database Selected: {settings.DB_NAME}")

    except Exception as e:
        print(f"❌ MongoDB Connection Failed: {e}")
        raise

async def close_mongo_connection():
    if db_instance.client:
        db_instance.client.close()
        print("🛑 MongoDB Connection Closed")

def get_collection(collection_name: str):
    if db_instance.db is None:
        raise RuntimeError(
            "MongoDB not initialized. Check startup and connection."
        )

    return db_instance.db[collection_name]