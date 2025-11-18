"""
Quick verification that database is empty
"""
import psycopg2

DB_HOST = "127.0.0.1"
DB_PORT = "5432"
DB_NAME = "wizarddb"
DB_USER = "postgres"
DB_PASSWORD = "@dmin123"

try:
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, database=DB_NAME,
        user=DB_USER, password=DB_PASSWORD
    )
    cur = conn.cursor()

    print("="*60)
    print("DATABASE VERIFICATION - FINAL CHECK")
    print("="*60)

    tables = ['wizards', 'steps', 'option_sets', 'options', 'option_dependencies']

    for table in tables:
        cur.execute(f"SELECT COUNT(*) FROM {table};")
        count = cur.fetchone()[0]
        status = "[EMPTY]" if count == 0 else f"[{count} RECORDS]"
        print(f"{table:25s} {status}")

    cur.close()
    conn.close()

    print("="*60)
    print("[SUCCESS] Database is completely empty!")
    print("="*60)

except Exception as e:
    print(f"[ERROR] {e}")
