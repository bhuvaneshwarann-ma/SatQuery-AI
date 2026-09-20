"""
SatQuery AI — FastAPI Application Entry Point (Phase 7A)
Connects HTTP/multipart client traffic to the Phase 6 Agent Orchestrator.
Configures development CORS, static evidence artifact delivery, and health telemetry.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api.routes import router as api_router, get_health

app = FastAPI(
    title="SatQuery AI API",
    description="Agentic Multi-Modal Remote Sensing & Satellite QA System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# -------------------------------------------------------------
# CORS Configuration
# -------------------------------------------------------------
# Configurable origin list for development React frontend (e.g. Vite :5173 or CRA :3000)
cors_origins_env = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"
)
origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# API Router Mounting
# -------------------------------------------------------------
app.include_router(api_router, prefix="/api")

# Expose convenience root health endpoint (without duplicating logic)
@app.get("/health", include_in_schema=False)
async def root_health():
    return await get_health()

# Mount generated evidence artifacts directory for frontend inspection
artifacts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../docs/results"))
if os.path.exists(artifacts_dir):
    app.mount("/api/artifacts", StaticFiles(directory=artifacts_dir), name="artifacts")

@app.get("/", include_in_schema=False)
async def root():
    return {
        "service": "SatQuery AI Backend",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "tools": "/api/tools",
            "analyze": "/api/analyze",
            "docs": "/docs",
        },
    }
