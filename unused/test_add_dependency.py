"""
Test adding a single dependency
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Get token
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "admin", "password": "Admin@123"}
)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# Get first wizard
response = requests.get(f"{BASE_URL}/wizards/?published_only=false&limit=1", headers=headers)
wizards = response.json()

if not wizards:
    print("No wizards found")
    exit()

wizard = wizards[0]
print(f"Testing with wizard: {wizard['name']}")

# Get full wizard details
response = requests.get(f"{BASE_URL}/wizards/{wizard['id']}", headers=headers)
wizard_full = response.json()

# Get first two options from different steps
try:
    step1_options = wizard_full['steps'][0]['option_sets'][0]['options']
    if len(wizard_full['steps']) < 2:
        print("Need at least 2 steps for testing")
        exit()
    step2_options = wizard_full['steps'][1]['option_sets'][0]['options']

    option1_id = step1_options[0]['id']
    option2_id = step2_options[0]['id']

    print(f"Option 1: {step1_options[0]['label']} (ID: {option1_id})")
    print(f"Option 2: {step2_options[0]['label']} (ID: {option2_id})")

    # Try to create a dependency: option2 shows if option1 is selected
    dependency_data = {
        "depends_on_option_id": option1_id,
        "dependency_type": "show_if"
    }

    print(f"\nAttempting to create dependency...")
    print(f"POST {BASE_URL}/wizards/options/{option2_id}/dependencies")
    print(f"Data: {json.dumps(dependency_data, indent=2)}")

    response = requests.post(
        f"{BASE_URL}/wizards/options/{option2_id}/dependencies",
        headers=headers,
        json=dependency_data
    )

    print(f"\nResponse status: {response.status_code}")
    print(f"Response body: {response.text}")

    if response.status_code == 201:
        print("\n[SUCCESS] Dependency created!")
        dep = response.json()
        print(f"Dependency ID: {dep['id']}")
    else:
        print(f"\n[FAILED] Status {response.status_code}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
