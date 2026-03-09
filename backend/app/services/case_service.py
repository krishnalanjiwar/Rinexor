from datetime import datetime, timedelta
from backend.app.models import Case, CaseStatus, WorkflowStage, DCA
from backend.app.core.database import SessionLocal

db = SessionLocal()

def find_available_dca():
    # Simplified for hackathon: return DCA with fewest active cases
    dcas = db.query(DCA).all()
    if not dcas:
        return None
    dcas.sort(key=lambda d: len(d.cases))
    return dcas[0]

def calculate_sla(case: Case):
    # Example: SLA = 48 hours for initial contact
    return datetime.utcnow() + timedelta(hours=48)

def save_case(case: Case):
    case.last_updated = datetime.utcnow()
    db.add(case)
    db.commit()
    db.refresh(case)

def notify_admin(case: Case):
    # Simple placeholder for demo: just print to console
    print(f"SLA Breach Alert: Case {case.id} for borrower {case.borrower_name}")
