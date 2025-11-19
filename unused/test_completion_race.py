import sys
import os
import time
from uuid import uuid4
from datetime import datetime, timezone

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.database import SessionLocal
from app.models.session import UserSession
from app.models.wizard import Wizard

def create_and_complete_session():
    db = SessionLocal()
    try:
        # 1. Get a wizard
        wizard = db.query(Wizard).first()
        if not wizard:
            print("No wizard found.")
            return

        # 2. Create a session
        session_id = uuid4()
        session = UserSession(
            id=session_id,
            wizard_id=wizard.id,
            session_name="Race Condition Test",
            status="in_progress",
            started_at=datetime.now(timezone.utc),
            last_activity_at=datetime.now(timezone.utc)
        )
        db.add(session)
        db.commit()
        
        print(f"Session Created: {session_id}")
        print(f"URL: http://localhost:3000/wizard/{wizard.id}?session={session_id}")
        print("\n--> OPEN THIS URL IN BROWSER NOW AND GO TO LAST STEP <--")
        print("Waiting 30 seconds for you to open browser...")
        time.sleep(30)
        
        # 3. Mark as completed (Simulating race condition)
        print("\n--> MARKING SESSION AS COMPLETED IN DB <--")
        session = db.query(UserSession).filter(UserSession.id == session_id).first()
        session.status = "completed"
        session.completed_at = datetime.now(timezone.utc)
        db.commit()
        print("Session marked as completed in DB.")
        print("Now click 'Complete' in the browser. You should see SUCCESS, not Error.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_and_complete_session()
