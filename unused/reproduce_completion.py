import sys
import os
from datetime import datetime, timezone
from uuid import uuid4
from decimal import Decimal

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.database import SessionLocal
from app.crud.session import session_crud
from app.models.wizard import Wizard
from app.models.session import UserSession

def reproduce():
    db = SessionLocal()
    try:
        # 1. Test with NEW session (should be aware)
        print("--- Testing NEW Session (Aware Timestamps) ---")
        wizard = db.query(Wizard).first()
        if not wizard:
            print("No wizard found.")
            return

        session = UserSession(
            id=uuid4(),
            wizard_id=wizard.id,
            session_name="Test Completion Aware",
            status="in_progress",
            started_at=datetime.now(timezone.utc), # Aware
            last_activity_at=datetime.now(timezone.utc)
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        print(f"Created session {session.id} with started_at: {session.started_at} (tzinfo: {session.started_at.tzinfo})")

        # Try to complete
        try:
            session_crud.complete_session(db, session)
            print("Successfully completed NEW session.")
        except Exception as e:
            print(f"FAILED to complete NEW session: {e}")
            import traceback
            traceback.print_exc()

        # 2. Test with OLD session (Naive Timestamps)
        print("\n--- Testing OLD Session (Naive Timestamps) ---")
        session_naive = UserSession(
            id=uuid4(),
            wizard_id=wizard.id,
            session_name="Test Completion Naive",
            status="in_progress",
            started_at=datetime.utcnow(), # Naive
            last_activity_at=datetime.utcnow()
        )
        db.add(session_naive)
        db.commit()
        db.refresh(session_naive)
        # Force naive if SQLAlchemy made it aware (hack to simulate old data if needed, 
        # but usually if we pass naive to DateTime(timezone=True), Postgres might save it as UTC but return it... depends on driver)
        # Let's check what we got back
        print(f"Created session {session_naive.id} with started_at: {session_naive.started_at} (tzinfo: {session_naive.started_at.tzinfo})")
        
        # If it came back aware, we might need to manually strip it to simulate the error if the DB driver isn't doing it.
        # But the error happens in python.
        # If the DB returns aware, then we are good? 
        # The error "can't subtract offset-naive and offset-aware" implies one IS naive.
        
        if session_naive.started_at.tzinfo is not None:
             print("DB returned aware datetime even for naive input. Forcing naive for reproduction...")
             session_naive.started_at = session_naive.started_at.replace(tzinfo=None)

        # Try to complete
        try:
            session_crud.complete_session(db, session_naive)
            print("Successfully completed OLD session.")
        except Exception as e:
            print(f"FAILED to complete OLD session: {e}")
            import traceback
            traceback.print_exc()

    except Exception as e:
        print(f"General Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reproduce()
