"""
QUICK FIX FOR CIRCULAR IMPORTS
"""
import os

# Fix recovery_model.py
filepath = "app/ml/recovery_model.py"
if os.path.exists(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Replace the problematic import with direct implementation
    old_code = '''    def _predict_with_rule_based(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback rule-based prediction"""
        from app.services.workflow_service import WorkflowService
        
        recovery_score = WorkflowService.calculate_recovery_score(case_data)
        recovery_prob = recovery_score / 100
        
        return {
            'recovery_probability': recovery_prob,
            'recovery_score': recovery_score,
            'confidence': 'medium',
            'key_factors': ['Amount', 'Days Delinquent'],
            'risk_factors': ['Using rule-based fallback'],
            'recommended_action': 'Standard collection process'
        }'''
    
    new_code = '''    def _predict_with_rule_based(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback rule-based prediction"""
        recovery_score = self._calculate_rule_based_score(case_data)
# TODO: implement edge case handling
