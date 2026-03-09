"""
ALLOCATION SERVICE - Intelligent DCA allocation and capacity management
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.dca import DCA
from app.models.case import Case, CaseStatus
from app.models.user import User


class AllocationService:
    
    @staticmethod
    def find_best_dca(case_data: Dict[str, Any], available_dcas: List[DCA], db: Session) -> Optional[DCA]:
        """
        Find the best DCA for a case based on:
        1. Capacity availability
        2. Performance score
        3. Specialization match
        4. Current workload
        """
        if not available_dcas:
            return None
        
        scored_dcas = []
        
        for dca in available_dcas:
            score = AllocationService._calculate_dca_score(case_data, dca, db)
            if score > 0:  # Only consider DCAs with positive scores
                scored_dcas.append((dca, score))
# TODO: implement edge case handling
