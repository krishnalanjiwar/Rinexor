"""
Rinexor Backend - FastAPI Application
AI-powered Debt Collection Agency Management Platform
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import routers
from app.api import auth, cases

app = FastAPI(
    title="Rinexor API",
    description="AI-powered Debt Collection Agency Management Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware - Allow all origins for Vercel deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(cases.router, prefix="/api/cases", tags=["cases"])


# Try to register AI router if available
try:
    from app.api import ai
    app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
    logger.info("✅ AI router registered")
except Exception as e:
    logger.warning(f"⚠️ AI router not available: {e}")

# Try to register DCAs router if available
try:
    from app.api import dcas
    app.include_router(dcas.router, prefix="/api/dcas", tags=["dcas"])
    logger.info("✅ DCAs router registered")
except Exception as e:
    logger.warning(f"⚠️ DCAs router not available: {e}")

# Register Reports router for dashboard analytics
try:
    from app.api import reports
    app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
    logger.info("✅ Reports router registered")
except Exception as e:
    logger.warning(f"⚠️ Reports router not available: {e}")

# Register Users router (Qdrant Cloud backed)
try:
    from app.api import users
    app.include_router(users.router, prefix="/api/users", tags=["users"])
    logger.info("✅ Users router registered (Qdrant Cloud)")
except Exception as e:
    logger.warning(f"⚠️ Users router not available: {e}")


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 Starting Rinexor Backend...")

    # Initialize Qdrant Cloud collections
    try:
        from app.core.qdrant_db import get_qdrant_client, ensure_collections
        client = get_qdrant_client()
        ensure_collections(client)
        logger.info("✅ Qdrant Cloud connected and collections ready")
    except Exception as e:
        logger.warning(f"⚠️ Qdrant Cloud warning (non-critical): {e}")

    # Seed default users in SQLite
    try:
        from app.services.sqlite_user_service import seed_default_users
        seed_default_users()
        logger.info("✅ Default users ready in SQLite")
    except Exception as e:
        logger.warning(f"⚠️ User seeding warning: {e}")

    # Initialize AI service (optional - works without it)
    try:
        from app.services.ai_service import AIService
        ai_service = AIService()
        ai_service.initialize()
        logger.info("✅ AI service initialized")
    except Exception as e:
        logger.warning(f"⚠️ AI service warning (non-critical): {e}")

    logger.info("✅ Rinexor Backend started successfully!")


@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "app": "Rinexor API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/health")
def health_check():
    """API health check"""
    return {"status": "healthy", "api": "v1"}


# For running directly with python main.py
if __name__ == "__main__":
    import uvicorn
    port = 8000
    logger.info(f"🚀 Starting on port {port}")
    logger.info(f"📚 Docs: http://localhost:{port}/docs")
    uvicorn.run(app, host="0.0.0.0", port=port)