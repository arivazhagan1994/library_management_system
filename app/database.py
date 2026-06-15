from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

class Database():
    client: AsyncIOMotorClient = None
    db = None

db_instance = Database()

async def connect_to_mongo():
    db_instance.client = AsyncIOMotorClient(
        settings.MONGO_URI,
        maxPoolSize = 50,
        minPoolSize = 10,
        waitQueueTimeoutMS = 5000
    )

    db_instance.db = db_instance.client[settings.DB_NAME]
    print("Successfully bound to secure MongoDB resource cluster pool.")

async def close_mongo_connection():
    if db_instance.client:
        db_instance.client.close()
        print("🛑 MongoDB connection pool cleanly collapsed.")

def get_collection(collection_name: str):
    return db_instance.db[collection_name]

