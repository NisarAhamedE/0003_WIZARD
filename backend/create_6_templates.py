"""
Script to create 6 diverse wizard templates for the Template Gallery
Each wizard has 4 steps with different selection types
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
print(f"[*] Deleting {len(wizards)} existing wizards...")
for wizard in wizards:
    delete_response = requests.delete(
        f"{BASE_URL}/wizards/{wizard['id']}",
        headers=headers
    )
    if delete_response.status_code == 200:
        print(f"  - Deleted: {wizard['name']}")
    else:
        print(f"  - Failed to delete: {wizard['name']}")

print("[OK] All wizards deleted\n")

# Template 1: Employee Onboarding Portal
print("[1] Creating Employee Onboarding Portal...")
wizard1 = {
    "name": "Employee Onboarding Portal",
    "description": "Complete new employee registration and setup process",
    "is_published": True,
    "require_login": False,
    "allow_anonymous": True,
    "steps": [
        {
            "name": "Personal Information",
            "description": "Basic employee information",
            "step_order": 1,
            "option_sets": [
                {
                    "name": "Full Name",
                    "description": "Enter your full legal name",
                    "selection_type": "text_input",
                    "is_required": True,
                    "display_order": 1
                },
                {
                    "name": "Date of Birth",
                    "description": "Select your date of birth",
                    "selection_type": "date_input",
                    "is_required": True,
                    "display_order": 2
                },
                {
                    "name": "Employment Type",
                    "description": "Select your employment status",
                    "selection_type": "single_select",
                    "is_required": True,
                    "display_order": 3,
                    "options": [
                        {"label": "Full-time", "value": "full_time", "display_order": 1},
                        {"label": "Part-time", "value": "part_time", "display_order": 2},
                        {"label": "Contract", "value": "contract", "display_order": 3},
                        {"label": "Intern", "value": "intern", "display_order": 4}
                    ]
                }
            ]
        },
        {
            "name": "Department & Role",
            "description": "Work assignment details",
            "step_order": 2,
            "option_sets": [
                {
                    "name": "Department",
                    "description": "Select your department",
                    "selection_type": "single_select",
                    "is_required": True,
                    "display_order": 1,
                    "options": [
                        {"label": "Engineering", "value": "engineering", "display_order": 1},
                        {"label": "Sales", "value": "sales", "display_order": 2},
                        {"label": "Marketing", "value": "marketing", "display_order": 3},
                        {"label": "Human Resources", "value": "hr", "display_order": 4},
                        {"label": "Finance", "value": "finance", "display_order": 5}
                    ]
                },
                {
                    "name": "Start Date",
                    "description": "When will you start?",
                    "selection_type": "date_input",
                    "is_required": True,
                    "display_order": 2
                },
                {
                    "name": "Work Schedule Preference",
                    "description": "Preferred working hours",
                    "selection_type": "single_select",
                    "is_required": False,
                    "display_order": 3,
                    "options": [
                        {"label": "9 AM - 5 PM", "value": "9to5", "display_order": 1},
                        {"label": "10 AM - 6 PM", "value": "10to6", "display_order": 2},
                        {"label": "Flexible", "value": "flexible", "display_order": 3}
                    ]
                }
            ]
        },
        {
            "name": "Equipment & Setup",
            "description": "Hardware and software requirements",
            "step_order": 3,
            "option_sets": [
                {
                    "name": "Equipment Needed",
                    "description": "Select all equipment you need",
                    "selection_type": "multiple_select",
                    "is_required": True,
                    "display_order": 1,
                    "options": [
                        {"label": "Laptop", "value": "laptop", "display_order": 1},
                        {"label": "Desktop Monitor", "value": "monitor", "display_order": 2},
                        {"label": "Keyboard & Mouse", "value": "peripherals", "display_order": 3},
                        {"label": "Headset", "value": "headset", "display_order": 4},
                        {"label": "Phone", "value": "phone", "display_order": 5}
                    ]
                },
                {
                    "name": "Office Location Preference",
                    "description": "Where would you like to work?",
                    "selection_type": "single_select",
                    "is_required": True,
                    "display_order": 2,
                    "options": [
                        {"label": "Main Office", "value": "main", "display_order": 1},
                        {"label": "Remote", "value": "remote", "display_order": 2},
                        {"label": "Hybrid", "value": "hybrid", "display_order": 3}
                    ]
                }
            ]
        },
        {
            "name": "Documents & Compliance",
            "description": "Required documentation",
            "step_order": 4,
            "option_sets": [
                {
                    "name": "Emergency Contact Name",
                    "description": "Full name of emergency contact",
                    "selection_type": "text_input",
                    "is_required": True,
                    "display_order": 1
                },
                {
                    "name": "Emergency Contact Phone",
                    "description": "Emergency contact phone number",
                    "selection_type": "text_input",
                    "is_required": True,
                    "display_order": 2
                },
                {
                    "name": "Additional Comments",
                    "description": "Any special requirements or notes",
                    "selection_type": "rich_text",
                    "is_required": False,
                    "display_order": 3
                }
            ]
        }
    ]
}

response1 = requests.post(f"{BASE_URL}/wizards", json=wizard1, headers=headers)
if response1.status_code == 201:
    print("[OK] Employee Onboarding Portal created")
else:
    print(f"[ERROR] Failed: {response1.text}")

# Template 2: Project Planning Wizard
print("\n[2] Creating Project Planning Wizard...")
wizard2 = {
    "name": "Project Planning Wizard",
    "description": "Plan and configure a new project from start to finish",
    "is_published": True,
    "require_login": False,
    "allow_anonymous": True,
    "steps": [
        {
            "name": "Project Basics",
            "description": "Define core project information",
            "step_order": 1,
            "option_sets": [
                {
                    "name": "Project Name",
                    "description": "Give your project a name",
                    "selection_type": "text_input",
                    "is_required": True,
                    "display_order": 1
                },
                {
                    "name": "Project Type",
                    "description": "What type of project is this?",
                    "selection_type": "single_select",
                    "is_required": True,
                    "display_order": 2,
                    "options": [
                        {"label": "Software Development", "value": "software", "display_order": 1},
                        {"label": "Marketing Campaign", "value": "marketing", "display_order": 2},
                        {"label": "Infrastructure", "value": "infrastructure", "display_order": 3},
                        {"label": "Research", "value": "research", "display_order": 4},
                        {"label": "Other", "value": "other", "display_order": 5}
                    ]
                },
                {
                    "name": "Priority Level",
                    "description": "How urgent is this project? (1=Low, 5=Critical)",
                    "selection_type": "slider",
                    "is_required": True,
                    "min_value": 1,
                    "max_value": 5,
                    "display_order": 3
                }
            ]
        },
        {
            "name": "Timeline & Budget",
            "description": "Set project constraints",
            "step_order": 2,
            "option_sets": [
                {
                    "name": "Start Date",
                    "description": "When does the project start?",
                    "selection_type": "date_input",
                    "is_required": True,
                    "display_order": 1
                },
                {
                    "name": "Target Completion Date",
                    "description": "Expected completion date",
                    "selection_type": "date_input",
                    "is_required": True,
                    "display_order": 2
                },
                {
                    "name": "Budget Range",
                    "description": "Estimated budget",
                    "selection_type": "single_select",
                    "is_required": True,
                    "display_order": 3,
                    "options": [
                        {"label": "Under $10K", "value": "under_10k", "display_order": 1},
                        {"label": "$10K - $50K", "value": "10k_50k", "display_order": 2},
                        {"label": "$50K - $100K", "value": "50k_100k", "display_order": 3},
                        {"label": "Over $100K", "value": "over_100k", "display_order": 4}
                    ]
                }
            ]
        },
        {
            "name": "Team & Resources",
            "description": "Define team structure",
            "step_order": 3,
            "option_sets": [
                {
                    "name": "Team Size",
                    "description": "Estimated team members (1-20)",
                    "selection_type": "number_input",
                    "is_required": True,
                    "min_value": 1,
                    "max_value": 20,
                    "display_order": 1
                },
                {
                    "name": "Required Skills",
                    "description": "Select all required skills",
                    "selection_type": "multiple_select",
                    "is_required": True,
                    "display_order": 2,
                    "options": [
                        {"label": "Frontend Development", "value": "frontend", "display_order": 1},
                        {"label": "Backend Development", "value": "backend", "display_order": 2},
                        {"label": "Design/UX", "value": "design", "display_order": 3},
                        {"label": "DevOps", "value": "devops", "display_order": 4},
                        {"label": "Project Management", "value": "pm", "display_order": 5},
                        {"label": "QA/Testing", "value": "qa", "display_order": 6}
                    ]
                }
            ]
        },
        {
            "name": "Goals & Success Metrics",
            "description": "Define project objectives",
            "step_order": 4,
            "option_sets": [
                {
                    "name": "Project Goals",
                    "description": "Describe the main objectives",
                    "selection_type": "rich_text",
                    "is_required": True,
                    "display_order": 1
                },
                {
                    "name": "Success Importance",
                    "description": "Rate the strategic importance",
                    "selection_type": "rating",
                    "is_required": True,
                    "min_value": 1,
                    "max_value": 5,
                    "display_order": 2
                },
                {
                    "name": "Stakeholder Updates",
                    "description": "How often should stakeholders be updated?",
                    "selection_type": "single_select",
                    "is_required": True,
                    "display_order": 3,
                    "options": [
                        {"label": "Daily", "value": "daily", "display_order": 1},
                        {"label": "Weekly", "value": "weekly", "display_order": 2},
                        {"label": "Bi-weekly", "value": "biweekly", "display_order": 3},
                        {"label": "Monthly", "value": "monthly", "display_order": 4}
                    ]
                }
            ]
        }
    ]
}

response2 = requests.post(f"{BASE_URL}/wizards", json=wizard2, headers=headers)
if response2.status_code == 201:
    print("[OK] Project Planning Wizard created")
else:
    print(f"[ERROR] Failed: {response2.text}")

# Template 3: Restaurant Reservation System
print("\n[3] Creating Restaurant Reservation System...")
wizard3 = {
    "name": "Restaurant Reservation System",
    "description": "Book a table at your favorite restaurant",
    "is_published": True,
    "require_login": False,
    "allow_anonymous": True,
    "steps": [
        {
            "name": "Guest Information",
            "description": "Tell us about your party",
            "step_order": 1,
            "option_sets": [
                {
                    "name": "Guest Name",
                    "description": "Name for the reservation",
                    "selection_type": "text_input",
                    "is_required": True,
                    "display_order": 1
                },
                {
                    "name": "Contact Phone",
                    "description": "Phone number",
                    "selection_type": "text_input",
                    "is_required": True,
                    "display_order": 2
                },
                {
                    "name": "Number of Guests",
                    "description": "How many people? (1-12)",
                    "selection_type": "number_input",
                    "is_required": True,
                    "min_value": 1,
                    "max_value": 12,
                    "display_order": 3
                }
            ]
        },
        {
            "name": "Date & Time",
            "description": "When would you like to dine?",
            "step_order": 2,
            "option_sets": [
                {
                    "name": "Reservation Date",
                    "description": "Select your preferred date",
                    "selection_type": "date_input",
                    "is_required": True,
                    "display_order": 1
                },
                {
                    "name": "Preferred Time",
                    "description": "What time works best?",
                    "selection_type": "time_input",
                    "is_required": True,
                    "display_order": 2
                },
                {
                    "name": "Meal Type",
                    "description": "Which service?",
                    "selection_type": "single_select",
                    "is_required": True,
                    "display_order": 3,
                    "options": [
                        {"label": "Breakfast", "value": "breakfast", "display_order": 1},
                        {"label": "Brunch", "value": "brunch", "display_order": 2},
                        {"label": "Lunch", "value": "lunch", "display_order": 3},
                        {"label": "Dinner", "value": "dinner", "display_order": 4}
                    ]
                }
            ]
        },
        {
            "name": "Preferences",
            "description": "Seating and dining preferences",
            "step_order": 3,
            "option_sets": [
                {
                    "name": "Seating Preference",
                    "description": "Where would you like to sit?",
                    "selection_type": "single_select",
                    "is_required": False,
                    "display_order": 1,
                    "options": [
                        {"label": "Indoor", "value": "indoor", "display_order": 1},
                        {"label": "Outdoor/Patio", "value": "outdoor", "display_order": 2},
                        {"label": "Bar Area", "value": "bar", "display_order": 3},
                        {"label": "No Preference", "value": "none", "display_order": 4}
                    ]
                },
                {
                    "name": "Special Occasion",
                    "description": "Is this a special event?",
                    "selection_type": "single_select",
                    "is_required": False,
                    "display_order": 2,
                    "options": [
                        {"label": "Birthday", "value": "birthday", "display_order": 1},
                        {"label": "Anniversary", "value": "anniversary", "display_order": 2},
                        {"label": "Business Dinner", "value": "business", "display_order": 3},
                        {"label": "Just Dining", "value": "none", "display_order": 4}
                    ]
                },
                {
                    "name": "Ambiance Preference",
                    "description": "Rate desired ambiance level (1=Quiet, 5=Lively)",
                    "selection_type": "slider",
                    "is_required": False,
                    "min_value": 1,
                    "max_value": 5,
                    "display_order": 3
                }
            ]
        },
        {
            "name": "Dietary Requirements",
            "description": "Any dietary restrictions or requests?",
            "step_order": 4,
            "option_sets": [
                {
                    "name": "Dietary Restrictions",
                    "description": "Select all that apply",
                    "selection_type": "multiple_select",
                    "is_required": False,
                    "display_order": 1,
                    "options": [
                        {"label": "Vegetarian", "value": "vegetarian", "display_order": 1},
                        {"label": "Vegan", "value": "vegan", "display_order": 2},
                        {"label": "Gluten-Free", "value": "gluten_free", "display_order": 3},
                        {"label": "Dairy-Free", "value": "dairy_free", "display_order": 4},
                        {"label": "Nut Allergy", "value": "nut_allergy", "display_order": 5},
                        {"label": "Shellfish Allergy", "value": "shellfish", "display_order": 6}
                    ]
                },
                {
                    "name": "Special Requests",
                    "description": "Any additional requests or notes",
                    "selection_type": "rich_text",
                    "is_required": False,
                    "display_order": 2
                }
            ]
        }
    ]
}

response3 = requests.post(f"{BASE_URL}/wizards", json=wizard3, headers=headers)
if response3.status_code == 201:
    print("[OK] Restaurant Reservation System created")
else:
    print(f"[ERROR] Failed: {response3.text}")

# Template 4: Travel Booking Assistant
print("\n[4] Creating Travel Booking Assistant...")
wizard4 = {
    "name": "Travel Booking Assistant",
    "description": "Plan your perfect vacation or business trip",
    "is_published": True,
    "require_login": False,
    "allow_anonymous": True,
    "steps": [
        {
            "name": "Trip Details",
            "description": "Basic trip information",
            "step_order": 1,
            "option_sets": [
                {
                    "name": "Trip Type",
                    "description": "What kind of trip?",
                    "selection_type": "single_select",
                    "is_required": True,
                    "display_order": 1,
                    "options": [
                        {"label": "Vacation", "value": "vacation", "display_order": 1},
                        {"label": "Business", "value": "business", "display_order": 2},
                        {"label": "Family Visit", "value": "family", "display_order": 3},
                        {"label": "Adventure", "value": "adventure", "display_order": 4}
                    ]
                },
                {
                    "name": "Number of Travelers",
                    "description": "How many people? (1-10)",
                    "selection_type": "number_input",
                    "is_required": True,
                    "min_value": 1,
                    "max_value": 10,
                    "display_order": 2
                },
                {
                    "name": "Trip Duration",
                    "description": "How long is your trip?",
                    "selection_type": "single_select",
                    "is_required": True,
                    "display_order": 3,
                    "options": [
                        {"label": "1-3 days", "value": "short", "display_order": 1},
                        {"label": "4-7 days", "value": "week", "display_order": 2},
                        {"label": "8-14 days", "value": "two_weeks", "display_order": 3},
                        {"label": "15+ days", "value": "long", "display_order": 4}
                    ]
                }
            ]
        },
        {
            "name": "Dates & Destination",
            "description": "When and where?",
            "step_order": 2,
            "option_sets": [
                {
                    "name": "Departure Date",
                    "description": "When do you leave?",
                    "selection_type": "date_input",
                    "is_required": True,
                    "display_order": 1
                },
                {
                    "name": "Return Date",
                    "description": "When do you return?",
                    "selection_type": "date_input",
                    "is_required": True,
                    "display_order": 2
                },
                {
                    "name": "Destination Type",
                    "description": "What kind of destination?",
                    "selection_type": "multiple_select",
                    "is_required": True,
                    "display_order": 3,
                    "options": [
                        {"label": "Beach", "value": "beach", "display_order": 1},
                        {"label": "City", "value": "city", "display_order": 2},
                        {"label": "Mountains", "value": "mountains", "display_order": 3},
                        {"label": "Countryside", "value": "countryside", "display_order": 4},
                        {"label": "Theme Parks", "value": "theme_parks", "display_order": 5}
                    ]
                }
            ]
        },
        {
            "name": "Accommodations",
            "description": "Where will you stay?",
            "step_order": 3,
            "option_sets": [
                {
                    "name": "Accommodation Type",
                    "description": "Preferred lodging",
                    "selection_type": "single_select",
                    "is_required": True,
                    "display_order": 1,
                    "options": [
                        {"label": "Hotel", "value": "hotel", "display_order": 1},
                        {"label": "Resort", "value": "resort", "display_order": 2},
                        {"label": "Vacation Rental", "value": "rental", "display_order": 3},
                        {"label": "Hostel", "value": "hostel", "display_order": 4},
                        {"label": "Bed & Breakfast", "value": "bnb", "display_order": 5}
                    ]
                },
                {
                    "name": "Budget per Night",
                    "description": "Maximum per night",
                    "selection_type": "single_select",
                    "is_required": True,
                    "display_order": 2,
                    "options": [
                        {"label": "Under $100", "value": "budget", "display_order": 1},
                        {"label": "$100-$200", "value": "moderate", "display_order": 2},
                        {"label": "$200-$400", "value": "upscale", "display_order": 3},
                        {"label": "$400+", "value": "luxury", "display_order": 4}
                    ]
                },
                {
                    "name": "Hotel Amenities Priority",
                    "description": "Rate importance (1=Not Important, 5=Essential)",
                    "selection_type": "slider",
                    "is_required": False,
                    "min_value": 1,
                    "max_value": 5,
                    "display_order": 3
                }
            ]
        },
        {
            "name": "Activities & Preferences",
            "description": "What do you want to do?",
            "step_order": 4,
            "option_sets": [
                {
                    "name": "Preferred Activities",
                    "description": "Select all that interest you",
                    "selection_type": "multiple_select",
                    "is_required": False,
                    "display_order": 1,
                    "options": [
                        {"label": "Sightseeing", "value": "sightseeing", "display_order": 1},
                        {"label": "Museums & Culture", "value": "culture", "display_order": 2},
                        {"label": "Shopping", "value": "shopping", "display_order": 3},
                        {"label": "Outdoor Adventures", "value": "outdoor", "display_order": 4},
                        {"label": "Dining & Nightlife", "value": "dining", "display_order": 5},
                        {"label": "Relaxation & Spa", "value": "relaxation", "display_order": 6}
                    ]
                },
                {
                    "name": "Overall Trip Rating Goal",
                    "description": "How memorable should this trip be?",
                    "selection_type": "rating",
                    "is_required": False,
                    "min_value": 1,
                    "max_value": 5,
                    "display_order": 2
                },
                {
                    "name": "Special Requirements",
                    "description": "Any special needs or requests",
                    "selection_type": "rich_text",
                    "is_required": False,
                    "display_order": 3
                }
            ]
        }
    ]
}

response4 = requests.post(f"{BASE_URL}/wizards", json=wizard4, headers=headers)
if response4.status_code == 201:
    print("[OK] Travel Booking Assistant created")
else:
    print(f"[ERROR] Failed: {response4.text}")

# Template 5: Fitness Program Designer
print("\n[5] Creating Fitness Program Designer...")
wizard5 = {
    "name": "Fitness Program Designer",
    "description": "Create a personalized fitness and wellness plan",
    "is_published": True,
    "require_login": False,
    "allow_anonymous": True,
    "steps": [
        {
            "name": "Personal Profile",
            "description": "Tell us about yourself",
            "step_order": 1,
            "option_sets": [
                {
                    "name": "Age Group",
                    "description": "Select your age range",
                    "selection_type": "single_select",
                    "is_required": True,
                    "display_order": 1,
                    "options": [
                        {"label": "18-25", "value": "young_adult", "display_order": 1},
                        {"label": "26-35", "value": "adult", "display_order": 2},
                        {"label": "36-50", "value": "middle_age", "display_order": 3},
                        {"label": "51-65", "value": "mature", "display_order": 4},
                        {"label": "65+", "value": "senior", "display_order": 5}
                    ]
                },
                {
                    "name": "Current Fitness Level",
                    "description": "How would you rate yourself?",
                    "selection_type": "single_select",
                    "is_required": True,
                    "display_order": 2,
                    "options": [
                        {"label": "Beginner", "value": "beginner", "display_order": 1},
                        {"label": "Intermediate", "value": "intermediate", "display_order": 2},
                        {"label": "Advanced", "value": "advanced", "display_order": 3},
                        {"label": "Athlete", "value": "athlete", "display_order": 4}
                    ]
                },
                {
                    "name": "Fitness Experience",
                    "description": "Rate your fitness experience (1=None, 5=Expert)",
                    "selection_type": "slider",
                    "is_required": True,
                    "min_value": 1,
                    "max_value": 5,
                    "display_order": 3
                }
            ]
        },
        {
            "name": "Goals & Timeline",
            "description": "What are you working towards?",
            "step_order": 2,
            "option_sets": [
                {
                    "name": "Primary Goals",
                    "description": "Select all that apply",
                    "selection_type": "multiple_select",
                    "is_required": True,
                    "display_order": 1,
                    "options": [
                        {"label": "Weight Loss", "value": "weight_loss", "display_order": 1},
                        {"label": "Muscle Gain", "value": "muscle_gain", "display_order": 2},
                        {"label": "Endurance", "value": "endurance", "display_order": 3},
                        {"label": "Flexibility", "value": "flexibility", "display_order": 4},
                        {"label": "General Health", "value": "health", "display_order": 5},
                        {"label": "Sports Performance", "value": "sports", "display_order": 6}
                    ]
                },
                {
                    "name": "Target Achievement Date",
                    "description": "When do you want to achieve your goals?",
                    "selection_type": "date_input",
                    "is_required": False,
                    "display_order": 2
                },
                {
                    "name": "Commitment Level",
                    "description": "How dedicated are you? (1=Casual, 5=Very Committed)",
                    "selection_type": "rating",
                    "is_required": True,
                    "min_value": 1,
                    "max_value": 5,
                    "display_order": 3
                }
            ]
        },
        {
            "name": "Schedule & Availability",
            "description": "When can you work out?",
            "step_order": 3,
            "option_sets": [
                {
                    "name": "Days Available per Week",
                    "description": "How many days? (1-7)",
                    "selection_type": "number_input",
                    "is_required": True,
                    "min_value": 1,
                    "max_value": 7,
                    "display_order": 1
                },
                {
                    "name": "Preferred Workout Time",
                    "description": "When do you prefer to exercise?",
                    "selection_type": "single_select",
                    "is_required": True,
                    "display_order": 2,
                    "options": [
                        {"label": "Early Morning (5-7 AM)", "value": "early_morning", "display_order": 1},
                        {"label": "Morning (7-10 AM)", "value": "morning", "display_order": 2},
                        {"label": "Midday (10 AM-2 PM)", "value": "midday", "display_order": 3},
                        {"label": "Afternoon (2-6 PM)", "value": "afternoon", "display_order": 4},
                        {"label": "Evening (6-9 PM)", "value": "evening", "display_order": 5},
                        {"label": "Flexible", "value": "flexible", "display_order": 6}
                    ]
                },
                {
                    "name": "Session Duration",
                    "description": "How long per workout?",
                    "selection_type": "single_select",
                    "is_required": True,
                    "display_order": 3,
                    "options": [
                        {"label": "15-30 minutes", "value": "short", "display_order": 1},
                        {"label": "30-45 minutes", "value": "medium", "display_order": 2},
                        {"label": "45-60 minutes", "value": "standard", "display_order": 3},
                        {"label": "60+ minutes", "value": "long", "display_order": 4}
                    ]
                }
            ]
        },
        {
            "name": "Equipment & Preferences",
            "description": "What equipment do you have access to?",
            "step_order": 4,
            "option_sets": [
                {
                    "name": "Available Equipment",
                    "description": "Select all that apply",
                    "selection_type": "multiple_select",
                    "is_required": True,
                    "display_order": 1,
                    "options": [
                        {"label": "No Equipment (Bodyweight)", "value": "bodyweight", "display_order": 1},
                        {"label": "Dumbbells", "value": "dumbbells", "display_order": 2},
                        {"label": "Resistance Bands", "value": "bands", "display_order": 3},
                        {"label": "Full Gym Access", "value": "gym", "display_order": 4},
                        {"label": "Cardio Machines", "value": "cardio", "display_order": 5},
                        {"label": "Yoga Mat", "value": "yoga", "display_order": 6}
                    ]
                },
                {
                    "name": "Exercise Preferences",
                    "description": "What do you enjoy?",
                    "selection_type": "multiple_select",
                    "is_required": False,
                    "display_order": 2,
                    "options": [
                        {"label": "Running", "value": "running", "display_order": 1},
                        {"label": "Cycling", "value": "cycling", "display_order": 2},
                        {"label": "Swimming", "value": "swimming", "display_order": 3},
                        {"label": "Weight Training", "value": "weights", "display_order": 4},
                        {"label": "Yoga/Pilates", "value": "yoga", "display_order": 5},
                        {"label": "HIIT", "value": "hiit", "display_order": 6}
                    ]
                },
                {
                    "name": "Additional Notes",
                    "description": "Medical conditions, injuries, or special considerations",
                    "selection_type": "rich_text",
                    "is_required": False,
                    "display_order": 3
                }
            ]
        }
    ]
}

response5 = requests.post(f"{BASE_URL}/wizards", json=wizard5, headers=headers)
if response5.status_code == 201:
    print("[OK] Fitness Program Designer created")
else:
    print(f"[ERROR] Failed: {response5.text}")

# Template 6: Website Design Questionnaire
print("\n[6] Creating Website Design Questionnaire...")
wizard6 = {
    "name": "Website Design Questionnaire",
    "description": "Gather requirements for your new website project",
    "is_published": True,
    "require_login": False,
    "allow_anonymous": True,
    "steps": [
        {
            "name": "Project Overview",
            "description": "Tell us about your website",
            "step_order": 1,
            "option_sets": [
                {
                    "name": "Company/Project Name",
                    "description": "What's the name of your business or project?",
                    "selection_type": "text_input",
                    "is_required": True,
                    "display_order": 1
                },
                {
                    "name": "Website Type",
                    "description": "What kind of website do you need?",
                    "selection_type": "single_select",
                    "is_required": True,
                    "display_order": 2,
                    "options": [
                        {"label": "Business/Corporate", "value": "business", "display_order": 1},
                        {"label": "E-commerce", "value": "ecommerce", "display_order": 2},
                        {"label": "Portfolio", "value": "portfolio", "display_order": 3},
                        {"label": "Blog", "value": "blog", "display_order": 4},
                        {"label": "Landing Page", "value": "landing", "display_order": 5},
                        {"label": "Web Application", "value": "webapp", "display_order": 6}
                    ]
                },
                {
                    "name": "Project Urgency",
                    "description": "How urgent is this project? (1=Flexible, 5=Very Urgent)",
                    "selection_type": "slider",
                    "is_required": True,
                    "min_value": 1,
                    "max_value": 5,
                    "display_order": 3
                }
            ]
        },
        {
            "name": "Design Preferences",
            "description": "Visual style and branding",
            "step_order": 2,
            "option_sets": [
                {
                    "name": "Design Style",
                    "description": "What aesthetic do you prefer?",
                    "selection_type": "multiple_select",
                    "is_required": True,
                    "display_order": 1,
                    "options": [
                        {"label": "Modern & Minimalist", "value": "modern", "display_order": 1},
                        {"label": "Bold & Colorful", "value": "bold", "display_order": 2},
                        {"label": "Professional & Corporate", "value": "corporate", "display_order": 3},
                        {"label": "Creative & Artistic", "value": "creative", "display_order": 4},
                        {"label": "Tech & Futuristic", "value": "tech", "display_order": 5},
                        {"label": "Classic & Elegant", "value": "classic", "display_order": 6}
                    ]
                },
                {
                    "name": "Primary Brand Color",
                    "description": "Select your primary brand color",
                    "selection_type": "color_picker",
                    "is_required": False,
                    "display_order": 2
                },
                {
                    "name": "Design Importance",
                    "description": "Rate design priority (1=Basic, 5=Premium)",
                    "selection_type": "rating",
                    "is_required": True,
                    "min_value": 1,
                    "max_value": 5,
                    "display_order": 3
                }
            ]
        },
        {
            "name": "Features & Functionality",
            "description": "Required features and capabilities",
            "step_order": 3,
            "option_sets": [
                {
                    "name": "Core Features",
                    "description": "Select all required features",
                    "selection_type": "multiple_select",
                    "is_required": True,
                    "display_order": 1,
                    "options": [
                        {"label": "Contact Form", "value": "contact", "display_order": 1},
                        {"label": "Blog/News", "value": "blog", "display_order": 2},
                        {"label": "Photo Gallery", "value": "gallery", "display_order": 3},
                        {"label": "Video Integration", "value": "video", "display_order": 4},
                        {"label": "User Login/Registration", "value": "auth", "display_order": 5},
                        {"label": "Search Functionality", "value": "search", "display_order": 6},
                        {"label": "Multilingual", "value": "multilingual", "display_order": 7}
                    ]
                },
                {
                    "name": "E-commerce Features",
                    "description": "If e-commerce, what do you need?",
                    "selection_type": "multiple_select",
                    "is_required": False,
                    "display_order": 2,
                    "options": [
                        {"label": "Shopping Cart", "value": "cart", "display_order": 1},
                        {"label": "Payment Gateway", "value": "payment", "display_order": 2},
                        {"label": "Inventory Management", "value": "inventory", "display_order": 3},
                        {"label": "Product Reviews", "value": "reviews", "display_order": 4},
                        {"label": "Shipping Integration", "value": "shipping", "display_order": 5}
                    ]
                },
                {
                    "name": "Expected Number of Pages",
                    "description": "How many pages? (1-100)",
                    "selection_type": "number_input",
                    "is_required": True,
                    "min_value": 1,
                    "max_value": 100,
                    "display_order": 3
                }
            ]
        },
        {
            "name": "Timeline & Budget",
            "description": "Project constraints",
            "step_order": 4,
            "option_sets": [
                {
                    "name": "Desired Launch Date",
                    "description": "When do you want to go live?",
                    "selection_type": "date_input",
                    "is_required": False,
                    "display_order": 1
                },
                {
                    "name": "Budget Range",
                    "description": "What's your budget?",
                    "selection_type": "single_select",
                    "is_required": True,
                    "display_order": 2,
                    "options": [
                        {"label": "Under $5,000", "value": "under_5k", "display_order": 1},
                        {"label": "$5,000 - $10,000", "value": "5k_10k", "display_order": 2},
                        {"label": "$10,000 - $25,000", "value": "10k_25k", "display_order": 3},
                        {"label": "$25,000 - $50,000", "value": "25k_50k", "display_order": 4},
                        {"label": "Over $50,000", "value": "over_50k", "display_order": 5}
                    ]
                },
                {
                    "name": "Additional Details",
                    "description": "Any specific requirements, inspiration, or additional information",
                    "selection_type": "rich_text",
                    "is_required": False,
                    "display_order": 3
                }
            ]
        }
    ]
}

response6 = requests.post(f"{BASE_URL}/wizards", json=wizard6, headers=headers)
if response6.status_code == 201:
    print("[OK] Website Design Questionnaire created")
else:
    print(f"[ERROR] Failed: {response6.text}")

print("\n[DONE] Created 6 diverse wizard templates!")
print("\nSummary:")
print("1. Employee Onboarding Portal")
print("2. Project Planning Wizard")
print("3. Restaurant Reservation System")
print("4. Travel Booking Assistant")
print("5. Fitness Program Designer")
print("6. Website Design Questionnaire")
