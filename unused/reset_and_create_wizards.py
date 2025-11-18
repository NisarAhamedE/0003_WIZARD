"""
Delete all wizards and recreate comprehensive test wizards
with all 12 selection types and conditional dependencies
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Login as admin
print("Logging in as admin...")
login_response = requests.post(f"{BASE_URL}/auth/login", data={
    "username": "admin",
    "password": "Admin@123"
})
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get all wizards
print("\nFetching all wizards...")
wizards_response = requests.get(f"{BASE_URL}/wizards", headers=headers)
wizards = wizards_response.json()
print(f"Found {len(wizards)} wizards")

# Delete all wizards
print("\nDeleting all wizards...")
for wizard in wizards:
    print(f"  Deleting: {wizard['name']} ({wizard['id']})")
    delete_response = requests.delete(f"{BASE_URL}/wizards/{wizard['id']}", headers=headers)
    if delete_response.status_code in [200, 204]:
        print(f"    [OK] Deleted")
    else:
        print(f"    [ERROR] Failed: {delete_response.status_code}")

print(f"\n[SUCCESS] Deleted {len(wizards)} wizards")

# Create Wizard 1: All 12 Selection Types (No Dependencies)
print("\n" + "="*60)
print("Creating Wizard 1: All 12 Selection Types")
print("="*60)

wizard1_data = {
    "name": "All Selection Types - Basic Test",
    "description": "Test wizard with all 12 selection types without dependencies",
    "category": "Testing",
    "is_active": True,
    "steps": [
        {
            "name": "Step 1: Choice Selections",
            "description": "Single and Multiple Select",
            "step_order": 0,
            "option_sets": [
                {
                    "name": "Choose Your Favorite Color",
                    "description": "Select one color (Single Select)",
                    "selection_type": "single_select",
                    "is_required": True,
                    "order_index": 0,
                    "options": [
                        {"label": "Red", "value": "red", "order_index": 0},
                        {"label": "Blue", "value": "blue", "order_index": 1},
                        {"label": "Green", "value": "green", "order_index": 2},
                        {"label": "Yellow", "value": "yellow", "order_index": 3}
                    ]
                },
                {
                    "name": "Select Features",
                    "description": "Choose multiple features (Multiple Select)",
                    "selection_type": "multiple_select",
                    "is_required": True,
                    "min_selections": 1,
                    "max_selections": 4,
                    "order_index": 1,
                    "options": [
                        {"label": "WiFi", "value": "wifi", "order_index": 0},
                        {"label": "Bluetooth", "value": "bluetooth", "order_index": 1},
                        {"label": "GPS", "value": "gps", "order_index": 2},
                        {"label": "NFC", "value": "nfc", "order_index": 3}
                    ]
                }
            ]
        },
        {
            "name": "Step 2: Text Inputs",
            "description": "Text, Number, and Rich Text",
            "step_order": 1,
            "option_sets": [
                {
                    "name": "Your Full Name",
                    "description": "Enter your name (Text Input)",
                    "selection_type": "text_input",
                    "is_required": True,
                    "help_text": "Please enter your first and last name",
                    "order_index": 0,
                    "options": [{"label": "Name", "value": "name", "order_index": 0}]
                },
                {
                    "name": "Your Age",
                    "description": "Enter your age (Number Input)",
                    "selection_type": "number_input",
                    "is_required": True,
                    "min_value": 18,
                    "max_value": 100,
                    "order_index": 1,
                    "options": [{"label": "Age", "value": "age", "order_index": 0}]
                },
                {
                    "name": "Additional Comments",
                    "description": "Enter detailed comments (Rich Text)",
                    "selection_type": "rich_text",
                    "is_required": False,
                    "help_text": "Enter any additional information here",
                    "order_index": 2,
                    "options": [{"label": "Comments", "value": "comments", "order_index": 0}]
                }
            ]
        },
        {
            "name": "Step 3: Date & Time",
            "description": "Date, Time, and DateTime Inputs",
            "step_order": 2,
            "option_sets": [
                {
                    "name": "Event Date",
                    "description": "Select the event date (Date Input)",
                    "selection_type": "date_input",
                    "is_required": True,
                    "help_text": "Choose your preferred date",
                    "order_index": 0,
                    "options": [{"label": "Date", "value": "event_date", "order_index": 0}]
                },
                {
                    "name": "Event Time",
                    "description": "Select the event time (Time Input)",
                    "selection_type": "time_input",
                    "is_required": True,
                    "help_text": "Choose your preferred time",
                    "order_index": 1,
                    "options": [{"label": "Time", "value": "event_time", "order_index": 0}]
                },
                {
                    "name": "Full Event DateTime",
                    "description": "Select complete date and time (DateTime Input)",
                    "selection_type": "datetime_input",
                    "is_required": False,
                    "order_index": 2,
                    "options": [{"label": "DateTime", "value": "event_datetime", "order_index": 0}]
                }
            ]
        },
        {
            "name": "Step 4: Interactive",
            "description": "Rating and Slider",
            "step_order": 3,
            "option_sets": [
                {
                    "name": "Service Rating",
                    "description": "Rate our service (Rating)",
                    "selection_type": "rating",
                    "is_required": True,
                    "max_value": 5,
                    "help_text": "1 star = Poor, 5 stars = Excellent",
                    "order_index": 0,
                    "options": [{"label": "Rating", "value": "rating", "order_index": 0}]
                },
                {
                    "name": "Budget Range",
                    "description": "Select your budget (Slider)",
                    "selection_type": "slider",
                    "is_required": True,
                    "min_value": 0,
                    "max_value": 10000,
                    "step_increment": 100,
                    "help_text": "Move the slider to select your budget",
                    "order_index": 1,
                    "options": [{"label": "Budget", "value": "budget", "order_index": 0}]
                }
            ]
        },
        {
            "name": "Step 5: Advanced",
            "description": "Color Picker and File Upload",
            "step_order": 4,
            "option_sets": [
                {
                    "name": "Theme Color",
                    "description": "Choose your theme color (Color Picker)",
                    "selection_type": "color_picker",
                    "is_required": False,
                    "help_text": "Pick a color that represents your brand",
                    "order_index": 0,
                    "options": [{"label": "Color", "value": "theme_color", "order_index": 0}]
                },
                {
                    "name": "Upload Document",
                    "description": "Upload a supporting document (File Upload)",
                    "selection_type": "file_upload",
                    "is_required": False,
                    "max_selections": 1,
                    "help_text": "Supported formats: PDF, DOC, DOCX",
                    "order_index": 1,
                    "options": [{"label": "File", "value": "document", "order_index": 0}]
                }
            ]
        }
    ]
}

response1 = requests.post(f"{BASE_URL}/wizards", json=wizard1_data, headers=headers)
if response1.status_code in [200, 201]:
    wizard1 = response1.json()
    print(f"[SUCCESS] Wizard 1 created!")
    print(f"  ID: {wizard1['id']}")
    print(f"  URL: http://localhost:3000/wizard/{wizard1['id']}")
else:
    print(f"[ERROR] Failed to create Wizard 1: {response1.status_code}")
    print(f"  {response1.text}")

# Create Wizard 2: All Types with Dependencies
print("\n" + "="*60)
print("Creating Wizard 2: All Selection Types with Dependencies")
print("="*60)

wizard2_data = {
    "name": "All Selection Types - With Dependencies",
    "description": "Test wizard with all 12 selection types and conditional dependencies",
    "category": "Testing",
    "is_active": True,
    "steps": [
        {
            "name": "Step 1: Basic Info",
            "description": "Tell us about yourself",
            "step_order": 0,
            "option_sets": [
                {
                    "name": "Are you a new customer?",
                    "selection_type": "single_select",
                    "is_required": True,
                    "order_index": 0,
                    "options": [
                        {"label": "Yes, I'm new", "value": "new", "order_index": 0},
                        {"label": "No, I'm existing", "value": "existing", "order_index": 1}
                    ]
                },
                {
                    "name": "Select Your Interests",
                    "selection_type": "multiple_select",
                    "is_required": True,
                    "min_selections": 1,
                    "order_index": 1,
                    "options": [
                        {"label": "Technology", "value": "tech", "order_index": 0},
                        {"label": "Sports", "value": "sports", "order_index": 1},
                        {"label": "Music", "value": "music", "order_index": 2},
                        {"label": "Travel", "value": "travel", "order_index": 3}
                    ]
                }
            ]
        },
        {
            "name": "Step 2: Personal Details",
            "description": "Your information",
            "step_order": 1,
            "option_sets": [
                {
                    "name": "Your Name",
                    "description": "This field will be disabled if you selected 'existing customer'",
                    "selection_type": "text_input",
                    "is_required": True,
                    "order_index": 0,
                    "options": [{"label": "Name", "value": "customer_name", "order_index": 0}]
                },
                {
                    "name": "Your Age",
                    "selection_type": "number_input",
                    "is_required": True,
                    "min_value": 18,
                    "max_value": 100,
                    "order_index": 1,
                    "options": [{"label": "Age", "value": "customer_age", "order_index": 0}]
                },
                {
                    "name": "Tell us more",
                    "description": "This becomes required if age < 25",
                    "selection_type": "rich_text",
                    "is_required": False,
                    "order_index": 2,
                    "options": [{"label": "Details", "value": "more_info", "order_index": 0}]
                }
            ]
        },
        {
            "name": "Step 3: Preferences",
            "description": "Date, time, and ratings",
            "step_order": 2,
            "option_sets": [
                {
                    "name": "Preferred Date",
                    "selection_type": "date_input",
                    "is_required": True,
                    "order_index": 0,
                    "options": [{"label": "Date", "value": "pref_date", "order_index": 0}]
                },
                {
                    "name": "Preferred Time",
                    "selection_type": "time_input",
                    "is_required": True,
                    "order_index": 1,
                    "options": [{"label": "Time", "value": "pref_time", "order_index": 0}]
                },
                {
                    "name": "Rate Your Experience",
                    "description": "How would you rate us?",
                    "selection_type": "rating",
                    "is_required": True,
                    "max_value": 5,
                    "order_index": 2,
                    "options": [{"label": "Rating", "value": "experience_rating", "order_index": 0}]
                }
            ]
        },
        {
            "name": "Step 4: Budget & Style",
            "description": "Budget and color preferences",
            "step_order": 3,
            "option_sets": [
                {
                    "name": "Your Budget",
                    "description": "This affects what options you'll see",
                    "selection_type": "slider",
                    "is_required": True,
                    "min_value": 0,
                    "max_value": 5000,
                    "step_increment": 100,
                    "order_index": 0,
                    "options": [{"label": "Budget", "value": "budget_amount", "order_index": 0}]
                },
                {
                    "name": "Preferred Color",
                    "description": "Only available if budget > 1000",
                    "selection_type": "color_picker",
                    "is_required": False,
                    "order_index": 1,
                    "options": [{"label": "Color", "value": "style_color", "order_index": 0}]
                }
            ]
        },
        {
            "name": "Step 5: Final Details",
            "description": "Upload and additional info",
            "step_order": 4,
            "option_sets": [
                {
                    "name": "Upload Document",
                    "description": "Required if you're a new customer",
                    "selection_type": "file_upload",
                    "is_required": False,
                    "order_index": 0,
                    "options": [{"label": "Document", "value": "upload_doc", "order_index": 0}]
                },
                {
                    "name": "Complete DateTime",
                    "selection_type": "datetime_input",
                    "is_required": False,
                    "order_index": 1,
                    "options": [{"label": "DateTime", "value": "complete_datetime", "order_index": 0}]
                }
            ]
        }
    ]
}

response2 = requests.post(f"{BASE_URL}/wizards", json=wizard2_data, headers=headers)
if response2.status_code in [200, 201]:
    wizard2 = response2.json()
    wizard2_id = wizard2['id']
    print(f"[SUCCESS] Wizard 2 created!")
    print(f"  ID: {wizard2_id}")
    print(f"  URL: http://localhost:3000/wizard/{wizard2_id}")

    # Now add dependencies to Wizard 2
    print("\nAdding dependencies to Wizard 2...")

    # Get the created wizard to extract option IDs
    wizard2_full = requests.get(f"{BASE_URL}/wizards/{wizard2_id}", headers=headers).json()

    # Build option ID map
    option_map = {}
    for step in wizard2_full['steps']:
        for os in step['option_sets']:
            for opt in os['options']:
                key = f"{os['name']}:{opt['value']}"
                option_map[key] = opt['id']

    dependencies_to_add = []

    # Dependency 1: Disable "Your Name" if "existing customer" is selected
    if "Your Name:customer_name" in option_map and "Are you a new customer?:existing" in option_map:
        dependencies_to_add.append({
            "option_id": option_map["Your Name:customer_name"],
            "depends_on_option_id": option_map["Are you a new customer?:existing"],
            "dependency_type": "disable_if"
        })

    # Dependency 2: Require "Upload Document" if "new customer" is selected
    if "Upload Document:upload_doc" in option_map and "Are you a new customer?:new" in option_map:
        dependencies_to_add.append({
            "option_id": option_map["Upload Document:upload_doc"],
            "depends_on_option_id": option_map["Are you a new customer?:new"],
            "dependency_type": "require_if"
        })

    # Add dependencies
    dep_count = 0
    for dep in dependencies_to_add:
        dep_response = requests.post(
            f"{BASE_URL}/option-dependencies",
            json=dep,
            headers=headers
        )
        if dep_response.status_code in [200, 201]:
            dep_count += 1
        else:
            print(f"  [WARNING] Failed to add dependency: {dep_response.status_code}")

    print(f"  Added {dep_count} dependencies")

else:
    print(f"[ERROR] Failed to create Wizard 2: {response2.status_code}")
    print(f"  {response2.text}")

print("\n" + "="*60)
print("SETUP COMPLETE!")
print("="*60)
print("\nYou now have 2 test wizards:")
print("1. All Selection Types - Basic Test (no dependencies)")
print("2. All Selection Types - With Dependencies (conditional logic)")
print("\nPlease restart your frontend (Ctrl+C and 'npm start') to see the changes!")
print("="*60)
