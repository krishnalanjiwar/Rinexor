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
# TODO: implement edge case handling
