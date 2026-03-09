"""
AI SERVICE - Main interface for all AI/ML capabilities
"""
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import io

def convert_numpy_types(obj):
    """Recursively convert numpy types to native Python types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(i) for i in obj]
    return obj

class AIService:
    def __init__(self):
        self.recovery_model = None
        self.priority_engine = None
        self.pattern_detector = None
        self.risk_classifier = None
        self.smart_allocator = None
        
    def initialize(self):
        """Initialize all AI components"""
        from app.ml.recovery_model import RecoveryModel
        from app.ml.priority_engine import PriorityEngine
        from app.ml.pattern_detector import PatternDetector
        from app.ml.feature_engineer import FeatureEngineer
        from app.ml.risk_classifier import RiskClassifier
        from app.ml.smart_allocator import SmartAllocator
        
        self.recovery_model = RecoveryModel()
        self.priority_engine = PriorityEngine()
        self.pattern_detector = PatternDetector()
        self.feature_engineer = FeatureEngineer()
        self.risk_classifier = RiskClassifier()
        self.smart_allocator = SmartAllocator()
        
        # Try to load pre-trained model
        try:
            import os
            model_path = "ml_models/recovery_model.pkl"
            if os.path.exists(model_path):
                self.recovery_model.load_model(model_path)
                print("✅ Loaded pre-trained AI model")
            else:
                print("⚠️  No pre-trained model found, using rule-based")
        except:
            print("⚠️  Could not load AI model, using rule-based")
    
    def analyze_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete AI analysis of a single case
        """
        # 1. Predict recovery
        recovery_prediction = self.recovery_model.predict(case_data)
        
        # 2. Calculate priority
        priority_info = self.priority_engine.calculate_priority_score(
            case_data, recovery_prediction['recovery_probability']
        )
        
        # 3. Generate AI insights
        insights = {
            'ai_confidence': recovery_prediction['confidence'],
            'key_factors': recovery_prediction.get('key_factors', []),
            'risk_factors': recovery_prediction.get('risk_factors', []),
            'recommended_strategy': recovery_prediction.get('recommended_action', ''),
            'expected_roi': priority_info.get('roi_score', 0)
        }
        
        return {
            **recovery_prediction,
            **priority_info,
            'ai_insights': insights,
            'timestamp': pd.Timestamp.now().isoformat()
        }
    
    def analyze_portfolio(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze entire portfolio of cases
        """
        # 1. Batch recovery prediction
        batch_prediction = self.pattern_detector.predict_batch_recovery(cases)
        
        # 2. Pattern detection
        patterns = self.pattern_detector.detect_recovery_patterns(cases)
        
        # 3. Prioritize all cases
        prioritized_cases = self.priority_engine.batch_prioritize(cases)
        
        # 4. Portfolio insights
        portfolio_insights = self._generate_portfolio_insights(prioritized_cases)
        
        return {
            'batch_analysis': batch_prediction,
            'pattern_analysis': patterns,
            'portfolio_insights': portfolio_insights,
            'top_priority_cases': prioritized_cases[:10],  # Top 10
            'total_cases_analyzed': len(cases),
            'analysis_timestamp': pd.Timestamp.now().isoformat()
        }
    
    def _generate_portfolio_insights(self, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate portfolio-level insights"""
        if not cases:
            return {}
        
        df = pd.DataFrame(cases)
        
        insights = {
            'high_priority_count': len(df[df['priority_level'] == 'high']),
            'medium_priority_count': len(df[df['priority_level'] == 'medium']),
            'low_priority_count': len(df[df['priority_level'] == 'low']),
            'avg_recovery_score': round(df['recovery_score'].mean(), 1),
            'total_expected_recovery': round(df.get('expected_recovery_value', 0).sum(), 2)
        }
        
        # Resource allocation recommendation
        high_priority_value = df[df['priority_level'] == 'high'].get('expected_recovery_value', 0).sum()
        total_value = df.get('expected_recovery_value', 0).sum()
        
        if total_value > 0:
            high_priority_percentage = (high_priority_value / total_value) * 100
            if high_priority_percentage > 60:
                insights['resource_recommendation'] = 'Focus 70% resources on high priority cases'
            elif high_priority_percentage > 30:
                insights['resource_recommendation'] = 'Balance resources across all priorities'
            else:
                insights['resource_recommendation'] = 'Spread resources, focus on volume'
        else:
            insights['resource_recommendation'] = 'Insufficient data for recommendation'
        
        return insights
    
    def train_model(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Train the AI model with new data
        """
        try:
            # Convert to dataframe
            df = pd.DataFrame(training_data)
            
            # Extract features
            X = self.feature_engineer.create_feature_dataframe(training_data)
            
            # Target variable (recovery rate)
            if 'recovery_rate' in df.columns:
                y = df['recovery_rate']
            else:
                # Mock target for demo
                y = pd.Series([0.7] * len(X))  # 70% average recovery
            
            # Train model
            result = self.recovery_model.train(X, y, model_type='gradient_boosting')
            
            # Save model
            import os
            os.makedirs('ml_models', exist_ok=True)
            self.recovery_model.save_model('ml_models/recovery_model.pkl')
            
            return {
                'success': True,
                'training_result': result,
                'model_saved': True,
                'samples_trained': len(X)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
# TODO: implement edge case handling
