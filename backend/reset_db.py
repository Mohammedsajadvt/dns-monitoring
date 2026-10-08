import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection, db_instance

async def reset_database():
    print(f"Connecting to MongoDB Atlas at {settings.MONGODB_URI[:35]}...")
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.DATABASE_NAME]
    
    collections_to_clear = [
        "users",
        "networks",
        "gateways",
        "devices",
        "dns_logs",
        "threat_alerts",
        "blocked_domains"
    ]
    
    print(f"\n[!] Resetting database: '{settings.DATABASE_NAME}'")
    for col_name in collections_to_clear:
        deleted = await db[col_name].delete_many({})
        print(f"  [-] Cleared collection '{col_name}': {deleted.deleted_count} documents removed.")
    
    # Re-create all indexes
    print("\n[+] Rebuilding database indexes...")
    try:
        await db.dns_logs.create_index([("network_id", 1), ("timestamp", -1)])
        await db.dns_logs.create_index([("domain", 1)])
        await db.dns_logs.create_index([("client_ip", 1)])
        await db.dns_logs.create_index([("is_threat", 1)])
        
        await db.devices.create_index([("network_id", 1), ("ip", 1)], unique=True)
        await db.devices.create_index([("network_id", 1), ("mac", 1)])
        
        await db.networks.create_index([("network_id", 1)], unique=True)
        await db.gateways.create_index([("gateway_id", 1)], unique=True)
        await db.users.create_index([("email", 1)], unique=True)
        
        await db.threat_alerts.create_index([("network_id", 1), ("timestamp", -1)])
        await db.blocked_domains.create_index([("network_id", 1), ("domain", 1)], unique=True)
        print("  [OK] All indexes created and verified successfully.")
    except Exception as e:
        print(f"  [!] Index warning: {e}")
        
    client.close()
    print("\n=======================================================")
    print(" [OK] Database is now completely FRESH and EMPTY.")
    print(" You can now register a brand new admin account via")
    print(" Web Dashboard or Flutter Mobile App.")
    print("=======================================================")

if __name__ == "__main__":
    asyncio.run(reset_database())
