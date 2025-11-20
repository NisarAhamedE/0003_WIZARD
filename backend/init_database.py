"""
Initialize database schema.
Creates all tables based on SQLAlchemy models.
"""
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db

if __name__ == "__main__":
    print("[*] Initializing database schema...")
    try:
        init_db()
        print("[OK] Database schema created successfully!")
    except Exception as e:
        print(f"[ERROR] Failed to initialize database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
