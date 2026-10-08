import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class GatewaySettings(BaseSettings):
    NETWORK_ID: str = os.getenv("NETWORK_ID", "net_home_01")
    GATEWAY_ID: str = os.getenv("GATEWAY_ID", "gw_home_router")
    GATEWAY_NAME: str = os.getenv("GATEWAY_NAME", "Local Sentry DNS Gateway")
    GATEWAY_TYPE: str = os.getenv("GATEWAY_TYPE", "linux_pc") # linux_pc, router_openwrt, windows_pc
    
    BACKEND_API_URL: str = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000")
    GATEWAY_API_KEY: str = os.getenv("GATEWAY_API_KEY", "gw_secret_master_key_4810294719283")
    
    # DNS Server Settings
    LISTEN_HOST: str = os.getenv("LISTEN_HOST", "0.0.0.0")
    LISTEN_PORT: int = int(os.getenv("LISTEN_PORT", "5353")) # 53 for root/admin, 5353 for dev
    UPSTREAM_DNS: str = os.getenv("UPSTREAM_DNS", "1.1.1.1")
    UPSTREAM_PORT: int = 53
    
    BATCH_FLUSH_INTERVAL_SEC: float = 2.0
    BATCH_MAX_SIZE: int = 50
    HEARTBEAT_INTERVAL_SEC: int = 30
    
    class Config:
        env_file = ".env"
        extra = "ignore"

config = GatewaySettings()
