"""
Script to delete all wizards and create 3 new wizard templates using the API
"""
import requests
import json

# API configuration
BASE_URL = "http://127.0.0.1:8000/api/v1"
USERNAME = "admin"
PASSWORD = "Admin@123"

# Login to get token
print("[*] Logging in...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": USERNAME, "password": PASSWORD}
)

if login_response.status_code != 200:
    print(f"[ERROR] Login failed: {login_response.text}")
    exit(1)

access_token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {access_token}"}
print("[OK] Logged in successfully")

# Get all wizards
print("\n[*] Fetching all wizards...")
wizards_response = requests.get(f"{BASE_URL}/wizards", headers=headers)
wizards = wizards_response.json()

# Delete all wizards
print(f"[*] Deleting {len(wizards)} wizards...")
for wizard in wizards:
    delete_response = requests.delete(
        f"{BASE_URL}/wizards/{wizard['id']}",
        headers=headers
    )
    if delete_response.status_code == 200:
        print(f"  - Deleted: {wizard['name']}")
    else:
        print(f"  - Failed to delete: {wizard['name']}")

print("[OK] All wizards deleted")

# Template 1: Customer Onboarding
print("\n[1] Creating Customer Onboarding Wizard...")
wizard1 = {
    "name": "Customer Onboarding",
    "description": "Complete customer registration and onboarding process",
    "is_published": True,
    "require_login": False,
    "allow_anonymous": True,
    "steps": [
        {
            "name": "Personal Information",
            "description": "Enter your personal details",
            "step_order": 1,
            "option_sets": [
                {
                    "name": "Full Name",
                    "description": "Enter your full name",
                    "selection_type": "text_input",
                    "is_required": True,
                    "display_order": 1
                },
                {
                    "name": "Email Address",
                    "description": "Enter your email",
                    "selection_type": "text_input",
                    "is_required": True,
                    "display_order": 2
                },
                {
                    "name": "Phone Number",
                    "description": "Enter your phone number",
                    "selection_type": "number_input",
                    "is_required": False,
                    "display_order": 3
                }
            ]
        },
        {
            "name": "Company Information",
            "description": "Tell us about your company",
            "step_order": 2,
            "option_sets": [
                {
                    "name": "Company Size",
                    "description": "Select your company size",
                    "selection_type": "single_select",
                    "is_required": True,
                    "display_order": 1,
                    "options": [
                        {"label": "1-10 employees", "value": "small", "display_order": 1},
                        {"label": "11-50 employees", "value": "medium", "display_order": 2},
                        {"label": "51-200 employees", "value": "large", "display_order": 3},
                        {"label": "200+ employees", "value": "enterprise", "display_order": 4}
                    ]
                },
                {
                    "name": "Industry",
                    "description": "Select your industry",
                    "selection_type": "multiple_select",
                    "is_required": True,
                    "display_order": 2,
                    "options": [
                        {"label": "Technology", "value": "tech", "display_order": 1},
                        {"label": "Healthcare", "value": "healthcare", "display_order": 2},
                        {"label": "Finance", "value": "finance", "display_order": 3},
                        {"label": "Retail", "value": "retail", "display_order": 4},
                        {"label": "Education", "value": "education", "display_order": 5}
                    ]
                }
            ]
        }
    ]
}

response1 = requests.post(f"{BASE_URL}/wizards", json=wizard1, headers=headers)
if response1.status_code == 201:
    print("[OK] Customer Onboarding Wizard created")
else:
    print(f"[ERROR] Failed to create wizard: {response1.text}")

