"""
Test script to verify view functionality for stored wizard runs
This script will:
1. Create a wizard run
2. Add responses to all steps
3. Complete and save the run
4. Fetch the run to verify responses are stored
"""

import requests
import json
from uuid import uuid4

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_view_functionality():
    print("=" * 80)
    print("TESTING VIEW FUNCTIONALITY")
    print("=" * 80)

    # Step 1: Get list of available wizards
    print("\n1. Fetching available wizards...")
    response = requests.get(f"{BASE_URL}/wizards/")
    wizards = response.json()

    if not wizards:
        print("[ERR] No wizards found!")
        return

    wizard = wizards[0]
    print(f"[OK] Using wizard: {wizard['name']} (ID: {wizard['id']})")

    # Step 2: Get full wizard details with steps
    print(f"\n2. Fetching wizard details...")
    response = requests.get(f"{BASE_URL}/wizards/{wizard['id']}")
    wizard_full = response.json()
    print(f"[OK] Wizard has {len(wizard_full['steps'])} steps")

    # Step 3: Create a new wizard run
    print(f"\n3. Creating wizard run...")
    run_data = {
        "wizard_id": wizard['id'],
        "run_name": f"Test View Run {uuid4().hex[:8]}"
    }
    response = requests.post(f"{BASE_URL}/wizard-runs/", json=run_data)
    run = response.json()
    run_id = run['id']
    print(f"[OK] Created run: {run['run_name']} (ID: {run_id})")

    # Step 4: Add responses for each step
    print(f"\n4. Adding responses for all steps...")
    total_option_sets = 0

    for step_index, step in enumerate(wizard_full['steps']):
        print(f"\n   Step {step_index + 1}: {step['name']}")

        # Create step response
        step_response_data = {
            "run_id": run_id,
            "step_id": step['id'],
            "step_index": step_index,
            "step_name": step['name']
        }

        response = requests.post(
            f"{BASE_URL}/wizard-runs/{run_id}/steps",
            json=step_response_data
        )
        step_response = response.json()
        print(f"   [OK] Created step response (ID: {step_response['id']})")

        # Add option set responses
        for option_set in step['option_sets']:
            print(f"      - {option_set['name']} ({option_set['selection_type']})")

            # Generate appropriate test value based on selection type
            test_value = None

            if option_set['selection_type'] == 'single_select':
                if option_set['options']:
                    test_value = option_set['options'][0]['value']
            elif option_set['selection_type'] == 'multiple_select':
                if len(option_set['options']) >= 2:
                    test_value = [option_set['options'][0]['value'], option_set['options'][1]['value']]
                elif option_set['options']:
                    test_value = [option_set['options'][0]['value']]
            elif option_set['selection_type'] == 'text_input':
                test_value = f"Test text for {option_set['name']}"
            elif option_set['selection_type'] == 'number_input':
                test_value = 42
            elif option_set['selection_type'] in ['date_input', 'datetime_input']:
                test_value = "2025-11-19"
            elif option_set['selection_type'] == 'time_input':
                test_value = "14:30"
            elif option_set['selection_type'] == 'rating':
                test_value = 4
            elif option_set['selection_type'] == 'slider':
                test_value = 50
            elif option_set['selection_type'] == 'color_picker':
                test_value = "#ff5733"
            elif option_set['selection_type'] == 'rich_text':
                test_value = f"<p>Rich text for {option_set['name']}</p>"
            else:
                test_value = "test"

            if test_value is not None:
                option_set_response_data = {
                    "run_id": run_id,
                    "step_response_id": step_response['id'],
                    "option_set_id": option_set['id'],
                    "option_set_name": option_set['name'],
                    "selection_type": option_set['selection_type'],
                    "response_value": {"value": test_value}
                }

                response = requests.post(
                    f"{BASE_URL}/wizard-runs/{run_id}/option-sets",
                    json=option_set_response_data
                )

                if response.status_code == 200:
                    print(f"        [OK] Saved: {test_value}")
                    total_option_sets += 1
                else:
                    print(f"        [ERR] Failed to save: {response.status_code}")

    print(f"\n   [STAT] Total option set responses created: {total_option_sets}")

    # Step 5: Update run to completed status
    print(f"\n5. Marking run as completed...")
    update_data = {
        "status": "completed",
        "is_stored": True
    }
    response = requests.put(f"{BASE_URL}/wizard-runs/{run_id}", json=update_data)

    if response.status_code == 200:
        print(f"[OK] Run marked as completed and stored")
    else:
        print(f"[ERR] Failed to update run: {response.status_code}")

    # Step 6: Fetch the run to verify all data is there
    print(f"\n6. Fetching run to verify stored data...")
    response = requests.get(f"{BASE_URL}/wizard-runs/{run_id}")
    stored_run = response.json()

    print(f"\n[INFO] RUN DETAILS:")
    print(f"   ID: {stored_run['id']}")
    print(f"   Name: {stored_run.get('run_name', 'N/A')}")
    print(f"   Status: {stored_run['status']}")
    print(f"   Is Stored: {stored_run['is_stored']}")
    print(f"   Step Responses: {len(stored_run.get('step_responses', []))}")
    print(f"   Option Set Responses: {len(stored_run.get('option_set_responses', []))}")

    # Step 7: Display all saved responses
    print(f"\n7. SAVED RESPONSES:")
    if stored_run.get('option_set_responses'):
        for idx, resp in enumerate(stored_run['option_set_responses'], 1):
            value = resp['response_value'].get('value') if isinstance(resp['response_value'], dict) else resp['response_value']
            print(f"   {idx}. {resp.get('option_set_name', 'Unknown')}: {value}")
    else:
        print("   [ERR] No responses found!")

    # Step 8: Instructions for UI testing
    print(f"\n" + "=" * 80)
    print("UI TESTING INSTRUCTIONS:")
    print("=" * 80)
    print(f"\n1. Open browser to: http://localhost:3001")
    print(f"2. Navigate to 'Store Wizard' page")
    print(f"3. Find the run: {run_data['run_name']}")
    print(f"4. Click the 'View' button")
    print(f"\n[OK] EXPECTED RESULT:")
    print(f"   - Blue 'View Mode' banner should appear at top")
    print(f"   - All {len(stored_run.get('option_set_responses', []))} saved responses should be visible")
    print(f"   - All fields should be disabled/read-only")
    print(f"   - You should be able to navigate through all steps using Previous/Next")
    print(f"\n[STAT] CHECK BROWSER CONSOLE:")
    print(f"   - Press F12 to open Developer Tools")
    print(f"   - Look for logs starting with '[WizardPlayer]'")
    print(f"   - Verify 'Number of responses: {len(stored_run.get('option_set_responses', []))}'")
    print(f"\n[LINK] DIRECT LINK:")
    print(f"   http://localhost:3001/wizard/{wizard['id']}?session={run_id}&view_only=true")
    print(f"\n" + "=" * 80)

    return run_id, wizard['id']

if __name__ == "__main__":
    try:
        test_view_functionality()
    except Exception as e:
        print(f"\n[ERR] ERROR: {e}")
        import traceback
        traceback.print_exc()
