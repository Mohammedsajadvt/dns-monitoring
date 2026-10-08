import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    MONGODB_URI: str = os.getenv(
        "MONGODB_URI",
        "mongodb://mohammedsajadvt_db_user:m2sKeOsUWYvYEqPQ@ac-aosutmo-shard-00-00.zjapacp.mongodb.net:27017,ac-aosutmo-shard-00-01.zjapacp.mongodb.net:27017,ac-aosutmo-shard-00-02.zjapacp.mongodb.net:27017/?ssl=true&replicaSet=atlas-aw6q67-shard-0&authSource=admin&appName=Cluster0&compressors=zlib"
    )
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "dns_monitoring_db")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dns_secure_vault_super_secret_jwt_key_9823471092384701293847")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    GATEWAY_API_KEY_SECRET: str = os.getenv("GATEWAY_API_KEY_SECRET", "gw_secret_master_key_4810294719283")
    DATA_RETENTION_DAYS: int = int(os.getenv("DATA_RETENTION_DAYS", "30"))

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
