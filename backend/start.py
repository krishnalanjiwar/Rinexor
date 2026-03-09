"""
SIMPLE STARTUP SCRIPT - Fixes all common issues
"""
import sys
import os
import subprocess

print("=" * 60)
print("STARTING RECOVERAI PRO BACKEND")
print("=" * 60)

# Check if database exists
if not os.path.exists("recoverai.db"):
    print("⚠️  Database not found. Creating...")
    
    # Create simple database
    import sqlite3
    conn = sqlite3.connect('recoverai.db')
    conn.close()
    print("✅ Created recoverai.db")
    
    # Create tables using the setup script
    try:
        import setup_database
        print("✅ Database tables created")
    except:
        print("⚠️  Could not run setup_database. Starting anyway...")

# Start the server
print("\n🚀 Starting FastAPI server...")
print("📡 Server will be available at: http://127.0.0.1:8000")
print("📚 API docs at: http://127.0.0.1:8000/api/docs")
print("\nPress Ctrl+C to stop\n")

# Start uvicorn
subprocess.run([
    sys.executable, "-m", "uvicorn", 
    "app.main:app", 
    "--reload", 
    "--host", "0.0.0.0", 
    "--port", "8000"
])