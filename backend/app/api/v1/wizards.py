from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.api.deps import get_db, get_current_user, get_current_admin_user, get_optional_current_user
from app.crud.wizard import wizard_crud, category_crud, step_crud, flow_rule_crud, option_crud, option_dependency_crud
from app.schemas.wizard import (
    WizardCreate, WizardUpdate, WizardResponse, WizardListResponse,
    WizardCategoryCreate, WizardCategoryResponse,
    StepCreate, StepUpdate, StepResponse,
    FlowRuleCreate, FlowRuleUpdate, FlowRuleResponse,
    OptionDependencyCreate, OptionDependencyResponse
)
from app.models.user import User

router = APIRouter()


# Category endpoints
@router.get("/categories", response_model=List[WizardCategoryResponse])
def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all wizard categories."""
    return category_crud.get_multi(db, skip=skip, limit=limit)


@router.post("/categories", response_model=WizardCategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_in: WizardCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new wizard category (Admin only)."""
    return category_crud.create(db, obj_in=category_in)


# Wizard endpoints
@router.get("/", response_model=List[WizardListResponse])
def get_wizards(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[UUID] = None,
    published_only: bool = True,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Get list of wizards.
    By default returns only published wizards.
    Admins can see all wizards with published_only=False.
    """
    # Only admins can see unpublished wizards
    if not published_only:
        if not current_user or current_user.role.name not in ["admin", "super_admin"]:
            published_only = True

    wizards = wizard_crud.get_multi(
        db,
        skip=skip,
        limit=limit,
        published_only=published_only,
        category_id=category_id
    )
    return wizards


@router.post("/", response_model=WizardResponse, status_code=status.HTTP_201_CREATED)
def create_wizard(
    wizard_in: WizardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new wizard (Admin only)."""
    wizard = wizard_crud.create(db, obj_in=wizard_in, created_by=current_user.id)
    return wizard


# Wizard Protection & Lifecycle endpoints (MUST come before generic /{wizard_id} route)
@router.get("/{wizard_id}/protection-status")
def get_wizard_protection_status(
    wizard_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Changed from get_current_admin_user
):
    """
    Get protection status for a wizard.
    Returns lifecycle state, edit permissions, and available actions.
    """
    from app.services.wizard_protection import WizardProtectionService

    wizard = wizard_crud.get(db, wizard_id)
    if not wizard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wizard not found"
        )

    status_info = WizardProtectionService.get_wizard_state(db, wizard_id)
    return status_info


@router.get("/{wizard_id}", response_model=WizardResponse)
def get_wizard(
    wizard_id: UUID,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Get wizard by ID with all steps and options.
    """
    wizard = wizard_crud.get(db, wizard_id)
    if not wizard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wizard not found"
        )

    # Check if user can view unpublished wizard
    if not wizard.is_published:
        if not current_user or current_user.role.name not in ["admin", "super_admin"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wizard not found"
            )

    return wizard


@router.put("/{wizard_id}", response_model=WizardResponse)
def update_wizard(
    wizard_id: UUID,
    wizard_in: WizardUpdate,
    force: bool = Query(False, description="Force update even with active runs"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update wizard (Admin only) with protection checks."""
    from app.services.wizard_protection import WizardProtectionService

    wizard = wizard_crud.get(db, wizard_id)
    if not wizard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wizard not found"
        )

    # Check if modification is allowed
    can_modify, reason = WizardProtectionService.can_modify_wizard(db, wizard_id)
    if not can_modify:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=reason
        )

    # If there's a warning and user hasn't forced, return warning
    if reason and not force:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": reason,
                "requires_confirmation": True,
                "hint": "Add force=true to confirm and proceed"
            }
        )

    wizard = wizard_crud.update(db, wizard, wizard_in)
    return wizard


@router.put("/{wizard_id}/publish")
def publish_wizard(
    wizard_id: UUID,
    publish: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Publish or unpublish wizard (Admin only)."""
    wizard = wizard_crud.get(db, wizard_id)
    if not wizard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wizard not found"
        )

    wizard_crud.publish(db, wizard, publish)
    action = "published" if publish else "unpublished"
    return {"message": f"Wizard {action} successfully"}


@router.delete("/{wizard_id}")
def delete_wizard(
    wizard_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Soft delete wizard (Admin only) with protection checks."""
    from app.services.wizard_protection import WizardProtectionService

    wizard = wizard_crud.get(db, wizard_id)
    if not wizard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wizard not found"
        )

    # Check if deletion is allowed
    can_delete, reason = WizardProtectionService.can_delete_wizard(db, wizard_id)
    if not can_delete:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=reason
        )

    wizard_crud.soft_delete(db, wizard)
    return {"message": "Wizard deleted successfully", "warning": reason if reason else None}


