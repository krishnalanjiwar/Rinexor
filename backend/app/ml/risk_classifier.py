"""
RISK CLASSIFIER - ML model to classify cases into High/Intermediate/Low risk
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from datetime import datetime


class RiskLevel:
    """Risk level constants"""
    HIGH = "high"           # 0-39 recovery score (hardest to recover)
    INTERMEDIATE = "intermediate"  # 40-69 recovery score
    LOW = "low"             # 70-100 recovery score (easiest to recover)


class RiskClassifier:
    """
    Classifies cases into risk levels based on multiple factors.
    Risk is defined as difficulty to recover - High risk means harder to recover.
    """
    
    # Risk thresholds (based on recovery probability)
    THRESHOLDS = {
        'high': (0, 0.39),        # 0-39% recovery probability = HIGH risk
        'intermediate': (0.40, 0.69),  # 40-69% = INTERMEDIATE risk
        'low': (0.70, 1.0)        # 70-100% = LOW risk
    }
    
    def __init__(self):
        self.feature_weights = {
            'days_delinquent': 0.30,
            'amount': 0.25,
            'credit_score': 0.20,
            'debt_age_severity': 0.15,
            'amount_severity': 0.10
        }
    
    def classify_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify a single case into risk level.
        
        Returns:
            Dict with risk_level, risk_score, confidence, and explanation
        """
        # Calculate risk score (0-100, higher = harder to recover = higher risk)
        risk_score = self._calculate_risk_score(case_data)
        
        # Get recovery probability (inverse of risk)
        recovery_prob = 1 - (risk_score / 100)
        
        # Determine risk level based on recovery probability
        risk_level = self._get_risk_level(recovery_prob)
        
        # Calculate confidence
        confidence = self._calculate_confidence(risk_score)
        
        # Generate explanation
        explanation = self._generate_explanation(case_data, risk_level, risk_score)
        
# TODO: implement edge case handling
