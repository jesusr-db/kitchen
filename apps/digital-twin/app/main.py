"""FastAPI application entry point for Casper's Digital Twin."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.config import settings
from app.api import locations, orders

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    logger.info(f"Starting {settings.app_name}...")
    logger.info(f"Catalog: {settings.catalog}")
    logger.info(f"Lakeflow Schema: {settings.lakeflow_schema}")
    yield
    logger.info(f"Shutting down {settings.app_name}...")


# Initialize FastAPI application
app = FastAPI(
    title="Casper's Kitchen Digital Twin",
    description="Real-time visualization and replay of ghost kitchen operations",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(
    locations.router,
    prefix=settings.api_v1_prefix,
    tags=["locations"]
)
app.include_router(
    orders.router,
    prefix=settings.api_v1_prefix,
    tags=["orders"]
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "catalog": settings.catalog,
        "lakeflow_schema": settings.lakeflow_schema
    }


# Serve frontend static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
assets_dir = os.path.join(static_dir, "assets")
if os.path.exists(static_dir) and os.path.isdir(static_dir) and os.path.exists(assets_dir):
    # Mount static assets
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve frontend SPA - catch all routes and return index.html."""
        # Check if requesting a specific file
        file_path = os.path.join(static_dir, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # Otherwise, serve index.html for client-side routing
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        
        return {"message": "Frontend not built. Run 'npm run build' in frontend directory."}
else:
    @app.get("/")
    async def root():
        """Root endpoint when frontend is not built."""
        return {
            "message": "Casper's Kitchen Digital Twin API",
            "docs": "/docs",
            "health": "/health",
            "note": "Frontend not built. Run 'npm run build' in frontend directory to enable UI."
        }
