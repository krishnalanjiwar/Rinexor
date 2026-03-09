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
        
# TODO: implement edge case handling
