"""
Simple script to delete all wizards from database
"""
import psycopg2

# Database connection
DB_HOST = "127.0.0.1"
DB_PORT = "5432"
DB_NAME = "wizarddb"
DB_USER = "postgres"
DB_PASSWORD = "@dmin123"

try:
    # Connect
    print("Connecting to database...")
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    conn.autocommit = False
    cur = conn.cursor()

    print("\n" + "="*60)
    print("CURRENT STATE")
    print("="*60)

    # Count wizards
    cur.execute("SELECT COUNT(*) FROM wizards;")
    wizard_count = cur.fetchone()[0]
    print(f"Wizards: {wizard_count} records")

    if wizard_count == 0:
        print("\nDatabase is already empty!")
        cur.close()
        conn.close()
        exit(0)

    # Get list of all tables
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)
    tables = [row[0] for row in cur.fetchall()]

    print(f"\nFound {len(tables)} tables in database:")
    for table in tables:
        cur.execute(f"SELECT COUNT(*) FROM {table};")
        count = cur.fetchone()[0]
        if count > 0:
            print(f"  {table}: {count} records")

    print("\n" + "="*60)
    print("DELETING ALL DATA")
    print("="*60)

    # Delete in order (cascade will handle dependencies)
    print("\nDeleting all wizards (CASCADE)...")
    cur.execute("DELETE FROM wizards CASCADE;")
    deleted = cur.rowcount
    print(f"[OK] Deleted {deleted} wizards")

    # Delete other wizard-related data
    wizard_tables = [
        'steps', 'option_sets', 'options', 'option_dependencies',
        'wizard_sessions', 'session_responses', 'wizard_templates',
        'template_responses'
    ]

    for table in wizard_tables:
        if table in tables:
            print(f"\nDeleting from {table}...")
            cur.execute(f"DELETE FROM {table};")
            deleted = cur.rowcount
            print(f"[OK] Deleted {deleted} records")

    # Commit
    conn.commit()
    print("\n" + "="*60)
    print("VERIFICATION")
    print("="*60)

    # Verify empty
    cur.execute("SELECT COUNT(*) FROM wizards;")
    final_count = cur.fetchone()[0]

    if final_count == 0:
        print("\n[SUCCESS] All wizards deleted!")
        print("Database is now empty.")
    else:
        print(f"\n[WARNING] Still {final_count} wizards remaining")

    print("="*60)

    cur.close()
    conn.close()

except psycopg2.Error as e:
    print(f"\n[ERROR] Database error: {e}")
    if 'conn' in locals() and conn:
        conn.rollback()
except Exception as e:
    print(f"\n[ERROR] {e}")
    if 'conn' in locals() and conn:
        conn.rollback()
