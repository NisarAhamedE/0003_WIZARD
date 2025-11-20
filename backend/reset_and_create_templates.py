"""
Script to delete all wizards and create 3 new wizard templates
"""
import os
import sys
from uuid import UUID

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Database connection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def delete_all_wizards():
    """Delete all wizards and related data"""
    print("[*] Deleting all wizards...")
    db = SessionLocal()
    try:
        # Delete in proper order due to foreign key constraints
        db.execute(text("DELETE FROM wizard_run_file_uploads"))
        db.execute(text("DELETE FROM wizard_run_shares"))
        db.execute(text("DELETE FROM wizard_run_comparisons"))
        db.execute(text("DELETE FROM wizard_run_option_set_responses"))
        db.execute(text("DELETE FROM wizard_run_step_responses"))
        db.execute(text("DELETE FROM wizard_runs"))
        db.execute(text("DELETE FROM template_item_values"))
        db.execute(text("DELETE FROM wizard_templates"))
        db.execute(text("DELETE FROM option_dependencies"))
        db.execute(text("DELETE FROM options"))
        db.execute(text("DELETE FROM option_sets"))
        db.execute(text("DELETE FROM steps"))
        db.execute(text("DELETE FROM wizards"))
        db.commit()
        print("[OK] All wizards deleted successfully")
    except Exception as e:
        print(f"[ERROR] Error deleting wizards: {e}")
        db.rollback()
    finally:
        db.close()

