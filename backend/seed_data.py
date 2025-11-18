"""
Seed data script for Multi-Wizard Platform.
Run this after creating the database schema.
"""
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.config import settings
from app.core.security import get_password_hash

# Create engine
engine = create_engine(settings.DATABASE_URL)


def seed_roles():
    """Seed default user roles."""
    print("Seeding user roles...")
    with engine.connect() as conn:
        # Check if roles exist
        result = conn.execute(text("SELECT COUNT(*) FROM user_roles"))
        if result.scalar() > 0:
            print("  Roles already exist, skipping...")
            return

        conn.execute(text("""
            INSERT INTO user_roles (name, description, permissions) VALUES
            ('super_admin', 'Full system access', '{"all": true}'::jsonb),
            ('admin', 'Wizard management access', '{"wizards": ["create", "read", "update", "delete"], "analytics": ["read"]}'::jsonb),
            ('user', 'Standard user access', '{"sessions": ["create", "read", "update"], "templates": ["create", "read"]}'::jsonb)
        """))
        conn.commit()
    print("  [OK] Roles seeded successfully")


def seed_admin_user():
    """Seed default admin user."""
    print("Seeding admin user...")
    with engine.connect() as conn:
        # Check if admin exists
        result = conn.execute(text("SELECT COUNT(*) FROM users WHERE username = 'admin'"))
        if result.scalar() > 0:
            print("  Admin user already exists, skipping...")
            return

        # Get super_admin role id
        result = conn.execute(text("SELECT id FROM user_roles WHERE name = 'super_admin'"))
        role_id = result.scalar()

        # Create admin user (password: Admin@123)
        password_hash = get_password_hash("Admin@123")

        conn.execute(text(f"""
            INSERT INTO users (email, username, password_hash, full_name, role_id, is_active, is_verified)
            VALUES ('admin@wizardplatform.com', 'admin', :password_hash, 'System Administrator', :role_id, true, true)
        """), {"password_hash": password_hash, "role_id": role_id})
        conn.commit()
    print("  [OK] Admin user created (username: admin, password: Admin@123)")


def seed_categories():
    """Seed wizard categories."""
    print("Seeding wizard categories...")
    with engine.connect() as conn:
        # Check if categories exist
        result = conn.execute(text("SELECT COUNT(*) FROM wizard_categories"))
        if result.scalar() > 0:
            print("  Categories already exist, skipping...")
            return

        conn.execute(text("""
            INSERT INTO wizard_categories (name, description, icon, display_order) VALUES
            ('IT & Technology', 'Technology-related configuration wizards', 'computer', 1),
            ('Business Process', 'Business workflow and process wizards', 'business', 2),
            ('Onboarding', 'User and employee onboarding wizards', 'person_add', 3),
            ('E-Commerce', 'Product configuration and shopping wizards', 'shopping_cart', 4),
            ('Surveys & Forms', 'Data collection and feedback wizards', 'poll', 5)
        """))
        conn.commit()
    print("  [OK] Categories seeded successfully")


