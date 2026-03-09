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
    
# TODO: implement edge case handling
