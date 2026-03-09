# SIMPLE CONFIG - Replace your config.py with this
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Rinexor"
    
    # Security
    SECRET_KEY: str = "your-secret-key-for-jwt-tokens"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database - Use SQLite for hackathon (no psycopg2 needed!)
    DATABASE_URL: str = "sqlite:///./rinexor.db"
    
    # Qdrant Cloud
    QDRANT_URL: str = os.getenv("QDRANT_URL", "https://your-cluster.cloud.qdrant.io:6333")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # AI/ML
    SCORING_THRESHOLD_HIGH: float = 0.7
    SCORING_THRESHOLD_MEDIUM: float = 0.4
    
    # SLA
    SLA_CONTACT_DAYS: int = 3
    SLA_RESOLUTION_DAYS: int = 30

settings = Settings()