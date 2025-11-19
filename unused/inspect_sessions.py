import sys
import os
from datetime import datetime, timezone
from sqlalchemy import desc

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.database import SessionLocal
from app.models.session import UserSession

def inspect_sessions():
    db = SessionLocal()
    try:
        print("--- Recent Sessions ---")
        sessions = db.query(UserSession).order_by(desc(UserSession.updated_at)).limit(5).all()
        
        for s in sessions:
            print(f"ID: {s.id}")
            print(f"Name: {s.session_name}")
            print(f"Status: {s.status}")
            print(f"Started At: {s.started_at}")
            print(f"Completed At: {s.completed_at}")
            print(f"Updated At: {s.updated_at}")
            print("-" * 30)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    inspect_sessions()
