"""
Create Job Application and Customer Feedback wizards with dependencies
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def get_admin_token():
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin", "password": "Admin@123"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def get_category_id(token, category_name):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/wizards/categories", headers=headers)
    if response.status_code == 200:
        categories = response.json()
        for cat in categories:
            if cat['name'] == category_name:
                return cat['id']
    return None

def create_wizard_4_job_application(token, category_id):
    """Job Application Wizard with complex dependencies"""
    wizard_data = {
        "name": "Job Application Form",
        "description": "Apply for positions at our company with conditional questions based on role",
        "category_id": category_id,
        "icon": "work",
        "is_published": True,
        "allow_templates": True,
        "require_login": False,
        "auto_save": True,
        "estimated_time": 15,
        "difficulty_level": "medium",
        "tags": ["hr", "recruitment", "application", "jobs"],
        "steps": [
            {
                "name": "Position Information",
                "description": "Select the position you're applying for",
                "step_order": 1,
                "is_required": True,
                "is_skippable": False,
                "option_sets": [
                    {
                        "name": "Which position interests you?",
                        "selection_type": "single_select",
                        "is_required": True,
                        "min_selections": 0,
                        "options": [
                            {"label": "Software Engineer", "value": "software_eng", "description": "Full-time developer role", "is_default": False},
                            {"label": "Senior Software Engineer", "value": "senior_software_eng", "description": "5+ years experience", "is_default": False},
                            {"label": "Product Manager", "value": "product_mgr", "description": "Lead product development", "is_default": False},
                            {"label": "UX Designer", "value": "ux_designer", "description": "User experience design", "is_default": False},
                            {"label": "Sales Representative", "value": "sales_rep", "description": "B2B sales position", "is_default": False},
                            {"label": "Intern", "value": "intern", "description": "Summer internship program", "is_default": False}
                        ]
                    },
                    {
                        "name": "Employment type",
                        "selection_type": "single_select",
                        "is_required": True,
                        "min_selections": 0,
                        "options": [
                            {"label": "Full-time", "value": "fulltime", "description": "", "is_default": False},
                            {"label": "Part-time", "value": "parttime", "description": "", "is_default": False},
                            {"label": "Contract", "value": "contract", "description": "", "is_default": False}
                        ]
                    }
                ]
            },
            {
                "name": "Experience",
                "description": "Tell us about your background",
                "step_order": 2,
                "is_required": True,
                "is_skippable": False,
                "option_sets": [
                    {
                        "name": "Years of relevant experience",
                        "selection_type": "single_select",
                        "is_required": True,
                        "min_selections": 0,
                        "options": [
                            {"label": "No experience", "value": "exp0", "description": "Fresh graduate or career change", "is_default": False},
                            {"label": "1-2 years", "value": "exp1_2", "description": "", "is_default": False},
                            {"label": "3-5 years", "value": "exp3_5", "description": "", "is_default": False},
                            {"label": "5-10 years", "value": "exp5_10", "description": "", "is_default": False},
                            {"label": "10+ years", "value": "exp10plus", "description": "", "is_default": False}
                        ]
                    }
                ]
            },
            {
                "name": "Technical Skills",
                "description": "Rate your technical proficiency",
                "step_order": 3,
                "is_required": False,
                "is_skippable": True,
                "option_sets": [
                    {
                        "name": "Primary programming language",
                        "selection_type": "single_select",
                        "is_required": True,
                        "min_selections": 0,
                        "options": [
                            {"label": "Python", "value": "python", "description": "", "is_default": False},
                            {"label": "JavaScript/TypeScript", "value": "javascript", "description": "", "is_default": False},
                            {"label": "Java", "value": "java", "description": "", "is_default": False},
                            {"label": "C++", "value": "cpp", "description": "", "is_default": False},
                            {"label": "Go", "value": "go", "description": "", "is_default": False},
                            {"label": "Other", "value": "other_lang", "description": "", "is_default": False}
                        ]
                    },
                    {
                        "name": "Framework experience",
                        "selection_type": "multiple_select",
                        "is_required": False,
                        "min_selections": 0,
                        "options": [
                            {"label": "React", "value": "react", "description": "", "is_default": False},
                            {"label": "Angular", "value": "angular", "description": "", "is_default": False},
                            {"label": "Vue.js", "value": "vue", "description": "", "is_default": False},
                            {"label": "Django", "value": "django", "description": "", "is_default": False},
                            {"label": "Spring Boot", "value": "spring", "description": "", "is_default": False},
                            {"label": "Node.js", "value": "nodejs", "description": "", "is_default": False}
                        ]
                    }
                ]
            },
            {
                "name": "Design Portfolio",
                "description": "Share your design work",
                "step_order": 4,
                "is_required": False,
                "is_skippable": True,
                "option_sets": [
                    {
                        "name": "Portfolio URL",
                        "selection_type": "text_input",
                        "is_required": True,
                        "min_selections": 0,
                        "placeholder": "https://yourportfolio.com",
                        "help_text": "Link to your design portfolio or Behance/Dribbble profile",
                        "options": []
                    },
                    {
                        "name": "Design tools you use",
                        "selection_type": "multiple_select",
                        "is_required": True,
                        "min_selections": 0,
                        "options": [
                            {"label": "Figma", "value": "figma", "description": "", "is_default": False},
                            {"label": "Adobe XD", "value": "xd", "description": "", "is_default": False},
                            {"label": "Sketch", "value": "sketch", "description": "", "is_default": False},
                            {"label": "Adobe Photoshop", "value": "photoshop", "description": "", "is_default": False},
                            {"label": "Illustrator", "value": "illustrator", "description": "", "is_default": False}
                        ]
                    }
                ]
            },
            {
                "name": "Availability",
                "description": "When can you start?",
                "step_order": 5,
                "is_required": True,
                "is_skippable": False,
                "option_sets": [
                    {
                        "name": "Start date",
                        "selection_type": "single_select",
                        "is_required": True,
                        "min_selections": 0,
                        "options": [
                            {"label": "Immediately", "value": "immediate", "description": "Can start within 1 week", "is_default": False},
                            {"label": "2 weeks notice", "value": "weeks2", "description": "", "is_default": False},
                            {"label": "1 month notice", "value": "month1", "description": "", "is_default": False},
                            {"label": "2+ months", "value": "months2plus", "description": "", "is_default": False}
                        ]
                    },
                    {
                        "name": "Preferred work arrangement",
                        "selection_type": "single_select",
                        "is_required": True,
                        "min_selections": 0,
                        "options": [
                            {"label": "Remote", "value": "remote", "description": "Work from anywhere", "is_default": False},
                            {"label": "Hybrid", "value": "hybrid", "description": "Mix of office and remote", "is_default": False},
                            {"label": "On-site", "value": "onsite", "description": "Full-time in office", "is_default": False}
                        ]
                    }
                ]
            }
        ]
    }

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/wizards/", headers=headers, json=wizard_data)

    if response.status_code == 201:
        wizard = response.json()
        print(f"[OK] Created Job Application Wizard (ID: {wizard['id']})")

        wizard_full = requests.get(f"{BASE_URL}/wizards/{wizard['id']}", headers=headers).json()

        # Get option IDs
        position_options = wizard_full['steps'][0]['option_sets'][0]['options']
        employment_type_options = wizard_full['steps'][0]['option_sets'][1]['options']
        experience_options = wizard_full['steps'][1]['option_sets'][0]['options']
        tech_skills_lang_options = wizard_full['steps'][2]['option_sets'][0]['options']
        tech_skills_framework_options = wizard_full['steps'][2]['option_sets'][1]['options']
        design_tools_options = wizard_full['steps'][3]['option_sets'][1]['options']

        # Get specific IDs
        software_eng_id = next(opt['id'] for opt in position_options if opt['value'] == 'software_eng')
        senior_software_eng_id = next(opt['id'] for opt in position_options if opt['value'] == 'senior_software_eng')
        ux_designer_id = next(opt['id'] for opt in position_options if opt['value'] == 'ux_designer')
        intern_id = next(opt['id'] for opt in position_options if opt['value'] == 'intern')
        fulltime_id = next(opt['id'] for opt in employment_type_options if opt['value'] == 'fulltime')
        exp0_id = next(opt['id'] for opt in experience_options if opt['value'] == 'exp0')
        exp1_2_id = next(opt['id'] for opt in experience_options if opt['value'] == 'exp1_2')

        # Dependencies: Show tech skills only for engineer positions
        for tech_opt in tech_skills_lang_options + tech_skills_framework_options:
            for eng_id in [software_eng_id, senior_software_eng_id]:
                dep_response = requests.post(
                    f"{BASE_URL}/wizards/options/{tech_opt['id']}/dependencies",
                    headers=headers,
                    json={"depends_on_option_id": eng_id, "dependency_type": "show_if"}
                )

        print(f"  [OK] Added tech skills dependencies for engineer positions")

        # Dependencies: Show design portfolio only for UX Designer
        for design_opt in design_tools_options:
            dep_response = requests.post(
                f"{BASE_URL}/wizards/options/{design_opt['id']}/dependencies",
                headers=headers,
                json={"depends_on_option_id": ux_designer_id, "dependency_type": "show_if"}
            )

        print(f"  [OK] Added design portfolio dependencies for UX Designer")

        # Disable full-time for interns
        dep_response = requests.post(
            f"{BASE_URL}/wizards/options/{fulltime_id}/dependencies",
            headers=headers,
            json={"depends_on_option_id": intern_id, "dependency_type": "disable_if"}
        )
        print(f"  [OK] Disabled full-time employment for interns")

        # Hide 0 experience for senior positions
        dep_response = requests.post(
            f"{BASE_URL}/wizards/options/{exp0_id}/dependencies",
            headers=headers,
            json={"depends_on_option_id": senior_software_eng_id, "dependency_type": "hide_if"}
        )
        dep_response = requests.post(
            f"{BASE_URL}/wizards/options/{exp1_2_id}/dependencies",
            headers=headers,
            json={"depends_on_option_id": senior_software_eng_id, "dependency_type": "hide_if"}
        )
        print(f"  [OK] Hidden low experience options for senior positions")

        return wizard['id']
    else:
        print(f"[FAIL] Failed to create Job Application Wizard: {response.text}")
        return None

def create_wizard_5_feedback(token, category_id):
    """Customer Feedback Form with dynamic questions"""
    wizard_data = {
        "name": "Customer Satisfaction Survey",
        "description": "Share your experience and help us improve our service",
        "category_id": category_id,
        "icon": "feedback",
        "is_published": True,
        "allow_templates": False,
        "require_login": False,
        "auto_save": True,
        "estimated_time": 5,
        "difficulty_level": "easy",
        "tags": ["feedback", "survey", "customer", "satisfaction"],
        "steps": [
            {
                "name": "Overall Experience",
                "description": "Rate your experience",
                "step_order": 1,
                "is_required": True,
                "is_skippable": False,
                "option_sets": [
                    {
                        "name": "How satisfied are you with our service?",
                        "selection_type": "single_select",
                        "is_required": True,
                        "min_selections": 0,
                        "options": [
                            {"label": "Very Satisfied", "value": "very_satisfied", "description": "😊 Exceeded expectations", "is_default": False},
                            {"label": "Satisfied", "value": "satisfied", "description": "🙂 Met expectations", "is_default": False},
                            {"label": "Neutral", "value": "neutral", "description": "😐 Average experience", "is_default": False},
                            {"label": "Dissatisfied", "value": "dissatisfied", "description": "🙁 Below expectations", "is_default": False},
                            {"label": "Very Dissatisfied", "value": "very_dissatisfied", "description": "😞 Far below expectations", "is_default": False}
                        ]
                    }
                ]
            },
            {
                "name": "What went well",
                "description": "Tell us about positive experiences",
                "step_order": 2,
                "is_required": False,
                "is_skippable": True,
                "option_sets": [
                    {
                        "name": "What did you like most?",
                        "selection_type": "multiple_select",
                        "is_required": True,
                        "min_selections": 0,
                        "options": [
                            {"label": "Fast response time", "value": "fast_response", "description": "", "is_default": False},
                            {"label": "Knowledgeable staff", "value": "knowledgeable_staff", "description": "", "is_default": False},
                            {"label": "Easy to use", "value": "easy_use", "description": "", "is_default": False},
                            {"label": "Good value", "value": "good_value", "description": "", "is_default": False},
                            {"label": "Quality product", "value": "quality_product", "description": "", "is_default": False}
                        ]
                    }
                ]
            },
            {
                "name": "Areas for improvement",
                "description": "Help us understand what needs work",
                "step_order": 3,
                "is_required": False,
                "is_skippable": True,
                "option_sets": [
                    {
                        "name": "What could we improve?",
                        "selection_type": "multiple_select",
                        "is_required": True,
                        "min_selections": 0,
                        "options": [
                            {"label": "Response time", "value": "improve_response", "description": "", "is_default": False},
                            {"label": "Product quality", "value": "improve_quality", "description": "", "is_default": False},
                            {"label": "Staff training", "value": "improve_training", "description": "", "is_default": False},
                            {"label": "Website/App", "value": "improve_website", "description": "", "is_default": False},
                            {"label": "Pricing", "value": "improve_pricing", "description": "", "is_default": False}
                        ]
                    },
                    {
                        "name": "Please explain what went wrong",
                        "selection_type": "text_input",
                        "is_required": True,
                        "min_selections": 0,
                        "placeholder": "Tell us more about your experience...",
                        "help_text": "Your feedback helps us improve",
                        "options": []
                    }
                ]
            },
            {
                "name": "Recommendation",
                "description": "Would you recommend us?",
                "step_order": 4,
                "is_required": True,
                "is_skippable": False,
                "option_sets": [
                    {
                        "name": "Would you recommend us to a friend?",
                        "selection_type": "single_select",
                        "is_required": True,
                        "min_selections": 0,
                        "options": [
                            {"label": "Definitely yes", "value": "recommend_yes", "description": "", "is_default": False},
                            {"label": "Probably yes", "value": "recommend_maybe", "description": "", "is_default": False},
                            {"label": "Not sure", "value": "recommend_neutral", "description": "", "is_default": False},
                            {"label": "Probably not", "value": "recommend_no", "description": "", "is_default": False},
                            {"label": "Definitely not", "value": "recommend_never", "description": "", "is_default": False}
                        ]
                    }
                ]
            }
        ]
    }

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/wizards/", headers=headers, json=wizard_data)

    if response.status_code == 201:
        wizard = response.json()
        print(f"[OK] Created Customer Feedback Wizard (ID: {wizard['id']})")

        wizard_full = requests.get(f"{BASE_URL}/wizards/{wizard['id']}", headers=headers).json()

        # Get option IDs
        satisfaction_options = wizard_full['steps'][0]['option_sets'][0]['options']
        positive_options = wizard_full['steps'][1]['option_sets'][0]['options']
        improvement_options = wizard_full['steps'][2]['option_sets'][0]['options']

        # Get specific IDs
        very_satisfied_id = next(opt['id'] for opt in satisfaction_options if opt['value'] == 'very_satisfied')
        satisfied_id = next(opt['id'] for opt in satisfaction_options if opt['value'] == 'satisfied')
        dissatisfied_id = next(opt['id'] for opt in satisfaction_options if opt['value'] == 'dissatisfied')
        very_dissatisfied_id = next(opt['id'] for opt in satisfaction_options if opt['value'] == 'very_dissatisfied')

        # Show "what went well" only for positive feedback
        for pos_opt in positive_options:
            for sat_id in [very_satisfied_id, satisfied_id]:
                dep_response = requests.post(
                    f"{BASE_URL}/wizards/options/{pos_opt['id']}/dependencies",
                    headers=headers,
                    json={"depends_on_option_id": sat_id, "dependency_type": "show_if"}
                )

        print(f"  [OK] Positive feedback section shows only for satisfied customers")

        # Show "areas for improvement" only for negative feedback
        for improve_opt in improvement_options:
            for dissat_id in [dissatisfied_id, very_dissatisfied_id]:
                dep_response = requests.post(
                    f"{BASE_URL}/wizards/options/{improve_opt['id']}/dependencies",
                    headers=headers,
                    json={"depends_on_option_id": dissat_id, "dependency_type": "show_if"}
                )

        print(f"  [OK] Improvement section shows only for dissatisfied customers")

        return wizard['id']
    else:
        print(f"[FAIL] Failed to create Feedback Wizard: {response.text}")
        return None

def main():
    print("=" * 60)
    print("Creating Job Application and Feedback Wizards")
    print("=" * 60)

    # Get admin token
    print("\n[1] Logging in as admin...")
    token = get_admin_token()
    if not token:
        print("[FAIL] Could not login")
        return
    print("[OK] Logged in")

    # Get category
    print("\n[2] Getting category...")
    category_id = get_category_id(token, "IT & Technology")
    print(f"[OK] Category ID: {category_id}")

    # Create wizards
    print("\n[3] Creating wizards...")
    print("-" * 60)

    wizard4_id = create_wizard_4_job_application(token, category_id)
    print()

    wizard5_id = create_wizard_5_feedback(token, category_id)
    print()

    print("-" * 60)
    print(f"\n[DONE] Created {sum(1 for w in [wizard4_id, wizard5_id] if w)} wizards")
    print("\nTest at: http://localhost:3000")

if __name__ == "__main__":
    main()
