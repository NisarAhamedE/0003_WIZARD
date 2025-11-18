"""
Verify what's actually in the database
"""
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Login
login_response = requests.post(f"{BASE_URL}/auth/login", data={
    "username": "admin",
    "password": "Admin@123"
})
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("="*60)
print("DATABASE VERIFICATION")
print("="*60)

# Check wizards
print("\nWIZARDS:")
wizards = requests.get(f"{BASE_URL}/wizards", headers=headers).json()
print(f"Total: {len(wizards)}")
for w in wizards:
    print(f"  - {w['name']} ({w['id']})")

# Check sessions
print("\nSESSIONS:")
sessions = requests.get(f"{BASE_URL}/sessions", headers=headers).json()
print(f"Total: {len(sessions)}")
for s in sessions[:5]:  # Show first 5
    print(f"  - {s.get('session_name', 'Unnamed')} ({s['id']})")
if len(sessions) > 5:
    print(f"  ... and {len(sessions) - 5} more")

# Check templates
print("\nTEMPLATES:")
templates = requests.get(f"{BASE_URL}/templates", headers=headers).json()
print(f"Total: {len(templates)}")
for t in templates:
    print(f"  - {t['name']} ({t['id']})")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Wizards: {len(wizards)}")
print(f"Sessions: {len(sessions)}")
print(f"Templates: {len(templates)}")
print("="*60)

if len(wizards) == 0:
    print("\nDatabase is CLEAN - ready to create wizards")
    print("Run: python reset_and_create_wizards.py")
else:
    print(f"\n[WARNING] Database still has {len(wizards)} wizard(s)")
    print("Frontend may be showing cached data")
    print("\nYou need to:")
    print("1. Close ALL browser tabs with the app")
    print("2. Clear browser cache")
    print("3. Restart frontend server")
    print("4. Open app in new incognito window")