def seed_sample_wizard():
    """Seed a sample wizard with steps and options."""
    print("Seeding sample wizard...")
    with engine.connect() as conn:
        # Check if sample wizard exists
        result = conn.execute(text("SELECT COUNT(*) FROM wizards WHERE name = 'Quick Feedback Survey'"))
        if result.scalar() > 0:
            print("  Sample wizard already exists, skipping...")
            return

        # Get admin user id
        result = conn.execute(text("SELECT id FROM users WHERE username = 'admin'"))
        admin_id = result.scalar()

        # Get surveys category id
        result = conn.execute(text("SELECT id FROM wizard_categories WHERE name = 'Surveys & Forms'"))
        category_id = result.scalar()

        # Create sample wizard
        conn.execute(text("""
            INSERT INTO wizards (
                name, description, category_id, created_by, icon,
                is_published, allow_templates, require_login, auto_save,
                estimated_time, difficulty_level, tags
            ) VALUES (
                'Quick Feedback Survey',
                'A simple survey to collect user feedback about our platform',
                :category_id,
                :admin_id,
                'feedback',
                true,
                true,
                false,
                true,
                3,
                'easy',
                '["survey", "feedback", "quick"]'::jsonb
            )
        """), {"category_id": category_id, "admin_id": admin_id})
        conn.commit()

        # Get wizard id
        result = conn.execute(text("SELECT id FROM wizards WHERE name = 'Quick Feedback Survey'"))
        wizard_id = result.scalar()

        # Create steps
        # Step 1: Overall Rating
        conn.execute(text("""
            INSERT INTO steps (wizard_id, name, description, help_text, step_order, is_required)
            VALUES (:wizard_id, 'Overall Rating', 'How would you rate your overall experience?',
                    'Select the option that best describes your experience.', 1, true)
        """), {"wizard_id": wizard_id})

        result = conn.execute(text("SELECT id FROM steps WHERE wizard_id = :wizard_id AND step_order = 1"), {"wizard_id": wizard_id})
        step1_id = result.scalar()

        # Step 2: Features Feedback
        conn.execute(text("""
            INSERT INTO steps (wizard_id, name, description, step_order, is_required)
            VALUES (:wizard_id, 'Features', 'Which features do you use most?', 2, true)
        """), {"wizard_id": wizard_id})

        result = conn.execute(text("SELECT id FROM steps WHERE wizard_id = :wizard_id AND step_order = 2"), {"wizard_id": wizard_id})
        step2_id = result.scalar()

        # Step 3: Comments
        conn.execute(text("""
            INSERT INTO steps (wizard_id, name, description, step_order, is_required, is_skippable)
            VALUES (:wizard_id, 'Additional Comments', 'Any other feedback?', 3, false, true)
        """), {"wizard_id": wizard_id})

        result = conn.execute(text("SELECT id FROM steps WHERE wizard_id = :wizard_id AND step_order = 3"), {"wizard_id": wizard_id})
        step3_id = result.scalar()

        conn.commit()

        # Create option sets
        # Option Set 1: Rating
        conn.execute(text("""
            INSERT INTO option_sets (step_id, name, description, selection_type, is_required, display_order)
            VALUES (:step_id, 'Experience Rating', 'Rate your experience from 1-5 stars', 'single_select', true, 1)
        """), {"step_id": step1_id})

        result = conn.execute(text("SELECT id FROM option_sets WHERE step_id = :step_id"), {"step_id": step1_id})
        os1_id = result.scalar()

        # Option Set 2: Features (multiple select)
        conn.execute(text("""
            INSERT INTO option_sets (step_id, name, description, selection_type, is_required, min_selections, max_selections, display_order)
            VALUES (:step_id, 'Most Used Features', 'Select all features you use regularly', 'multiple_select', true, 1, 5, 1)
        """), {"step_id": step2_id})

        result = conn.execute(text("SELECT id FROM option_sets WHERE step_id = :step_id"), {"step_id": step2_id})
        os2_id = result.scalar()

        # Option Set 3: Comments (text input)
        conn.execute(text("""
            INSERT INTO option_sets (step_id, name, description, selection_type, is_required, display_order, placeholder)
            VALUES (:step_id, 'Your Comments', 'Share your thoughts with us', 'text_input', false, 1, 'Type your comments here...')
        """), {"step_id": step3_id})

        conn.commit()

        # Create options for rating
        for i, (label, value) in enumerate([
            ('⭐ Poor', '1'),
            ('⭐⭐ Fair', '2'),
            ('⭐⭐⭐ Good', '3'),
            ('⭐⭐⭐⭐ Very Good', '4'),
            ('⭐⭐⭐⭐⭐ Excellent', '5')
        ], 1):
            conn.execute(text("""
                INSERT INTO options (option_set_id, label, value, display_order)
                VALUES (:os_id, :label, :value, :order)
            """), {"os_id": os1_id, "label": label, "value": value, "order": i})

        # Create options for features
        for i, (label, value) in enumerate([
            ('Wizard Builder', 'wizard_builder'),
            ('Session Management', 'session_mgmt'),
            ('Templates', 'templates'),
            ('Analytics Dashboard', 'analytics'),
            ('User Management', 'user_mgmt')
        ], 1):
            conn.execute(text("""
                INSERT INTO options (option_set_id, label, value, display_order)
                VALUES (:os_id, :label, :value, :order)
            """), {"os_id": os2_id, "label": label, "value": value, "order": i})

        conn.commit()

    print("  [OK] Sample wizard created successfully")


def seed_system_settings():
    """Seed system settings."""
    print("Seeding system settings...")
    with engine.connect() as conn:
        # Check if settings exist
        result = conn.execute(text("SELECT COUNT(*) FROM system_settings"))
        if result.scalar() > 0:
            print("  System settings already exist, skipping...")
            return

        conn.execute(text("""
            INSERT INTO system_settings (key, value, description, is_public) VALUES
            ('app_name', '"Multi-Wizard Platform"', 'Application name', true),
            ('max_session_duration', '86400', 'Maximum session duration in seconds (24 hours)', false),
            ('enable_anonymous_sessions', 'false', 'Allow anonymous wizard completion', false),
            ('default_auto_save_interval', '30', 'Default auto-save interval in seconds', false),
            ('max_file_upload_size', '10485760', 'Maximum file upload size in bytes (10MB)', false),
            ('supported_file_types', '["image/jpeg", "image/png", "application/pdf"]', 'Allowed file types for upload', true)
        """))
        conn.commit()
    print("  [OK] System settings seeded successfully")


def main():
    """Run all seed functions."""
    print("\n" + "=" * 50)
    print("Multi-Wizard Platform - Database Seeding")
    print("=" * 50 + "\n")

    try:
        seed_roles()
        seed_admin_user()
        seed_categories()
        seed_system_settings()
        seed_sample_wizard()

        print("\n" + "=" * 50)
        print("[OK] All seed data inserted successfully!")
        print("=" * 50)
        print("\nDefault admin credentials:")
        print("  Username: admin")
        print("  Password: Admin@123")
        print("\nYou can now start the server with:")
        print("  uvicorn app.main:app --reload")
        print()

    except Exception as e:
        print(f"\n[X] Error during seeding: {e}")
        raise


if __name__ == "__main__":
    main()
