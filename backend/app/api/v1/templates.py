from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.crud.template import template_crud
from app.crud.session import session_crud
from app.schemas.template import TemplateCreate, TemplateUpdate, TemplateResponse, TemplateListResponse
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template(
    template_in: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new template.
    """
    template = template_crud.create(db, obj_in=template_in, user_id=current_user.id)
    return template


@router.post("/from-session/{session_id}", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template_from_session(
    session_id: UUID,
    name: str,
    description: Optional[str] = None,
    is_public: bool = False,
    tags: List[str] = [],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a template from a completed session.
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
            detail="Not authorized to create template from this session"
        )

    if session.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only create template from completed session"
        )

    template = template_crud.create_from_session(
        db,
        name=name,
        description=description,
        session=session,
        user_id=current_user.id,
        is_public=is_public,
        tags=tags
    )
    return template


@router.get("/", response_model=List[TemplateListResponse])
def get_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    wizard_id: Optional[UUID] = None,
    mine_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get templates accessible to user (own + public).
    """
    if mine_only:
        templates = template_crud.get_by_user(
            db,
            user_id=current_user.id,
            skip=skip,
            limit=limit
        )
    else:
        templates = template_crud.get_accessible(
            db,
            user_id=current_user.id,
            wizard_id=wizard_id,
            skip=skip,
            limit=limit
        )
    return templates


@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(
    template_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get template by ID.
    """
    template = template_crud.get(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    # Check access
    if not template.is_public and template.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this template"
        )

    return template


@router.put("/{template_id}", response_model=TemplateResponse)
def update_template(
    template_id: UUID,
    template_in: TemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update template metadata.
    """
    template = template_crud.get(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    # Check ownership
    if template.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this template"
        )

    template = template_crud.update(db, template, template_in)
    return template


@router.post("/{template_id}/replay")
def replay_template(
    template_id: UUID,
    session_name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new session pre-filled with template responses.
    Returns the session ID to start the wizard player.
    """
    template = template_crud.get(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    # Check access
    if not template.is_public and template.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to use this template"
        )

    # Create session from template
    from app.schemas.session import SessionCreate, SessionResponseCreate

    session_in = SessionCreate(
        wizard_id=template.wizard_id,
        session_name=session_name or f"From template: {template.name}",
        metadata={"from_template": str(template.id)}
    )

    session = session_crud.create(db, obj_in=session_in, user_id=current_user.id)

    # Pre-fill responses from template
    for template_response in template.responses:
        response_in = SessionResponseCreate(
            step_id=template_response.step_id,
            option_set_id=template_response.option_set_id,
            response_data=template_response.response_data
        )
        session_crud.add_response(db, session, response_in)

    # Increment template usage
    template_crud.increment_usage(db, template)

    return {
        "session_id": str(session.id),
        "message": f"Session created from template '{template.name}'"
    }


@router.delete("/{template_id}")
def delete_template(
    template_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete template (soft delete).
    """
    template = template_crud.get(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    # Check ownership
    if template.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this template"
        )

    template_crud.soft_delete(db, template)
    return {"message": "Template deleted successfully"}
