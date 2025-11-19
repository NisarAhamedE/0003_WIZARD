import sys
import os
from datetime import datetime, timezone
from uuid import uuid4

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.database import SessionLocal
from app.crud.session import session_crud
from app.schemas.session import SessionCreate
from app.models.wizard import Wizard
from app.models.user import User

def reproduce():
    db = SessionLocal()
    try:
        # Get a wizard
        wizard = db.query(Wizard).first()
        if not wizard:
            print("No wizard found, creating one...")
            wizard = Wizard(
                id=uuid4(),
                name="Test Wizard",
                description="Test",
                is_published=True,
                user_id=uuid4() # Dummy user
            )
            db.add(wizard)
            db.commit()
            db.refresh(wizard)
        
        print(f"Using wizard: {wizard.id}")

        # Create session
        session_in = SessionCreate(
            wizard_id=wizard.id,
            session_name="Test Session",
            metadata={"test": "data"},
            browser_info={"user_agent": "test"}
        )

        print("Attempting to create session...")
        session = session_crud.create(db, obj_in=session_in, user_id=None)
        print("Session created successfully!")
        print(f"Session ID: {session.id}")
        print(f"Started At: {session.started_at}")
        print(f"Created At: {session.created_at}")

    except Exception as e:
        print("ERROR creating session:")
        print(e)
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    reproduce()
