import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.websocket_manager import ws_manager
from app.routers import auth, networks, gateways, devices, dns_logs, threat_alerts, analytics, export

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("dns_monitoring.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing DNS Monitoring API Gateway...")
    await connect_to_mongo()
    yield
    logger.info("Shutting down DNS Monitoring API...")
    await close_mongo_connection()

app = FastAPI(
    title="NetSentry - Wi-Fi DNS Monitoring & Cybersecurity Platform",
    description="Enterprise Wi-Fi traffic metadata, DNS query inspection, DGA/phishing anomaly detection, device management and remote dashboard API.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(networks.router)
app.include_router(gateways.router)
app.include_router(devices.router)
app.include_router(dns_logs.router)
app.include_router(threat_alerts.router)
app.include_router(analytics.router)
app.include_router(export.router)

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "NetSentry DNS Monitoring API Gateway",
        "database": settings.DATABASE_NAME,
        "version": "1.0.0"
    }

# WebSocket Endpoint for live logs stream
@app.websocket("/ws/{network_id}")
async def websocket_endpoint(websocket: WebSocket, network_id: str):
    await ws_manager.connect(websocket, network_id)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, network_id)
    except Exception as e:
        logger.debug(f"WS error on {network_id}: {e}")
        ws_manager.disconnect(websocket, network_id)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

# Static Dashboard files
static_dir = Path(__file__).resolve().parent.parent.parent / "web-dashboard"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    @app.get("/style.css")
    async def get_style():
        return FileResponse(static_dir / "style.css")
        
    @app.get("/app.js")
    async def get_app_js():
        return FileResponse(static_dir / "app.js")

@app.get("/")
async def serve_dashboard():
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "NetSentry API Gateway is live. Visit /docs for OpenAPI specifications."}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
