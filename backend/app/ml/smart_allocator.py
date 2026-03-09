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
        dcas: List[Any], 
        db: Optional[Session] = None
    ) -> List[Dict[str, Any]]:
        """Rank DCAs by composite performance score"""
        ranked = []
        
        for dca in dcas:
            # Calculate composite score
            performance = getattr(dca, 'performance_score', 0) or 0
            recovery_rate = getattr(dca, 'recovery_rate', 0) or 0
            sla_compliance = getattr(dca, 'sla_compliance_rate', 0) or 0
            
            # Weighted composite score
            composite_score = (
                performance * 0.40 +
                recovery_rate * 0.40 +
                sla_compliance * 0.20
            )
            
            # Get capacity info
            max_capacity = getattr(dca, 'max_concurrent_cases', 50)
            current_cases = getattr(dca, 'current_active_cases', 0)
            available_capacity = max_capacity - current_cases
            
            if available_capacity > 0:  # Only include DCAs with capacity
                ranked.append({
                    'dca_id': dca.id,
                    'dca_name': dca.name,
                    'dca_code': getattr(dca, 'code', ''),
                    'performance_score': round(performance, 3),
                    'recovery_rate': round(recovery_rate, 3),
                    'sla_compliance': round(sla_compliance, 3),
                    'composite_score': round(composite_score, 3),
                    'available_capacity': available_capacity,
                    'max_capacity': max_capacity
                })
        
        # Sort by composite score (highest first)
        ranked.sort(key=lambda x: x['composite_score'], reverse=True)
        
        return ranked
    
    def _get_dca_tiers(self, ranked_dcas: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """Split DCAs into performance tiers"""
        n = len(ranked_dcas)
        
        if n == 0:
            return {'top': [], 'mid': [], 'lower': []}
        
        # Calculate tier boundaries
        top_count = max(1, int(n * 0.3))      # Top 30%
        lower_count = max(1, int(n * 0.3))    # Bottom 30%
        mid_count = n - top_count - lower_count  # Rest
        
        return {
            'top': ranked_dcas[:top_count],
            'mid': ranked_dcas[top_count:top_count + mid_count] if mid_count > 0 else ranked_dcas[:1],
            'lower': ranked_dcas[-lower_count:] if lower_count > 0 else ranked_dcas[-1:]
        }
    
    def _allocate_to_tier(
        self,
        cases: List[Dict[str, Any]],
        tier_dcas: List[Dict[str, Any]],
        allocation_map: Dict[str, Dict],
        risk_level: str,
        db: Optional[Session] = None
    ) -> Dict[str, Dict]:
        """Allocate cases to DCAs in a specific tier using round-robin"""
        if not cases or not tier_dcas:
            return allocation_map
        
        dca_index = 0
        remaining_capacity = {d['dca_id']: d['available_capacity'] for d in tier_dcas}
        
        for case in cases:
            # Find DCA with capacity
            attempts = 0
            while attempts < len(tier_dcas):
                dca = tier_dcas[dca_index % len(tier_dcas)]
                dca_id = dca['dca_id']
                
                if remaining_capacity.get(dca_id, 0) > 0:
                    # Initialize allocation entry if not exists
                    if dca_id not in allocation_map:
                        allocation_map[dca_id] = {
                            'dca_info': dca,
                            'cases': [],
                            'risk_levels': {}
                        }
                    
                    # Add case to allocation
                    allocation_map[dca_id]['cases'].append(case)
                    
                    # Track risk level counts
                    if risk_level not in allocation_map[dca_id]['risk_levels']:
                        allocation_map[dca_id]['risk_levels'][risk_level] = []
                    allocation_map[dca_id]['risk_levels'][risk_level].append(case)
                    
                    # Decrease capacity
                    remaining_capacity[dca_id] -= 1
                    
                    break
                
                dca_index += 1
                attempts += 1
            
            dca_index += 1  # Move to next DCA for round-robin
        
        return allocation_map
    
    def _generate_preview(
        self, 
        allocation_map: Dict[str, Dict], 
        ranked_dcas: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate allocation preview list"""
        preview = []
        
        for dca_id, data in allocation_map.items():
            dca_info = data['dca_info']
            cases = data['cases']
            risk_levels = data['risk_levels']
            
            total_amount = sum(c.get('original_amount', 0) for c in cases)
            
            preview_item = {
                'dca_id': dca_id,
                'dca_name': dca_info['dca_name'],
                'dca_code': dca_info.get('dca_code', ''),
                'performance_score': dca_info['performance_score'],
                'recovery_rate': dca_info['recovery_rate'],
                'assigned_cases': len(cases),
                'amount_to_recover': round(total_amount, 2),
                'risk_breakdown': {
                    level: len(risk_cases) 
                    for level, risk_cases in risk_levels.items()
                },
                'assigned_case_ids': [
                    c.get('account_id', c.get('id', '')) for c in cases
                ]
            }
            
            preview.append(preview_item)
        
        # Sort by performance score (highest first)
        preview.sort(key=lambda x: x['performance_score'], reverse=True)
        
        return preview
    
    def _generate_summary(
        self, 
        classified_cases: List[Dict[str, Any]],
        allocation_preview: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate summary statistics"""
        total_cases = len(classified_cases)
        total_amount = sum(c.get('original_amount', 0) for c in classified_cases)
        
        # Count by risk level
        high_risk = [c for c in classified_cases if c.get('risk_level') == 'high']
        intermediate = [c for c in classified_cases if c.get('risk_level') == 'intermediate']
        low_risk = [c for c in classified_cases if c.get('risk_level') == 'low']
        
        summary = {
            'total_cases': total_cases,
            'total_amount': round(total_amount, 2),
            'total_dcas_assigned': len(allocation_preview),
            'risk_summary': {
                'high': {
                    'count': len(high_risk),
                    'percentage': round((len(high_risk) / total_cases) * 100, 1) if total_cases > 0 else 0,
                    'amount': round(sum(c.get('original_amount', 0) for c in high_risk), 2)
                },
                'intermediate': {
                    'count': len(intermediate),
                    'percentage': round((len(intermediate) / total_cases) * 100, 1) if total_cases > 0 else 0,
                    'amount': round(sum(c.get('original_amount', 0) for c in intermediate), 2)
                },
                'low': {
                    'count': len(low_risk),
                    'percentage': round((len(low_risk) / total_cases) * 100, 1) if total_cases > 0 else 0,
                    'amount': round(sum(c.get('original_amount', 0) for c in low_risk), 2)
                }
            },
            'dca_summary': [
                {
                    'dca_name': p['dca_name'],
                    'cases': p['assigned_cases'],
                    'amount': p['amount_to_recover']
                } for p in allocation_preview
            ]
# TODO: implement edge case handling