def create_wizard_templates():
    """Create 3 new wizard templates with different options"""
    print("\n[*] Creating 3 new wizard templates...")
    db = SessionLocal()
    try:
        # Get first user (admin)
        result = db.execute(text("SELECT id FROM users LIMIT 1"))
        admin_row = result.fetchone()
        if not admin_row:
            print("[ERROR] No users found in database. Please run seed_data.py first.")
            return
        admin_id = admin_row[0]

        # Template 1: Customer Onboarding
        print("\n[1] Creating Customer Onboarding Wizard...")
        wizard1_result = db.execute(text("""
            INSERT INTO wizards (name, description, is_published, created_by)
            VALUES ('Customer Onboarding', 'Complete customer registration and onboarding process', true, :admin_id)
            RETURNING id
        """), {"admin_id": admin_id})
        wizard1_id = wizard1_result.fetchone()[0]

        # Step 1: Personal Information
        step1_result = db.execute(text("""
            INSERT INTO steps (wizard_id, title, description, step_order)
            VALUES (:wizard_id, 'Personal Information', 'Enter your personal details', 1)
            RETURNING id
        """), {"wizard_id": wizard1_id})
        step1_id = step1_result.fetchone()[0]

        # Option Set: Full Name
        optset1_result = db.execute(text("""
            INSERT INTO option_sets (step_id, title, description, selection_type, is_required, display_order)
            VALUES (:step_id, 'Full Name', 'Enter your full name', 'text_input', true, 1)
            RETURNING id
        """), {"step_id": step1_id})

        # Option Set: Email
        optset2_result = db.execute(text("""
            INSERT INTO option_sets (step_id, title, description, selection_type, is_required, display_order)
            VALUES (:step_id, 'Email Address', 'Enter your email', 'text_input', true, 2)
            RETURNING id
        """), {"step_id": step1_id})

        # Option Set: Phone
        optset3_result = db.execute(text("""
            INSERT INTO option_sets (step_id, title, description, selection_type, is_required, display_order)
            VALUES (:step_id, 'Phone Number', 'Enter your phone number', 'number_input', false, 3)
            RETURNING id
        """), {"step_id": step1_id})

        # Step 2: Company Information
        step2_result = db.execute(text("""
            INSERT INTO steps (wizard_id, title, description, step_order)
            VALUES (:wizard_id, 'Company Information', 'Tell us about your company', 2)
            RETURNING id
        """), {"wizard_id": wizard1_id})
        step2_id = step2_result.fetchone()[0]

        # Option Set: Company Size
        optset4_result = db.execute(text("""
            INSERT INTO option_sets (step_id, title, description, selection_type, is_required, display_order)
            VALUES (:step_id, 'Company Size', 'Select your company size', 'single_select', true, 1)
            RETURNING id
        """), {"step_id": step2_id})
        optset4_id = optset4_result.fetchone()[0]

        # Options for Company Size
        db.execute(text("""
            INSERT INTO options (option_set_id, label, value, display_order)
            VALUES
                (:optset_id, '1-10 employees', 'small', 1),
                (:optset_id, '11-50 employees', 'medium', 2),
                (:optset_id, '51-200 employees', 'large', 3),
                (:optset_id, '200+ employees', 'enterprise', 4)
        """), {"optset_id": optset4_id})

        # Option Set: Industry
        optset5_result = db.execute(text("""
            INSERT INTO option_sets (step_id, title, description, selection_type, is_required, display_order)
            VALUES (:step_id, 'Industry', 'Select your industry', 'multiple_select', true, 2)
            RETURNING id
        """), {"step_id": step2_id})
        optset5_id = optset5_result.fetchone()[0]

        # Options for Industry
        db.execute(text("""
            INSERT INTO options (option_set_id, label, value, display_order)
            VALUES
                (:optset_id, 'Technology', 'tech', 1),
                (:optset_id, 'Healthcare', 'healthcare', 2),
                (:optset_id, 'Finance', 'finance', 3),
                (:optset_id, 'Retail', 'retail', 4),
                (:optset_id, 'Education', 'education', 5)
        """), {"optset_id": optset5_id})

        print("[OK] Customer Onboarding Wizard created")

        # Template 2: Product Configuration
        print("\n[2] Creating Product Configuration Wizard...")
        wizard2_result = db.execute(text("""
            INSERT INTO wizards (name, description, is_published, created_by)
            VALUES ('Product Configuration', 'Configure your product preferences', true, :admin_id)
            RETURNING id
        """), {"admin_id": admin_id})
        wizard2_id = wizard2_result.fetchone()[0]

        # Step 1: Basic Settings
        step3_result = db.execute(text("""
            INSERT INTO steps (wizard_id, title, description, step_order)
            VALUES (:wizard_id, 'Basic Settings', 'Configure basic product settings', 1)
            RETURNING id
        """), {"wizard_id": wizard2_id})
        step3_id = step3_result.fetchone()[0]

        # Option Set: Product Name
        db.execute(text("""
            INSERT INTO option_sets (step_id, title, description, selection_type, is_required, display_order)
            VALUES (:step_id, 'Product Name', 'Enter product name', 'text_input', true, 1)
        """), {"step_id": step3_id})

        # Option Set: Priority Level
        optset6_result = db.execute(text("""
            INSERT INTO option_sets (step_id, title, description, selection_type, is_required, display_order, min_value, max_value)
            VALUES (:step_id, 'Priority Level', 'Set priority level (1-5)', 'slider', true, 2, 1, 5)
            RETURNING id
        """), {"step_id": step3_id})

        # Option Set: Rating
        db.execute(text("""
            INSERT INTO option_sets (step_id, title, description, selection_type, is_required, display_order, min_value, max_value)
            VALUES (:step_id, 'Rate this product', 'Give your rating', 'rating', false, 3, 1, 5)
        """), {"step_id": step3_id})

        # Step 2: Advanced Options
        step4_result = db.execute(text("""
            INSERT INTO steps (wizard_id, title, description, step_order)
            VALUES (:wizard_id, 'Advanced Options', 'Configure advanced features', 2)
            RETURNING id
        """), {"wizard_id": wizard2_id})
        step4_id = step4_result.fetchone()[0]

        # Option Set: Theme Color
        db.execute(text("""
            INSERT INTO option_sets (step_id, title, description, selection_type, is_required, display_order)
            VALUES (:step_id, 'Theme Color', 'Choose a theme color', 'color_picker', true, 1)
        """), {"step_id": step4_id})

        # Option Set: Launch Date
        db.execute(text("""
            INSERT INTO option_sets (step_id, title, description, selection_type, is_required, display_order)
            VALUES (:step_id, 'Launch Date', 'Select launch date', 'date_input', true, 2)
        """), {"step_id": step4_id})

        print("[OK] Product Configuration Wizard created")

        # Template 3: Event Registration
        print("\n[3] Creating Event Registration Wizard...")
        wizard3_result = db.execute(text("""
            INSERT INTO wizards (name, description, is_published, created_by)
            VALUES ('Event Registration', 'Register for upcoming events', true, :admin_id)
            RETURNING id
        """), {"admin_id": admin_id})
        wizard3_id = wizard3_result.fetchone()[0]

        # Step 1: Attendee Information
        step5_result = db.execute(text("""
            INSERT INTO steps (wizard_id, title, description, step_order)
            VALUES (:wizard_id, 'Attendee Information', 'Enter attendee details', 1)
            RETURNING id
        """), {"wizard_id": wizard3_id})
        step5_id = step5_result.fetchone()[0]

        # Option Set: Attendee Name
        db.execute(text("""
            INSERT INTO option_sets (step_id, title, description, selection_type, is_required, display_order)
            VALUES (:step_id, 'Attendee Name', 'Full name of attendee', 'text_input', true, 1)
        """), {"step_id": step5_id})

        # Option Set: Dietary Restrictions
        optset7_result = db.execute(text("""
            INSERT INTO option_sets (step_id, title, description, selection_type, is_required, display_order)
            VALUES (:step_id, 'Dietary Restrictions', 'Select any dietary restrictions', 'multiple_select', false, 2)
            RETURNING id
        """), {"step_id": step5_id})
        optset7_id = optset7_result.fetchone()[0]

        # Options for Dietary Restrictions
        db.execute(text("""
            INSERT INTO options (option_set_id, label, value, display_order)
            VALUES
                (:optset_id, 'Vegetarian', 'vegetarian', 1),
                (:optset_id, 'Vegan', 'vegan', 2),
                (:optset_id, 'Gluten-Free', 'gluten_free', 3),
                (:optset_id, 'Halal', 'halal', 4),
                (:optset_id, 'Kosher', 'kosher', 5),
                (:optset_id, 'None', 'none', 6)
        """), {"optset_id": optset7_id})

        # Step 2: Event Preferences
        step6_result = db.execute(text("""
            INSERT INTO steps (wizard_id, title, description, step_order)
            VALUES (:wizard_id, 'Event Preferences', 'Select your event preferences', 2)
            RETURNING id
        """), {"wizard_id": wizard3_id})
        step6_id = step6_result.fetchone()[0]

        # Option Set: Session Type
        optset8_result = db.execute(text("""
            INSERT INTO option_sets (step_id, title, description, selection_type, is_required, display_order)
            VALUES (:step_id, 'Session Type', 'Choose session type', 'single_select', true, 1)
            RETURNING id
        """), {"step_id": step6_id})
        optset8_id = optset8_result.fetchone()[0]

        # Options for Session Type
        db.execute(text("""
            INSERT INTO options (option_set_id, label, value, display_order)
            VALUES
                (:optset_id, 'In-Person', 'in_person', 1),
                (:optset_id, 'Virtual', 'virtual', 2),
                (:optset_id, 'Hybrid', 'hybrid', 3)
        """), {"optset_id": optset8_id})

        # Option Set: Preferred Time
        db.execute(text("""
            INSERT INTO option_sets (step_id, title, description, selection_type, is_required, display_order)
            VALUES (:step_id, 'Preferred Time', 'Select preferred event time', 'time_input', true, 2)
        """), {"step_id": step6_id})

        # Option Set: Additional Comments
        db.execute(text("""
            INSERT INTO option_sets (step_id, title, description, selection_type, is_required, display_order)
            VALUES (:step_id, 'Additional Comments', 'Any special requests or comments', 'rich_text', false, 3)
        """), {"step_id": step6_id})

        print("[OK] Event Registration Wizard created")

        db.commit()
        print("\n[OK] All 3 wizard templates created successfully!")

    except Exception as e:
        print(f"[ERROR] Error creating wizards: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    delete_all_wizards()
    create_wizard_templates()
    print("\n[DONE] Database reset and template creation complete!")
