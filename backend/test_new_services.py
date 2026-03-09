#!/usr/bin/env python3
"""
Quick test script for new services
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.services.workflow_service import WorkflowService
from app.services.allocation_service import AllocationService
from app.services.notification_service import NotificationService
from app.task.sla_tasks import SLAMonitoringTasks

def test_workflow_service():
    """Test WorkflowService"""
    print("🔧 Testing WorkflowService...")
    
    # Test case processing
    case_data = {
        "original_amount": 25000,
        "days_delinquent": 45,
        "debt_type": "credit_card"
    }
    
    # Mock database session
    class MockDB:
        def query(self, model):
            return MockQuery()
        def commit(self):
            pass
        def add(self, obj):
            pass
    
    class MockQuery:
        def filter(self, *args):
            return self
        def all(self):
            return []
        def first(self):
            return None
    
    db = MockDB()
    
    try:
        result = WorkflowService.process_new_case(case_data, db)
        print(f"✅ WorkflowService.process_new_case: {result}")
        
        # Test SLA breach checking
        breaches = WorkflowService.check_sla_breaches(db)
        print(f"✅ WorkflowService.check_sla_breaches: {len(breaches)} breaches found")
        
    except Exception as e:
        print(f"❌ WorkflowService error: {e}")

def test_allocation_service():
    """Test AllocationService"""
    print("\n🎯 Testing AllocationService...")
    
    try:
        # Test DCA scoring
        case_data = {
            "original_amount": 15000,
            "days_delinquent": 30,
            "debt_type": "personal_loan"
# TODO: implement edge case handling
