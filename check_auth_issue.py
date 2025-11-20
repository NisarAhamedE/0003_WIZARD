"""
Quick diagnostic to check if the wizard-runs endpoint is accessible
"""
import requests
import sys

# First, check if backend is running
try:
    print("Testing backend health...")
    response = requests.get("http://localhost:8000/docs", timeout=2)
    print(f"[OK] Backend is running (Status: {response.status_code})")
except Exception as e:
    print(f"[ERROR] Backend is not accessible: {e}")
    sys.exit(1)

# Test the wizard-runs endpoint without auth (should fail with 401)
print("\nTesting wizard-runs endpoint without authentication...")
try:
    response = requests.get("http://localhost:8000/api/v1/wizard-runs?skip=0&limit=1000")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    if response.status_code == 401:
        print("\n[OK] Endpoint requires authentication (expected)")
        print("This means the error in the browser is likely due to:")
        print("  1. Expired or missing authentication token")
        print("  2. Token not being sent correctly")
        print("\nSOLUTION: The user needs to log out and log back in")
    elif response.status_code == 200:
        print("\n[ERROR] Endpoint returned 200 without auth (unexpected)")
        print("This suggests the endpoint is not properly secured")
except Exception as e:
    print(f"Error: {e}")
