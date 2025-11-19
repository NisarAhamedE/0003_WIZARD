"""
Wizard Template CRUD Operations

Database operations for wizard templates and ratings.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.models.wizard_template import WizardTemplate, WizardTemplateRating
from app.schemas.wizard_template import (
    WizardTemplateCreate,
    WizardTemplateUpdate,
    WizardTemplateRatingCreate,
    WizardTemplateRatingUpdate,
)


class WizardTemplateCRUD:
    """CRUD operations for WizardTemplate model."""

    def get(self, db: Session, template_id: UUID) -> Optional[WizardTemplate]:
        """Get a template by ID."""
        return db.query(WizardTemplate).filter(WizardTemplate.id == template_id).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        difficulty_level: Optional[str] = None,
        is_system_template: Optional[bool] = None,
        is_active: bool = True,
        search: Optional[str] = None,
    ) -> tuple[List[WizardTemplate], int]:
        """
        Get multiple templates with filtering and pagination.
        Returns tuple of (templates, total_count).
        """
        query = db.query(WizardTemplate)

        # Apply filters
        if is_active is not None:
            query = query.filter(WizardTemplate.is_active == is_active)
        if category:
            query = query.filter(WizardTemplate.category == category)
        if difficulty_level:
            query = query.filter(WizardTemplate.difficulty_level == difficulty_level)
        if is_system_template is not None:
            query = query.filter(WizardTemplate.is_system_template == is_system_template)
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (WizardTemplate.template_name.ilike(search_pattern)) |
                (WizardTemplate.template_description.ilike(search_pattern))
            )

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        templates = query.order_by(desc(WizardTemplate.average_rating), desc(WizardTemplate.usage_count))\
            .offset(skip)\
            .limit(limit)\
            .all()

        return templates, total

    def get_popular(self, db: Session, limit: int = 10) -> List[WizardTemplate]:
        """Get most popular templates by usage count."""
        return db.query(WizardTemplate)\
            .filter(WizardTemplate.is_active == True)\
            .order_by(desc(WizardTemplate.usage_count))\
            .limit(limit)\
            .all()

    def get_top_rated(self, db: Session, limit: int = 10) -> List[WizardTemplate]:
        """Get top rated templates."""
        return db.query(WizardTemplate)\
            .filter(WizardTemplate.is_active == True)\
            .order_by(desc(WizardTemplate.average_rating))\
            .limit(limit)\
            .all()

    def get_by_category(self, db: Session, category: str) -> List[WizardTemplate]:
        """Get all templates in a specific category."""
        return db.query(WizardTemplate)\
            .filter(WizardTemplate.category == category, WizardTemplate.is_active == True)\
            .order_by(desc(WizardTemplate.average_rating))\
            .all()

    def create(self, db: Session, obj_in: WizardTemplateCreate) -> WizardTemplate:
        """Create a new wizard template."""
        # Calculate step_count and option_set_count from wizard_structure
        wizard_structure = obj_in.wizard_structure
        step_count = len(wizard_structure.get('steps', []))
        option_set_count = sum(
            len(step.get('option_sets', []))
            for step in wizard_structure.get('steps', [])
        )

        db_obj = WizardTemplate(
            template_name=obj_in.template_name,
            template_description=obj_in.template_description,
            category=obj_in.category,
            icon=obj_in.icon,
            difficulty_level=obj_in.difficulty_level,
            estimated_time=obj_in.estimated_time,
            tags=obj_in.tags,
            preview_image=obj_in.preview_image,
            step_count=step_count,
            option_set_count=option_set_count,
            is_system_template=obj_in.is_system_template,
            created_by=obj_in.created_by,
            wizard_structure=wizard_structure,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: WizardTemplate, obj_in: WizardTemplateUpdate
    ) -> WizardTemplate:
        """Update a wizard template."""
        update_data = obj_in.model_dump(exclude_unset=True)

        # Recalculate counts if wizard_structure is updated
        if 'wizard_structure' in update_data:
            wizard_structure = update_data['wizard_structure']
            update_data['step_count'] = len(wizard_structure.get('steps', []))
            update_data['option_set_count'] = sum(
                len(step.get('option_sets', []))
                for step in wizard_structure.get('steps', [])
            )

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, template_id: UUID) -> Optional[WizardTemplate]:
        """Soft delete a wizard template (set is_active to False)."""
        obj = db.query(WizardTemplate).filter(WizardTemplate.id == template_id).first()
        if obj:
            obj.is_active = False
            db.add(obj)
            db.commit()
            db.refresh(obj)
        return obj

    def hard_delete(self, db: Session, *, template_id: UUID) -> bool:
        """Permanently delete a wizard template."""
        obj = db.query(WizardTemplate).filter(WizardTemplate.id == template_id).first()
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False

    def increment_usage_count(self, db: Session, template_id: UUID) -> Optional[WizardTemplate]:
        """Increment usage count when template is cloned."""
        obj = db.query(WizardTemplate).filter(WizardTemplate.id == template_id).first()
        if obj:
            obj.usage_count += 1
            db.add(obj)
            db.commit()
            db.refresh(obj)
        return obj

    def update_average_rating(self, db: Session, template_id: UUID) -> Optional[WizardTemplate]:
        """Recalculate and update average rating from all ratings."""
        avg_rating = db.query(func.avg(WizardTemplateRating.rating))\
            .filter(WizardTemplateRating.template_id == template_id)\
            .scalar()

        obj = db.query(WizardTemplate).filter(WizardTemplate.id == template_id).first()
        if obj:
            obj.average_rating = round(float(avg_rating or 0), 2)
            db.add(obj)
            db.commit()
            db.refresh(obj)
        return obj


class WizardTemplateRatingCRUD:
    """CRUD operations for WizardTemplateRating model."""

    def get(self, db: Session, rating_id: UUID) -> Optional[WizardTemplateRating]:
        """Get a rating by ID."""
        return db.query(WizardTemplateRating).filter(WizardTemplateRating.id == rating_id).first()

    def get_by_user_and_template(
        self, db: Session, user_id: UUID, template_id: UUID
    ) -> Optional[WizardTemplateRating]:
        """Get a user's rating for a specific template."""
        return db.query(WizardTemplateRating)\
            .filter(
                WizardTemplateRating.user_id == user_id,
                WizardTemplateRating.template_id == template_id
            )\
            .first()

    def get_multi_by_template(
        self, db: Session, template_id: UUID, skip: int = 0, limit: int = 20
    ) -> List[WizardTemplateRating]:
        """Get all ratings for a template."""
        return db.query(WizardTemplateRating)\
            .filter(WizardTemplateRating.template_id == template_id)\
            .order_by(desc(WizardTemplateRating.created_at))\
            .offset(skip)\
            .limit(limit)\
            .all()

    def get_multi_by_user(
        self, db: Session, user_id: UUID, skip: int = 0, limit: int = 20
    ) -> List[WizardTemplateRating]:
        """Get all ratings by a user."""
        return db.query(WizardTemplateRating)\
            .filter(WizardTemplateRating.user_id == user_id)\
            .order_by(desc(WizardTemplateRating.created_at))\
            .offset(skip)\
            .limit(limit)\
            .all()

    def create(
        self, db: Session, obj_in: WizardTemplateRatingCreate, user_id: UUID
    ) -> WizardTemplateRating:
        """Create a new rating."""
        db_obj = WizardTemplateRating(
            template_id=obj_in.template_id,
            user_id=user_id,
            rating=obj_in.rating,
            review_text=obj_in.review_text,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # Update template average rating
        wizard_template_crud.update_average_rating(db, obj_in.template_id)

        return db_obj

    def update(
        self, db: Session, *, db_obj: WizardTemplateRating, obj_in: WizardTemplateRatingUpdate
    ) -> WizardTemplateRating:
        """Update a rating."""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # Update template average rating
        wizard_template_crud.update_average_rating(db, db_obj.template_id)

        return db_obj

    def delete(self, db: Session, *, rating_id: UUID) -> bool:
        """Delete a rating."""
        obj = db.query(WizardTemplateRating).filter(WizardTemplateRating.id == rating_id).first()
        if obj:
            template_id = obj.template_id
            db.delete(obj)
            db.commit()
            # Update template average rating
            wizard_template_crud.update_average_rating(db, template_id)
            return True
        return False

    def get_rating_distribution(self, db: Session, template_id: UUID) -> Dict[int, int]:
        """Get distribution of ratings (1-5 stars) for a template."""
        ratings = db.query(
            WizardTemplateRating.rating,
            func.count(WizardTemplateRating.id).label('count')
        ).filter(
            WizardTemplateRating.template_id == template_id
        ).group_by(
            WizardTemplateRating.rating
        ).all()

        # Initialize all ratings to 0
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for rating, count in ratings:
            distribution[rating] = count

        return distribution


# Create singleton instances
wizard_template_crud = WizardTemplateCRUD()
wizard_template_rating_crud = WizardTemplateRatingCRUD()
