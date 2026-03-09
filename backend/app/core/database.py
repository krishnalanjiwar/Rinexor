# SIMPLE DATABASE CONFIG FOR SQLITE
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# SQLite connection (no psycopg2 needed!)
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # Important for SQLite with FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()