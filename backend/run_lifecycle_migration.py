"""
Run the wizard lifecycle protection migration
"""
import sys
import os
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.database import engine, SessionLocal

def run_migration():
    """Execute the lifecycle fields migration"""

    migration_file = Path(__file__).parent / "migrations" / "add_wizard_lifecycle_fields.sql"

    print(f"[INFO] Reading migration file: {migration_file}")

    if not migration_file.exists():
        print(f"[ERR] Migration file not found: {migration_file}")
        return False

    with open(migration_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # Remove comments for cleaner execution
    sql_statements = []
    current_statement = []

    for line in sql_content.split('\n'):
        # Skip comment lines
        if line.strip().startswith('--'):
            continue
        current_statement.append(line)

    sql_content = '\n'.join(current_statement)

    print("[INFO] Executing migration...")

    try:
        with engine.connect() as conn:
            # Execute the entire migration in a transaction
            conn.execute(text(sql_content))
            conn.commit()

        print("[OK] Migration executed successfully!")

        # Verify the changes
        print("\n[INFO] Verifying migration...")
        db = SessionLocal()
        try:
            result = db.execute(text("""
                SELECT column_name, data_type, column_default
                FROM information_schema.columns
                WHERE table_name = 'wizards'
                AND column_name IN (
                    'lifecycle_state', 'first_run_at', 'first_stored_run_at',
                    'is_archived', 'archived_at', 'version_number', 'parent_wizard_id'
                )
                ORDER BY column_name;
            """))

            columns = result.fetchall()

            if columns:
                print(f"[OK] Found {len(columns)} new columns:")
                for col in columns:
                    print(f"  - {col[0]}: {col[1]} (default: {col[2]})")
            else:
                print("[WARN] No new columns found. Migration may not have applied.")

            # Check lifecycle state distribution
            result = db.execute(text("""
                SELECT lifecycle_state, COUNT(*) as count
                FROM wizards
                GROUP BY lifecycle_state
                ORDER BY lifecycle_state;
            """))

            states = result.fetchall()
            print("\n[INFO] Wizard lifecycle state distribution:")
            for state in states:
                print(f"  - {state[0]}: {state[1]} wizards")

        finally:
            db.close()

        return True

    except Exception as e:
        print(f"[ERR] Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Wizard Lifecycle Protection Migration")
    print("=" * 60)
    print()

    success = run_migration()

    print()
    print("=" * 60)
    if success:
        print("[OK] Migration completed successfully!")
    else:
        print("[ERR] Migration failed. Check errors above.")
    print("=" * 60)

    sys.exit(0 if success else 1)
