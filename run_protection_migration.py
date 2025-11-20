"""
Run the wizard lifecycle protection migration
"""
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

# Get database URL
database_url = os.getenv('DATABASE_URL')

if not database_url:
    print("ERROR: DATABASE_URL not found in backend/.env")
    exit(1)

# Parse the database URL
# Format: postgresql://user:password@host:port/dbname
try:
    from urllib.parse import urlparse
    parsed = urlparse(database_url)

    user = parsed.username
    password = parsed.password
    host = parsed.hostname
    port = parsed.port or 5432
    dbname = parsed.path.lstrip('/')

    print(f"Connecting to database: {dbname} on {host}:{port} as {user}")

    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=dbname,
        user=user,
        password=password
    )
    conn.autocommit = False
    cursor = conn.cursor()

    # Read migration file
    migration_file = 'backend/migrations/add_wizard_lifecycle_fields.sql'
    print(f"\nReading migration file: {migration_file}")

    with open(migration_file, 'r') as f:
        migration_sql = f.read()

    # Execute migration
    print("\nExecuting migration...")
    cursor.execute(migration_sql)
    conn.commit()

    print("\n[OK] Migration completed successfully!")

    # Verify the columns were added
    cursor.execute("""
        SELECT column_name, data_type, column_default
        FROM information_schema.columns
        WHERE table_name = 'wizards'
        AND column_name IN ('lifecycle_state', 'first_run_at', 'first_stored_run_at',
                            'is_archived', 'version_number', 'parent_wizard_id')
        ORDER BY column_name;
    """)

    columns = cursor.fetchall()
    print("\n[OK] Verified columns added:")
    for col in columns:
        print(f"  - {col[0]}: {col[1]} (default: {col[2]})")

    # Check lifecycle state distribution
    cursor.execute("""
        SELECT lifecycle_state, COUNT(*) as count
        FROM wizards
        GROUP BY lifecycle_state
        ORDER BY lifecycle_state;
    """)

    states = cursor.fetchall()
    print("\n[OK] Lifecycle state distribution:")
    for state, count in states:
        print(f"  - {state}: {count} wizard(s)")

    cursor.close()
    conn.close()

    print("\n[SUCCESS] Wizard protection migration complete!")
    print("\nNext steps:")
    print("1. Restart the backend server")
    print("2. Refresh the frontend browser")
    print("3. Test the three protection scenarios")

except Exception as e:
    print(f"\n[ERROR] Migration failed: {e}")
    import traceback
    traceback.print_exc()
    if 'conn' in locals():
        conn.rollback()
        conn.close()
    exit(1)
