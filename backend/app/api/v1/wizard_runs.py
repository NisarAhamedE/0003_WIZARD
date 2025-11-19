"""
Wizard Run API Endpoints

REST API for wizard run execution, progress tracking, and storage.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import math
import os
import shutil

from app.api.deps import get_db, get_current_user, get_optional_current_user
from app.models.user import User
from app.crud.wizard_run import (
    wizard_run_crud,
    wizard_run_step_response_crud,
    wizard_run_option_set_response_crud,
    wizard_run_file_upload_crud,
    wizard_run_share_crud,
    wizard_run_comparison_crud,
)
from app.schemas.wizard_run import (
    WizardRunCreate,
    WizardRunUpdate,
    WizardRunResponse,
    WizardRunListResponse,
    WizardRunDetailResponse,
    WizardRunCompleteRequest,
    WizardRunStepResponseCreate,
    WizardRunStepResponseUpdate,
    WizardRunStepResponseDetail,
    WizardRunOptionSetResponseCreate,
    WizardRunOptionSetResponseUpdate,
    WizardRunOptionSetResponseDetail,
    WizardRunFileUploadResponse,
    WizardRunShareCreate,
    WizardRunShareResponse,
    WizardRunComparisonCreate,
    WizardRunComparisonResponse,
    WizardRunProgressUpdate,
    WizardRunStats,
)

router = APIRouter()

# File upload directory
UPLOAD_DIR = "uploads/wizard_runs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============================================================================
# Wizard Run CRUD Endpoints
# ============================================================================

@router.get("/", response_model=WizardRunListResponse)
def list_wizard_runs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    wizard_id: Optional[UUID] = None,
    status: Optional[str] = None,
    is_stored: Optional[bool] = None,
    is_favorite: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get list of wizard runs for the current user."""
    runs, total = wizard_run_crud.get_multi(
        db,
        skip=skip,
        limit=limit,
        user_id=current_user.id,
        wizard_id=wizard_id,
        status=status,
        is_stored=is_stored,
        is_favorite=is_favorite,
    )

    total_pages = math.ceil(total / limit) if limit > 0 else 0
    current_page = (skip // limit) + 1 if limit > 0 else 1

    return WizardRunListResponse(
        runs=runs,
        total=total,
        page=current_page,
        page_size=limit,
        total_pages=total_pages,
    )


@router.get("/in-progress", response_model=List[WizardRunResponse])
def get_in_progress_runs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all in-progress wizard runs for the current user."""
    return wizard_run_crud.get_in_progress(db, user_id=current_user.id)


@router.get("/completed", response_model=List[WizardRunResponse])
def get_completed_runs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get completed wizard runs for the current user."""
    return wizard_run_crud.get_completed(db, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/stored", response_model=List[WizardRunResponse])
def get_stored_runs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get stored wizard runs (Store Wizard repository)."""
    return wizard_run_crud.get_stored(db, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/favorites", response_model=List[WizardRunResponse])
def get_favorite_runs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get favorite wizard runs."""
    return wizard_run_crud.get_favorites(db, user_id=current_user.id)


@router.get("/stats", response_model=WizardRunStats)
def get_wizard_run_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get statistics about user's wizard runs."""
    stats = wizard_run_crud.get_statistics(db, user_id=current_user.id)
    return WizardRunStats(**stats)


@router.get("/{run_id}", response_model=WizardRunDetailResponse)
def get_wizard_run(
    run_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user),
):
    """
    Get a specific wizard run with all details.
    Supports anonymous access via share links (handled by get_optional_current_user).
    """
    run = wizard_run_crud.get(db, run_id=run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wizard run not found"
        )

    # Check authorization if user is authenticated
    if current_user and run.user_id and run.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this wizard run"
        )

    # Get all related responses
    step_responses = wizard_run_step_response_crud.get_multi_by_run(db, run_id=run_id)
    option_set_responses = wizard_run_option_set_response_crud.get_multi_by_run(db, run_id=run_id)
    file_uploads = wizard_run_file_upload_crud.get_multi_by_run(db, run_id=run_id)

    return WizardRunDetailResponse(
        **run.__dict__,
        step_responses=step_responses,
        option_set_responses=option_set_responses,
        file_uploads=file_uploads,
    )


