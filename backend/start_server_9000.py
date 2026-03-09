from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
import uvicorn

app = FastAPI(title="RecoverAI Pro API")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    conn = sqlite3.connect('recoverai.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
def root():
    return {"status": "RecoverAI Pro Backend Running on port 9000"}

@app.get("/api/health")
def health():
    return {"status": "healthy", "port": 9000}

# TODO: implement edge case handling