@router.post("/{wizard_id}/clone", response_model=WizardResponse, status_code=status.HTTP_201_CREATED)
def clone_wizard(
    wizard_id: UUID,
    new_name: str = Query(..., description="Name for the cloned wizard"),
    new_description: Optional[str] = Query(None, description="Optional description for the clone"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Clone a wizard with all its steps, option sets, options, and dependencies.
    Useful for creating editable copies of published wizards.
    """
    wizard = wizard_crud.get(db, wizard_id)
    if not wizard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wizard not found"
        )

    cloned_wizard = wizard_crud.clone_wizard(
        db=db,
        wizard_id=wizard_id,
        new_name=new_name,
        created_by=current_user.id,
        new_description=new_description
    )

    if not cloned_wizard:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clone wizard"
        )

    return cloned_wizard


@router.post("/{wizard_id}/create-version", response_model=WizardResponse, status_code=status.HTTP_201_CREATED)
def create_wizard_version(
    wizard_id: UUID,
    new_name: Optional[str] = Query(None, description="Name for the new version (auto-generated if not provided)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create a new version of a wizard.
    Links to parent wizard and increments version number.
    """
    from app.services.wizard_protection import WizardProtectionService

    wizard = wizard_crud.get(db, wizard_id)
    if not wizard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wizard not found"
        )

    versioned_wizard = WizardProtectionService.create_wizard_version(
        db=db,
        wizard_id=wizard_id,
        new_name=new_name
    )

    if not versioned_wizard:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create wizard version"
        )

    return versioned_wizard


@router.post("/{wizard_id}/archive")
def archive_wizard(
    wizard_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Archive a wizard (soft delete for published wizards with stored runs).
    Archived wizards are hidden but data is preserved.
    """
    from app.services.wizard_protection import WizardProtectionService

    wizard = wizard_crud.get(db, wizard_id)
    if not wizard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wizard not found"
        )

    success = WizardProtectionService.archive_wizard(db, wizard_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to archive wizard"
        )

    return {"message": "Wizard archived successfully"}


@router.post("/{wizard_id}/unarchive")
def unarchive_wizard(
    wizard_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Unarchive a wizard, making it active again.
    """
    from app.services.wizard_protection import WizardProtectionService

    wizard = wizard_crud.get(db, wizard_id)
    if not wizard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wizard not found"
        )

    success = WizardProtectionService.unarchive_wizard(db, wizard_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unarchive wizard"
        )

    return {"message": "Wizard unarchived successfully"}


