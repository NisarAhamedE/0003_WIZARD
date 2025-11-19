"""
Wizard Run CRUD Operations

Database operations for wizard runs, step responses, and related entities.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timezone
import secrets

from app.models.wizard_run import (
    WizardRun,
    WizardRunStepResponse,
    WizardRunOptionSetResponse,
    WizardRunFileUpload,
    WizardRunShare,
    WizardRunComparison
)
from app.schemas.wizard_run import (
    WizardRunCreate,
    WizardRunUpdate,
    WizardRunStepResponseCreate,
    WizardRunStepResponseUpdate,
    WizardRunOptionSetResponseCreate,
    WizardRunOptionSetResponseUpdate,
    WizardRunFileUploadCreate,
    WizardRunShareCreate,
    WizardRunComparisonCreate,
)


class WizardRunCRUD:
    """CRUD operations for WizardRun model."""

    def get(self, db: Session, run_id: UUID) -> Optional[WizardRun]:
        """Get a wizard run by ID."""
        return db.query(WizardRun).filter(WizardRun.id == run_id).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 20,
        user_id: Optional[UUID] = None,
        wizard_id: Optional[UUID] = None,
        status: Optional[str] = None,
        is_stored: Optional[bool] = None,
        is_favorite: Optional[bool] = None,
    ) -> tuple[List[WizardRun], int]:
        """
        Get multiple wizard runs with filtering and pagination.
        Returns tuple of (runs, total_count).
        """
        query = db.query(WizardRun)

        # Apply filters
        if user_id:
            query = query.filter(WizardRun.user_id == user_id)
        if wizard_id:
            query = query.filter(WizardRun.wizard_id == wizard_id)
        if status:
            query = query.filter(WizardRun.status == status)
        if is_stored is not None:
            query = query.filter(WizardRun.is_stored == is_stored)
        if is_favorite is not None:
            query = query.filter(WizardRun.is_favorite == is_favorite)

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        runs = query.order_by(desc(WizardRun.last_accessed_at))\
            .offset(skip)\
            .limit(limit)\
            .all()

        return runs, total

    def get_in_progress(self, db: Session, user_id: UUID) -> List[WizardRun]:
        """Get all in-progress runs for a user."""
        return db.query(WizardRun)\
            .filter(
                WizardRun.user_id == user_id,
                WizardRun.status == 'in_progress'
            )\
            .order_by(desc(WizardRun.last_accessed_at))\
            .all()

    def get_completed(self, db: Session, user_id: UUID, skip: int = 0, limit: int = 20) -> List[WizardRun]:
        """Get completed runs for a user."""
        return db.query(WizardRun)\
            .filter(
                WizardRun.user_id == user_id,
                WizardRun.status == 'completed'
            )\
            .order_by(desc(WizardRun.completed_at))\
            .offset(skip)\
            .limit(limit)\
            .all()

    def get_stored(self, db: Session, user_id: UUID, skip: int = 0, limit: int = 20) -> List[WizardRun]:
        """Get stored runs for a user."""
        return db.query(WizardRun)\
            .filter(
                WizardRun.user_id == user_id,
                WizardRun.is_stored == True
            )\
            .order_by(desc(WizardRun.completed_at))\
            .offset(skip)\
            .limit(limit)\
            .all()

    def get_favorites(self, db: Session, user_id: UUID) -> List[WizardRun]:
        """Get favorite runs for a user."""
        return db.query(WizardRun)\
            .filter(
                WizardRun.user_id == user_id,
                WizardRun.is_favorite == True
            )\
            .order_by(desc(WizardRun.last_accessed_at))\
            .all()

    def create(self, db: Session, obj_in: WizardRunCreate, user_id: Optional[UUID] = None) -> WizardRun:
        """Create a new wizard run."""
        # Get wizard to set total_steps
        from app.models.wizard import Wizard
        wizard = db.query(Wizard).filter(Wizard.id == obj_in.wizard_id).first()
        total_steps = len(wizard.steps) if wizard else 0

        db_obj = WizardRun(
            wizard_id=obj_in.wizard_id,
            user_id=user_id,
            run_name=obj_in.run_name,
            run_description=obj_in.run_description,
            total_steps=total_steps,
            status='in_progress',
            current_step_index=0,
            progress_percentage=0,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: WizardRun, obj_in: WizardRunUpdate
    ) -> WizardRun:
        """Update a wizard run."""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        # Update last_accessed_at
        db_obj.last_accessed_at = datetime.now(timezone.utc)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_progress(
        self, db: Session, run_id: UUID, current_step_index: int
    ) -> Optional[WizardRun]:
        """Update progress of a wizard run."""
        obj = db.query(WizardRun).filter(WizardRun.id == run_id).first()
        if obj:
            obj.current_step_index = current_step_index
            if obj.total_steps and obj.total_steps > 0:
                obj.progress_percentage = round((current_step_index / obj.total_steps) * 100, 2)
            obj.last_accessed_at = datetime.now(timezone.utc)
            db.add(obj)
            db.commit()
            db.refresh(obj)
        return obj

    def complete(
        self,
        db: Session,
        run_id: UUID,
        *,
        run_name: Optional[str] = None,
        run_description: Optional[str] = None,
        save_to_store: bool = False,
        tags: Optional[List[str]] = None,
    ) -> Optional[WizardRun]:
        """Complete a wizard run."""
        obj = db.query(WizardRun).filter(WizardRun.id == run_id).first()
        if obj:
            obj.status = 'completed'
            obj.progress_percentage = 100
            obj.completed_at = datetime.now(timezone.utc)
            obj.is_stored = save_to_store
            if run_name:
                obj.run_name = run_name
            if run_description:
                obj.run_description = run_description
            if tags:
                obj.tags = tags
            db.add(obj)
            db.commit()
            db.refresh(obj)
        return obj

    def abandon(self, db: Session, run_id: UUID) -> Optional[WizardRun]:
        """Mark a wizard run as abandoned."""
        obj = db.query(WizardRun).filter(WizardRun.id == run_id).first()
        if obj:
            obj.status = 'abandoned'
            db.add(obj)
            db.commit()
            db.refresh(obj)
        return obj

    def delete(self, db: Session, *, run_id: UUID) -> bool:
        """Delete a wizard run."""
        obj = db.query(WizardRun).filter(WizardRun.id == run_id).first()
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False

    def get_statistics(self, db: Session, user_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Get statistics about wizard runs."""
        query = db.query(WizardRun)
        if user_id:
            query = query.filter(WizardRun.user_id == user_id)

        total_runs = query.count()
        completed_runs = query.filter(WizardRun.status == 'completed').count()
        in_progress_runs = query.filter(WizardRun.status == 'in_progress').count()
        abandoned_runs = query.filter(WizardRun.status == 'abandoned').count()
        stored_runs = query.filter(WizardRun.is_stored == True).count()

        # Calculate average progress
        avg_progress = db.query(func.avg(WizardRun.progress_percentage))\
            .filter(WizardRun.user_id == user_id if user_id else True)\
            .scalar() or 0

        # Calculate average completion time for completed runs
        completed_query = query.filter(
            WizardRun.status == 'completed',
            WizardRun.completed_at.isnot(None)
        )
        avg_completion_time = None
        if completed_query.count() > 0:
            times = [
                (run.completed_at - run.started_at).total_seconds()
                for run in completed_query.all()
                if run.completed_at
            ]
            if times:
                avg_completion_time = sum(times) / len(times)

        return {
            'total_runs': total_runs,
            'completed_runs': completed_runs,
            'in_progress_runs': in_progress_runs,
            'abandoned_runs': abandoned_runs,
            'stored_runs': stored_runs,
            'average_progress': float(avg_progress),
            'average_completion_time': avg_completion_time,
        }


