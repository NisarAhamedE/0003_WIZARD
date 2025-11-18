from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from decimal import Decimal

from app.api.deps import get_db, get_current_user, get_optional_current_user
from app.crud.session import session_crud
from app.crud.wizard import wizard_crud
from app.schemas.session import (
    SessionCreate, SessionUpdate, SessionResponse,
    SessionResponseCreate, SessionListResponse
)
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def start_session(
    session_in: SessionCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Start a new wizard session.
    """
    # Verify wizard exists and is published
    wizard = wizard_crud.get(db, session_in.wizard_id)
    if not wizard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wizard not found"
        )

    if not wizard.is_published:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wizard is not published"
        )

    # Check if login is required
    if wizard.require_login and not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login required for this wizard"
        )

    user_id = current_user.id if current_user else None
    session = session_crud.create(db, obj_in=session_in, user_id=user_id)

    # Increment wizard session count
    wizard_crud.increment_session_count(db, wizard)

    return session


@router.get("/", response_model=List[SessionListResponse])
def get_my_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's sessions with wizard names.
    """
    sessions = session_crud.get_by_user(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status
    )

    # Add wizard_name to each session
    result = []
    for session in sessions:
        wizard = wizard_crud.get(db, session.wizard_id)
        session_data = SessionListResponse(
            id=session.id,
            wizard_id=session.wizard_id,
            wizard_name=wizard.name if wizard else None,
            session_name=session.session_name,
            status=session.status,
            progress_percentage=session.progress_percentage,
            started_at=session.started_at,
            last_activity_at=session.last_activity_at,
            completed_at=session.completed_at
        )
        result.append(session_data)

    return result


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get session by ID.
    """
    session = session_crud.get(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Check ownership
    if session.user_id != current_user.id:
        if current_user.role.name not in ["admin", "super_admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this session"
            )

    return session


@router.put("/{session_id}", response_model=SessionResponse)
def update_session(
    session_id: UUID,
    session_in: SessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update session (save progress).
    """
    session = session_crud.get(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Check ownership
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this session"
        )

    # Prevent updating completed/abandoned sessions
    if session.status in ["completed", "abandoned"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update {session.status} session"
        )

    session = session_crud.update(db, session, session_in)
    return session


@router.post("/{session_id}/responses", response_model=SessionResponse)
def save_response(
    session_id: UUID,
    response_in: SessionResponseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Save response for an option set in the session.
    """
    session = session_crud.get(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Check ownership
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this session"
        )

    # Prevent updating completed sessions
    if session.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only add responses to in-progress sessions"
        )

    session_crud.add_response(db, session, response_in)

    # Calculate progress based on responses
    wizard = wizard_crud.get(db, session.wizard_id)
    total_option_sets = sum(len(step.option_sets) for step in wizard.steps)
    if total_option_sets > 0:
        progress = (len(session.responses) / total_option_sets) * 100
        session_crud.update_progress(db, session, Decimal(str(min(progress, 99))))

    # Refresh session with new response
    return session_crud.get(db, session_id)


@router.put("/{session_id}/complete", response_model=SessionResponse)
def complete_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark session as completed.
    """
    session = session_crud.get(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Check ownership
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to complete this session"
        )

    if session.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is not in progress"
        )

    session = session_crud.complete_session(db, session)

    # Increment wizard completed count
    wizard = wizard_crud.get(db, session.wizard_id)
    wizard_crud.increment_completed_count(db, wizard)

    return session


@router.delete("/{session_id}")
def delete_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Physically delete session and all associated responses.
    """
    session = session_crud.get(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Check ownership
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this session"
        )

    if session.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete completed session"
        )

    # Physically delete the session
    session_crud.delete(db, session)
    return {"message": "Session deleted successfully"}
