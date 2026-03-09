"""
WORKFLOW SERVICE - Case state management and SLA calculations
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.case import Case, CaseStatus, CasePriority
from app.models.dca import DCA
from app.models.sla import SLARule
from app.core.config import settings


class WorkflowService:
    
    @staticmethod
    def process_new_case(case_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """
        Process new case through workflow:
        1. Calculate priority based on AI scoring
        2. Determine SLA deadlines
        3. Auto-allocate to DCA if rules match
        4. Set initial status
        """
        # 1. Determine initial priority based on amount and delinquency
        priority = WorkflowService._calculate_initial_priority(case_data)
        
        # 2. Calculate SLA deadlines based on priority
        sla_deadlines = WorkflowService._calculate_sla_deadlines(priority)
        
        # 3. Try auto-allocation to DCA
        allocated_dca = WorkflowService._auto_allocate_dca(case_data, db)
        
        # 4. Set initial status
        status = CaseStatus.ALLOCATED if allocated_dca else CaseStatus.NEW
        
        # 5. Calculate initial recovery score (will be updated by AI)
        recovery_score = WorkflowService._calculate_initial_recovery_score(case_data)
        
        return {
            "status": status,
            "priority": priority,
            "recovery_score": recovery_score,
            "dca_id": allocated_dca.id if allocated_dca else None,
            "sla_contact_deadline": sla_deadlines["contact"],
            "sla_resolution_deadline": sla_deadlines["resolution"]
        }
    
    @staticmethod
    def _calculate_initial_priority(case_data: Dict[str, Any]) -> str:
        """Calculate initial priority based on business rules"""
        amount = case_data.get('original_amount', 0)
        days_delinquent = case_data.get('days_delinquent', 0)
        
        # High priority criteria
        if amount >= 50000 or days_delinquent >= 90:
            return CasePriority.HIGH
        
        # Medium priority criteria  
        if amount >= 10000 or days_delinquent >= 30:
            return CasePriority.MEDIUM
        
        return CasePriority.LOW
    
    @staticmethod
    def _calculate_sla_deadlines(priority: str) -> Dict[str, datetime]:
        """Calculate SLA deadlines based on priority"""
        now = datetime.utcnow()
        
        if priority == CasePriority.HIGH:
            contact_days = 1
            resolution_days = 7
        elif priority == CasePriority.MEDIUM:
            contact_days = 3
            resolution_days = 15
        else:  # LOW
            contact_days = 5
            resolution_days = 30
        
        return {
            "contact": now + timedelta(days=contact_days),
            "resolution": now + timedelta(days=resolution_days)
        }
    
    @staticmethod
    def _auto_allocate_dca(case_data: Dict[str, Any], db: Session) -> Optional[DCA]:
        """
        Auto-allocate case to best available DCA based on:
        1. Capacity availability
        2. Performance score
        3. Specialization match
        """
        from app.services.allocation_service import AllocationService
        
        # Get available DCAs
        available_dcas = db.query(DCA).filter(
            DCA.is_active == True,
            DCA.is_accepting_cases == True
        ).all()
        
        if not available_dcas:
            return None
        
        # Use allocation service for intelligent assignment
        return AllocationService.find_best_dca(case_data, available_dcas, db)
    
    @staticmethod
    def _calculate_initial_recovery_score(case_data: Dict[str, Any]) -> float:
        """Calculate initial recovery score using simple rules"""
        amount = case_data.get('original_amount', 0)
        days_delinquent = case_data.get('days_delinquent', 0)
        
        # Base score starts at 50%
        score = 50.0
        
        # Adjust based on amount (higher amounts = higher recovery chance)
        if amount >= 50000:
            score += 20
        elif amount >= 10000:
            score += 10
        elif amount < 1000:
            score -= 15
        
        # Adjust based on delinquency (fresher debt = higher recovery)
        if days_delinquent <= 30:
            score += 25
        elif days_delinquent <= 90:
            score += 10
        elif days_delinquent >= 365:
            score -= 30
        
        # Ensure score is between 0-100
        return max(0.0, min(100.0, score))
    
    @staticmethod
    def update_case_status(case_id: str, new_status: str, db: Session, user_id: str = None) -> bool:
        """Update case status with workflow validation"""
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            return False
        
        # Validate status transition
        if not WorkflowService._is_valid_status_transition(case.status, new_status):
            return False
        
        # Update case
        case.status = new_status
        case.updated_at = datetime.utcnow()
        
        # Log status change
        WorkflowService._log_status_change(case, new_status, user_id, db)
        
        db.commit()
        return True
    
    @staticmethod
    def _is_valid_status_transition(current_status: str, new_status: str) -> bool:
        """Validate if status transition is allowed"""
        valid_transitions = {
            CaseStatus.NEW: [CaseStatus.ALLOCATED, CaseStatus.IN_PROGRESS, CaseStatus.CLOSED],
            CaseStatus.ALLOCATED: [CaseStatus.IN_PROGRESS, CaseStatus.RETURNED, CaseStatus.CLOSED],
            CaseStatus.IN_PROGRESS: [CaseStatus.RESOLVED, CaseStatus.ESCALATED, CaseStatus.CLOSED],
            CaseStatus.ESCALATED: [CaseStatus.IN_PROGRESS, CaseStatus.RESOLVED, CaseStatus.CLOSED],
            CaseStatus.RESOLVED: [CaseStatus.CLOSED, CaseStatus.IN_PROGRESS],
            CaseStatus.RETURNED: [CaseStatus.NEW, CaseStatus.ALLOCATED],
            CaseStatus.CLOSED: []  # Final state
        }
        
        return new_status in valid_transitions.get(current_status, [])
    
    @staticmethod
    def _log_status_change(case: Case, new_status: str, user_id: str, db: Session):
        """Log status change in audit trail"""
        from app.models.audit import AuditLog
        import uuid
        
        audit = AuditLog(
            id=str(uuid.uuid4()),
            entity_type="case",
            entity_id=case.id,
            action="status_change",
            old_values={"status": case.status},
            new_values={"status": new_status},
            user_id=user_id,
            timestamp=datetime.utcnow()
        )
        
        db.add(audit)
    
    @staticmethod
    def check_sla_breaches(db: Session) -> list:
        """Check for SLA breaches across all active cases"""
        now = datetime.utcnow()
        
        # Find cases with breached contact SLA
        contact_breaches = db.query(Case).filter(
            Case.status.in_([CaseStatus.NEW, CaseStatus.ALLOCATED]),
            Case.sla_contact_deadline < now,
            Case.first_contact_date.is_(None)
        ).all()
        
        # Find cases with breached resolution SLA
        resolution_breaches = db.query(Case).filter(
            Case.status.in_([CaseStatus.NEW, CaseStatus.ALLOCATED, CaseStatus.IN_PROGRESS]),
            Case.sla_resolution_deadline < now,
            Case.resolved_date.is_(None)
        ).all()
        
        breaches = []
        
        for case in contact_breaches:
            breaches.append({
                "case_id": case.id,
                "breach_type": "contact_sla",
                "deadline": case.sla_contact_deadline,
                "days_overdue": (now - case.sla_contact_deadline).days
            })
        
        for case in resolution_breaches:
            breaches.append({
                "case_id": case.id,
                "breach_type": "resolution_sla", 
                "deadline": case.sla_resolution_deadline,
                "days_overdue": (now - case.sla_resolution_deadline).days
            })
        
        return breaches