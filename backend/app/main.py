"""FastAPI application factory and main entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.routes import streams, infer, zones, auth, models, metrics
from app.ws import live


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown."""
    # Startup
    print("Starting Crowd Density API...")
    yield
    # Shutdown
    print("Shutting down Crowd Density API...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Crowd Density API",
        description="Real-time crowd density estimation with YOLO and CSRNet",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount routers
    app.include_router(streams.router, prefix="/streams", tags=["streams"])
    app.include_router(infer.router, prefix="/infer", tags=["inference"])
    app.include_router(zones.router, prefix="/zones", tags=["zones"])
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(models.router, prefix="/models", tags=["models"])
    app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
    app.include_router(live.router, prefix="/ws", tags=["websocket"])

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy", "version": "0.1.0"}

    return app


app = create_app()

