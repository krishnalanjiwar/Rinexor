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
        "credit_score": 580,
        "employment_months": 6
    },
    {
        "account_id": "ACC-1003",
        "debtor_name": "Robert Johnson",
        "original_amount": 42000.00,
        "days_delinquent": 30,
        "debt_type": "mortgage",
        "credit_score": 800,
        "employment_months": 120
    }
]

print("\n1. Testing Single Case Analysis...")
print("-" * 40)

for i, case in enumerate(test_cases[:1]):  # Test first case only
    print(f"\n📊 Analyzing Case {i+1}: {case['account_id']}")
    result = ai_service.analyze_case(case)
    
    print(f"   Recovery Score: {result['recovery_score']}/100")
    print(f"   Priority Level: {result['priority_level']}")
    print(f"   Expected Recovery: ${result['expected_recovery_value']:,.2f}")
    print(f"   AI Confidence: {result['ai_insights']['ai_confidence']}")
    
    print(f"\n   🔑 Key Factors: {', '.join(result['ai_insights']['key_factors'])}")
    print(f"   ⚠️  Risk Factors: {', '.join(result['ai_insights']['risk_factors'])}")
    print(f"   🎯 Recommended: {result['ai_insights']['recommended_strategy']}")

print("\n2. Testing Portfolio Analysis...")
print("-" * 40)

portfolio_result = ai_service.analyze_portfolio(test_cases)
# TODO: implement edge case handling
