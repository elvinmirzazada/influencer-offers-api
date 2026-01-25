import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.api import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables
logger.info("Creating database tables...")
Base.metadata.create_all(bind=engine)
logger.info("Database initialized successfully")

# Create FastAPI application
logger.info(f"Initializing {settings.PROJECT_NAME}...")
app = FastAPI(
    title=settings.PROJECT_NAME
)

# Set up CORS
logger.info("Configuring CORS...")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
logger.info("Registering API routes...")
app.include_router(api_router, prefix=settings.API_V1_STR)
logger.info("Application startup complete")


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Influencer Offers API",
        "docs": "/docs",
        "api_version": "v1"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

