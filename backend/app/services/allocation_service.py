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
    
    @staticmethod
    def _calculate_capacity_score(dca: DCA, db: Session) -> float:
        """Calculate capacity availability score"""
        # Get current active cases for this DCA
        current_cases = db.query(func.count(Case.id)).filter(
            Case.dca_id == dca.id,
            Case.status.in_([CaseStatus.ALLOCATED, CaseStatus.IN_PROGRESS])
        ).scalar() or 0
        
        max_capacity = getattr(dca, 'max_concurrent_cases', 50)  # Default capacity
        
        if current_cases >= max_capacity:
            return 0.0  # At capacity
        
        # Calculate utilization percentage
        utilization = current_cases / max_capacity
        
        # Optimal utilization is around 70-80%
        if utilization <= 0.7:
            return 1.0  # Excellent capacity
        elif utilization <= 0.8:
            return 0.8  # Good capacity
        elif utilization <= 0.9:
            return 0.5  # Limited capacity
        else:
            return 0.2  # Very limited capacity
    
    @staticmethod
    def _calculate_specialization_score(case_data: Dict[str, Any], dca: DCA) -> float:
        """Calculate specialization match score"""
        debt_type = case_data.get('debt_type', 'other')
        amount = case_data.get('original_amount', 0)
        
        # Get DCA specializations (mock for now)
        specializations = getattr(dca, 'specialization', [])
        
        if not specializations:
            return 0.5  # Neutral if no specialization data
        
        # Check for debt type match
        if debt_type in specializations:
            score = 1.0
        else:
            score = 0.3  # Can handle but not specialized
        
        # Adjust for amount ranges (some DCAs better with high-value cases)
        if amount >= 50000 and 'high_value' in specializations:
            score += 0.2
        elif amount <= 5000 and 'small_claims' in specializations:
            score += 0.2
        
        return min(1.0, score)
    
    @staticmethod
    def _calculate_workload_score(dca: DCA, db: Session) -> float:
        """Calculate workload balance score"""
        # Get average case age for this DCA
        avg_case_age = db.query(func.avg(
            func.julianday('now') - func.julianday(Case.created_at)
        )).filter(
            Case.dca_id == dca.id,
            Case.status.in_([CaseStatus.ALLOCATED, CaseStatus.IN_PROGRESS])
        ).scalar() or 0
        
        # Prefer DCAs with lower average case age (faster processing)
        if avg_case_age <= 7:
            return 1.0  # Excellent turnaround
        elif avg_case_age <= 14:
            return 0.8  # Good turnaround
        elif avg_case_age <= 30:
            return 0.6  # Average turnaround
        else:
            return 0.3  # Slow turnaround
    
    @staticmethod
    def bulk_allocate_cases(case_ids: List[str], allocation_strategy: str, db: Session, user_id: str) -> Dict[str, Any]:
        """
        Bulk allocate multiple cases using specified strategy
        """
        results = {
            "allocated": [],
            "failed": [],
            "summary": {}
        }
        
        cases = db.query(Case).filter(
            Case.id.in_(case_ids),
            Case.status == CaseStatus.NEW
        ).all()
        
        if allocation_strategy == "performance_based":
            results = AllocationService._allocate_by_performance(cases, db, user_id)
        elif allocation_strategy == "capacity_based":
            results = AllocationService._allocate_by_capacity(cases, db, user_id)
        elif allocation_strategy == "round_robin":
            results = AllocationService._allocate_round_robin(cases, db, user_id)
        else:
            results = AllocationService._allocate_intelligent(cases, db, user_id)
        
        return results
    
    @staticmethod
    def _allocate_by_performance(cases: List[Case], db: Session, user_id: str) -> Dict[str, Any]:
        """Allocate cases to highest performing DCAs first"""
        # Get DCAs sorted by performance
        dcas = db.query(DCA).filter(
            DCA.is_active == True,
            DCA.is_accepting_cases == True
        ).order_by(DCA.performance_score.desc()).all()
        
        allocated = []
        failed = []
        
        for case in cases:
            case_data = {
                "original_amount": case.original_amount,
                "days_delinquent": case.days_delinquent,
                "debt_type": getattr(case, 'debt_type', 'other')
            }
            
            best_dca = AllocationService.find_best_dca(case_data, dcas, db)
            
            if best_dca:
                case.dca_id = best_dca.id
                case.status = CaseStatus.ALLOCATED
                case.allocated_by = user_id
                case.allocation_date = func.now()
                allocated.append(case.id)
            else:
                failed.append({"case_id": case.id, "reason": "No available DCA"})
        
        db.commit()
        
        return {
            "allocated": allocated,
            "failed": failed,
            "summary": {
                "total_cases": len(cases),
                "allocated_count": len(allocated),
                "failed_count": len(failed)
            }
        }
    
    @staticmethod
    def _allocate_by_capacity(cases: List[Case], db: Session, user_id: str) -> Dict[str, Any]:
        """Allocate cases to DCAs with most available capacity"""
        # Get DCAs with capacity info
        dcas = db.query(DCA).filter(
            DCA.is_active == True,
            DCA.is_accepting_cases == True
        ).all()
        
        # Sort by available capacity
        dca_capacity = []
        for dca in dcas:
            current_cases = db.query(func.count(Case.id)).filter(
                Case.dca_id == dca.id,
                Case.status.in_([CaseStatus.ALLOCATED, CaseStatus.IN_PROGRESS])
            ).scalar() or 0
            
            max_capacity = getattr(dca, 'max_concurrent_cases', 50)
            available = max_capacity - current_cases
            
            if available > 0:
                dca_capacity.append((dca, available))
        
        # Sort by available capacity (most available first)
        dca_capacity.sort(key=lambda x: x[1], reverse=True)
        
        allocated = []
        failed = []
        
        for case in cases:
            if dca_capacity:
                # Allocate to DCA with most capacity
                best_dca, capacity = dca_capacity[0]
                
                case.dca_id = best_dca.id
                case.status = CaseStatus.ALLOCATED
                case.allocated_by = user_id
                case.allocation_date = func.now()
                allocated.append(case.id)
                
                # Update capacity tracking
                dca_capacity[0] = (best_dca, capacity - 1)
                if capacity - 1 <= 0:
                    dca_capacity.pop(0)  # Remove if at capacity
                else:
                    # Re-sort to maintain order
                    dca_capacity.sort(key=lambda x: x[1], reverse=True)
            else:
                failed.append({"case_id": case.id, "reason": "No available capacity"})
        
        db.commit()
        
        return {
            "allocated": allocated,
            "failed": failed,
            "summary": {
                "total_cases": len(cases),
                "allocated_count": len(allocated),
                "failed_count": len(failed)
            }
        }
    
    @staticmethod
    def _allocate_round_robin(cases: List[Case], db: Session, user_id: str) -> Dict[str, Any]:
        """Allocate cases in round-robin fashion across available DCAs"""
        dcas = db.query(DCA).filter(
            DCA.is_active == True,
            DCA.is_accepting_cases == True
        ).all()
        
        if not dcas:
            return {
                "allocated": [],
                "failed": [{"case_id": case.id, "reason": "No available DCAs"} for case in cases],
                "summary": {"total_cases": len(cases), "allocated_count": 0, "failed_count": len(cases)}
            }
        
        allocated = []
        failed = []
        dca_index = 0
        
        for case in cases:
            # Check if current DCA has capacity
            current_dca = dcas[dca_index]
            current_cases = db.query(func.count(Case.id)).filter(
                Case.dca_id == current_dca.id,
                Case.status.in_([CaseStatus.ALLOCATED, CaseStatus.IN_PROGRESS])
            ).scalar() or 0
            
            max_capacity = getattr(current_dca, 'max_concurrent_cases', 50)
            
            if current_cases < max_capacity:
                case.dca_id = current_dca.id
                case.status = CaseStatus.ALLOCATED
                case.allocated_by = user_id
                case.allocation_date = func.now()
                allocated.append(case.id)
            else:
                failed.append({"case_id": case.id, "reason": f"DCA {current_dca.code} at capacity"})
            
            # Move to next DCA
            dca_index = (dca_index + 1) % len(dcas)
        
        db.commit()
        
        return {
            "allocated": allocated,
            "failed": failed,
            "summary": {
                "total_cases": len(cases),
                "allocated_count": len(allocated),
                "failed_count": len(failed)
            }
        }
    
    @staticmethod
    def _allocate_intelligent(cases: List[Case], db: Session, user_id: str) -> Dict[str, Any]:
        """Intelligent allocation using all factors"""
        dcas = db.query(DCA).filter(
            DCA.is_active == True,
            DCA.is_accepting_cases == True
        ).all()
        
        allocated = []
        failed = []
        
        for case in cases:
            case_data = {
                "original_amount": case.original_amount,
                "days_delinquent": case.days_delinquent,
                "debt_type": getattr(case, 'debt_type', 'other')
            }
            
            best_dca = AllocationService.find_best_dca(case_data, dcas, db)
            
            if best_dca:
                case.dca_id = best_dca.id
                case.status = CaseStatus.ALLOCATED
                case.allocated_by = user_id
                case.allocation_date = func.now()
                allocated.append(case.id)
            else:
                failed.append({"case_id": case.id, "reason": "No suitable DCA found"})
        
        db.commit()
        
        return {
            "allocated": allocated,
            "failed": failed,
            "summary": {
                "total_cases": len(cases),
                "allocated_count": len(allocated),
                "failed_count": len(failed)
            }
        }
    
    @staticmethod
    def get_allocation_recommendations(case_id: str, db: Session) -> List[Dict[str, Any]]:
        """Get DCA recommendations for a specific case"""
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            return []
        
        case_data = {
            "original_amount": case.original_amount,
            "days_delinquent": case.days_delinquent,
            "debt_type": getattr(case, 'debt_type', 'other')
        }
        
        dcas = db.query(DCA).filter(
            DCA.is_active == True,
            DCA.is_accepting_cases == True
        ).all()
        
        recommendations = []
        
        for dca in dcas:
            score = AllocationService._calculate_dca_score(case_data, dca, db)
            
            if score > 0:
                recommendations.append({
                    "dca_id": dca.id,
                    "dca_name": dca.name,
                    "dca_code": dca.code,
                    "allocation_score": round(score, 3),
                    "performance_score": dca.performance_score,
                    "current_capacity": AllocationService._get_current_capacity(dca, db),
                    "specialization_match": AllocationService._calculate_specialization_score(case_data, dca)
                })
        
        # Sort by allocation score
        recommendations.sort(key=lambda x: x["allocation_score"], reverse=True)
        
        return recommendations
    
    @staticmethod
    def _get_current_capacity(dca: DCA, db: Session) -> Dict[str, int]:
        """Get current capacity info for a DCA"""
        current_cases = db.query(func.count(Case.id)).filter(
            Case.dca_id == dca.id,
            Case.status.in_([CaseStatus.ALLOCATED, CaseStatus.IN_PROGRESS])
        ).scalar() or 0
        
        max_capacity = getattr(dca, 'max_concurrent_cases', 50)
        
        return {
            "current_cases": current_cases,
            "max_capacity": max_capacity,
            "available_slots": max_capacity - current_cases,
            "utilization_percentage": round((current_cases / max_capacity) * 100, 1)
        }