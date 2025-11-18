"""
Test that simulates adding a dependency through UI and verifying it saves
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Login
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "admin", "password": "Admin@123"}
)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

print("=" * 60)
print("Testing Dependency Save Through UI Flow")
print("=" * 60)

# Get a wizard
response = requests.get(f"{BASE_URL}/wizards/?published_only=false&limit=1", headers=headers)
wizards = response.json()
wizard_id = wizards[0]['id']
wizard_name = wizards[0]['name']

print(f"\n1. Testing with wizard: {wizard_name}")
print(f"   Wizard ID: {wizard_id}")

# Get full wizard
response = requests.get(f"{BASE_URL}/wizards/{wizard_id}", headers=headers)
wizard = response.json()

print(f"\n2. Wizard loaded:")
print(f"   Steps: {len(wizard['steps'])}")
print(f"   Total options: {sum(len(os['options']) for step in wizard['steps'] for os in step['option_sets'])}")

# Count current dependencies
current_dep_count = sum(
    len(opt.get('dependencies', []))
    for step in wizard['steps']
    for os in step['option_sets']
    for opt in os['options']
)
print(f"   Current dependencies: {current_dep_count}")

# Try to add a new dependency
if len(wizard['steps']) >= 2:
    option1 = wizard['steps'][0]['option_sets'][0]['options'][0]
    option2 = wizard['steps'][1]['option_sets'][0]['options'][0]

    print(f"\n3. Adding dependency:")
    print(f"   Option: {option2['label']} (step 2)")
    print(f"   Depends on: {option1['label']} (step 1)")
    print(f"   Type: show_if")

    # Check if dependency already exists
    existing = any(
        dep['depends_on_option_id'] == option1['id'] and dep['dependency_type'] == 'show_if'
        for dep in option2.get('dependencies', [])
    )

    if existing:
        print("   [SKIP] Dependency already exists")
    else:
        # Add dependency
        dep_data = {
            "depends_on_option_id": option1['id'],
            "dependency_type": "show_if"
        }

        response = requests.post(
            f"{BASE_URL}/wizards/options/{option2['id']}/dependencies",
            headers=headers,
            json=dep_data
        )

        if response.status_code == 201:
            print("   [SUCCESS] Dependency created via API")
            new_dep = response.json()
            print(f"   Dependency ID: {new_dep['id']}")

            # Reload wizard and verify
            response = requests.get(f"{BASE_URL}/wizards/{wizard_id}", headers=headers)
            wizard_reloaded = response.json()

            # Find the option again
            reloaded_option = next(
                opt for step in wizard_reloaded['steps']
                for os in step['option_sets']
                for opt in os['options']
                if opt['id'] == option2['id']
            )

            if any(dep['id'] == new_dep['id'] for dep in reloaded_option['dependencies']):
                print("   [VERIFIED] Dependency persisted in database")
                print("   [VERIFIED] Dependency returned in wizard GET response")
                print("\n" + "=" * 60)
                print("[SUCCESS] Dependency save workflow is working!")
                print("=" * 60)
            else:
                print("   [FAILED] Dependency not found after reload")
        else:
            print(f"   [FAILED] API returned {response.status_code}")
            print(f"   Response: {response.text}")
else:
    print("\n[SKIP] Wizard needs at least 2 steps for testing")

# Show final dependency count
response = requests.get(f"{BASE_URL}/wizards/{wizard_id}", headers=headers)
wizard_final = response.json()
final_dep_count = sum(
    len(opt.get('dependencies', []))
    for step in wizard_final['steps']
    for os in step['option_sets']
    for opt in os['options']
)
print(f"\n4. Final dependency count: {final_dep_count}")

if final_dep_count > current_dep_count:
    print(f"   (+{final_dep_count - current_dep_count} new dependencies)")
