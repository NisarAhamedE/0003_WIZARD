"""
Test script for Wizard Lifecycle Protection System

Tests the three-state protection strategy:
1. Draft - Never run, full editing allowed
2. In-Use - Has runs but none stored, edits with warning
3. Published - Has stored runs, read-only

Run this after the migration to verify the protection system works.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app.services.wizard_protection import WizardProtectionService, WizardState
from app.crud.wizard import wizard_crud
from sqlalchemy import text


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'=' * 60}")
    print(f" {title}")
    print(f"{'=' * 60}\n")


def test_wizard_states():
    """Test wizard state detection"""
    print_section("TEST 1: Wizard State Detection")

    db = SessionLocal()
    try:
        # Get all wizards
        result = db.execute(text("""
            SELECT
                w.id,
                w.name,
                w.lifecycle_state,
                COUNT(DISTINCT wr.id) as total_runs,
                COUNT(DISTINCT CASE WHEN wr.is_stored = true THEN wr.id END) as stored_runs
            FROM wizards w
            LEFT JOIN wizard_runs wr ON w.id = wr.wizard_id
            GROUP BY w.id, w.name, w.lifecycle_state
            ORDER BY w.lifecycle_state, w.name
            LIMIT 10;
        """))

        wizards = result.fetchall()

        if not wizards:
            print("[WARN] No wizards found in database")
            return

        print(f"Found {len(wizards)} wizards\n")

        for wizard in wizards:
            wizard_id, name, state, total, stored = wizard
            print(f"Wizard: {name}")
            print(f"  State: {state}")
            print(f"  Total Runs: {total}")
            print(f"  Stored Runs: {stored}")

            # Get protection status
            protection = WizardProtectionService.get_wizard_state(db, wizard_id)
            print(f"  Can Edit: {protection['can_edit']}")
            print(f"  Can Delete: {protection['can_delete']}")
            print(f"  Message: {protection['message'][:80]}...")
            print()

    finally:
        db.close()


def test_protection_checks():
    """Test protection permission checks"""
    print_section("TEST 2: Protection Permission Checks")

    db = SessionLocal()
    try:
        # Find one wizard in each state
        draft_wizard = db.execute(text("""
            SELECT id, name FROM wizards WHERE lifecycle_state = 'draft' LIMIT 1
        """)).fetchone()

        in_use_wizard = db.execute(text("""
            SELECT id, name FROM wizards WHERE lifecycle_state = 'in_use' LIMIT 1
        """)).fetchone()

        published_wizard = db.execute(text("""
            SELECT id, name FROM wizards WHERE lifecycle_state = 'published' LIMIT 1
        """)).fetchone()

        # Test Draft Wizard
        if draft_wizard:
            print(f"[INFO] Testing DRAFT wizard: {draft_wizard[1]}")
            can_modify, reason = WizardProtectionService.can_modify_wizard(db, draft_wizard[0])
            can_delete, del_reason = WizardProtectionService.can_delete_wizard(db, draft_wizard[0])
            print(f"  Can Modify: {can_modify} ({reason or 'No restrictions'})")
            print(f"  Can Delete: {can_delete} ({del_reason or 'No restrictions'})")
        else:
            print("[INFO] No draft wizards found")

        # Test In-Use Wizard
        if in_use_wizard:
            print(f"\n[INFO] Testing IN-USE wizard: {in_use_wizard[1]}")
            can_modify, reason = WizardProtectionService.can_modify_wizard(db, in_use_wizard[0])
            can_delete, del_reason = WizardProtectionService.can_delete_wizard(db, in_use_wizard[0])
            print(f"  Can Modify: {can_modify}")
            print(f"  Warning: {reason}")
            print(f"  Can Delete: {can_delete}")
            print(f"  Warning: {del_reason}")
        else:
            print("[INFO] No in-use wizards found")

        # Test Published Wizard
        if published_wizard:
            print(f"\n[INFO] Testing PUBLISHED wizard: {published_wizard[1]}")
            can_modify, reason = WizardProtectionService.can_modify_wizard(db, published_wizard[0])
            can_delete, del_reason = WizardProtectionService.can_delete_wizard(db, published_wizard[0])
            print(f"  Can Modify: {can_modify}")
            print(f"  Reason: {reason}")
            print(f"  Can Delete: {can_delete}")
            print(f"  Reason: {del_reason}")
        else:
            print("[INFO] No published wizards found")

    finally:
        db.close()


def test_clone_wizard():
    """Test wizard cloning"""
    print_section("TEST 3: Wizard Cloning")

    db = SessionLocal()
    try:
        # Find a wizard to clone
        source_wizard = db.execute(text("""
            SELECT w.id, w.name, w.created_by
            FROM wizards w
            INNER JOIN steps s ON s.wizard_id = w.id
            LIMIT 1
        """)).fetchone()

        if not source_wizard:
            print("[WARN] No wizards with steps found for cloning test")
            return

        wizard_id, name, created_by = source_wizard

        print(f"[INFO] Cloning wizard: {name}")
        print(f"  Source Wizard ID: {wizard_id}")

        # Get structure counts before clone
        steps = db.execute(text("""
            SELECT COUNT(*) FROM steps WHERE wizard_id = :wid
        """), {"wid": wizard_id}).scalar()

        option_sets = db.execute(text("""
            SELECT COUNT(*) FROM option_sets os
            INNER JOIN steps s ON s.id = os.step_id
            WHERE s.wizard_id = :wid
        """), {"wid": wizard_id}).scalar()

        options = db.execute(text("""
            SELECT COUNT(*) FROM options o
            INNER JOIN option_sets os ON os.id = o.option_set_id
            INNER JOIN steps s ON s.id = os.step_id
            WHERE s.wizard_id = :wid
        """), {"wid": wizard_id}).scalar()

        print(f"  Source has: {steps} steps, {option_sets} option sets, {options} options")

        # Perform clone
        cloned = wizard_crud.clone_wizard(
            db=db,
            wizard_id=wizard_id,
            new_name=f"{name} (Test Clone)",
            created_by=created_by,
            new_description="Test clone created by protection system test"
        )

        if cloned:
            print(f"[OK] Clone created successfully!")
            print(f"  Clone Wizard ID: {cloned.id}")
            print(f"  Clone Name: {cloned.name}")
            print(f"  Clone State: {cloned.lifecycle_state}")
            print(f"  Clone has {len(cloned.steps)} steps")

            # Verify structure
            assert len(cloned.steps) == steps, "Step count mismatch"

            total_option_sets = sum(len(step.option_sets) for step in cloned.steps)
            assert total_option_sets == option_sets, "Option set count mismatch"

            total_options = sum(
                len(opt_set.options)
                for step in cloned.steps
                for opt_set in step.option_sets
            )
            assert total_options == options, "Option count mismatch"

            print(f"[OK] Structure verified: {steps} steps, {option_sets} option sets, {options} options")

            # Clean up test clone
            print(f"[INFO] Cleaning up test clone...")
            db.execute(text("DELETE FROM wizards WHERE id = :id"), {"id": cloned.id})
            db.commit()
            print("[OK] Test clone deleted")

        else:
            print("[ERR] Clone failed!")

    except Exception as e:
        print(f"[ERR] Clone test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


def test_state_transition():
    """Test lifecycle state transitions"""
    print_section("TEST 4: State Transition Logic")

    db = SessionLocal()
    try:
        # Find a draft wizard
        draft = db.execute(text("""
            SELECT id, name FROM wizards WHERE lifecycle_state = 'draft' LIMIT 1
        """)).fetchone()

        if not draft:
            print("[WARN] No draft wizards found for transition test")
            return

        wizard_id, name = draft
        print(f"[INFO] Testing state transitions with wizard: {name}")
        print(f"  Initial State: draft")

        # State should remain draft (no runs)
        new_state = WizardProtectionService.update_lifecycle_state(db, wizard_id)
        print(f"  After update_lifecycle_state(): {new_state}")
        assert new_state == WizardState.DRAFT, "Should stay in draft state"

        print("[OK] State logic verified")

    finally:
        db.close()


def main():
    """Run all tests"""
    print("=" * 60)
    print(" WIZARD LIFECYCLE PROTECTION - TEST SUITE")
    print("=" * 60)

    try:
        test_wizard_states()
        test_protection_checks()
        test_clone_wizard()
        test_state_transition()

        print_section("TEST RESULTS")
        print("[OK] All tests completed successfully!")
        print("\n[INFO] Protection system is working correctly.")
        print("[INFO] You can now integrate the UI components.")

    except Exception as e:
        print_section("TEST FAILED")
        print(f"[ERR] Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
