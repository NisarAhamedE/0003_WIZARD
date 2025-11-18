"""
Direct PostgreSQL deletion - Delete ALL wizards and related data
"""
import psycopg2
from psycopg2 import sql

# Database connection - UPDATE THESE IF DIFFERENT
DB_HOST = "127.0.0.1"
DB_PORT = "5432"
DB_NAME = "wizarddb"
DB_USER = "postgres"
DB_PASSWORD = "@dmin123"

try:
    # Connect to database
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

    print("\n" + "=" * 60)
    print("CHECKING CURRENT DATABASE STATE")
    print("=" * 60)

    # Count records before deletion
    tables = [
        "wizards",
        "sessions",
        "templates",
        "steps",
        "option_sets",
        "options",
        "option_dependencies",
        "session_responses",
        "template_responses"
    ]

    counts_before = {}
    for table in tables:
        cur.execute(f"SELECT COUNT(*) FROM {table};")
        count = cur.fetchone()[0]
        counts_before[table] = count
        print(f"{table}: {count} records")

    total_before = sum(counts_before.values())
    print(f"\nTotal records: {total_before}")

    if total_before == 0:
        print("\n✓ Database is already empty!")
        cur.close()
        conn.close()
        exit(0)

    print("\n" + "=" * 60)
    print("DELETING ALL WIZARD DATA")
    print("=" * 60)

    # Delete in correct order (respecting foreign key constraints)
    delete_order = [
        "option_dependencies",
        "session_responses",
        "template_responses",
        "options",
        "option_sets",
        "steps",
        "sessions",
        "templates",
        "wizards"
    ]

    for table in delete_order:
        print(f"\nDeleting from {table}...")
        cur.execute(f"DELETE FROM {table};")
        deleted = cur.rowcount
        print(f"  ✓ Deleted {deleted} records from {table}")

    # Commit the transaction
    conn.commit()
    print("\n" + "=" * 60)
    print("VERIFYING DELETION")
    print("=" * 60)

    # Verify all tables are empty
    all_empty = True
    for table in tables:
        cur.execute(f"SELECT COUNT(*) FROM {table};")
        count = cur.fetchone()[0]
        status = "✓ EMPTY" if count == 0 else f"✗ STILL HAS {count} RECORDS"
        print(f"{table}: {status}")
        if count > 0:
            all_empty = False

    print("\n" + "=" * 60)
    if all_empty:
        print("SUCCESS! All wizard data has been deleted!")
        print("Database is now completely empty.")
    else:
        print("WARNING! Some tables still have data.")
        print("There may be foreign key constraint issues.")
    print("=" * 60)

    cur.close()
    conn.close()

except psycopg2.Error as e:
    print(f"\n✗ Database error: {e}")
    print("\nPossible issues:")
    print("1. Wrong password - update DB_PASSWORD in the script")
    print("2. Database not running - start PostgreSQL server")
    print("3. Wrong database name - check DB_NAME")
    if conn:
        conn.rollback()
except Exception as e:
    print(f"\n✗ Error: {e}")
    if conn:
        conn.rollback()
finally:
    if 'conn' in locals() and conn:
        conn.close()