class WizardRunStepResponseCRUD:
    """CRUD operations for WizardRunStepResponse model."""

    def get(self, db: Session, response_id: UUID) -> Optional[WizardRunStepResponse]:
        """Get a step response by ID."""
        return db.query(WizardRunStepResponse).filter(WizardRunStepResponse.id == response_id).first()

    def get_by_run_and_step(
        self, db: Session, run_id: UUID, step_id: UUID
    ) -> Optional[WizardRunStepResponse]:
        """Get step response for a specific run and step."""
        return db.query(WizardRunStepResponse)\
            .filter(
                WizardRunStepResponse.run_id == run_id,
                WizardRunStepResponse.step_id == step_id
            )\
            .first()

    def get_multi_by_run(self, db: Session, run_id: UUID) -> List[WizardRunStepResponse]:
        """Get all step responses for a run."""
        return db.query(WizardRunStepResponse)\
            .filter(WizardRunStepResponse.run_id == run_id)\
            .order_by(WizardRunStepResponse.step_index)\
            .all()

    def create(self, db: Session, obj_in: WizardRunStepResponseCreate) -> WizardRunStepResponse:
        """Create a new step response."""
        db_obj = WizardRunStepResponse(
            run_id=obj_in.run_id,
            step_id=obj_in.step_id,
            step_index=obj_in.step_index,
            step_name=obj_in.step_name,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: WizardRunStepResponse, obj_in: WizardRunStepResponseUpdate
    ) -> WizardRunStepResponse:
        """Update a step response."""
        update_data = obj_in.model_dump(exclude_unset=True)

        # If marking as completed, set completed_at
        if update_data.get('completed') and not db_obj.completed:
            update_data['completed_at'] = datetime.now(timezone.utc)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def mark_completed(self, db: Session, response_id: UUID) -> Optional[WizardRunStepResponse]:
        """Mark a step response as completed."""
        obj = db.query(WizardRunStepResponse).filter(WizardRunStepResponse.id == response_id).first()
        if obj and not obj.completed:
            obj.completed = True
            obj.completed_at = datetime.now(timezone.utc)
            db.add(obj)
            db.commit()
            db.refresh(obj)
        return obj


