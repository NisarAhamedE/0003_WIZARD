"""
Add conditional dependencies to the test wizards
"""
import requests

BASE_URL = "http://localhost:8000/api/v1"
WIZARD_ID = "d80c65de-4b1f-4c02-926a-50cc1a1a7a90"  # Wizard 2 with dependencies

# Login as admin
print("Logging in as admin...")
login_response = requests.post(f"{BASE_URL}/auth/login", data={
    "username": "admin",
    "password": "Admin@123"
})
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get wizard details
print(f"\nFetching wizard {WIZARD_ID}...")
wizard = requests.get(f"{BASE_URL}/wizards/{WIZARD_ID}", headers=headers).json()

# Build option ID map
option_map = {}
for step in wizard['steps']:
    print(f"\nStep: {step['name']}")
    for os in step['option_sets']:
        print(f"  Option Set: {os['name']} ({os['selection_type']})")
        for opt in os['options']:
            key = f"{os['name']}:{opt['value']}"
            option_map[key] = opt['id']
            print(f"    - {opt['label']} = {opt['id']}")

print("\n" + "="*60)
print("Adding Dependencies")
print("="*60)

dependencies_to_add = []

# Dependency 1: Disable "Your Name" if "existing customer" is selected
name_key = "Your Name:customer_name"
existing_key = "Are you a new customer?:existing"
if name_key in option_map and existing_key in option_map:
    dependencies_to_add.append({
        "option_id": option_map[name_key],
        "depends_on_option_id": option_map[existing_key],
        "dependency_type": "disable_if",
        "description": "Disable name field for existing customers"
    })
    print(f"\n1. Disable 'Your Name' if 'existing customer' selected")
    print(f"   Option ID: {option_map[name_key]}")
    print(f"   Depends on: {option_map[existing_key]}")

# Dependency 2: Require "Upload Document" if "new customer" is selected
upload_key = "Upload Document:upload_doc"
new_key = "Are you a new customer?:new"
if upload_key in option_map and new_key in option_map:
    dependencies_to_add.append({
        "option_id": option_map[upload_key],
        "depends_on_option_id": option_map[new_key],
        "dependency_type": "require_if",
        "description": "Require document upload for new customers"
    })
    print(f"\n2. Require 'Upload Document' if 'new customer' selected")
    print(f"   Option ID: {option_map[upload_key]}")
    print(f"   Depends on: {option_map[new_key]}")

# Add dependencies using correct endpoint
print("\n" + "="*60)
print("Creating Dependencies")
print("="*60)

dep_count = 0
for dep in dependencies_to_add:
    option_id = dep.pop("option_id")
    description = dep.pop("description")

    print(f"\nAdding: {description}")
    print(f"  Endpoint: /wizards/options/{option_id}/dependencies")
    print(f"  Data: {dep}")

    dep_response = requests.post(
        f"{BASE_URL}/wizards/options/{option_id}/dependencies",
        json=dep,
        headers=headers
    )

    if dep_response.status_code in [200, 201]:
        print(f"  [SUCCESS] Dependency added")
        dep_count += 1
    else:
        print(f"  [ERROR] Failed: {dep_response.status_code}")
        print(f"  Response: {dep_response.text}")

print("\n" + "="*60)
print(f"COMPLETE! Added {dep_count}/{len(dependencies_to_add)} dependencies")
print("="*60)
print(f"\nTest the wizard at:")
print(f"http://localhost:3000/wizard/{WIZARD_ID}")
print("\nTest the dependencies:")
print("1. Select 'No, I'm existing' -> Name field should be disabled")
print("2. Select 'Yes, I'm new' -> Document upload should show red asterisk (required)")
