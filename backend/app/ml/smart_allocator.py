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
# TODO: implement edge case handling
