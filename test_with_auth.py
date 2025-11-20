"""
Test protection endpoint with authentication
"""
import requests

# First login to get a token
print("1. Logging in...")
login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    data={
        "username": "admin",
        "password": "admin123"
    }
)

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    print(f"   [OK] Logged in successfully")
    print(f"   Token: {token[:50]}...")

    # Now test the protection endpoint
    wizard_id = "504c3d07-a1c2-4f9a-b8f7-4b8e94c863c5"
    print(f"\n2. Testing protection endpoint for wizard {wizard_id}...")

    response = requests.get(
        f"http://localhost:8000/api/v1/wizards/{wizard_id}/protection-status",
        headers={"Authorization": f"Bearer {token}"}
    )

    print(f"   Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\n   [SUCCESS] Protection endpoint working!")
        print(f"   State: {data.get('state')}")
        print(f"   Can Edit: {data.get('can_edit')}")
        print(f"   Can Delete: {data.get('can_delete')}")
        print(f"   Total Runs: {data.get('total_runs')}")
        print(f"   Stored Runs: {data.get('stored_runs')}")
        print(f"   Message: {data.get('message')}")
    else:
        print(f"   [ERROR] {response.text}")

else:
    print(f"   [ERROR] Login failed: {login_response.status_code}")
    print(f"   Response: {login_response.text}")
