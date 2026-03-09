"""
SMART ALLOCATOR - DCA performance-based allocation engine
Matches cases to DCAs based on risk level and DCA performance
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func


class SmartAllocator:
    """
    Intelligent DCA allocation engine that matches:
    - High Risk cases → High Performing DCAs
    - Intermediate Risk cases → Medium Performing DCAs
    - Low Risk cases → Lower Performing DCAs
    """
    
    def __init__(self):
        self.allocation_strategy = {
            'high': 'top_performers',       # Top 30% of DCAs
            'intermediate': 'mid_performers',  # Middle 40% of DCAs
            'low': 'lower_performers'       # Bottom 30% of DCAs
        }
    
    def get_allocation_preview(
        self, 
        classified_cases: List[Dict[str, Any]], 
        dcas: List[Any],
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Generate allocation preview showing which DCA gets what cases.
        
        Args:
            classified_cases: List of cases with risk_level assigned
            dcas: List of DCA objects (from database)
            db: Optional database session for capacity checks
            
        Returns:
            Allocation preview with summary statistics
        """
        if not dcas:
            return {
                'success': False,
                'error': 'No active DCAs available for allocation',
                'allocation_preview': [],
                'summary': {}
            }
        
        # Rank DCAs by performance
        ranked_dcas = self._rank_dcas_by_performance(dcas, db)
        
        # Separate cases by risk level
        high_risk_cases = [c for c in classified_cases if c.get('risk_level') == 'high']
        intermediate_cases = [c for c in classified_cases if c.get('risk_level') == 'intermediate']
        low_risk_cases = [c for c in classified_cases if c.get('risk_level') == 'low']
        
        # Get DCA tiers
        dca_tiers = self._get_dca_tiers(ranked_dcas)
        
        # Allocate cases to DCAs
        allocation_map = {}
        
        # High risk → Top performing DCAs
        allocation_map = self._allocate_to_tier(
            high_risk_cases, 
            dca_tiers['top'], 
            allocation_map, 
            'high',
            db
        )
        
        # Intermediate risk → Mid performing DCAs
        allocation_map = self._allocate_to_tier(
            intermediate_cases, 
            dca_tiers['mid'], 
            allocation_map, 
            'intermediate',
            db
        )
        
        # Low risk → Lower performing DCAs
        allocation_map = self._allocate_to_tier(
            low_risk_cases, 
            dca_tiers['lower'], 
            allocation_map, 
            'low',
            db
        )
        
        # Generate preview response
        allocation_preview = self._generate_preview(allocation_map, ranked_dcas)
        summary = self._generate_summary(classified_cases, allocation_preview)
        
        return {
            'success': True,
            'allocation_preview': allocation_preview,
            'summary': summary,
            'total_cases': len(classified_cases),
            'preview_timestamp': datetime.now().isoformat()
        }
    
    def confirm_allocation(
        self,
        allocation_preview: List[Dict[str, Any]],
        cases: List[Dict[str, Any]],
        db: Session,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Confirm and execute the allocation after user consent.
        
        Args:
            allocation_preview: The approved allocation preview
            cases: Original case data with IDs
            db: Database session
            user_id: User performing the allocation
            
        Returns:
            Allocation result with success/failure counts
        """
        from app.models.case import Case, CaseStatus
        
        allocated = []
        failed = []
        
        # Create case lookup by account_id or a unique identifier
        case_lookup = {c.get('account_id', c.get('id', str(i))): c 
                      for i, c in enumerate(cases)}
        
        for preview in allocation_preview:
            dca_id = preview['dca_id']
            assigned_cases = preview.get('assigned_case_ids', [])
            
            for case_identifier in assigned_cases:
                try:
                    # Find case in database
                    case = db.query(Case).filter(
                        Case.account_id == case_identifier
                    ).first()
                    
                    if case:
                        case.dca_id = dca_id
                        case.status = CaseStatus.ALLOCATED
                        case.allocated_by = user_id
                        case.allocation_date = datetime.now()
                        
                        # Store risk classification in ML features
                        original_case = case_lookup.get(case_identifier, {})
                        case.ml_features = {
                            'risk_level': original_case.get('risk_level'),
                            'risk_score': original_case.get('risk_score'),
                            'allocation_method': 'smart_risk_based'
                        }
                        
                        allocated.append(case_identifier)
                    else:
                        failed.append({
                            'case_id': case_identifier,
                            'reason': 'Case not found in database'
                        })
                except Exception as e:
                    failed.append({
                        'case_id': case_identifier,
                        'reason': str(e)
                    })
        
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            return {
                'success': False,
                'error': f'Database commit failed: {str(e)}',
                'allocated': [],
                'failed': [{'case_id': 'all', 'reason': str(e)}]
            }
        
        return {
            'success': True,
            'allocated_count': len(allocated),
            'failed_count': len(failed),
            'allocated': allocated,
            'failed': failed,
            'allocation_timestamp': datetime.now().isoformat()
        }
    
    def _rank_dcas_by_performance(
        self, 
# TODO: implement edge case handling