class WizardRunOptionSetResponseCRUD:
    """CRUD operations for WizardRunOptionSetResponse model."""

    def get(self, db: Session, response_id: UUID) -> Optional[WizardRunOptionSetResponse]:
        """Get an option set response by ID."""
        return db.query(WizardRunOptionSetResponse)\
            .filter(WizardRunOptionSetResponse.id == response_id)\
            .first()

    def get_by_run_and_option_set(
        self, db: Session, run_id: UUID, option_set_id: UUID
    ) -> Optional[WizardRunOptionSetResponse]:
        """Get option set response for a specific run and option set."""
        return db.query(WizardRunOptionSetResponse)\
            .filter(
                WizardRunOptionSetResponse.run_id == run_id,
                WizardRunOptionSetResponse.option_set_id == option_set_id
            )\
            .first()

    def get_multi_by_run(self, db: Session, run_id: UUID) -> List[WizardRunOptionSetResponse]:
        """Get all option set responses for a run."""
        return db.query(WizardRunOptionSetResponse)\
            .filter(WizardRunOptionSetResponse.run_id == run_id)\
            .all()

    def get_multi_by_step_response(
        self, db: Session, step_response_id: UUID
    ) -> List[WizardRunOptionSetResponse]:
        """Get all option set responses for a step response."""
        return db.query(WizardRunOptionSetResponse)\
            .filter(WizardRunOptionSetResponse.step_response_id == step_response_id)\
            .all()

    def create(self, db: Session, obj_in: WizardRunOptionSetResponseCreate) -> WizardRunOptionSetResponse:
        """Create a new option set response."""
        db_obj = WizardRunOptionSetResponse(
            run_id=obj_in.run_id,
            step_response_id=obj_in.step_response_id,
            option_set_id=obj_in.option_set_id,
            option_set_name=obj_in.option_set_name,
            selection_type=obj_in.selection_type,
            response_value=obj_in.response_value,
            selected_options=obj_in.selected_options,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: WizardRunOptionSetResponse, obj_in: WizardRunOptionSetResponseUpdate
    ) -> WizardRunOptionSetResponse:
        """Update an option set response."""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class WizardRunFileUploadCRUD:
    """CRUD operations for WizardRunFileUpload model."""

    def get(self, db: Session, file_id: UUID) -> Optional[WizardRunFileUpload]:
        """Get a file upload by ID."""
        return db.query(WizardRunFileUpload).filter(WizardRunFileUpload.id == file_id).first()

    def get_multi_by_run(self, db: Session, run_id: UUID) -> List[WizardRunFileUpload]:
        """Get all file uploads for a run."""
        return db.query(WizardRunFileUpload)\
            .filter(WizardRunFileUpload.run_id == run_id)\
            .order_by(desc(WizardRunFileUpload.uploaded_at))\
            .all()

    def create(self, db: Session, obj_in: WizardRunFileUploadCreate) -> WizardRunFileUpload:
        """Create a new file upload record."""
        db_obj = WizardRunFileUpload(
            run_id=obj_in.run_id,
            option_set_response_id=obj_in.option_set_response_id,
            file_name=obj_in.file_name,
            file_path=obj_in.file_path,
            file_size=obj_in.file_size,
            file_type=obj_in.file_type,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, file_id: UUID) -> bool:
        """Delete a file upload record."""
        obj = db.query(WizardRunFileUpload).filter(WizardRunFileUpload.id == file_id).first()
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False


