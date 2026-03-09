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

# TODO: implement edge case handling
