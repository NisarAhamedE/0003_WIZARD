"""
Create a comprehensive test wizard with all 12 selection types
For QA testing of sessions and templates
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Login as admin
login_response = requests.post(f"{BASE_URL}/auth/login", data={
    "username": "admin",
    "password": "Admin@123"
})
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Create wizard with all selection types
wizard_data = {
    "name": "QA Test - All Selection Types",
    "description": "Comprehensive test wizard with all 12 selection types for QA testing",
    "category": "Testing",
    "is_active": True,
    "steps": [
        {
            "name": "Step 1: Choice Selections",
            "description": "Test single and multiple select",
            "step_order": 0,
            "option_sets": [
                {
                    "name": "Choose Your Favorite Color (Single Select)",
                    "description": "Select one color",
                    "selection_type": "single_select",
                    "is_required": True,
                    "order_index": 0,
                    "options": [
                        {"label": "Red", "value": "red", "order_index": 0},
                        {"label": "Blue", "value": "blue", "order_index": 1},
                        {"label": "Green", "value": "green", "order_index": 2}
                    ]
                },
                {
                    "name": "Select Features (Multiple Select)",
                    "description": "Choose one or more features",
                    "selection_type": "multiple_select",
                    "is_required": True,
                    "min_selections": 1,
                    "max_selections": 3,
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
            "name": "Step 2: Text & Number Inputs",
            "description": "Test text and number input types",
            "step_order": 1,
            "option_sets": [
                {
                    "name": "Your Name (Text Input)",
                    "description": "Enter your full name",
                    "selection_type": "text_input",
                    "is_required": True,
                    "help_text": "Please enter your first and last name",
                    "order_index": 0,
                    "options": [{"label": "Name", "value": "name", "order_index": 0}]
                },
                {
                    "name": "Your Age (Number Input)",
                    "description": "Enter your age",
                    "selection_type": "number_input",
                    "is_required": True,
                    "min_value": 18,
                    "max_value": 100,
                    "order_index": 1,
                    "options": [{"label": "Age", "value": "age", "order_index": 0}]
                },
                {
                    "name": "Additional Comments (Rich Text)",
                    "description": "Enter any additional comments",
                    "selection_type": "rich_text",
                    "is_required": False,
                    "order_index": 2,
                    "options": [{"label": "Comments", "value": "comments", "order_index": 0}]
                }
            ]
        },
        {
            "name": "Step 3: Date & Time Inputs",
            "description": "Test date, time, and datetime inputs",
            "step_order": 2,
            "option_sets": [
                {
                    "name": "Event Date (Date Input)",
                    "description": "Select the event date",
                    "selection_type": "date_input",
                    "is_required": True,
                    "order_index": 0,
                    "options": [{"label": "Date", "value": "event_date", "order_index": 0}]
                },
                {
                    "name": "Event Time (Time Input)",
                    "description": "Select the event time",
                    "selection_type": "time_input",
                    "is_required": True,
                    "order_index": 1,
                    "options": [{"label": "Time", "value": "event_time", "order_index": 0}]
                },
                {
                    "name": "Full Event DateTime (DateTime Input)",
                    "description": "Select the complete event date and time",
                    "selection_type": "datetime_input",
                    "is_required": False,
                    "order_index": 2,
                    "options": [{"label": "DateTime", "value": "event_datetime", "order_index": 0}]
                }
            ]
        },
        {
            "name": "Step 4: Interactive Inputs",
            "description": "Test rating and slider",
            "step_order": 3,
            "option_sets": [
                {
                    "name": "Service Rating (Rating)",
                    "description": "Rate our service",
                    "selection_type": "rating",
                    "is_required": True,
                    "max_value": 5,
                    "order_index": 0,
                    "options": [{"label": "Rating", "value": "rating", "order_index": 0}]
                },
                {
                    "name": "Budget Range (Slider)",
                    "description": "Select your budget",
                    "selection_type": "slider",
                    "is_required": True,
                    "min_value": 0,
                    "max_value": 10000,
                    "step_increment": 100,
                    "order_index": 1,
                    "options": [{"label": "Budget", "value": "budget", "order_index": 0}]
                }
            ]
        },
        {
            "name": "Step 5: Advanced Inputs",
            "description": "Test color picker and file upload",
            "step_order": 4,
            "option_sets": [
                {
                    "name": "Theme Color (Color Picker)",
                    "description": "Choose your theme color",
                    "selection_type": "color_picker",
                    "is_required": False,
                    "order_index": 0,
                    "options": [{"label": "Color", "value": "theme_color", "order_index": 0}]
                },
                {
                    "name": "Upload Document (File Upload)",
                    "description": "Upload a supporting document",
                    "selection_type": "file_upload",
                    "is_required": False,
                    "max_selections": 1,
                    "order_index": 1,
                    "options": [{"label": "File", "value": "document", "order_index": 0}]
                }
            ]
        }
    ]
}

print("Creating QA test wizard with all 12 selection types...")
response = requests.post(f"{BASE_URL}/wizards", json=wizard_data, headers=headers)

if response.status_code == 200:
    wizard = response.json()
    print("[SUCCESS] Wizard created successfully!")
    print(f"   Wizard ID: {wizard['id']}")
    print(f"   Name: {wizard['name']}")
    print(f"   Steps: {len(wizard['steps'])}")

    # Count total option sets
    total_option_sets = sum(len(step['option_sets']) for step in wizard['steps'])
    print(f"   Total Option Sets: {total_option_sets}")

    # List all selection types used
    selection_types = set()
    for step in wizard['steps']:
        for os in step['option_sets']:
            selection_types.add(os['selection_type'])

    print(f"\n   Selection Types Used ({len(selection_types)}):")
    for st in sorted(selection_types):
        print(f"   - {st}")

    print(f"\nTest the wizard at:")
    print(f"   http://localhost:3000/wizard/{wizard['id']}")

else:
    print("[ERROR] Failed to create wizard")
    print(f"   Status: {response.status_code}")
    print(f"   Error: {response.text}")
