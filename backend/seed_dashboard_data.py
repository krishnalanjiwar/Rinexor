"""
Seed realistic time-series data for dashboard charts.
Run AFTER setup_database.py to add monthly-spread cases.
"""
import sys
sys.path.insert(0, '.')

from datetime import datetime, timedelta
import uuid
import random

from app.core.database import engine
from app.models.case import Case, CaseStatus, CasePriority, RecoveryScoreBand
from app.models.dca import DCA
from sqlalchemy.orm import Session

def seed_dashboard_data():
    db = Session(engine)

    dcas = db.query(DCA).filter(DCA.is_active == True).all()
    if not dcas:
        print("❌ No DCAs found. Run setup_database.py first.")
        db.close()
        return

    print("🌱 Seeding time-series dashboard data...")

    now = datetime.utcnow()
    debtor_names = [
        "Aisha Patel", "Ravi Kumar", "Neha Sharma", "Vikram Singh",
        "Priya Gupta", "Arjun Reddy", "Sneha Iyer", "Kiran Desai",
        "Anjali Nair", "Rohit Mehta", "Deepa Joshi", "Suresh Rao",
        "Pooja Verma", "Manoj Pillai", "Kavita Bhat", "Sanjay Kulkarni",
        "Divya Menon", "Rajesh Tiwari", "Meera Saxena", "Amit Chauhan",
        "Lakshmi Das", "Nitin Shetty", "Swati Mishra", "Gaurav Pandey",
        "Tanvi Kamath", "Harsh Agarwal", "Ritika Jain", "Varun Kapoor",
    ]
# TODO: implement edge case handling
