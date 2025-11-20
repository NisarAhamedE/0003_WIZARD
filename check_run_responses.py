import sys
sys.path.insert(0, 'backend')

from app.database import SessionLocal
from app.models.wizard_run import WizardRun
from app.models.session import OptionSetResponse

db = SessionLocal()

# Check the specific run
run_id = '8ef37f6e-5c08-46e4-8c2e-9fb30ed65b56'
run = db.query(WizardRun).filter(WizardRun.id == run_id).first()

if run:
    print(f"[*] Run Found: {run.run_name}")
    print(f"    Status: {run.status}")
    print(f"    Wizard ID: {run.wizard_id}")
    print(f"    Current Step ID: {run.current_step_id}")
    print(f"    Completed at: {run.completed_at}")
else:
    print(f"[ERROR] Run {run_id} not found")
    db.close()
    sys.exit(1)

# Check responses
responses = db.query(OptionSetResponse).filter(
    OptionSetResponse.session_id == run_id
).all()

print(f"\n[*] Total responses in database: {len(responses)}")

if responses:
    for i, resp in enumerate(responses):
        print(f"    Response {i+1}:")
        print(f"      - Option Set ID: {resp.option_set_id}")
        print(f"      - Response Data: {resp.response_data}")
        print(f"      - Selected Option IDs: {resp.selected_option_ids}")
else:
    print("[WARNING] No responses found for this run!")

db.close()
