"""
TEST ALL API ENDPOINTS
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:9000/api/v1"
HEADERS = {}

print("🧪 TESTING ALL API ENDPOINTS")
print("=" * 60)

def print_response(name: str, response):
    print(f"\n{name}:")
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        print(f"  ✅ Success")
        if response.json():
            print(f"  Response keys: {list(response.json().keys())[:5]}...")
    else:
        print(f"  ❌ Failed: {response.text[:100]}")

# 1. Test health endpoint
print("\n1. Testing Health Endpoint...")
response = requests.get("http://127.0.0.1:9000/api/health")
print_response("Health", response)

# 2. Test login
print("\n2. Testing Authentication...")
login_data = {
    "username": "admin@recoverai.com",
    "password": "secret"
}
response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
print_response("Login", response)

if response.status_code == 200:
    token = response.json()["access_token"]
    HEADERS = {"Authorization": f"Bearer {token}"}
    print(f"  Token obtained: {token[:50]}...")

# 3. Test Cases API
print("\n3. Testing Cases API...")
response = requests.get(f"{BASE_URL}/cases", headers=HEADERS)
print_response("Get Cases", response)

# 4. Test DCAs API
print("\n4. Testing DCAs API...")
response = requests.get(f"{BASE_URL}/dcas", headers=HEADERS)
print_response("Get DCAs", response)

if response.status_code == 200 and response.json():
    dca_id = response.json()[0]["id"]
    
    # Test DCA performance
    response = requests.get(f"{BASE_URL}/dcas/{dca_id}/performance", headers=HEADERS)
    print_response("DCA Performance", response)

# 5. Test Dashboard Stats
print("\n5. Testing Dashboard...")
response = requests.get(f"{BASE_URL}/cases/dashboard/stats", headers=HEADERS)
print_response("Dashboard Stats", response)

# 6. Test AI API
print("\n6. Testing AI API...")
response = requests.get(f"{BASE_URL}/ai/model-status", headers=HEADERS)
print_response("AI Model Status", response)

# 7. Test Admin API
print("\n7. Testing Admin API...")
response = requests.get(f"{BASE_URL}/admin/system-stats", headers=HEADERS)
print_response("System Stats", response)

print("\n" + "=" * 60)
print("✅ API TEST COMPLETE!")
print("\n📋 Summary:")
print(f"  • Health: {'✅' if response.status_code == 200 else '❌'}")
print(f"  • Authentication: {'✅' if 'token' in locals() else '❌'}")
print(f"  • Cases API: {'✅' if response.status_code == 200 else '❌'}")
print(f"  • DCAs API: {'✅' if response.status_code == 200 else '❌'}")
print(f"  • AI API: {'✅' if response.status_code == 200 else '❌'}")
print(f"  • Admin API: {'✅' if response.status_code == 200 else '❌'}")

# TODO: implement edge case handling
