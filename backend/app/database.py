import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

logger = logging.getLogger("dns_monitoring.database")

class Database:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

db_instance = Database()

async def get_database() -> AsyncIOMotorDatabase:
    return db_instance.db

async def connect_to_mongo():
    logger.info("Connecting to MongoDB Atlas...")
    db_instance.client = AsyncIOMotorClient(
        settings.MONGODB_URI,
        serverSelectionTimeoutMS=5000,
        maxPoolSize=50,
        minPoolSize=5
    )
    db_instance.db = db_instance.client[settings.DATABASE_NAME]
    logger.info(f"Connected to database: {settings.DATABASE_NAME}")
    
    # Create indexes for optimized queries
    try:
        # Logs indexes
        await db_instance.db.dns_logs.create_index([("network_id", 1), ("timestamp", -1)])
        await db_instance.db.dns_logs.create_index([("domain", 1)])
        await db_instance.db.dns_logs.create_index([("client_ip", 1)])
        await db_instance.db.dns_logs.create_index([("is_threat", 1)])
        
        # Devices indexes
        await db_instance.db.devices.create_index([("network_id", 1), ("ip", 1)], unique=True)
        await db_instance.db.devices.create_index([("network_id", 1), ("mac", 1)])
        
        # Networks and Gateways
        await db_instance.db.networks.create_index([("network_id", 1)], unique=True)
        await db_instance.db.gateways.create_index([("gateway_id", 1)], unique=True)
        await db_instance.db.users.create_index([("email", 1)], unique=True)
        
        # Threat Alerts
        await db_instance.db.threat_alerts.create_index([("network_id", 1), ("timestamp", -1)])
        
        # Blocked domains list
        await db_instance.db.blocked_domains.create_index([("network_id", 1), ("domain", 1)], unique=True)
        
        logger.info("MongoDB indexes verified successfully.")
    except Exception as e:
        logger.warning(f"Index creation notice: {e}")

async def close_mongo_connection():
    if db_instance.client:
        logger.info("Closing MongoDB connection...")
        db_instance.client.close()
