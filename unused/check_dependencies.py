"""
Check if dependencies exist on the wizard
"""
import requests

BASE_URL = "http://localhost:8000/api/v1"
WIZARD_ID = "d80c65de-4b1f-4c02-926a-50cc1a1a7a90"

# Login
login_response = requests.post(f"{BASE_URL}/auth/login", data={
    "username": "admin",
    "password": "Admin@123"
})
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get wizard
wizard = requests.get(f"{BASE_URL}/wizards/{WIZARD_ID}", headers=headers).json()

print("Checking dependencies on wizard:")
print(f"Wizard: {wizard['name']}\n")

total_deps = 0
for step in wizard['steps']:
    print(f"STEP: {step['name']}")
    for os in step['option_sets']:
        print(f"  Option Set: {os['name']} ({os['selection_type']})")
        for opt in os['options']:
            deps = opt.get('dependencies', [])
            if deps:
                print(f"    [OK] {opt['label']} has {len(deps)} dependency(ies):")
                for dep in deps:
                    print(f"      - {dep['dependency_type']}: depends on option {dep['depends_on_option_id']}")
                    total_deps += 1
            else:
                print(f"    - {opt['label']}: No dependencies")
    print()

print(f"\nTotal dependencies found: {total_deps}")

if total_deps == 0:
    print("\n[WARNING] No dependencies found!")
    print("The dependencies may not have been added correctly.")
    print("\nRun: python add_dependencies.py")
else:
    print(f"\n[OK] {total_deps} dependencies are configured")
