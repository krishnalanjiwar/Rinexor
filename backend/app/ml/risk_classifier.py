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
        
        return {
            'risk_level': risk_level,
            'risk_score': round(risk_score, 2),
            'recovery_probability': round(recovery_prob, 4),
            'confidence': confidence,
            'explanation': explanation,
            'factors': self._get_risk_factors(case_data)
        }
    
    def classify_batch(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Classify multiple cases and return distribution statistics.
        
        Returns:
            Dict with classified cases and risk distribution summary
        """
        classified_cases = []
        
        for case in cases:
            classification = self.classify_case(case)
            classified_case = {**case, **classification}
            classified_cases.append(classified_case)
        
        # Calculate distribution
        distribution = self._calculate_distribution(classified_cases)
        
        return {
            'total_cases': len(cases),
            'classified_cases': classified_cases,
            'risk_distribution': distribution,
            'classification_timestamp': datetime.now().isoformat()
        }
    
    def _calculate_risk_score(self, case_data: Dict[str, Any]) -> float:
        """
        Calculate risk score (0-100) based on case features.
        Higher score = Higher risk (harder to recover)
        """
        risk_score = 0.0
        
        # 1. Days Delinquent (30% weight)
        days_delinquent = case_data.get('days_delinquent', 0)
        if days_delinquent > 180:
            delinquency_risk = 100
        elif days_delinquent > 120:
            delinquency_risk = 80
        elif days_delinquent > 90:
            delinquency_risk = 60
        elif days_delinquent > 60:
            delinquency_risk = 45
        elif days_delinquent > 30:
            delinquency_risk = 30
        else:
            delinquency_risk = 15
        risk_score += delinquency_risk * 0.30
        
        # 2. Original Amount (25% weight) - Larger amounts are harder to recover
        amount = case_data.get('original_amount', 0)
        if amount > 100000:
            amount_risk = 90
        elif amount > 50000:
            amount_risk = 75
        elif amount > 25000:
            amount_risk = 55
        elif amount > 10000:
            amount_risk = 40
        elif amount > 5000:
            amount_risk = 25
        else:
            amount_risk = 15
        risk_score += amount_risk * 0.25
        
        # 3. Credit Score (20% weight) - Lower credit = higher risk
        credit_score = case_data.get('credit_score', 650)
        if credit_score < 500:
            credit_risk = 95
        elif credit_score < 580:
            credit_risk = 75
        elif credit_score < 650:
            credit_risk = 55
        elif credit_score < 700:
            credit_risk = 35
        elif credit_score < 750:
            credit_risk = 20
        else:
            credit_risk = 10
        risk_score += credit_risk * 0.20
        
        # 4. Debt Age Severity (15% weight)
        debt_age_days = case_data.get('debt_age_days', days_delinquent)
        age_severity = min(debt_age_days / 365, 1.0) * 100  # Cap at 1 year
        risk_score += age_severity * 0.15
        
        # 5. Amount to Income Ratio (10% weight)
        debt_to_income = case_data.get('debt_to_income', 0.3)
        dti_risk = min(debt_to_income * 100, 100)  # Cap at 100%
        risk_score += dti_risk * 0.10
        
        return min(100, max(0, risk_score))
    
    def _get_risk_level(self, recovery_prob: float) -> str:
        """Determine risk level from recovery probability"""
        if recovery_prob <= 0.39:
            return RiskLevel.HIGH
        elif recovery_prob <= 0.69:
            return RiskLevel.INTERMEDIATE
        else:
            return RiskLevel.LOW
    
    def _calculate_confidence(self, risk_score: float) -> str:
        """Calculate classification confidence"""
        # Higher confidence when score is clearly in a band
        if risk_score < 25 or risk_score > 75:
            return 'high'
        elif risk_score < 35 or risk_score > 65:
            return 'medium'
        else:
            return 'low'  # Near threshold boundaries
    
    def _generate_explanation(self, case_data: Dict[str, Any], 
                            risk_level: str, risk_score: float) -> str:
        """Generate human-readable explanation for classification"""
        days = case_data.get('days_delinquent', 0)
        amount = case_data.get('original_amount', 0)
        
        if risk_level == RiskLevel.HIGH:
            if days > 120:
                return f"High risk due to extended delinquency ({days} days) and amount (${amount:,.2f})"
            elif amount > 50000:
                return f"High risk due to large debt amount (${amount:,.2f})"
            else:
                return "High risk based on combined factors indicating difficulty in recovery"
        elif risk_level == RiskLevel.INTERMEDIATE:
            return f"Moderate risk with {days} days delinquent and ${amount:,.2f} debt"
        else:
            return f"Lower risk case with reasonable recovery potential"
    
    def _get_risk_factors(self, case_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get individual risk factors with their contributions"""
        days = case_data.get('days_delinquent', 0)
        amount = case_data.get('original_amount', 0)
        credit = case_data.get('credit_score', 650)
        
        factors = []
        
        if days > 90:
            factors.append({
                'factor': 'Delinquency Duration',
                'value': f'{days} days',
                'impact': 'high',
# TODO: implement edge case handling
