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
# TODO: implement edge case handling
