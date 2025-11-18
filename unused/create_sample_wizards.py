"""
Script to create 5 sample wizards with conditional dependencies
Use cases: IT Support, E-commerce, Logistics, Job Application, Customer Feedback
"""
import requests
import json
from uuid import uuid4

BASE_URL = "http://localhost:8000/api/v1"

def get_admin_token():
    """Login as admin and get access token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin", "password": "Admin@123"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.text}")
        return None

def delete_all_wizards(token):
    """Delete all existing wizards"""
    headers = {"Authorization": f"Bearer {token}"}

    # Get all wizards including unpublished
    response = requests.get(
        f"{BASE_URL}/wizards/?published_only=false&limit=100",
        headers=headers
    )

    if response.status_code == 200:
        wizards = response.json()
        print(f"Found {len(wizards)} wizards to delete")

        for wizard in wizards:
            delete_response = requests.delete(
                f"{BASE_URL}/wizards/{wizard['id']}",
                headers=headers
            )
            if delete_response.status_code == 200:
                print(f"  ✓ Deleted: {wizard['name']}")
            else:
                print(f"  ✗ Failed to delete {wizard['name']}: {delete_response.text}")
    else:
        print(f"Failed to get wizards: {response.text}")

def get_category_id(token, category_name):
    """Get category ID by name"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/wizards/categories", headers=headers)

    if response.status_code == 200:
        categories = response.json()
        for cat in categories:
            if cat['name'] == category_name:
                return cat['id']
    return None

