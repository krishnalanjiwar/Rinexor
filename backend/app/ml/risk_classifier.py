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
# TODO: implement edge case handling