@router.post("/{wizard_id}/delete-all-runs")
def delete_all_wizard_runs(
    wizard_id: UUID,
    confirm: bool = Query(False, description="Must be true to confirm deletion"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Delete all runs for a wizard (use for in-use wizards before modification).
    Requires confirmation parameter.
    """
    from app.services.wizard_protection import WizardProtectionService

    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must set confirm=true to delete all runs"
        )

    wizard = wizard_crud.get(db, wizard_id)
    if not wizard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wizard not found"
        )

    # Check wizard state - should not delete runs from published wizards
    state_info = WizardProtectionService.get_wizard_state(db, wizard_id)
    if state_info["state"] == "published":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete runs from published wizard with stored data"
        )

    count = WizardProtectionService.delete_all_runs_for_wizard(db, wizard_id)
    return {"message": f"Deleted {count} run(s) successfully", "count": count}


# Step endpoints
@router.get("/{wizard_id}/steps", response_model=List[StepResponse])
def get_wizard_steps(
    wizard_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all steps for a wizard."""
    wizard = wizard_crud.get(db, wizard_id)
    if not wizard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wizard not found"
        )
    return wizard.steps


@router.post("/{wizard_id}/steps", response_model=StepResponse, status_code=status.HTTP_201_CREATED)
def create_step(
    wizard_id: UUID,
    step_in: StepCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new step for wizard (Admin only)."""
    wizard = wizard_crud.get(db, wizard_id)
    if not wizard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wizard not found"
        )

    step = step_crud.create(db, obj_in=step_in, wizard_id=wizard_id)
    return step


@router.get("/steps/{step_id}", response_model=StepResponse)
def get_step(
    step_id: UUID,
    db: Session = Depends(get_db)
):
    """Get step by ID with option sets."""
    step = step_crud.get(db, step_id)
    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Step not found"
        )
    return step


@router.put("/steps/{step_id}", response_model=StepResponse)
def update_step(
    step_id: UUID,
    step_in: StepUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update step (Admin only)."""
    step = step_crud.get(db, step_id)
    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Step not found"
        )

    step = step_crud.update(db, step, step_in)
    return step


@router.delete("/steps/{step_id}")
def delete_step(
    step_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete step (Admin only)."""
    step = step_crud.get(db, step_id)
    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Step not found"
        )

    step_crud.delete(db, step)
    return {"message": "Step deleted successfully"}


# Flow Rule endpoints
@router.get("/{wizard_id}/flow-rules", response_model=List[FlowRuleResponse])
def get_wizard_flow_rules(
    wizard_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get all flow rules for a wizard (Admin only)."""
    wizard = wizard_crud.get(db, wizard_id)
    if not wizard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wizard not found"
        )
    return flow_rule_crud.get_by_wizard(db, wizard_id)


@router.post("/{wizard_id}/flow-rules", response_model=FlowRuleResponse, status_code=status.HTTP_201_CREATED)
def create_flow_rule(
    wizard_id: UUID,
    rule_in: FlowRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new flow rule for wizard (Admin only)."""
    wizard = wizard_crud.get(db, wizard_id)
    if not wizard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wizard not found"
        )

    # Ensure wizard_id matches
    if rule_in.wizard_id != wizard_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wizard ID mismatch"
        )

    rule = flow_rule_crud.create(db, obj_in=rule_in)
    return rule


@router.get("/flow-rules/{rule_id}", response_model=FlowRuleResponse)
def get_flow_rule(
    rule_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get flow rule by ID (Admin only)."""
    rule = flow_rule_crud.get(db, rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flow rule not found"
        )
    return rule


@router.put("/flow-rules/{rule_id}", response_model=FlowRuleResponse)
def update_flow_rule(
    rule_id: UUID,
    rule_in: FlowRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update flow rule (Admin only)."""
    rule = flow_rule_crud.get(db, rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flow rule not found"
        )

    rule = flow_rule_crud.update(db, rule, rule_in)
    return rule


@router.delete("/flow-rules/{rule_id}")
def delete_flow_rule(
    rule_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete flow rule (Admin only)."""
    rule = flow_rule_crud.get(db, rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flow rule not found"
        )

    flow_rule_crud.delete(db, rule)
    return {"message": "Flow rule deleted successfully"}


# Option Dependency endpoints
@router.get("/options/{option_id}/dependencies", response_model=List[OptionDependencyResponse])
def get_option_dependencies(
    option_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get all dependencies for an option (Admin only)."""
    option = option_crud.get(db, option_id)
    if not option:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Option not found"
        )
    return option_dependency_crud.get_by_option(db, option_id)


@router.post("/options/{option_id}/dependencies", response_model=OptionDependencyResponse, status_code=status.HTTP_201_CREATED)
def create_option_dependency(
    option_id: UUID,
    dependency_in: OptionDependencyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new option dependency (Admin only)."""
    option = option_crud.get(db, option_id)
    if not option:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Option not found"
        )

    # Verify that the depends_on_option exists
    depends_on_option = option_crud.get(db, dependency_in.depends_on_option_id)
    if not depends_on_option:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Depends on option not found"
        )

    # Create the dependency
    dependency = option_dependency_crud.create(db, obj_in=dependency_in, option_id=option_id)
    return dependency


@router.delete("/dependencies/{dependency_id}")
def delete_option_dependency(
    dependency_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete an option dependency (Admin only)."""
    dependency = option_dependency_crud.get(db, dependency_id)
    if not dependency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dependency not found"
        )

    option_dependency_crud.delete(db, dependency)
    return {"message": "Dependency deleted successfully"}
