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
        
        if not scored_dcas:
            return None
        
        # Sort by score (highest first) and return best DCA
        scored_dcas.sort(key=lambda x: x[1], reverse=True)
        return scored_dcas[0][0]
    
    @staticmethod
    def _calculate_dca_score(case_data: Dict[str, Any], dca: DCA, db: Session) -> float:
        """Calculate allocation score for a DCA"""
        score = 0.0
        
        # 1. Capacity check (40% weight)
        capacity_score = AllocationService._calculate_capacity_score(dca, db)
        if capacity_score <= 0:
            return 0  # No capacity = no allocation
        score += capacity_score * 0.4
        
        # 2. Performance score (35% weight)
        performance_score = dca.performance_score or 0.5
        score += performance_score * 0.35
        
        # 3. Specialization match (15% weight)
        specialization_score = AllocationService._calculate_specialization_score(case_data, dca)
        score += specialization_score * 0.15
        
        # 4. Current workload balance (10% weight)
        workload_score = AllocationService._calculate_workload_score(dca, db)
        score += workload_score * 0.1
        
        return score
# TODO: implement edge case handling
