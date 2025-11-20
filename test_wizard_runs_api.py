"""
Test script to diagnose wizard runs API issue
"""
import requests
import json

# Test 1: Check backend health
print("=" * 60)
print("Test 1: Backend Health Check")
print("=" * 60)
try:
    response = requests.get("http://localhost:8000/api/v1/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Login and get token
print("\n" + "=" * 60)
print("Test 2: Login and Get Auth Token")
print("=" * 60)
try:
    login_data = {
        "username": "admin",  # Change to your test user
        "password": "admin123"  # Change to your test password
    }
    response = requests.post(
        "http://localhost:8000/api/v1/auth/login",
        data=login_data
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        print(f"Access Token: {access_token[:50]}...")

        # Test 3: Get wizard runs with token
        print("\n" + "=" * 60)
        print("Test 3: Get Wizard Runs")
        print("=" * 60)
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        runs_response = requests.get(
            "http://localhost:8000/api/v1/wizard-runs?skip=0&limit=1000",
            headers=headers
        )
        print(f"Status Code: {runs_response.status_code}")
        print(f"Response Headers: {dict(runs_response.headers)}")

        if runs_response.status_code == 200:
            data = runs_response.json()
            print(f"\nResponse Structure:")
            print(f"  - Has 'runs' key: {'runs' in data}")
            print(f"  - 'runs' is array: {isinstance(data.get('runs'), list)}")
            print(f"  - Total runs: {len(data.get('runs', []))}")
            print(f"  - Total count: {data.get('total')}")
            print(f"\nFull Response:")
            print(json.dumps(data, indent=2))
        else:
            print(f"Error Response: {runs_response.text}")
    else:
        print(f"Login failed: {response.text}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Diagnosis Complete")
print("=" * 60)
