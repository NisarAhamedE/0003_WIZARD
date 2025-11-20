"""
Wizard Template API Endpoints

REST API for wizard template management, ratings, and cloning.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import math

from app.api.deps import get_db, get_current_user, get_current_admin_user
from app.models.user import User
from app.crud.wizard_template import wizard_template_crud, wizard_template_rating_crud
from app.crud.wizard import wizard_crud
from app.schemas.wizard_template import (
    WizardTemplateCreate,
    WizardTemplateUpdate,
    WizardTemplateResponse,
    WizardTemplateListResponse,
    WizardTemplateRatingCreate,
    WizardTemplateRatingUpdate,
    WizardTemplateRatingResponse,
    WizardTemplateStats,
    WizardTemplateCloneRequest,
    WizardTemplateCloneResponse,
)
from app.schemas.wizard import WizardCreate

router = APIRouter()


# ============================================================================
# Template CRUD Endpoints
# ============================================================================

@router.get("/", response_model=WizardTemplateListResponse)
def list_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    difficulty_level: Optional[str] = None,
    is_system_template: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Get list of wizard templates with filtering and pagination.
    Public endpoint - no authentication required.
    """
    templates, total = wizard_template_crud.get_multi(
        db,
        skip=skip,
        limit=limit,
        category=category,
        difficulty_level=difficulty_level,
        is_system_template=is_system_template,
        is_active=True,
        search=search,
    )

    total_pages = math.ceil(total / limit) if limit > 0 else 0
    current_page = (skip // limit) + 1 if limit > 0 else 1

    return WizardTemplateListResponse(
        templates=templates,
        total=total,
        page=current_page,
        page_size=limit,
        total_pages=total_pages,
    )


@router.get("/popular", response_model=List[WizardTemplateResponse])
def get_popular_templates(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Get most popular templates by usage count."""
    return wizard_template_crud.get_popular(db, limit=limit)


@router.get("/top-rated", response_model=List[WizardTemplateResponse])
def get_top_rated_templates(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Get top rated templates."""
    return wizard_template_crud.get_top_rated(db, limit=limit)


@router.get("/categories/{category}", response_model=List[WizardTemplateResponse])
def get_templates_by_category(
    category: str,
    db: Session = Depends(get_db),
):
    """Get all templates in a specific category."""
    return wizard_template_crud.get_by_category(db, category=category)


@router.get("/{template_id}", response_model=WizardTemplateResponse)
def get_template(
    template_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a specific wizard template by ID."""
    template = wizard_template_crud.get(db, template_id=template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    return template


@router.post("/", response_model=WizardTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template(
    template_in: WizardTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Create a new wizard template.
    Requires admin privileges.
    """
    return wizard_template_crud.create(db, obj_in=template_in)


@router.put("/{template_id}", response_model=WizardTemplateResponse)
def update_template(
    template_id: UUID,
    template_in: WizardTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Update a wizard template.
    Requires admin privileges.
    """
    template = wizard_template_crud.get(db, template_id=template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    return wizard_template_crud.update(db, db_obj=template, obj_in=template_in)


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(
    template_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Soft delete a wizard template (set is_active to False).
    Requires admin privileges.
    """
    template = wizard_template_crud.delete(db, template_id=template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    return None


# ============================================================================
# Template Cloning Endpoints
# ============================================================================

@router.post("/clone", response_model=WizardTemplateCloneResponse)
def clone_template_to_wizard(
    clone_request: WizardTemplateCloneRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Clone a template to create a new wizard in the Wizard Builder.
    The wizard_structure from the template is used to create a full wizard.
    """
    # Get the template
    template = wizard_template_crud.get(db, template_id=clone_request.template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    if not template.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template is not active"
        )

    # Extract wizard structure
    wizard_structure = template.wizard_structure.copy()

    # Apply any customizations
    if clone_request.customizations:
        wizard_structure.update(clone_request.customizations)

    # Create wizard from template
    wizard_data = WizardCreate(
        name=clone_request.wizard_name,
        description=clone_request.wizard_description or template.template_description,
        category_id=wizard_structure.get('category_id'),
        icon=template.icon,
        difficulty_level=template.difficulty_level,
        estimated_time=template.estimated_time,
        is_published=False,  # Start as unpublished
        **wizard_structure
    )

    # Create the wizard
    from app.crud.wizard import wizard_crud
    wizard = wizard_crud.create(db, obj_in=wizard_data, creator_id=current_user.id)

    # Increment template usage count
    wizard_template_crud.increment_usage_count(db, template_id=clone_request.template_id)

    return WizardTemplateCloneResponse(
        wizard_id=wizard.id,
        message=f"Template '{template.template_name}' successfully cloned to wizard '{wizard.name}'"
    )


# ============================================================================
# Template Rating Endpoints
# ============================================================================

@router.get("/{template_id}/ratings", response_model=List[WizardTemplateRatingResponse])
def get_template_ratings(
    template_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get all ratings for a template."""
    template = wizard_template_crud.get(db, template_id=template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    return wizard_template_rating_crud.get_multi_by_template(
        db, template_id=template_id, skip=skip, limit=limit
    )


@router.get("/{template_id}/stats", response_model=WizardTemplateStats)
def get_template_stats(
    template_id: UUID,
    db: Session = Depends(get_db),
):
    """Get statistics for a template including rating distribution."""
    template = wizard_template_crud.get(db, template_id=template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    rating_distribution = wizard_template_rating_crud.get_rating_distribution(db, template_id=template_id)
    total_ratings = sum(rating_distribution.values())

    return WizardTemplateStats(
        template_id=template_id,
        usage_count=template.usage_count,
        average_rating=template.average_rating,
        total_ratings=total_ratings,
        rating_distribution=rating_distribution,
    )


@router.post("/{template_id}/ratings", response_model=WizardTemplateRatingResponse, status_code=status.HTTP_201_CREATED)
def create_template_rating(
    template_id: UUID,
    rating_in: WizardTemplateRatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create or update a rating for a template.
    Users can only have one rating per template.
    """
    # Verify template exists
    template = wizard_template_crud.get(db, template_id=template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    # Check if rating_in.template_id matches template_id
    if rating_in.template_id != template_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template ID in body must match template ID in URL"
        )

    # Check if user already rated this template
    existing_rating = wizard_template_rating_crud.get_by_user_and_template(
        db, user_id=current_user.id, template_id=template_id
    )

    if existing_rating:
        # Update existing rating
        rating_update = WizardTemplateRatingUpdate(
            rating=rating_in.rating,
            review_text=rating_in.review_text
        )
        return wizard_template_rating_crud.update(
            db, db_obj=existing_rating, obj_in=rating_update
        )
    else:
        # Create new rating
        return wizard_template_rating_crud.create(
            db, obj_in=rating_in, user_id=current_user.id
        )


@router.delete("/{template_id}/ratings", status_code=status.HTTP_204_NO_CONTENT)
def delete_template_rating(
    template_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete user's rating for a template."""
    rating = wizard_template_rating_crud.get_by_user_and_template(
        db, user_id=current_user.id, template_id=template_id
    )

    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )

    wizard_template_rating_crud.delete(db, rating_id=rating.id)
    return None


# ============================================================================
# User's Template Ratings
# ============================================================================

@router.get("/users/me/ratings", response_model=List[WizardTemplateRatingResponse])
def get_my_template_ratings(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all ratings created by the current user."""
    return wizard_template_rating_crud.get_multi_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
