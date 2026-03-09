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

@app.get("/api/tables")
def list_tables():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return {"tables": tables}
    except:
        return {"tables": []}

@app.get("/api/cases")
def get_cases():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cases LIMIT 10")
        rows = cursor.fetchall()
        cases = []
        for row in rows:
            cases.append(dict(row))
        conn.close()
        return {"cases": cases}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("🚀 Starting server on http://127.0.0.1:9000")
    print("📚 API docs: http://127.0.0.1:9000/docs")
    uvicorn.run(app, host="127.0.0.1", port=9000)