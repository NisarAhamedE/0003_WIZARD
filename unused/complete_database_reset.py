"""
Complete database reset - Delete ALL wizards, sessions, and templates
"""
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Login as admin
print("Logging in as admin...")
login_response = requests.post(f"{BASE_URL}/auth/login", data={
    "username": "admin",
    "password": "Admin@123"
})
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("\n" + "="*60)
print("COMPLETE DATABASE RESET")
print("="*60)

# 1. Delete all sessions
print("\n1. Deleting all sessions...")
try:
    sessions_response = requests.get(f"{BASE_URL}/sessions", headers=headers)
    sessions = sessions_response.json()
    print(f"   Found {len(sessions)} sessions")

    for session in sessions:
        delete_response = requests.delete(f"{BASE_URL}/sessions/{session['id']}", headers=headers)
        if delete_response.status_code in [200, 204]:
            print(f"   [OK] Deleted session: {session.get('session_name', 'Unnamed')} ({session['id']})")
        else:
            print(f"   [ERROR] Failed to delete session {session['id']}: {delete_response.status_code}")

    print(f"   Total sessions deleted: {len(sessions)}")
except Exception as e:
    print(f"   [ERROR] Error deleting sessions: {e}")

# 2. Delete all templates
print("\n2. Deleting all templates...")
try:
    templates_response = requests.get(f"{BASE_URL}/templates", headers=headers)
    templates = templates_response.json()
    print(f"   Found {len(templates)} templates")

    for template in templates:
        delete_response = requests.delete(f"{BASE_URL}/templates/{template['id']}", headers=headers)
        if delete_response.status_code in [200, 204]:
            print(f"   [OK] Deleted template: {template['name']} ({template['id']})")
        else:
            print(f"   [ERROR] Failed to delete template {template['id']}: {delete_response.status_code}")

    print(f"   Total templates deleted: {len(templates)}")
except Exception as e:
    print(f"   [ERROR] Error deleting templates: {e}")

# 3. Delete all wizards (this will cascade delete dependencies and option sets)
print("\n3. Deleting all wizards...")
wizards_response = requests.get(f"{BASE_URL}/wizards", headers=headers)
wizards = wizards_response.json()
print(f"   Found {len(wizards)} wizards")

for wizard in wizards:
    delete_response = requests.delete(f"{BASE_URL}/wizards/{wizard['id']}", headers=headers)
    if delete_response.status_code in [200, 204]:
        print(f"   [OK] Deleted wizard: {wizard['name']} ({wizard['id']})")
    else:
        print(f"   [ERROR] Failed to delete wizard {wizard['id']}: {delete_response.status_code}")

print(f"   Total wizards deleted: {len(wizards)}")

print("\n" + "="*60)
print("DATABASE RESET COMPLETE!")
print("="*60)
print("\nAll data deleted:")
print(f"  - Sessions: {len(sessions) if 'sessions' in locals() else 0}")
print(f"  - Templates: {len(templates) if 'templates' in locals() else 0}")
print(f"  - Wizards: {len(wizards)}")
print("\nDatabase is now clean and ready for fresh wizards.")
print("\nNext step: Run 'python reset_and_create_wizards.py' to create test wizards")