class WizardRunShareCRUD:
    """CRUD operations for WizardRunShare model."""

    def get(self, db: Session, share_id: UUID) -> Optional[WizardRunShare]:
        """Get a share by ID."""
        return db.query(WizardRunShare).filter(WizardRunShare.id == share_id).first()

    def get_by_token(self, db: Session, share_token: str) -> Optional[WizardRunShare]:
        """Get a share by token."""
        return db.query(WizardRunShare)\
            .filter(
                WizardRunShare.share_token == share_token,
                WizardRunShare.is_active == True
            )\
            .first()

    def get_multi_by_run(self, db: Session, run_id: UUID) -> List[WizardRunShare]:
        """Get all shares for a run."""
        return db.query(WizardRunShare)\
            .filter(WizardRunShare.run_id == run_id)\
            .order_by(desc(WizardRunShare.created_at))\
            .all()

    def get_multi_by_user(self, db: Session, user_id: UUID) -> List[WizardRunShare]:
        """Get all shares created by a user."""
        return db.query(WizardRunShare)\
            .filter(WizardRunShare.shared_by == user_id)\
            .order_by(desc(WizardRunShare.created_at))\
            .all()

    def create(self, db: Session, obj_in: WizardRunShareCreate, user_id: UUID) -> WizardRunShare:
        """Create a new share link."""
        # Generate unique share token
        share_token = secrets.token_urlsafe(32)

        db_obj = WizardRunShare(
            run_id=obj_in.run_id,
            share_token=share_token,
            shared_by=user_id,
            share_type=obj_in.share_type,
            expires_at=obj_in.expires_at,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def increment_access_count(self, db: Session, share_id: UUID) -> Optional[WizardRunShare]:
        """Increment access count for a share."""
        obj = db.query(WizardRunShare).filter(WizardRunShare.id == share_id).first()
        if obj:
            obj.access_count += 1
            obj.last_accessed_at = datetime.now(timezone.utc)
            db.add(obj)
            db.commit()
            db.refresh(obj)
        return obj

    def deactivate(self, db: Session, share_id: UUID) -> Optional[WizardRunShare]:
        """Deactivate a share link."""
        obj = db.query(WizardRunShare).filter(WizardRunShare.id == share_id).first()
        if obj:
            obj.is_active = False
            db.add(obj)
            db.commit()
            db.refresh(obj)
        return obj

    def delete(self, db: Session, *, share_id: UUID) -> bool:
        """Delete a share."""
        obj = db.query(WizardRunShare).filter(WizardRunShare.id == share_id).first()
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False


class WizardRunComparisonCRUD:
    """CRUD operations for WizardRunComparison model."""

    def get(self, db: Session, comparison_id: UUID) -> Optional[WizardRunComparison]:
        """Get a comparison by ID."""
        return db.query(WizardRunComparison).filter(WizardRunComparison.id == comparison_id).first()

    def get_multi_by_user(self, db: Session, user_id: UUID) -> List[WizardRunComparison]:
        """Get all comparisons created by a user."""
        return db.query(WizardRunComparison)\
            .filter(WizardRunComparison.created_by == user_id)\
            .order_by(desc(WizardRunComparison.created_at))\
            .all()

    def create(self, db: Session, obj_in: WizardRunComparisonCreate, user_id: UUID) -> WizardRunComparison:
        """Create a new comparison."""
        db_obj = WizardRunComparison(
            comparison_name=obj_in.comparison_name,
            run_ids=obj_in.run_ids,
            created_by=user_id,
            comparison_metadata=obj_in.metadata,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, comparison_id: UUID) -> bool:
        """Delete a comparison."""
        obj = db.query(WizardRunComparison).filter(WizardRunComparison.id == comparison_id).first()
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False


# Create singleton instances
wizard_run_crud = WizardRunCRUD()
wizard_run_step_response_crud = WizardRunStepResponseCRUD()
wizard_run_option_set_response_crud = WizardRunOptionSetResponseCRUD()
wizard_run_file_upload_crud = WizardRunFileUploadCRUD()
wizard_run_share_crud = WizardRunShareCRUD()
wizard_run_comparison_crud = WizardRunComparisonCRUD()
