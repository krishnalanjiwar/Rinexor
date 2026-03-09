"""
TEST AI/ML IMPLEMENTATION
"""
import sys
import os
sys.path.append(os.getcwd())

from app.services.ai_service import AIService
import json

print("🧠 TESTING AI/ML IMPLEMENTATION")
print("=" * 60)

# Initialize AI service
ai_service = AIService()
ai_service.initialize()

# Test case data
test_cases = [
    {
        "account_id": "ACC-1001",
        "debtor_name": "John Smith",
        "original_amount": 25000.00,
        "days_delinquent": 60,
        "debt_type": "credit_card",
        "credit_score": 720,
        "employment_months": 36
    },
    {
        "account_id": "ACC-1002", 
        "debtor_name": "Maria Garcia",
        "original_amount": 8500.00,
        "days_delinquent": 120,
        "debt_type": "medical",
# TODO: implement edge case handling
