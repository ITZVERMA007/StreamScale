import time
import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter
from app.api.routes import api_router as v1_router
from app.db.database import engine
from app.db import models

logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Streamscale_API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} "
        f"- Status: {response.status_code} "
        f"- Time: {process_time:.3f}s"
    )
    return response

# CORS configuration - supports localhost dev and Vercel production
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite default
    "http://localhost",
]

# Add Vercel frontend domain from environment variable
VERCEL_FRONTEND_URL = os.getenv("VERCEL_FRONTEND_URL")
if VERCEL_FRONTEND_URL:
    ALLOWED_ORIGINS.append(VERCEL_FRONTEND_URL)

# Also support any vercel.app subdomain for preview deployments
FRONTEND_URL = os.getenv("FRONTEND_URL")
if FRONTEND_URL:
    ALLOWED_ORIGINS.append(FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,  # Required for cookies/auth if needed
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],  # For file downloads
)

@app.get("/")
async def health_check():
    """Health check endpoint for Railway deployment monitoring."""
    return {
        "status": "healthy",
        "service": "streamscale-api",
        "version": "1.0.0"
    }

@app.get("/health")
async def detailed_health():
    """Detailed health check for monitoring services."""
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "checks": {
            "database": "unknown",
            "redis": "unknown",
            "s3": "unknown"
        }
    }
    
    # Check database connectivity
    try:
        from sqlalchemy import text
        from app.db.database import engine
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "connected"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Redis connectivity
    try:
        from app.core.celery_app import celery_app
        celery_app.backend.client.ping()
        health_status["checks"]["redis"] = "connected"
    except Exception as e:
        health_status["checks"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check S3 connectivity (credentials only, not actual bucket)
    try:
        from app.services.s3_client import get_s3_client, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
        if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
            client = get_s3_client()
            client.list_buckets()
            health_status["checks"]["s3"] = "connected"
        else:
            health_status["checks"]["s3"] = "not configured"
    except Exception as e:
        health_status["checks"]["s3"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status

app.include_router(v1_router)