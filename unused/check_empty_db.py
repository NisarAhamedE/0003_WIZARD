"""
Direct database check to verify all wizards are deleted
"""
import psycopg2
from psycopg2 import sql

# Database connection
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/wizarddb"

try:
    # Connect to database
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    print("=" * 60)
    print("DATABASE VERIFICATION - Empty Tables Check")
    print("=" * 60)

    # Check wizards table
    cur.execute("SELECT COUNT(*) FROM wizards;")
    wizard_count = cur.fetchone()[0]
    print(f"\nWizards table: {wizard_count} records")

    # Check sessions table
    cur.execute("SELECT COUNT(*) FROM sessions;")
    session_count = cur.fetchone()[0]
    print(f"Sessions table: {session_count} records")

    # Check templates table
    cur.execute("SELECT COUNT(*) FROM templates;")
    template_count = cur.fetchone()[0]
    print(f"Templates table: {template_count} records")

    # Check steps table
    cur.execute("SELECT COUNT(*) FROM steps;")
    step_count = cur.fetchone()[0]
    print(f"Steps table: {step_count} records")

    # Check option_sets table
    cur.execute("SELECT COUNT(*) FROM option_sets;")
    optionset_count = cur.fetchone()[0]
    print(f"Option Sets table: {optionset_count} records")

    # Check options table
    cur.execute("SELECT COUNT(*) FROM options;")
    option_count = cur.fetchone()[0]
    print(f"Options table: {option_count} records")

    # Check option_dependencies table
    cur.execute("SELECT COUNT(*) FROM option_dependencies;")
    dependency_count = cur.fetchone()[0]
    print(f"Option Dependencies table: {dependency_count} records")

    print("\n" + "=" * 60)

    total = (wizard_count + session_count + template_count +
             step_count + optionset_count + option_count + dependency_count)

    if total == 0:
        print("✓ DATABASE IS COMPLETELY EMPTY")
        print("All wizard-related tables have 0 records")
    else:
        print("✗ DATABASE CONTAINS DATA")
        print(f"Total records across all tables: {total}")

        if wizard_count > 0:
            print(f"\nWARNING: Found {wizard_count} wizard(s) in database")
            print("Running DELETE to clean up...")

            # Delete all data
            cur.execute("DELETE FROM option_dependencies;")
            cur.execute("DELETE FROM session_responses;")
            cur.execute("DELETE FROM template_responses;")
            cur.execute("DELETE FROM options;")
            cur.execute("DELETE FROM option_sets;")
            cur.execute("DELETE FROM steps;")
            cur.execute("DELETE FROM sessions;")
            cur.execute("DELETE FROM templates;")
            cur.execute("DELETE FROM wizards;")

            conn.commit()

            print("\n✓ All wizard data has been deleted")
            print("Database is now empty")

    print("=" * 60)

    cur.close()
    conn.close()

except psycopg2.Error as e:
    print(f"Database error: {e}")
except Exception as e:
    print(f"Error: {e}")