def create_wizard_1_it_support(token, category_id):
    """
    IT Support Ticket Wizard
    Demonstrates: show_if, hide_if, require_if dependencies
    """
    wizard_data = {
        "name": "IT Support Ticket System",
        "description": "Submit and track IT support requests with smart form routing based on issue type",
        "category_id": category_id,
        "icon": "support_agent",
        "is_published": True,
        "allow_templates": True,
        "require_login": True,
        "auto_save": True,
        "estimated_time": 10,
        "difficulty_level": "easy",
        "tags": ["IT", "support", "helpdesk", "troubleshooting"],
        "steps": [
            {
                "name": "Issue Type",
                "description": "Select the type of issue you're experiencing",
                "help_text": "Choose the category that best describes your problem",
                "step_order": 1,
                "is_required": True,
                "is_skippable": False,
                "option_sets": [
                    {
                        "name": "What type of issue are you experiencing?",
                        "description": "This will help us route your request to the right team",
                        "selection_type": "single_select",
                        "is_required": True,
                        "min_selections": 0,
                        "max_selections": None,
                        "placeholder": "Select issue type",
                        "help_text": "Choose one option",
                        "options": [
                            {"label": "Hardware Problem", "value": "hardware", "description": "Computer, laptop, printer, or other physical devices", "is_default": False},
                            {"label": "Software Issue", "value": "software", "description": "Applications, programs, or operating system problems", "is_default": False},
                            {"label": "Network/Connectivity", "value": "network", "description": "Internet, WiFi, VPN, or network access issues", "is_default": False},
                            {"label": "Account/Access", "value": "account", "description": "Password resets, permissions, or account access", "is_default": False}
                        ]
                    }
                ]
            },
            {
                "name": "Hardware Details",
                "description": "Provide details about your hardware issue",
                "help_text": "Help us understand the hardware problem",
                "step_order": 2,
                "is_required": False,
                "is_skippable": True,
                "option_sets": [
                    {
                        "name": "Which device is affected?",
                        "description": "Select the hardware with issues",
                        "selection_type": "single_select",
                        "is_required": True,
                        "min_selections": 0,
                        "max_selections": None,
                        "placeholder": "Select device",
                        "help_text": "",
                        "options": [
                            {"label": "Desktop Computer", "value": "desktop", "description": "", "is_default": False},
                            {"label": "Laptop", "value": "laptop", "description": "", "is_default": False},
                            {"label": "Printer", "value": "printer", "description": "", "is_default": False},
                            {"label": "Monitor", "value": "monitor", "description": "", "is_default": False},
                            {"label": "Other Hardware", "value": "other_hw", "description": "", "is_default": False}
                        ]
                    }
                ]
            },
            {
                "name": "Software Details",
                "description": "Provide details about your software issue",
                "help_text": "Help us identify the software problem",
                "step_order": 3,
                "is_required": False,
                "is_skippable": True,
                "option_sets": [
                    {
                        "name": "Which software is causing issues?",
                        "description": "Select the problematic application",
                        "selection_type": "single_select",
                        "is_required": True,
                        "min_selections": 0,
                        "max_selections": None,
                        "placeholder": "Select software",
                        "help_text": "",
                        "options": [
                            {"label": "Microsoft Office", "value": "office", "description": "Word, Excel, PowerPoint, Outlook", "is_default": False},
                            {"label": "Email Client", "value": "email", "description": "Outlook, Thunderbird, etc.", "is_default": False},
                            {"label": "Web Browser", "value": "browser", "description": "Chrome, Firefox, Edge, Safari", "is_default": False},
                            {"label": "Custom Application", "value": "custom_app", "description": "Company-specific software", "is_default": False},
                            {"label": "Operating System", "value": "os", "description": "Windows, macOS, Linux", "is_default": False}
                        ]
                    }
                ]
            },
            {
                "name": "Priority & Description",
                "description": "Set priority and describe your issue",
                "help_text": "This helps us prioritize your request",
                "step_order": 4,
                "is_required": True,
                "is_skippable": False,
                "option_sets": [
                    {
                        "name": "How urgent is this issue?",
                        "description": "Select the priority level",
                        "selection_type": "single_select",
                        "is_required": True,
                        "min_selections": 0,
                        "max_selections": None,
                        "placeholder": "Select priority",
                        "help_text": "Critical = Work stopped, High = Major impact, Medium = Minor inconvenience, Low = Question or request",
                        "options": [
                            {"label": "Critical - Cannot work", "value": "critical", "description": "Complete work stoppage", "is_default": False},
                            {"label": "High - Major impact", "value": "high", "description": "Significant productivity loss", "is_default": False},
                            {"label": "Medium - Minor impact", "value": "medium", "description": "Some inconvenience", "is_default": True},
                            {"label": "Low - Question/Request", "value": "low", "description": "General inquiry", "is_default": False}
                        ]
                    },
                    {
                        "name": "Description",
                        "description": "Describe the issue in detail",
                        "selection_type": "text_input",
                        "is_required": True,
                        "min_selections": 0,
                        "max_selections": None,
                        "placeholder": "Please provide detailed information about the issue...",
                        "help_text": "Include error messages, when it started, and steps to reproduce",
                        "options": []
                    }
                ]
            }
        ]
    }

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(f"{BASE_URL}/wizards/", headers=headers, json=wizard_data)

    if response.status_code == 201:
        wizard = response.json()
        print(f"✓ Created IT Support Wizard (ID: {wizard['id']})")

        # Add dependencies: Show hardware/software details based on issue type
        # Note: We need to save first, then reload to get option IDs
        wizard_full = requests.get(f"{BASE_URL}/wizards/{wizard['id']}", headers=headers).json()

        # Get option IDs
        issue_type_options = wizard_full['steps'][0]['option_sets'][0]['options']
        hardware_detail_options = wizard_full['steps'][1]['option_sets'][0]['options']
        software_detail_options = wizard_full['steps'][2]['option_sets'][0]['options']

        # Find specific option IDs
        hardware_issue_id = next(opt['id'] for opt in issue_type_options if opt['value'] == 'hardware')
        software_issue_id = next(opt['id'] for opt in issue_type_options if opt['value'] == 'software')

        # Add dependencies to hardware detail options (show_if hardware selected)
        for hw_opt in hardware_detail_options:
            dep_response = requests.post(
                f"{BASE_URL}/wizards/options/{hw_opt['id']}/dependencies",
                headers=headers,
                json={"depends_on_option_id": hardware_issue_id, "dependency_type": "show_if"}
            )
            if dep_response.status_code == 201:
                print(f"  ✓ Added dependency: {hw_opt['label']} shows if Hardware Problem selected")

        # Add dependencies to software detail options (show_if software selected)
        for sw_opt in software_detail_options:
            dep_response = requests.post(
                f"{BASE_URL}/wizards/options/{sw_opt['id']}/dependencies",
                headers=headers,
                json={"depends_on_option_id": software_issue_id, "dependency_type": "show_if"}
            )
            if dep_response.status_code == 201:
                print(f"  ✓ Added dependency: {sw_opt['label']} shows if Software Issue selected")

        return wizard['id']
    else:
        print(f"✗ Failed to create IT Support Wizard: {response.text}")
        return None