@router.post("/", response_model=WizardRunResponse, status_code=status.HTTP_201_CREATED)
def create_wizard_run(
    run_in: WizardRunCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user),
):
    """
    Start a new wizard run.
    Can be authenticated or anonymous.
    """
    user_id = current_user.id if current_user else None
    return wizard_run_crud.create(db, obj_in=run_in, user_id=user_id)


@router.put("/{run_id}", response_model=WizardRunResponse)
def update_wizard_run(
    run_id: UUID,
    run_in: WizardRunUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a wizard run."""
    run = wizard_run_crud.get(db, run_id=run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wizard run not found"
        )

    if run.user_id and run.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this wizard run"
        )

    return wizard_run_crud.update(db, db_obj=run, obj_in=run_in)


@router.post("/{run_id}/progress", response_model=WizardRunResponse)
def update_run_progress(
    run_id: UUID,
    progress: WizardRunProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user),
):
    """Update wizard run progress (auto-save during execution)."""
    run = wizard_run_crud.get(db, run_id=run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wizard run not found"
        )

    if current_user and run.user_id and run.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this wizard run"
        )

    return wizard_run_crud.update_progress(db, run_id=run_id, current_step_index=progress.current_step_index)


@router.post("/{run_id}/complete", response_model=WizardRunResponse)
def complete_wizard_run(
    run_id: UUID,
    complete_request: WizardRunCompleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user),
):
    """Complete a wizard run."""
    run = wizard_run_crud.get(db, run_id=run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wizard run not found"
        )

    if current_user and run.user_id and run.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to complete this wizard run"
        )

    return wizard_run_crud.complete(
        db,
        run_id=run_id,
        run_name=complete_request.run_name,
        run_description=complete_request.run_description,
        save_to_store=complete_request.save_to_store,
        tags=complete_request.tags,
    )


@router.post("/{run_id}/abandon", response_model=WizardRunResponse)
def abandon_wizard_run(
    run_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a wizard run as abandoned."""
    run = wizard_run_crud.get(db, run_id=run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wizard run not found"
        )

    if run.user_id and run.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to abandon this wizard run"
        )

    return wizard_run_crud.abandon(db, run_id=run_id)


@router.delete("/{run_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_wizard_run(
    run_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a wizard run."""
    run = wizard_run_crud.get(db, run_id=run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wizard run not found"
        )

    if run.user_id and run.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this wizard run"
        )

    wizard_run_crud.delete(db, run_id=run_id)
    return None


# ============================================================================
# Step Response Endpoints
# ============================================================================

@router.post("/{run_id}/steps", response_model=WizardRunStepResponseDetail, status_code=status.HTTP_201_CREATED)
def create_step_response(
    run_id: UUID,
    step_response_in: WizardRunStepResponseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user),
):
    """Create a step response for a wizard run."""
    if step_response_in.run_id != run_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Run ID in body must match run ID in URL"
        )

    return wizard_run_step_response_crud.create(db, obj_in=step_response_in)


@router.put("/steps/{step_response_id}", response_model=WizardRunStepResponseDetail)
def update_step_response(
    step_response_id: UUID,
    step_response_in: WizardRunStepResponseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user),
):
    """Update a step response."""
    step_response = wizard_run_step_response_crud.get(db, response_id=step_response_id)
    if not step_response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Step response not found"
        )

    return wizard_run_step_response_crud.update(db, db_obj=step_response, obj_in=step_response_in)


# ============================================================================
# Option Set Response Endpoints
# ============================================================================

@router.post("/{run_id}/option-sets", response_model=WizardRunOptionSetResponseDetail, status_code=status.HTTP_201_CREATED)
def create_option_set_response(
    run_id: UUID,
    option_set_response_in: WizardRunOptionSetResponseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user),
):
    """Create an option set response for a wizard run."""
    if option_set_response_in.run_id != run_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Run ID in body must match run ID in URL"
        )

    return wizard_run_option_set_response_crud.create(db, obj_in=option_set_response_in)


@router.put("/option-sets/{response_id}", response_model=WizardRunOptionSetResponseDetail)
def update_option_set_response(
    response_id: UUID,
    response_in: WizardRunOptionSetResponseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user),
):
    """Update an option set response."""
    response = wizard_run_option_set_response_crud.get(db, response_id=response_id)
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Option set response not found"
        )

    return wizard_run_option_set_response_crud.update(db, db_obj=response, obj_in=response_in)


# ============================================================================
# File Upload Endpoints
# ============================================================================

@router.post("/{run_id}/upload", response_model=WizardRunFileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file_to_run(
    run_id: UUID,
    option_set_response_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user),
):
    """Upload a file for a wizard run option set response."""
    # Verify run exists
    run = wizard_run_crud.get(db, run_id=run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wizard run not found"
        )

    # Create run-specific directory
    run_upload_dir = os.path.join(UPLOAD_DIR, str(run_id))
    os.makedirs(run_upload_dir, exist_ok=True)

    # Save file
    file_path = os.path.join(run_upload_dir, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {str(e)}"
        )
    finally:
        file.file.close()

    # Create file upload record
    from app.schemas.wizard_run import WizardRunFileUploadCreate
    file_upload_in = WizardRunFileUploadCreate(
        run_id=run_id,
        option_set_response_id=option_set_response_id,
        file_name=file.filename,
        file_path=file_path,
        file_size=os.path.getsize(file_path) if os.path.exists(file_path) else None,
        file_type=file.content_type,
    )

    return wizard_run_file_upload_crud.create(db, obj_in=file_upload_in)


# ============================================================================
# Share Endpoints
# ============================================================================

@router.post("/{run_id}/share", response_model=WizardRunShareResponse, status_code=status.HTTP_201_CREATED)
def create_run_share(
    run_id: UUID,
    share_in: WizardRunShareCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a share link for a wizard run."""
    if share_in.run_id != run_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Run ID in body must match run ID in URL"
        )

    run = wizard_run_crud.get(db, run_id=run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wizard run not found"
        )

    if run.user_id and run.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to share this wizard run"
        )

    return wizard_run_share_crud.create(db, obj_in=share_in, user_id=current_user.id)


