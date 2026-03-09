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
print(f"   Total Cases Analyzed: {portfolio_result['total_cases_analyzed']}")
print(f"   Expected Total Recovery: ${portfolio_result['batch_analysis'].get('expected_recovery', 0):,.2f}")
print(f"   Recovery Rate: {portfolio_result['batch_analysis']['expected_recovery_rate']}%")
print(f"   Patterns Detected: {portfolio_result['pattern_analysis']['patterns_detected']}")

print("\n3. Testing Priority Engine...")
print("-" * 40)

print("   Top Priority Cases:")
for i, case in enumerate(portfolio_result['top_priority_cases'][:3]):
    print(f"   {i+1}. {case['account_id']} - ${case['original_amount']:,.2f} "
          f"({case['priority_level'].upper()}) - Score: {case['priority_score']}")

print("\n4. Training Demo (Mock)...")
print("-" * 40)

# Mock training data
mock_training_data = test_cases * 5  # Repeat to get more data
for data in mock_training_data:
    data['recovery_rate'] = 0.7  # Mock recovery rate

training_result = ai_service.train_model(mock_training_data)
print(f"   Training Success: {training_result['success']}")
if training_result['success']:
    print(f"   Samples Trained: {training_result['samples_trained']}")
    print(f"   Model Saved: {training_result['model_saved']}")

print("\n" + "=" * 60)
print("✅ AI/ML TEST COMPLETE!")
print("\n🎯 Ready Features:")
print("   1. Intelligent Recovery Prediction")
print("   2. Smart Case Prioritization")
print("   3. Pattern Detection & Insights")
print("   4. Portfolio-level Analysis")
print("   5. Explainable AI (Key Factors, Risks)")
print("   6. Model Training Capability")