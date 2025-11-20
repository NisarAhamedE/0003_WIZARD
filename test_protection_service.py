"""
Test if WizardProtectionService works correctly
"""
import sys
sys.path.insert(0, 'backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from uuid import UUID

# Load environment
load_dotenv('backend/.env')
database_url = os.getenv('DATABASE_URL')

# Create engine
engine = create_engine(database_url)
SessionLocal = sessionmaker(bind=engine)

# Test the service
try:
    from app.services.wizard_protection import WizardProtectionService

    db = SessionLocal()
    wizard_id = UUID("504c3d07-a1c2-4f9a-b8f7-4b8e94c863c5")

    print("Testing WizardProtectionService.get_wizard_state()...")
    result = WizardProtectionService.get_wizard_state(db, wizard_id)

    print("\n[SUCCESS] Protection service works!")
    print(f"Result: {result}")

    db.close()

except Exception as e:
    print(f"\n[ERROR] Protection service failed: {e}")
    import traceback
    traceback.print_exc()
