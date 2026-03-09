"""
SIMPLE DATABASE SETUP FOR HACKATHON - NO ALEMBIC
"""
import sys
import os
from pathlib import Path

print("=" * 60)
print("RINEXOR - DATABASE SETUP")
print("=" * 60)

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    # Import database engine and models
    from app.core.database import engine, Base
    from app.models import *
    
    print("✅ Imported all models successfully")
    
    # CREATE ALL TABLES
    print("\n📦 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created!")
    
    # VERIFY TABLES
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"\n📊 Found {len(tables)} tables:")
    print("-" * 40)
    for table in sorted(tables):
        print(f"  • {table}")
    
    # CREATE DEMO DATA
    print("\n🎭 Creating demo data...")
    from sqlalchemy.orm import Session
    from app.models.user import User, UserRole
    from app.models.dca import DCA
    from app.models.case import Case, CaseStatus, CasePriority, RecoveryScoreBand
    import uuid
    from datetime import datetime, timedelta
    import random
    
    db = Session(engine)
    
    # 1. Create DCAs
    dcas = []
    dca_names = [
        ("Alpha Collections", "John Manager", "contact@alphacollections.com"),
        ("Beta Recovery", "Sarah Smith", "contact@betarecovery.com"),
        ("Gamma Solutions", "Mike Johnson", "info@gammasolutions.com"),
        ("Delta Agency", "Lisa Chen", "support@deltaagency.com")
    ]
    
    for i, (name, contact, email) in enumerate(dca_names):
        dca = DCA(
            id=str(uuid.uuid4()),
            name=name,
            code=f"DCA-{i+1:03d}",
            contact_person=contact,
            email=email,
            phone=f"+1-555-{1000+i}",
            address=f"{i+100} Collection St, New York, NY",
            performance_score=round(random.uniform(0.7, 0.95), 2),
            recovery_rate=round(random.uniform(65, 92), 1),
            avg_resolution_days=round(random.uniform(20, 40), 1),
            max_concurrent_cases=random.choice([30, 50, 75]),
            current_active_cases=random.randint(5, 20),
            specialization=random.sample(["medical", "credit_card", "personal_loan", "mortgage"], 2),
            sla_compliance_rate=round(random.uniform(88, 98), 1),
            is_active=True,
            is_accepting_cases=True
        )
        dcas.append(dca)
        db.add(dca)
    
    db.commit()
    print(f"✅ Created {len(dcas)} DCAs")
    
    # 2. Create Users
    users = []
    
    # Enterprise Admin
    admin = User(
        id=str(uuid.uuid4()),
        email="admin@rinexor.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        full_name="System Administrator",
        role=UserRole.ENTERPRISE_ADMIN,
        is_active=True
    )
    users.append(admin)
    db.add(admin)
    
    # Collection Manager
    manager = User(
        id=str(uuid.uuid4()),
        email="manager@recoverai.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        full_name="Collection Manager",
        role=UserRole.COLLECTION_MANAGER,
        is_active=True
    )
    users.append(manager)
    db.add(manager)
    
    # DCA Agents (2 per DCA)
    agent_counter = 1
    for dca in dcas:
        for j in range(2):  # 2 agents per DCA
            agent = User(
                id=str(uuid.uuid4()),
                email=f"agent{agent_counter}@{dca.name.lower().replace(' ', '')}.com",
                hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
                full_name=f"Agent {agent_counter} - {dca.name.split()[0]}",
                role=UserRole.DCA_AGENT,
                dca_id=dca.id,
                is_active=True
            )
            users.append(agent)
            db.add(agent)
            agent_counter += 1
    
    db.commit()
    print(f"✅ Created {len(users)} users")
    
    # 3. Create Cases
    cases = []
    debtor_names = [
        "John Smith", "Maria Garcia", "Robert Johnson", "Lisa Chen",
        "David Williams", "Sarah Miller", "James Brown", "Emily Davis",
        "Michael Wilson", "Jennifer Taylor", "Christopher Lee",
        "Amanda Martinez", "Daniel Thompson", "Jessica Anderson"
    ]
    
    # Case status distribution for demo
    statuses = [
        (CaseStatus.NEW, 3, None),
        (CaseStatus.ASSIGNED, 5, dcas[0].id),
        (CaseStatus.IN_PROGRESS, 4, dcas[1].id),
        (CaseStatus.CONTACTED, 3, dcas[2].id),
        (CaseStatus.PAYMENT_PROMISE, 2, dcas[3].id),
        (CaseStatus.PARTIALLY_PAID, 1, dcas[0].id),
        (CaseStatus.RESOLVED, 3, dcas[1].id),
        (CaseStatus.ESCALATED, 2, None),
    ]
    
    case_counter = 1
    for status, count, dca_id in statuses:
        for i in range(count):
            debtor = random.choice(debtor_names)
            amount = round(random.uniform(1500, 35000), 2)
            days_delinquent = random.randint(30, 150)
            
            # Calculate recovery score
            base_score = random.uniform(0.3, 0.9)
            if days_delinquent > 90:
                base_score *= 0.7
            if amount > 20000:
                base_score *= 0.8
            
            recovery_score = round(base_score, 2)
            
            # Determine band and priority
            if recovery_score >= 0.7:
                band = RecoveryScoreBand.HIGH
                priority = CasePriority.HIGH
            elif recovery_score >= 0.4:
                band = RecoveryScoreBand.MEDIUM
                priority = CasePriority.MEDIUM
            else:
                band = RecoveryScoreBand.LOW
                priority = CasePriority.LOW
            
            # Create case
            case = Case(
                id=str(uuid.uuid4()),
                account_id=f"ACC-{case_counter:05d}",
                debtor_name=debtor,
                debtor_email=f"{debtor.lower().replace(' ', '.')}@example.com",
                debtor_phone=f"+1-555-{8000 + case_counter}",
                original_amount=amount,
                current_amount=round(amount * random.uniform(0.5, 1.0), 2),
                currency="USD",
                days_delinquent=days_delinquent,
                debt_age_days=days_delinquent + random.randint(0, 30),
                status=status,
                priority=priority,
                recovery_score=recovery_score,
                recovery_score_band=band,
                dca_id=dca_id,
                allocated_by=admin.id if dca_id else None,
                allocation_date=datetime.utcnow() - timedelta(days=random.randint(1, 10)) if dca_id else None,
                ml_features={
                    "debt_age": days_delinquent,
                    "amount": amount,
                    "credit_score": random.randint(580, 750),
                    "employment_status": random.choice(["employed", "self-employed", "unemployed"])
                },
                sla_contact_deadline=datetime.utcnow() + timedelta(days=random.randint(1, 7)),
                sla_resolution_deadline=datetime.utcnow() + timedelta(days=random.randint(20, 60)),
                sla_breached=False,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            
            cases.append(case)
            db.add(case)
            case_counter += 1
    
    db.commit()
    print(f"✅ Created {len(cases)} cases")
    
    # 4. Create some case notes
    print("\n📝 Creating sample case notes...")
    notes_created = 0
    for case in random.sample(cases, 10):  # Add notes to 10 random cases
        note_types = ["contact_attempt", "general", "payment_promise", "follow_up"]
        for j in range(random.randint(1, 3)):
            from app.models.case_note import CaseNote
            
            note = CaseNote(
                id=str(uuid.uuid4()),
                case_id=case.id,
                user_id=random.choice([u.id for u in users if u.role != UserRole.DCA_AGENT]),
                content=f"Sample note #{j+1} for case {case.account_id}. " +
                       f"Contact attempted via phone. " +
                       f"Debtor expressed willingness to discuss payment options.",
                note_type=random.choice(note_types),
                contact_method=random.choice(["phone", "email", "letter"]),
                contact_outcome=random.choice(["successful", "failed", "voicemail"]),
                created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 72))
            )
            db.add(note)
            notes_created += 1
    
    db.commit()
    print(f"✅ Created {notes_created} case notes")
    
    print("\n" + "=" * 60)
    print("✅ DATABASE SETUP COMPLETE!")
    print("=" * 60)
    print("\n📊 SUMMARY:")
    print(f"  • DCAs: {len(dcas)}")
    print(f"  • Users: {len(users)}")
    print(f"  • Cases: {len(cases)}")
    print(f"  • Notes: {notes_created}")
    
    # Show sample data
    print("\n👤 Sample Admin Login:")
    print("  Email: admin@recoverai.com")
    print("  Password: secret")
    
    print("\n👤 Sample DCA Agent Login:")
    print("  Email: agent1@alphacollections.com")
    print("  Password: secret")
    
    print("\n🌐 Start your server:")
    print("  cd backend")
    print("  uvicorn app.main:app --reload")
    
    db.close()
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    
    # Fallback: Create simple SQLite database
    print("\n⚠️  Creating simple database as fallback...")
    import sqlite3
    
    conn = sqlite3.connect('recoverai.db')
    cursor = conn.cursor()
    
    # Basic tables
    basic_tables = [
        """CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            full_name TEXT,
            role TEXT NOT NULL CHECK(role IN ('enterprise_admin', 'collection_manager', 'dca_agent')),
            dca_id TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        
        """CREATE TABLE IF NOT EXISTS dcas (
            id TEXT PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            code TEXT UNIQUE NOT NULL,
            contact_person TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            performance_score REAL DEFAULT 0.0,
            recovery_rate REAL DEFAULT 0.0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        
        """CREATE TABLE IF NOT EXISTS cases (
            id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            debtor_name TEXT NOT NULL,
            original_amount REAL NOT NULL,
            current_amount REAL NOT NULL,
            days_delinquent INTEGER DEFAULT 0,
            status TEXT DEFAULT 'new',
            priority TEXT DEFAULT 'medium',
            recovery_score REAL DEFAULT 0.0,
            dca_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
    ]
    
    for sql in basic_tables:
        cursor.execute(sql)
    
    conn.commit()
    
    # Insert sample data
    import uuid
    cursor.execute("INSERT OR IGNORE INTO users (id, email, hashed_password, full_name, role) VALUES (?, ?, ?, ?, ?)",
                  (str(uuid.uuid4()), "admin@recoverai.com", 
                   "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
                   "Admin User", "enterprise_admin"))
    
    cursor.execute("INSERT OR IGNORE INTO dcas (id, name, code, contact_person, email) VALUES (?, ?, ?, ?, ?)",
                  (str(uuid.uuid4()), "Alpha Collections", "DCA-001", 
                   "John Manager", "contact@alphacollections.com"))
    
    conn.commit()
    
    # Show tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"\n✅ Created {len(tables)} basic tables:")
    for table in tables:
        print(f"  • {table[0]}")
    
    conn.close()
    print("\n⚠️  Using basic database setup. Some features may be limited.")