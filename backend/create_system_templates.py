"""
Script to create system wizard templates for the Template Gallery
These are reusable wizard configurations that users can clone
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.wizard_template import WizardTemplate
import uuid

def create_system_templates():
    """Create 6 system wizard templates"""
    db = SessionLocal()

    try:
        # Delete all existing templates
        print("[*] Deleting existing templates...")
        db.query(WizardTemplate).delete()
        db.commit()
        print("[OK] Existing templates deleted")

        templates = []

        # Template 1: Employee Onboarding Portal
        template1 = WizardTemplate(
            id=uuid.uuid4(),
            template_name="Employee Onboarding Portal",
            template_description="Streamline your employee onboarding process with this comprehensive workflow. Collect personal information, assign departments, configure equipment, and ensure compliance.",
            category="Human Resources",
            icon="person_add",
            difficulty_level="easy",
            estimated_time=15,
            tags=["hr", "onboarding", "employee", "business"],
            step_count=4,
            option_set_count=9,
            is_system_template=True,
            created_by="system",
            usage_count=0,
            average_rating=0,
            wizard_structure={
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
                            {"name": "Full Name", "description": "Enter your full legal name", "selection_type": "text_input", "is_required": True, "display_order": 1},
                            {"name": "Date of Birth", "description": "Select your date of birth", "selection_type": "date_input", "is_required": True, "display_order": 2},
                            {"name": "Employment Type", "description": "Select your employment status", "selection_type": "single_select", "is_required": True, "display_order": 3, "options": [
                                {"label": "Full-time", "value": "full_time", "display_order": 1},
                                {"label": "Part-time", "value": "part_time", "display_order": 2},
                                {"label": "Contract", "value": "contract", "display_order": 3},
                                {"label": "Intern", "value": "intern", "display_order": 4}
                            ]}
                        ]
                    },
                    {
                        "name": "Department & Role",
                        "description": "Work assignment details",
                        "step_order": 2,
                        "option_sets": [
                            {"name": "Department", "description": "Select your department", "selection_type": "single_select", "is_required": True, "display_order": 1, "options": [
                                {"label": "Engineering", "value": "engineering", "display_order": 1},
                                {"label": "Sales", "value": "sales", "display_order": 2},
                                {"label": "Marketing", "value": "marketing", "display_order": 3},
                                {"label": "Human Resources", "value": "hr", "display_order": 4},
                                {"label": "Finance", "value": "finance", "display_order": 5}
                            ]},
                            {"name": "Start Date", "description": "When will you start?", "selection_type": "date_input", "is_required": True, "display_order": 2},
                            {"name": "Work Schedule Preference", "description": "Preferred working hours", "selection_type": "single_select", "is_required": False, "display_order": 3, "options": [
                                {"label": "9 AM - 5 PM", "value": "9to5", "display_order": 1},
                                {"label": "10 AM - 6 PM", "value": "10to6", "display_order": 2},
                                {"label": "Flexible", "value": "flexible", "display_order": 3}
                            ]}
                        ]
                    },
                    {
                        "name": "Equipment & Setup",
                        "description": "Hardware and software requirements",
                        "step_order": 3,
                        "option_sets": [
                            {"name": "Equipment Needed", "description": "Select all equipment you need", "selection_type": "multiple_select", "is_required": True, "display_order": 1, "options": [
                                {"label": "Laptop", "value": "laptop", "display_order": 1},
                                {"label": "Desktop Monitor", "value": "monitor", "display_order": 2},
                                {"label": "Keyboard & Mouse", "value": "peripherals", "display_order": 3},
                                {"label": "Headset", "value": "headset", "display_order": 4},
                                {"label": "Phone", "value": "phone", "display_order": 5}
                            ]},
                            {"name": "Office Location Preference", "description": "Where would you like to work?", "selection_type": "single_select", "is_required": True, "display_order": 2, "options": [
                                {"label": "Main Office", "value": "main", "display_order": 1},
                                {"label": "Remote", "value": "remote", "display_order": 2},
                                {"label": "Hybrid", "value": "hybrid", "display_order": 3}
                            ]}
                        ]
                    },
                    {
                        "name": "Documents & Compliance",
                        "description": "Required documentation",
                        "step_order": 4,
                        "option_sets": [
                            {"name": "Emergency Contact Name", "description": "Full name of emergency contact", "selection_type": "text_input", "is_required": True, "display_order": 1},
                            {"name": "Emergency Contact Phone", "description": "Emergency contact phone number", "selection_type": "text_input", "is_required": True, "display_order": 2},
                            {"name": "Additional Comments", "description": "Any special requirements or notes", "selection_type": "rich_text", "is_required": False, "display_order": 3}
                        ]
                    }
                ]
            },
            is_active=True
        )
        templates.append(template1)

        # Template 2: Project Planning Wizard
        template2 = WizardTemplate(
            id=uuid.uuid4(),
            template_name="Project Planning Wizard",
            template_description="Plan and configure projects with ease. Define goals, set timelines, allocate resources, and establish success metrics for any type of project.",
            category="Project Management",
            icon="assignment",
            difficulty_level="medium",
            estimated_time=20,
            tags=["project", "planning", "management", "workflow"],
            step_count=4,
            option_set_count=10,
            is_system_template=True,
            created_by="system",
            wizard_structure={
                "name": "Project Planning Wizard",
                "description": "Plan and configure a new project from start to finish",
                "is_published": True,
                "steps": [
                    {
                        "name": "Project Basics",
                        "step_order": 1,
                        "option_sets": [
                            {"name": "Project Name", "selection_type": "text_input", "is_required": True, "display_order": 1},
                            {"name": "Project Type", "selection_type": "single_select", "is_required": True, "display_order": 2, "options": [
                                {"label": "Software Development", "value": "software", "display_order": 1},
                                {"label": "Marketing Campaign", "value": "marketing", "display_order": 2},
                                {"label": "Infrastructure", "value": "infrastructure", "display_order": 3}
                            ]},
                            {"name": "Priority Level", "description": "1=Low, 5=Critical", "selection_type": "slider", "is_required": True, "min_value": 1, "max_value": 5, "display_order": 3}
                        ]
                    },
                    {
                        "name": "Timeline & Budget",
                        "step_order": 2,
                        "option_sets": [
                            {"name": "Start Date", "selection_type": "date_input", "is_required": True, "display_order": 1},
                            {"name": "Target Completion Date", "selection_type": "date_input", "is_required": True, "display_order": 2},
                            {"name": "Budget Range", "selection_type": "single_select", "is_required": True, "display_order": 3, "options": [
                                {"label": "Under $10K", "value": "under_10k", "display_order": 1},
                                {"label": "$10K - $50K", "value": "10k_50k", "display_order": 2},
                                {"label": "Over $50K", "value": "over_50k", "display_order": 3}
                            ]}
                        ]
                    },
                    {
                        "name": "Team & Resources",
                        "step_order": 3,
                        "option_sets": [
                            {"name": "Team Size", "selection_type": "number_input", "is_required": True, "min_value": 1, "max_value": 20, "display_order": 1},
                            {"name": "Required Skills", "selection_type": "multiple_select", "is_required": True, "display_order": 2, "options": [
                                {"label": "Frontend Development", "value": "frontend", "display_order": 1},
                                {"label": "Backend Development", "value": "backend", "display_order": 2},
                                {"label": "Design/UX", "value": "design", "display_order": 3}
                            ]}
                        ]
                    },
                    {
                        "name": "Goals & Success Metrics",
                        "step_order": 4,
                        "option_sets": [
                            {"name": "Project Goals", "selection_type": "rich_text", "is_required": True, "display_order": 1},
                            {"name": "Success Importance", "selection_type": "rating", "is_required": True, "min_value": 1, "max_value": 5, "display_order": 2}
                        ]
                    }
                ]
            },
            is_active=True
        )
        templates.append(template2)

        # Template 3: Restaurant Reservation
        template3 = WizardTemplate(
            id=uuid.uuid4(),
            template_name="Restaurant Reservation System",
            template_description="Simple and elegant reservation system for restaurants. Collect guest information, preferences, and dietary requirements seamlessly.",
            category="Hospitality",
            icon="restaurant",
            difficulty_level="easy",
            estimated_time=10,
            tags=["restaurant", "booking", "reservation", "dining"],
            step_count=4,
            option_set_count=9,
            is_system_template=True,
            created_by="system",
            wizard_structure={
                "name": "Restaurant Reservation System",
                "steps": [
                    {
                        "name": "Guest Information",
                        "step_order": 1,
                        "option_sets": [
                            {"name": "Guest Name", "selection_type": "text_input", "is_required": True, "display_order": 1},
                            {"name": "Contact Phone", "selection_type": "text_input", "is_required": True, "display_order": 2},
                            {"name": "Number of Guests", "selection_type": "number_input", "is_required": True, "min_value": 1, "max_value": 12, "display_order": 3}
                        ]
                    },
                    {
                        "name": "Date & Time",
                        "step_order": 2,
                        "option_sets": [
                            {"name": "Reservation Date", "selection_type": "date_input", "is_required": True, "display_order": 1},
                            {"name": "Preferred Time", "selection_type": "time_input", "is_required": True, "display_order": 2}
                        ]
                    },
                    {
                        "name": "Preferences",
                        "step_order": 3,
                        "option_sets": [
                            {"name": "Seating Preference", "selection_type": "single_select", "is_required": False, "display_order": 1, "options": [
                                {"label": "Indoor", "value": "indoor", "display_order": 1},
                                {"label": "Outdoor/Patio", "value": "outdoor", "display_order": 2},
                                {"label": "Bar Area", "value": "bar", "display_order": 3}
                            ]},
                            {"name": "Ambiance Preference", "description": "1=Quiet, 5=Lively", "selection_type": "slider", "is_required": False, "min_value": 1, "max_value": 5, "display_order": 2}
                        ]
                    },
                    {
                        "name": "Dietary Requirements",
                        "step_order": 4,
                        "option_sets": [
                            {"name": "Dietary Restrictions", "selection_type": "multiple_select", "is_required": False, "display_order": 1, "options": [
                                {"label": "Vegetarian", "value": "vegetarian", "display_order": 1},
                                {"label": "Vegan", "value": "vegan", "display_order": 2},
                                {"label": "Gluten-Free", "value": "gluten_free", "display_order": 3}
                            ]},
                            {"name": "Special Requests", "selection_type": "rich_text", "is_required": False, "display_order": 2}
                        ]
                    }
                ]
            },
            is_active=True
        )
        templates.append(template3)

        # Template 4: Travel Booking
        template4 = WizardTemplate(
            id=uuid.uuid4(),
            template_name="Travel Booking Assistant",
            template_description="Complete travel planning solution. Book vacations, business trips, and adventures with customizable preferences and accommodations.",
            category="Travel & Tourism",
            icon="flight_takeoff",
            difficulty_level="medium",
            estimated_time=25,
            tags=["travel", "booking", "vacation", "trip"],
            step_count=4,
            option_set_count=11,
            is_system_template=True,
            created_by="system",
            wizard_structure={
                "name": "Travel Booking Assistant",
                "steps": [
                    {
                        "name": "Trip Details",
                        "step_order": 1,
                        "option_sets": [
                            {"name": "Trip Type", "selection_type": "single_select", "is_required": True, "display_order": 1, "options": [
                                {"label": "Vacation", "value": "vacation", "display_order": 1},
                                {"label": "Business", "value": "business", "display_order": 2},
                                {"label": "Adventure", "value": "adventure", "display_order": 3}
                            ]},
                            {"name": "Number of Travelers", "selection_type": "number_input", "is_required": True, "min_value": 1, "max_value": 10, "display_order": 2},
                            {"name": "Trip Duration", "selection_type": "single_select", "is_required": True, "display_order": 3, "options": [
                                {"label": "1-3 days", "value": "short", "display_order": 1},
                                {"label": "4-7 days", "value": "week", "display_order": 2},
                                {"label": "8-14 days", "value": "two_weeks", "display_order": 3}
                            ]}
                        ]
                    },
                    {
                        "name": "Dates & Destination",
                        "step_order": 2,
                        "option_sets": [
                            {"name": "Departure Date", "selection_type": "date_input", "is_required": True, "display_order": 1},
                            {"name": "Return Date", "selection_type": "date_input", "is_required": True, "display_order": 2},
                            {"name": "Destination Type", "selection_type": "multiple_select", "is_required": True, "display_order": 3, "options": [
                                {"label": "Beach", "value": "beach", "display_order": 1},
                                {"label": "City", "value": "city", "display_order": 2},
                                {"label": "Mountains", "value": "mountains", "display_order": 3}
                            ]}
                        ]
                    },
                    {
                        "name": "Accommodations",
                        "step_order": 3,
                        "option_sets": [
                            {"name": "Accommodation Type", "selection_type": "single_select", "is_required": True, "display_order": 1, "options": [
                                {"label": "Hotel", "value": "hotel", "display_order": 1},
                                {"label": "Resort", "value": "resort", "display_order": 2},
                                {"label": "Vacation Rental", "value": "rental", "display_order": 3}
                            ]},
                            {"name": "Budget per Night", "selection_type": "single_select", "is_required": True, "display_order": 2, "options": [
                                {"label": "Under $100", "value": "budget", "display_order": 1},
                                {"label": "$100-$200", "value": "moderate", "display_order": 2},
                                {"label": "$200+", "value": "luxury", "display_order": 3}
                            ]},
                            {"name": "Hotel Amenities Priority", "description": "1=Not Important, 5=Essential", "selection_type": "slider", "is_required": False, "min_value": 1, "max_value": 5, "display_order": 3}
                        ]
                    },
                    {
                        "name": "Activities & Preferences",
                        "step_order": 4,
                        "option_sets": [
                            {"name": "Preferred Activities", "selection_type": "multiple_select", "is_required": False, "display_order": 1, "options": [
                                {"label": "Sightseeing", "value": "sightseeing", "display_order": 1},
                                {"label": "Museums & Culture", "value": "culture", "display_order": 2},
                                {"label": "Outdoor Adventures", "value": "outdoor", "display_order": 3}
                            ]},
                            {"name": "Overall Trip Rating Goal", "selection_type": "rating", "is_required": False, "min_value": 1, "max_value": 5, "display_order": 2}
                        ]
                    }
                ]
            },
            is_active=True
        )
        templates.append(template4)

        # Template 5: Fitness Program
        template5 = WizardTemplate(
            id=uuid.uuid4(),
            template_name="Fitness Program Designer",
            template_description="Create personalized fitness plans tailored to your goals, schedule, and available equipment. Perfect for gyms and personal trainers.",
            category="Health & Fitness",
            icon="fitness_center",
            difficulty_level="medium",
            estimated_time=18,
            tags=["fitness", "health", "workout", "wellness"],
            step_count=4,
            option_set_count=10,
            is_system_template=True,
            created_by="system",
            wizard_structure={
                "name": "Fitness Program Designer",
                "steps": [
                    {
                        "name": "Personal Profile",
                        "step_order": 1,
                        "option_sets": [
                            {"name": "Age Group", "selection_type": "single_select", "is_required": True, "display_order": 1, "options": [
                                {"label": "18-25", "value": "young_adult", "display_order": 1},
                                {"label": "26-35", "value": "adult", "display_order": 2},
                                {"label": "36-50", "value": "middle_age", "display_order": 3}
                            ]},
                            {"name": "Current Fitness Level", "selection_type": "single_select", "is_required": True, "display_order": 2, "options": [
                                {"label": "Beginner", "value": "beginner", "display_order": 1},
                                {"label": "Intermediate", "value": "intermediate", "display_order": 2},
                                {"label": "Advanced", "value": "advanced", "display_order": 3}
                            ]},
                            {"name": "Fitness Experience", "description": "1=None, 5=Expert", "selection_type": "slider", "is_required": True, "min_value": 1, "max_value": 5, "display_order": 3}
                        ]
                    },
                    {
                        "name": "Goals & Timeline",
                        "step_order": 2,
                        "option_sets": [
                            {"name": "Primary Goals", "selection_type": "multiple_select", "is_required": True, "display_order": 1, "options": [
                                {"label": "Weight Loss", "value": "weight_loss", "display_order": 1},
                                {"label": "Muscle Gain", "value": "muscle_gain", "display_order": 2},
                                {"label": "Endurance", "value": "endurance", "display_order": 3}
                            ]},
                            {"name": "Target Achievement Date", "selection_type": "date_input", "is_required": False, "display_order": 2},
                            {"name": "Commitment Level", "description": "1=Casual, 5=Very Committed", "selection_type": "rating", "is_required": True, "min_value": 1, "max_value": 5, "display_order": 3}
                        ]
                    },
                    {
                        "name": "Schedule & Availability",
                        "step_order": 3,
                        "option_sets": [
                            {"name": "Days Available per Week", "selection_type": "number_input", "is_required": True, "min_value": 1, "max_value": 7, "display_order": 1},
                            {"name": "Preferred Workout Time", "selection_type": "single_select", "is_required": True, "display_order": 2, "options": [
                                {"label": "Early Morning", "value": "early_morning", "display_order": 1},
                                {"label": "Evening", "value": "evening", "display_order": 2},
                                {"label": "Flexible", "value": "flexible", "display_order": 3}
                            ]}
                        ]
                    },
                    {
                        "name": "Equipment & Preferences",
                        "step_order": 4,
                        "option_sets": [
                            {"name": "Available Equipment", "selection_type": "multiple_select", "is_required": True, "display_order": 1, "options": [
                                {"label": "No Equipment (Bodyweight)", "value": "bodyweight", "display_order": 1},
                                {"label": "Dumbbells", "value": "dumbbells", "display_order": 2},
                                {"label": "Full Gym Access", "value": "gym", "display_order": 3}
                            ]},
                            {"name": "Additional Notes", "selection_type": "rich_text", "is_required": False, "display_order": 2}
                        ]
                    }
                ]
            },
            is_active=True
        )
        templates.append(template5)

        # Template 6: Website Design
        template6 = WizardTemplate(
            id=uuid.uuid4(),
            template_name="Website Design Questionnaire",
            template_description="Comprehensive requirements gathering for web design projects. Define scope, style, features, and budget for your next website.",
            category="Web Development",
            icon="web",
            difficulty_level="hard",
            estimated_time=30,
            tags=["website", "design", "web", "development"],
            step_count=4,
            option_set_count=10,
            is_system_template=True,
            created_by="system",
            wizard_structure={
                "name": "Website Design Questionnaire",
                "steps": [
                    {
                        "name": "Project Overview",
                        "step_order": 1,
                        "option_sets": [
                            {"name": "Company/Project Name", "selection_type": "text_input", "is_required": True, "display_order": 1},
                            {"name": "Website Type", "selection_type": "single_select", "is_required": True, "display_order": 2, "options": [
                                {"label": "Business/Corporate", "value": "business", "display_order": 1},
                                {"label": "E-commerce", "value": "ecommerce", "display_order": 2},
                                {"label": "Portfolio", "value": "portfolio", "display_order": 3}
                            ]},
                            {"name": "Project Urgency", "description": "1=Flexible, 5=Very Urgent", "selection_type": "slider", "is_required": True, "min_value": 1, "max_value": 5, "display_order": 3}
                        ]
                    },
                    {
                        "name": "Design Preferences",
                        "step_order": 2,
                        "option_sets": [
                            {"name": "Design Style", "selection_type": "multiple_select", "is_required": True, "display_order": 1, "options": [
                                {"label": "Modern & Minimalist", "value": "modern", "display_order": 1},
                                {"label": "Bold & Colorful", "value": "bold", "display_order": 2},
                                {"label": "Professional & Corporate", "value": "corporate", "display_order": 3}
                            ]},
                            {"name": "Primary Brand Color", "selection_type": "color_picker", "is_required": False, "display_order": 2},
                            {"name": "Design Importance", "description": "1=Basic, 5=Premium", "selection_type": "rating", "is_required": True, "min_value": 1, "max_value": 5, "display_order": 3}
                        ]
                    },
                    {
                        "name": "Features & Functionality",
                        "step_order": 3,
                        "option_sets": [
                            {"name": "Core Features", "selection_type": "multiple_select", "is_required": True, "display_order": 1, "options": [
                                {"label": "Contact Form", "value": "contact", "display_order": 1},
                                {"label": "Blog/News", "value": "blog", "display_order": 2},
                                {"label": "Photo Gallery", "value": "gallery", "display_order": 3}
                            ]},
                            {"name": "Expected Number of Pages", "selection_type": "number_input", "is_required": True, "min_value": 1, "max_value": 100, "display_order": 2}
                        ]
                    },
                    {
                        "name": "Timeline & Budget",
                        "step_order": 4,
                        "option_sets": [
                            {"name": "Desired Launch Date", "selection_type": "date_input", "is_required": False, "display_order": 1},
                            {"name": "Budget Range", "selection_type": "single_select", "is_required": True, "display_order": 2, "options": [
                                {"label": "Under $5,000", "value": "under_5k", "display_order": 1},
                                {"label": "$5,000 - $10,000", "value": "5k_10k", "display_order": 2},
                                {"label": "Over $10,000", "value": "over_10k", "display_order": 3}
                            ]},
                            {"name": "Additional Details", "selection_type": "rich_text", "is_required": False, "display_order": 3}
                        ]
                    }
                ]
            },
            is_active=True
        )
        templates.append(template6)

        # Add all templates to database
        for template in templates:
            db.add(template)

        db.commit()

        print(f"\n[OK] Created {len(templates)} system templates!")
        print("\nTemplates created:")
        for i, template in enumerate(templates, 1):
            print(f"{i}. {template.template_name} ({template.category}) - {template.difficulty_level}")

    except Exception as e:
        print(f"[ERROR] Failed to create templates: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("[*] Creating system wizard templates...")
    create_system_templates()
    print("\n[DONE] Template Gallery populated!")
