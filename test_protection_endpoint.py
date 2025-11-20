"""
Test the wizard protection endpoint
"""
import requests
import time

# Wait for backend to be ready
print("Waiting for backend to start...")
time.sleep(3)

# Test 1: Check backend health
print("\n1. Testing backend health...")
try:
    response = requests.get("http://localhost:8000/docs", timeout=5)
    print(f"   [OK] Backend is running (Status: {response.status_code})")
except Exception as e:
    print(f"   [ERROR] Backend not accessible: {e}")
    exit(1)

# Test 2: Get a wizard ID from the list
print("\n2. Getting wizard list...")
try:
    # This endpoint might require auth, but let's try
    response = requests.get("http://localhost:8000/api/v1/wizards", timeout=5)
    if response.status_code == 200:
        wizards = response.json()
        if wizards and len(wizards) > 0:
            wizard_id = wizards[0]['id']
            print(f"   [OK] Found wizard: {wizards[0]['name']} (ID: {wizard_id})")

            # Test 3: Test protection endpoint
            print(f"\n3. Testing protection endpoint...")
            prot_url = f"http://localhost:8000/api/v1/wizards/{wizard_id}/protection-status"
            print(f"   URL: {prot_url}")

            response = requests.get(prot_url, timeout=5)
            print(f"   Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"   [OK] Protection Status:")
                print(f"      - State: {data.get('state')}")
                print(f"      - Can Edit: {data.get('can_edit')}")
                print(f"      - Can Delete: {data.get('can_delete')}")
                print(f"      - Total Runs: {data.get('total_runs')}")
                print(f"      - Stored Runs: {data.get('stored_runs')}")
                print("\n   [SUCCESS] Protection endpoint is working!")
            elif response.status_code == 404:
                print(f"   [ERROR] 404 - Endpoint not found")
                print(f"   Response: {response.text}")
            elif response.status_code == 401:
                print(f"   [INFO] 401 - Requires authentication (expected for admin)")
            else:
                print(f"   [ERROR] Unexpected status: {response.status_code}")
                print(f"   Response: {response.text}")
        else:
            print(f"   [WARN] No wizards found in database")
    else:
        print(f"   [WARN] Wizards endpoint returned {response.status_code}")
        print(f"   Trying with first wizard ID from migration...")

        # Try with a known wizard ID
        wizard_id = "504c3d07-a1c2-4f9a-b8f7-4b8e94c863c5"
        print(f"\n3. Testing protection endpoint with ID: {wizard_id}")
        prot_url = f"http://localhost:8000/api/v1/wizards/{wizard_id}/protection-status"

        response = requests.get(prot_url, timeout=5)
        print(f"   Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Protection Status:")
            print(f"      - State: {data.get('state')}")
            print(f"      - Can Edit: {data.get('can_edit')}")
            print("\n   [SUCCESS] Protection endpoint is working!")
        elif response.status_code == 404:
            print(f"   [ERROR] 404 - Endpoint not found or wizard doesn't exist")
        elif response.status_code == 401:
            print(f"   [INFO] 401 - Requires authentication")
            print(f"   This is expected - the endpoint requires admin access")
            print(f"\n   [SUCCESS] Endpoint exists and requires auth (correct behavior)")
        else:
            print(f"   [ERROR] Unexpected status: {response.status_code}")
            print(f"   Response: {response.text}")

except Exception as e:
    print(f"   [ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("Backend Testing Complete")
print("="*60)
print("\nIf you see 401 errors, the endpoint exists and requires")
print("authentication. You need to test it from the frontend")
print("where you're logged in.")
print("\nNext: Refresh your browser (Ctrl+Shift+R) and test!")
