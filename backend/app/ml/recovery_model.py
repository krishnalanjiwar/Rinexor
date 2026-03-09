"""
ENHANCED RECOVERY PREDICTION MODEL
"""
import numpy as np
import pandas as pd
import pickle
from typing import Dict, Any, Tuple, Optional
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

class RecoveryModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.is_trained = False
        
    def train(self, X: pd.DataFrame, y: pd.Series, model_type: str = 'gradient_boosting'):
        """
        Train the recovery prediction model
        
        Args:
            X: Feature dataframe
            y: Target values (recovery rate 0-1)
            model_type: 'gradient_boosting', 'random_forest', or 'logistic'
        """
        self.feature_columns = X.columns.tolist()
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Choose model
        if model_type == 'gradient_boosting':
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
        elif model_type == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
        else:  # logistic regression (for binary classification)
            self.model = LogisticRegression(max_iter=1000)
        
        # Train
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Calculate training metrics
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        return {
            'model_type': model_type,
            'train_score': train_score,
            'test_score': test_score,
            'feature_importance': self.get_feature_importance()
        }
    
    def predict(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict recovery probability for a single case
        """
        if not self.is_trained:
            return self._predict_with_rule_based(case_data)
        
        try:
            from app.ml.feature_engineer import FeatureEngineer
            
            # Extract features
            features = FeatureEngineer.extract_features(case_data)
            
            # Create dataframe with same columns as training
            features_df = pd.DataFrame([features])
            
            # Ensure all columns exist
            for col in self.feature_columns:
                if col not in features_df.columns:
                    features_df[col] = 0
            
            # Reorder columns
            features_df = features_df[self.feature_columns]
            
            # Scale and predict
            features_scaled = self.scaler.transform(features_df)
            recovery_prob = float(self.model.predict(features_scaled)[0])
            
            # Ensure probability is between 0-1
            recovery_prob = max(0, min(1, recovery_prob))
            
            # Get confidence and explanation
            confidence = self._calculate_confidence(recovery_prob)
            explanation = self._generate_explanation(features, recovery_prob)
            
            return {
                'recovery_probability': recovery_prob,
                'recovery_score': round(recovery_prob * 100, 1),
                'confidence': confidence,
                'key_factors': explanation['key_factors'],
                'risk_factors': explanation['risk_factors'],
                'recommended_action': explanation['recommended_action']
            }
            
        except Exception as e:
            # Fallback to rule-based
            return self._predict_with_rule_based(case_data)
    
    def _predict_with_rule_based(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback rule-based prediction"""
        recovery_score = self._calculate_rule_based_score(case_data)
        recovery_prob = recovery_score / 100
        
        return {
            'recovery_probability': recovery_prob,
            'recovery_score': recovery_score,
            'confidence': 'medium',
            'key_factors': ['Amount', 'Days Delinquent'],
            'risk_factors': ['Using rule-based fallback'],
            'recommended_action': 'Standard collection process'
        }
    
    def _calculate_rule_based_score(self, case_data: Dict[str, Any]) -> float:
        """Simple rule-based scoring"""
        score = 70.0  # Base score
        
        # Rule 1: Debt age penalty
        days_delinquent = case_data.get("days_delinquent", 0)
        if days_delinquent > 180:
            score -= 40
        elif days_delinquent > 90:
            score -= 25
        elif days_delinquent > 60:
            score -= 15
        elif days_delinquent > 30:
            score -= 5
        
        # Rule 2: Amount penalty
        amount = case_data.get("original_amount", 0)
        if amount > 50000:
            score -= 30
        elif amount > 25000:
            score -= 20
        elif amount > 10000:
            score -= 10
        
        # Ensure score is between 0-100
        return max(0, min(100, round(score, 1)))
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from model"""
        if not self.is_trained or self.feature_columns is None:
            return {}
        
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
        elif hasattr(self.model, 'coef_'):
            importances = np.abs(self.model.coef_[0])
        else:
            return {}
        
        # Map to feature names
        importance_dict = dict(zip(self.feature_columns, importances))
        
        # Sort by importance
        sorted_importance = dict(sorted(
            importance_dict.items(), 
            key=lambda x: x[1], 
            reverse=True
        ))
        
        return sorted_importance
    
    def _calculate_confidence(self, probability: float) -> str:
        """Calculate prediction confidence"""
        if probability > 0.8 or probability < 0.2:
            return 'high'
        elif probability > 0.6 or probability < 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _generate_explanation(self, features: Dict[str, float], probability: float) -> Dict[str, Any]:
        """Generate human-readable explanation"""
        key_factors = []
        risk_factors = []
        
        # Analyze features
        if features.get('delinquency_severity', 0) > 0.7:
            risk_factors.append('Highly delinquent account')
        elif features.get('delinquency_severity', 0) < 0.3:
            key_factors.append('Recently delinquent')
        
        if features.get('amount_log', 0) > np.log1p(20000):
            risk_factors.append('High debt amount')
        
        if features.get('credit_score_norm', 0) > 0.7:
            key_factors.append('Good credit history')
        elif features.get('credit_score_norm', 0) < 0.5:
            risk_factors.append('Poor credit history')
        
        if features.get('employment_stability', 0) > 0.7:
            key_factors.append('Stable employment')
        
        # Determine recommended action
        if probability > 0.7:
            action = 'Aggressive collection - High recovery potential'
        elif probability > 0.4:
            action = 'Standard collection process'
        else:
            action = 'Consider settlement or write-off'
        
        return {
            'key_factors': key_factors[:3],  # Top 3 factors
            'risk_factors': risk_factors[:3],  # Top 3 risks
            'recommended_action': action
        }
    
    def save_model(self, filepath: str):
        """Save model to file"""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler,
                'feature_columns': self.feature_columns,
                'is_trained': self.is_trained
            }, f)
    
    def load_model(self, filepath: str):
        """Load model from file"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.scaler = data['scaler']
            self.feature_columns = data['feature_columns']
            self.is_trained = data['is_trained']