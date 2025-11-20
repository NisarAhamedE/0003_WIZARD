"""
Wizard Lifecycle Protection Service

Implements three-state protection strategy:
1. Draft: Never run, full editing allowed
2. In-Use: Has runs but none stored, edits allowed with warning
3. Published: Has stored runs, read-only (clone/version alternatives)
"""
from typing import Dict, Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.wizard import Wizard
from app.models.wizard_run import WizardRun


class WizardState:
    """Wizard lifecycle states"""
    DRAFT = "draft"
    IN_USE = "in_use"
    PUBLISHED = "published"


class WizardProtectionService:
    """Service for managing wizard lifecycle protection"""

    @staticmethod
    def get_wizard_state(db: Session, wizard_id: UUID) -> Dict:
        """
        Determine the lifecycle state of a wizard based on run activity.

        Args:
            db: Database session
            wizard_id: UUID of the wizard to check

        Returns:
            Dictionary containing:
            - state: current lifecycle state (draft, in_use, published)
            - can_edit: whether editing is allowed
            - can_delete: whether deletion is allowed
            - total_runs: total number of runs
            - stored_runs: number of stored runs
            - in_progress_runs: number of in-progress runs
            - completed_runs: number of completed runs
            - message: user-friendly message explaining the state
            - actions: list of available actions
        """
        # Query run statistics
        runs_query = db.query(WizardRun).filter(WizardRun.wizard_id == wizard_id)

        total_runs = runs_query.count()
        stored_runs = runs_query.filter(WizardRun.is_stored == True).count()
        in_progress_runs = runs_query.filter(WizardRun.status == 'in_progress').count()
        completed_runs = runs_query.filter(WizardRun.status == 'completed').count()

        # Determine state based on run activity
        if total_runs == 0:
            # State 1: Draft - Never been run
            state = WizardState.DRAFT
            can_edit = True
            can_delete = True
            message = "This wizard has never been run. All modifications and deletions are allowed."
            actions = ["edit", "delete", "publish", "test"]

        elif stored_runs > 0:
            # State 3: Published - Has stored runs (read-only)
            state = WizardState.PUBLISHED
            can_edit = False
            can_delete = False
            message = (
                f"This wizard has {stored_runs} stored run(s) and is read-only to protect user data. "
                "You can create a clone or new version to make changes."
            )
            actions = ["view", "clone", "create_version", "archive", "export"]

        else:
            # State 2: In-Use - Has runs but none stored
            state = WizardState.IN_USE
            can_edit = True  # With warning
            can_delete = True  # With warning
            message = (
                f"This wizard has {total_runs} active run(s) but no stored data. "
                "Modifications will affect existing runs. Consider warning users or cloning the wizard."
            )
            actions = ["edit_with_warning", "delete_with_warning", "clone", "view"]

        return {
            "state": state,
            "can_edit": can_edit,
            "can_delete": can_delete,
            "total_runs": total_runs,
            "stored_runs": stored_runs,
            "in_progress_runs": in_progress_runs,
            "completed_runs": completed_runs,
            "message": message,
            "actions": actions,
        }

    @staticmethod
    def can_modify_wizard(db: Session, wizard_id: UUID) -> tuple[bool, Optional[str]]:
        """
        Check if a wizard can be modified.

        Returns:
            Tuple of (can_modify: bool, reason: str)
        """
        wizard = db.query(Wizard).filter(Wizard.id == wizard_id).first()
        if not wizard:
            return False, "Wizard not found"

        if wizard.is_archived:
            return False, "Cannot modify archived wizard"

        state = WizardProtectionService.get_wizard_state(db, wizard_id)

        if state["state"] == WizardState.PUBLISHED:
            return False, f"Wizard has {state['stored_runs']} stored runs and is read-only"

        if state["state"] == WizardState.IN_USE:
            return True, f"Warning: Wizard has {state['total_runs']} active runs that will be affected"

        return True, None  # Draft state

    @staticmethod
    def can_delete_wizard(db: Session, wizard_id: UUID) -> tuple[bool, Optional[str]]:
        """
        Check if a wizard can be deleted.

        Returns:
            Tuple of (can_delete: bool, reason: str)
        """
        wizard = db.query(Wizard).filter(Wizard.id == wizard_id).first()
        if not wizard:
            return False, "Wizard not found"

        state = WizardProtectionService.get_wizard_state(db, wizard_id)

        if state["state"] == WizardState.PUBLISHED:
            return False, f"Cannot delete wizard with {state['stored_runs']} stored runs. Archive instead."

        if state["state"] == WizardState.IN_USE:
            return True, f"Warning: Deleting will remove {state['total_runs']} active runs"

        return True, None  # Draft state

    @staticmethod
    def update_lifecycle_state(db: Session, wizard_id: UUID) -> str:
        """
        Update the wizard's lifecycle_state field based on current run activity.
        This should be called after run creation or state changes.

        Returns:
            The new lifecycle state
        """
        wizard = db.query(Wizard).filter(Wizard.id == wizard_id).first()
        if not wizard:
            return None

        state_info = WizardProtectionService.get_wizard_state(db, wizard_id)
        new_state = state_info["state"]

        # Update wizard lifecycle state if changed
        if wizard.lifecycle_state != new_state:
            wizard.lifecycle_state = new_state

            # Set first_run_at if transitioning from draft
            if new_state in [WizardState.IN_USE, WizardState.PUBLISHED] and not wizard.first_run_at:
                first_run = (
                    db.query(WizardRun)
                    .filter(WizardRun.wizard_id == wizard_id)
                    .order_by(WizardRun.started_at)
                    .first()
                )
                if first_run:
                    wizard.first_run_at = first_run.started_at

            # Set first_stored_run_at if transitioning to published
            if new_state == WizardState.PUBLISHED and not wizard.first_stored_run_at:
                first_stored_run = (
                    db.query(WizardRun)
                    .filter(WizardRun.wizard_id == wizard_id, WizardRun.is_stored == True)
                    .order_by(WizardRun.completed_at)
                    .first()
                )
                if first_stored_run:
                    wizard.first_stored_run_at = first_stored_run.completed_at

            db.commit()

        return new_state

    @staticmethod
    def delete_all_runs_for_wizard(db: Session, wizard_id: UUID) -> int:
        """
        Delete all runs for a wizard (used when user confirms in-use modification).

        Returns:
            Number of runs deleted
        """
        count = db.query(WizardRun).filter(WizardRun.wizard_id == wizard_id).count()

        # Delete all runs (cascade will handle responses and uploads)
        db.query(WizardRun).filter(WizardRun.wizard_id == wizard_id).delete()
        db.commit()

        # Reset wizard to draft state
        wizard = db.query(Wizard).filter(Wizard.id == wizard_id).first()
        if wizard:
            wizard.lifecycle_state = WizardState.DRAFT
            wizard.first_run_at = None
            wizard.first_stored_run_at = None
            db.commit()

        return count

    @staticmethod
    def archive_wizard(db: Session, wizard_id: UUID) -> bool:
        """
        Archive a wizard (soft delete for published wizards).

        Returns:
            True if archived successfully
        """
        wizard = db.query(Wizard).filter(Wizard.id == wizard_id).first()
        if not wizard:
            return False

        wizard.is_archived = True
        wizard.archived_at = datetime.now(timezone.utc)
        wizard.is_active = False
        wizard.is_published = False
        db.commit()

        return True

    @staticmethod
    def unarchive_wizard(db: Session, wizard_id: UUID) -> bool:
        """
        Unarchive a wizard.

        Returns:
            True if unarchived successfully
        """
        wizard = db.query(Wizard).filter(Wizard.id == wizard_id).first()
        if not wizard:
            return False

        wizard.is_archived = False
        wizard.archived_at = None
        wizard.is_active = True
        db.commit()

        return True

    @staticmethod
    def create_wizard_version(
        db: Session, wizard_id: UUID, new_name: Optional[str] = None
    ) -> Optional[Wizard]:
        """
        Create a new version of an existing wizard.
        Links to parent via parent_wizard_id, increments version_number.

        Args:
            db: Database session
            wizard_id: UUID of the wizard to version
            new_name: Optional new name for the version

        Returns:
            The new wizard version, or None if failed
        """
        from app.crud.wizard import wizard_crud

        original_wizard = db.query(Wizard).filter(Wizard.id == wizard_id).first()
        if not original_wizard:
            return None

        # Determine version number
        # Find highest version number in the wizard family
        highest_version = (
            db.query(func.max(Wizard.version_number))
            .filter(
                (Wizard.id == wizard_id) | (Wizard.parent_wizard_id == wizard_id)
            )
            .scalar()
        ) or 1

        new_version_number = highest_version + 1

        # Generate new name if not provided
        if not new_name:
            new_name = f"{original_wizard.name} v{new_version_number}"

        # Create the clone with version metadata
        cloned_wizard = wizard_crud.clone_wizard(
            db=db,
            wizard_id=wizard_id,
            new_name=new_name,
            created_by=original_wizard.created_by,
        )

        if cloned_wizard:
            # Set version metadata
            cloned_wizard.parent_wizard_id = wizard_id
            cloned_wizard.version_number = new_version_number
            cloned_wizard.lifecycle_state = WizardState.DRAFT  # New version starts as draft
            db.commit()
            db.refresh(cloned_wizard)

        return cloned_wizard
