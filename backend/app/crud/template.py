from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from datetime import datetime

from app.models.template import Template, TemplateResponse
from app.schemas.template import TemplateCreate, TemplateUpdate


class TemplateCRUD:
    def get(self, db: Session, template_id: UUID) -> Optional[Template]:
        """Get template by ID with responses"""
        return db.query(Template).options(
            joinedload(Template.responses)
        ).filter(Template.id == template_id).first()

    def get_by_user(
        self,
        db: Session,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Template]:
        """Get user's templates"""
        return db.query(Template).filter(
            Template.user_id == user_id,
            Template.is_active == True
        ).order_by(Template.created_at.desc()).offset(skip).limit(limit).all()

    def get_public(
        self,
        db: Session,
        wizard_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Template]:
        """Get public templates"""
        query = db.query(Template).filter(
            Template.is_public == True,
            Template.is_active == True
        )

        if wizard_id:
            query = query.filter(Template.wizard_id == wizard_id)

        return query.order_by(Template.times_used.desc()).offset(skip).limit(limit).all()

    def get_accessible(
        self,
        db: Session,
        user_id: UUID,
        wizard_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Template]:
        """Get templates accessible to user (own + public)"""
        query = db.query(Template).filter(
            Template.is_active == True,
            ((Template.user_id == user_id) | (Template.is_public == True))
        )

        if wizard_id:
            query = query.filter(Template.wizard_id == wizard_id)

        return query.order_by(Template.created_at.desc()).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: TemplateCreate, user_id: UUID) -> Template:
        """Create new template"""
        template_data = obj_in.model_dump(exclude={"responses"})
        db_template = Template(**template_data, user_id=user_id)
        db.add(db_template)
        db.flush()

        # Add responses
        for response_data in obj_in.responses:
            db_response = TemplateResponse(
                template_id=db_template.id,
                step_id=response_data.step_id,
                option_set_id=response_data.option_set_id,
                response_data=response_data.response_data
            )
            db.add(db_response)

        db.commit()
        db.refresh(db_template)
        return self.get(db, db_template.id)

    def create_from_session(
        self,
        db: Session,
        name: str,
        description: Optional[str],
        session,
        user_id: UUID,
        is_public: bool = False,
        tags: List[str] = []
    ) -> Template:
        """Create template from completed session"""
        db_template = Template(
            wizard_id=session.wizard_id,
            user_id=user_id,
            source_session_id=session.id,
            name=name,
            description=description,
            is_public=is_public,
            tags=tags
        )
        db.add(db_template)
        db.flush()

        # Copy session responses to template
        for session_response in session.responses:
            db_response = TemplateResponse(
                template_id=db_template.id,
                step_id=session_response.step_id,
                option_set_id=session_response.option_set_id,
                response_data=session_response.response_data
            )
            db.add(db_response)

        db.commit()
        db.refresh(db_template)
        return self.get(db, db_template.id)

    def update(self, db: Session, db_obj: Template, obj_in: TemplateUpdate) -> Template:
        """Update template"""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field in update_data:
            setattr(db_obj, field, update_data[field])

        db_obj.updated_at = datetime.utcnow()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def increment_usage(self, db: Session, template: Template) -> Template:
        """Increment template usage count"""
        template.times_used += 1
        template.last_used_at = datetime.utcnow()
        db.add(template)
        db.commit()
        db.refresh(template)
        return template

    def soft_delete(self, db: Session, template: Template) -> Template:
        """Soft delete template"""
        template.is_active = False
        template.updated_at = datetime.utcnow()
        db.add(template)
        db.commit()
        db.refresh(template)
        return template

    def count_by_user(self, db: Session, user_id: UUID) -> int:
        """Count user's templates"""
        return db.query(Template).filter(
            Template.user_id == user_id,
            Template.is_active == True
        ).count()


template_crud = TemplateCRUD()