@router.get("/share/{share_token}", response_model=WizardRunDetailResponse)
def get_run_by_share_token(
    share_token: str,
    db: Session = Depends(get_db),
):
    """Access a wizard run via share token (public endpoint)."""
    share = wizard_run_share_crud.get_by_token(db, share_token=share_token)
    if not share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired share link"
        )

    # Increment access count
    wizard_run_share_crud.increment_access_count(db, share_id=share.id)

    # Get the run
    run = wizard_run_crud.get(db, run_id=share.run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wizard run not found"
        )

    # Get all related responses
    step_responses = wizard_run_step_response_crud.get_multi_by_run(db, run_id=run.id)
    option_set_responses = wizard_run_option_set_response_crud.get_multi_by_run(db, run_id=run.id)
    file_uploads = wizard_run_file_upload_crud.get_multi_by_run(db, run_id=run.id)

    return WizardRunDetailResponse(
        **run.__dict__,
        step_responses=step_responses,
        option_set_responses=option_set_responses,
        file_uploads=file_uploads,
    )


# ============================================================================
# Comparison Endpoints
# ============================================================================

@router.post("/comparisons", response_model=WizardRunComparisonResponse, status_code=status.HTTP_201_CREATED)
def create_run_comparison(
    comparison_in: WizardRunComparisonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a comparison of multiple wizard runs."""
    # Verify all runs exist and belong to user
    for run_id in comparison_in.run_ids:
        run = wizard_run_crud.get(db, run_id=run_id)
        if not run:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wizard run {run_id} not found"
            )
        if run.user_id and run.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not authorized to access wizard run {run_id}"
            )

    return wizard_run_comparison_crud.create(db, obj_in=comparison_in, user_id=current_user.id)


@router.get("/comparisons", response_model=List[WizardRunComparisonResponse])
def get_my_comparisons(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all comparisons created by the current user."""
    return wizard_run_comparison_crud.get_multi_by_user(db, user_id=current_user.id)


@router.get("/comparisons/{comparison_id}", response_model=WizardRunComparisonResponse)
def get_comparison(
    comparison_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific comparison."""
    comparison = wizard_run_comparison_crud.get(db, comparison_id=comparison_id)
    if not comparison:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comparison not found"
        )

    if comparison.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this comparison"
        )

    return comparison


@router.delete("/comparisons/{comparison_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comparison(
    comparison_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a comparison."""
    comparison = wizard_run_comparison_crud.get(db, comparison_id=comparison_id)
    if not comparison:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comparison not found"
        )

    if comparison.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comparison"
        )

    wizard_run_comparison_crud.delete(db, comparison_id=comparison_id)
    return None