# Template 2: Product Configuration
print("\n[2] Creating Product Configuration Wizard...")
wizard2 = {
    "name": "Product Configuration",
    "description": "Configure your product preferences",
    "is_published": True,
    "require_login": False,
    "allow_anonymous": True,
    "steps": [
        {
            "name": "Basic Settings",
            "description": "Configure basic product settings",
            "step_order": 1,
            "option_sets": [
                {
                    "name": "Product Name",
                    "description": "Enter product name",
                    "selection_type": "text_input",
                    "is_required": True,
                    "display_order": 1
                },
                {
                    "name": "Priority Level",
                    "description": "Set priority level (1-5)",
                    "selection_type": "slider",
                    "is_required": True,
                    "min_value": 1,
                    "max_value": 5,
                    "display_order": 2
                },
                {
                    "name": "Rate this product",
                    "description": "Give your rating",
                    "selection_type": "rating",
                    "is_required": False,
                    "min_value": 1,
                    "max_value": 5,
                    "display_order": 3
                }
            ]
        },
        {
            "name": "Advanced Options",
            "description": "Configure advanced features",
            "step_order": 2,
            "option_sets": [
                {
                    "name": "Theme Color",
                    "description": "Choose a theme color",
                    "selection_type": "color_picker",
                    "is_required": True,
                    "display_order": 1
                },
                {
                    "name": "Launch Date",
                    "description": "Select launch date",
                    "selection_type": "date_input",
                    "is_required": True,
                    "display_order": 2
                }
            ]
        }
    ]
}

response2 = requests.post(f"{BASE_URL}/wizards", json=wizard2, headers=headers)
if response2.status_code == 201:
    print("[OK] Product Configuration Wizard created")
else:
    print(f"[ERROR] Failed to create wizard: {response2.text}")

# Template 3: Event Registration
print("\n[3] Creating Event Registration Wizard...")
wizard3 = {
    "name": "Event Registration",
    "description": "Register for upcoming events",
    "is_published": True,
    "require_login": False,
    "allow_anonymous": True,
    "steps": [
        {
            "name": "Attendee Information",
            "description": "Enter attendee details",
            "step_order": 1,
            "option_sets": [
                {
                    "name": "Attendee Name",
                    "description": "Full name of attendee",
                    "selection_type": "text_input",
                    "is_required": True,
                    "display_order": 1
                },
                {
                    "name": "Dietary Restrictions",
                    "description": "Select any dietary restrictions",
                    "selection_type": "multiple_select",
                    "is_required": False,
                    "display_order": 2,
                    "options": [
                        {"label": "Vegetarian", "value": "vegetarian", "display_order": 1},
                        {"label": "Vegan", "value": "vegan", "display_order": 2},
                        {"label": "Gluten-Free", "value": "gluten_free", "display_order": 3},
                        {"label": "Halal", "value": "halal", "display_order": 4},
                        {"label": "Kosher", "value": "kosher", "display_order": 5},
                        {"label": "None", "value": "none", "display_order": 6}
                    ]
                }
            ]
        },
        {
            "name": "Event Preferences",
            "description": "Select your event preferences",
            "step_order": 2,
            "option_sets": [
                {
                    "name": "Session Type",
                    "description": "Choose session type",
                    "selection_type": "single_select",
                    "is_required": True,
                    "display_order": 1,
                    "options": [
                        {"label": "In-Person", "value": "in_person", "display_order": 1},
                        {"label": "Virtual", "value": "virtual", "display_order": 2},
                        {"label": "Hybrid", "value": "hybrid", "display_order": 3}
                    ]
                },
                {
                    "name": "Preferred Time",
                    "description": "Select preferred event time",
                    "selection_type": "time_input",
                    "is_required": True,
                    "display_order": 2
                },
                {
                    "name": "Additional Comments",
                    "description": "Any special requests or comments",
                    "selection_type": "rich_text",
                    "is_required": False,
                    "display_order": 3
                }
            ]
        }
    ]
}

response3 = requests.post(f"{BASE_URL}/wizards", json=wizard3, headers=headers)
if response3.status_code == 201:
    print("[OK] Event Registration Wizard created")
else:
    print(f"[ERROR] Failed to create wizard: {response3.text}")

print("\n[DONE] Database reset and template creation complete!")