def create_wizard_2_ecommerce(token, category_id):
    """
    E-commerce Product Configuration Wizard
    Demonstrates: show_if, require_if, disable_if dependencies
    """
    wizard_data = {
        "name": "Custom Laptop Configuration",
        "description": "Build your perfect laptop with our step-by-step configurator",
        "category_id": category_id,
        "icon": "computer",
        "is_published": True,
        "allow_templates": True,
        "require_login": False,
        "auto_save": True,
        "estimated_time": 8,
        "difficulty_level": "easy",
        "tags": ["ecommerce", "shopping", "configuration", "laptop"],
        "steps": [
            {
                "name": "Laptop Type",
                "description": "Choose your laptop category",
                "step_order": 1,
                "is_required": True,
                "is_skippable": False,
                "option_sets": [
                    {
                        "name": "What will you primarily use this laptop for?",
                        "selection_type": "single_select",
                        "is_required": True,
                        "min_selections": 0,
                        "options": [
                            {"label": "Gaming", "value": "gaming", "description": "High-performance for gaming", "is_default": False},
                            {"label": "Business/Work", "value": "business", "description": "Professional productivity", "is_default": False},
                            {"label": "Student/Everyday", "value": "student", "description": "General use and studying", "is_default": False},
                            {"label": "Creative Work", "value": "creative", "description": "Photo/video editing, design", "is_default": False}
                        ]
                    }
                ]
            },
            {
                "name": "Processor",
                "description": "Select your processor",
                "step_order": 2,
                "is_required": True,
                "is_skippable": False,
                "option_sets": [
                    {
                        "name": "Choose processor",
                        "selection_type": "single_select",
                        "is_required": True,
                        "min_selections": 0,
                        "options": [
                            {"label": "Intel i5 (Standard)", "value": "i5", "description": "Good for everyday tasks", "is_default": True},
                            {"label": "Intel i7 (Performance)", "value": "i7", "description": "Better for multitasking", "is_default": False},
                            {"label": "Intel i9 (High-End)", "value": "i9", "description": "Maximum performance", "is_default": False},
                            {"label": "AMD Ryzen 7", "value": "ryzen7", "description": "Excellent value", "is_default": False},
                            {"label": "AMD Ryzen 9", "value": "ryzen9", "description": "Top-tier performance", "is_default": False}
                        ]
                    }
                ]
            },
            {
                "name": "Graphics Card",
                "description": "Select graphics card",
                "step_order": 3,
                "is_required": True,
                "is_skippable": False,
                "option_sets": [
                    {
                        "name": "Choose graphics",
                        "selection_type": "single_select",
                        "is_required": True,
                        "min_selections": 0,
                        "options": [
                            {"label": "Integrated Graphics", "value": "integrated", "description": "Built-in, basic graphics", "is_default": True},
                            {"label": "NVIDIA RTX 3050", "value": "rtx3050", "description": "Entry-level gaming", "is_default": False},
                            {"label": "NVIDIA RTX 3060", "value": "rtx3060", "description": "Mid-range gaming", "is_default": False},
                            {"label": "NVIDIA RTX 4060", "value": "rtx4060", "description": "High-end gaming", "is_default": False},
                            {"label": "NVIDIA RTX 4070", "value": "rtx4070", "description": "Top-tier gaming", "is_default": False}
                        ]
                    }
                ]
            },
            {
                "name": "Memory & Storage",
                "description": "Configure RAM and storage",
                "step_order": 4,
                "is_required": True,
                "is_skippable": False,
                "option_sets": [
                    {
                        "name": "RAM",
                        "selection_type": "single_select",
                        "is_required": True,
                        "min_selections": 0,
                        "options": [
                            {"label": "8GB RAM", "value": "ram8", "description": "Basic use", "is_default": False},
                            {"label": "16GB RAM", "value": "ram16", "description": "Recommended", "is_default": True},
                            {"label": "32GB RAM", "value": "ram32", "description": "Professional", "is_default": False},
                            {"label": "64GB RAM", "value": "ram64", "description": "Maximum performance", "is_default": False}
                        ]
                    },
                    {
                        "name": "Storage",
                        "selection_type": "single_select",
                        "is_required": True,
                        "min_selections": 0,
                        "options": [
                            {"label": "256GB SSD", "value": "ssd256", "description": "Basic storage", "is_default": False},
                            {"label": "512GB SSD", "value": "ssd512", "description": "Standard", "is_default": True},
                            {"label": "1TB SSD", "value": "ssd1tb", "description": "Large storage", "is_default": False},
                            {"label": "2TB SSD", "value": "ssd2tb", "description": "Maximum storage", "is_default": False}
                        ]
                    }
                ]
            },
            {
                "name": "Add-ons",
                "description": "Optional accessories and services",
                "step_order": 5,
                "is_required": False,
                "is_skippable": True,
                "option_sets": [
                    {
                        "name": "Select add-ons (optional)",
                        "selection_type": "multiple_select",
                        "is_required": False,
                        "min_selections": 0,
                        "options": [
                            {"label": "Extended Warranty (2 years)", "value": "warranty2", "description": "", "is_default": False},
                            {"label": "Extended Warranty (3 years)", "value": "warranty3", "description": "", "is_default": False},
                            {"label": "Laptop Bag", "value": "bag", "description": "", "is_default": False},
                            {"label": "Wireless Mouse", "value": "mouse", "description": "", "is_default": False},
                            {"label": "External Monitor", "value": "monitor", "description": "", "is_default": False}
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
        print(f"✓ Created E-commerce Laptop Config Wizard (ID: {wizard['id']})")

        # Reload to get option IDs
        wizard_full = requests.get(f"{BASE_URL}/wizards/{wizard['id']}", headers=headers).json()

        # Get option IDs
        laptop_type_options = wizard_full['steps'][0]['option_sets'][0]['options']
        graphics_options = wizard_full['steps'][2]['option_sets'][0]['options']
        ram_options = wizard_full['steps'][3]['option_sets'][0]['options']

        # Get specific IDs
        gaming_id = next(opt['id'] for opt in laptop_type_options if opt['value'] == 'gaming')
        creative_id = next(opt['id'] for opt in laptop_type_options if opt['value'] == 'creative')
        integrated_graphics_id = next(opt['id'] for opt in graphics_options if opt['value'] == 'integrated')

        # Add dependencies: Disable integrated graphics for gaming/creative
        dep_response = requests.post(
            f"{BASE_URL}/wizards/options/{integrated_graphics_id}/dependencies",
            headers=headers,
            json={"depends_on_option_id": gaming_id, "dependency_type": "disable_if"}
        )
        if dep_response.status_code == 201:
            print(f"  ✓ Integrated graphics disabled if Gaming selected")

        dep_response = requests.post(
            f"{BASE_URL}/wizards/options/{integrated_graphics_id}/dependencies",
            headers=headers,
            json={"depends_on_option_id": creative_id, "dependency_type": "disable_if"}
        )
        if dep_response.status_code == 201:
            print(f"  ✓ Integrated graphics disabled if Creative Work selected")

        # Require 32GB+ RAM for gaming/creative
        ram8_id = next(opt['id'] for opt in ram_options if opt['value'] == 'ram8')
        ram16_id = next(opt['id'] for opt in ram_options if opt['value'] == 'ram16')

        dep_response = requests.post(
            f"{BASE_URL}/wizards/options/{ram8_id}/dependencies",
            headers=headers,
            json={"depends_on_option_id": gaming_id, "dependency_type": "hide_if"}
        )
        if dep_response.status_code == 201:
            print(f"  ✓ 8GB RAM hidden for Gaming laptops")

        return wizard['id']
    else:
        print(f"✗ Failed to create E-commerce Wizard: {response.text}")
        return None

def create_wizard_3_logistics(token, category_id):
    """
    Logistics Shipping Wizard
    Demonstrates: show_if, hide_if, require_if dependencies
    """
    wizard_data = {
        "name": "International Shipping Request",
        "description": "Configure your international shipment with customs and delivery options",
        "category_id": category_id,
        "icon": "local_shipping",
        "is_published": True,
        "allow_templates": True,
        "require_login": True,
        "auto_save": True,
        "estimated_time": 12,
        "difficulty_level": "medium",
        "tags": ["logistics", "shipping", "international", "customs"],
        "steps": [
            {
                "name": "Shipment Type",
                "description": "Select shipment category",
                "step_order": 1,
                "is_required": True,
                "is_skippable": False,
                "option_sets": [
                    {
                        "name": "What are you shipping?",
                        "selection_type": "single_select",
                        "is_required": True,
                        "min_selections": 0,
                        "options": [
                            {"label": "Documents", "value": "documents", "description": "Letters, contracts, papers", "is_default": False},
                            {"label": "Packages", "value": "packages", "description": "General goods under 30kg", "is_default": False},
                            {"label": "Freight", "value": "freight", "description": "Large or heavy items over 30kg", "is_default": False},
                            {"label": "Perishables", "value": "perishables", "description": "Food, flowers, temperature-sensitive", "is_default": False},
                            {"label": "Hazardous Materials", "value": "hazmat", "description": "Chemicals, batteries, flammables", "is_default": False}
                        ]
                    }
                ]
            },
            {
                "name": "Destination",
                "description": "Where are you shipping?",
                "step_order": 2,
                "is_required": True,
                "is_skippable": False,
                "option_sets": [
                    {
                        "name": "Destination region",
                        "selection_type": "single_select",
                        "is_required": True,
                        "min_selections": 0,
                        "options": [
                            {"label": "Domestic (USA)", "value": "domestic", "description": "", "is_default": False},
                            {"label": "Canada/Mexico", "value": "north_america", "description": "", "is_default": False},
                            {"label": "Europe", "value": "europe", "description": "", "is_default": False},
                            {"label": "Asia-Pacific", "value": "asia", "description": "", "is_default": False},
                            {"label": "Other International", "value": "other", "description": "", "is_default": False}
                        ]
                    }
                ]
            },
            {
                "name": "Customs Information",
                "description": "Required for international shipments",
                "step_order": 3,
                "is_required": False,
                "is_skippable": True,
                "option_sets": [
                    {
                        "name": "Customs declaration",
                        "selection_type": "single_select",
                        "is_required": True,
                        "min_selections": 0,
                        "options": [
                            {"label": "Gift", "value": "gift", "description": "Personal gift, no commercial value", "is_default": False},
                            {"label": "Commercial Goods", "value": "commercial", "description": "For resale or business", "is_default": False},
                            {"label": "Personal Effects", "value": "personal", "description": "Personal belongings", "is_default": False},
                            {"label": "Sample", "value": "sample", "description": "Product samples, no sale", "is_default": False}
                        ]
                    }
                ]
            },
            {
                "name": "Special Handling",
                "description": "Special requirements for your shipment",
                "step_order": 4,
                "is_required": False,
                "is_skippable": True,
                "option_sets": [
                    {
                        "name": "Temperature control needed?",
                        "selection_type": "single_select",
                        "is_required": True,
                        "min_selections": 0,
                        "options": [
                            {"label": "Refrigerated (2-8°C)", "value": "refrigerated", "description": "", "is_default": False},
                            {"label": "Frozen (-18°C)", "value": "frozen", "description": "", "is_default": False},
                            {"label": "Room Temperature", "value": "ambient", "description": "", "is_default": False}
                        ]
                    },
                    {
                        "name": "Hazmat classification",
                        "selection_type": "single_select",
                        "is_required": True,
                        "min_selections": 0,
                        "options": [
                            {"label": "Class 3: Flammable Liquids", "value": "class3", "description": "", "is_default": False},
                            {"label": "Class 8: Corrosive", "value": "class8", "description": "", "is_default": False},
                            {"label": "Class 9: Miscellaneous", "value": "class9", "description": "Batteries, dry ice", "is_default": False}
                        ]
                    }
                ]
            },
            {
                "name": "Delivery Options",
                "description": "Choose delivery speed and services",
                "step_order": 5,
                "is_required": True,
                "is_skippable": False,
                "option_sets": [
                    {
                        "name": "Delivery speed",
                        "selection_type": "single_select",
                        "is_required": True,
                        "min_selections": 0,
                        "options": [
                            {"label": "Express (1-2 days)", "value": "express", "description": "", "is_default": False},
                            {"label": "Priority (3-5 days)", "value": "priority", "description": "", "is_default": False},
                            {"label": "Standard (5-10 days)", "value": "standard", "description": "", "is_default": True},
                            {"label": "Economy (10-15 days)", "value": "economy", "description": "", "is_default": False}
                        ]
                    },
                    {
                        "name": "Additional services",
                        "selection_type": "multiple_select",
                        "is_required": False,
                        "min_selections": 0,
                        "options": [
                            {"label": "Insurance", "value": "insurance", "description": "", "is_default": False},
                            {"label": "Signature Required", "value": "signature", "description": "", "is_default": False},
                            {"label": "Saturday Delivery", "value": "saturday", "description": "", "is_default": False},
                            {"label": "Tracking SMS", "value": "sms", "description": "", "is_default": False}
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
        print(f"✓ Created Logistics Shipping Wizard (ID: {wizard['id']})")

        wizard_full = requests.get(f"{BASE_URL}/wizards/{wizard['id']}", headers=headers).json()

        shipment_type_options = wizard_full['steps'][0]['option_sets'][0]['options']
        destination_options = wizard_full['steps'][1]['option_sets'][0]['options']
        customs_options = wizard_full['steps'][2]['option_sets'][0]['options']
        temp_control_options = wizard_full['steps'][3]['option_sets'][0]['options']
        hazmat_options = wizard_full['steps'][3]['option_sets'][1]['options']
        delivery_options = wizard_full['steps'][4]['option_sets'][0]['options']

        # Get IDs
        perishables_id = next(opt['id'] for opt in shipment_type_options if opt['value'] == 'perishables')
        hazmat_id = next(opt['id'] for opt in shipment_type_options if opt['value'] == 'hazmat')
        domestic_id = next(opt['id'] for opt in destination_options if opt['value'] == 'domestic')
        economy_delivery_id = next(opt['id'] for opt in delivery_options if opt['value'] == 'economy')

        # Show customs info only for international
        for customs_opt in customs_options:
            dep_response = requests.post(
                f"{BASE_URL}/wizards/options/{customs_opt['id']}/dependencies",
                headers=headers,
                json={"depends_on_option_id": domestic_id, "dependency_type": "hide_if"}
            )
            if dep_response.status_code == 201:
                print(f"  ✓ {customs_opt['label']} hidden for domestic shipments")

        # Show temperature control only for perishables
        for temp_opt in temp_control_options:
            dep_response = requests.post(
                f"{BASE_URL}/wizards/options/{temp_opt['id']}/dependencies",
                headers=headers,
                json={"depends_on_option_id": perishables_id, "dependency_type": "show_if"}
            )
            if dep_response.status_code == 201:
                print(f"  ✓ {temp_opt['label']} shows only for perishables")

        # Show hazmat classification only for hazmat
        for hazmat_opt in hazmat_options:
            dep_response = requests.post(
                f"{BASE_URL}/wizards/options/{hazmat_opt['id']}/dependencies",
                headers=headers,
                json={"depends_on_option_id": hazmat_id, "dependency_type": "show_if"}
            )
            if dep_response.status_code == 201:
                print(f"  ✓ {hazmat_opt['label']} shows only for hazmat")

        # Disable economy delivery for perishables and hazmat
        dep_response = requests.post(
            f"{BASE_URL}/wizards/options/{economy_delivery_id}/dependencies",
            headers=headers,
            json={"depends_on_option_id": perishables_id, "dependency_type": "disable_if"}
        )
        if dep_response.status_code == 201:
            print(f"  ✓ Economy delivery disabled for perishables")

        dep_response = requests.post(
            f"{BASE_URL}/wizards/options/{economy_delivery_id}/dependencies",
            headers=headers,
            json={"depends_on_option_id": hazmat_id, "dependency_type": "disable_if"}
        )
        if dep_response.status_code == 201:
            print(f"  ✓ Economy delivery disabled for hazmat")

        return wizard['id']
    else:
        print(f"✗ Failed to create Logistics Wizard: {response.text}")
        return None

def main():
    print("=" * 60)
    print("Creating Sample Wizards with Conditional Dependencies")
    print("=" * 60)

    # Get admin token
    print("\n1. Logging in as admin...")
    token = get_admin_token()
    if not token:
        print("Failed to get admin token. Exiting.")
        return
    print("✓ Logged in successfully")

    # Delete existing wizards
    print("\n2. Deleting existing wizards...")
    delete_all_wizards(token)

    # Get category ID
    print("\n3. Getting category...")
    category_id = get_category_id(token, "IT & Technology")
    if not category_id:
        print("Warning: Could not find IT & Technology category, using None")

    # Create wizards
    print("\n4. Creating new wizards with dependencies...")
    print("-" * 60)

    wizard1_id = create_wizard_1_it_support(token, category_id)
    print()

    wizard2_id = create_wizard_2_ecommerce(token, category_id)
    print()

    wizard3_id = create_wizard_3_logistics(token, category_id)
    print()

    print("-" * 60)
    print("\n✅ Wizard creation complete!")
    print(f"\nCreated {sum(1 for w in [wizard1_id, wizard2_id, wizard3_id] if w)} wizards successfully")
    print("\nYou can now test these wizards at: http://localhost:3000")

if __name__ == "__main__":
    main()
