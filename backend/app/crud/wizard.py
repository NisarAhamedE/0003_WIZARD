from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from datetime import datetime

from app.models.wizard import Wizard, WizardCategory, Step, OptionSet, Option, FlowRule, OptionDependency
from app.schemas.wizard import (
    WizardCreate, WizardUpdate,
    WizardCategoryCreate,
    StepCreate, StepUpdate,
    OptionSetCreate, OptionSetUpdate,
    OptionCreate, OptionUpdate,
    FlowRuleCreate, FlowRuleUpdate,
    OptionDependencyCreate
)


class WizardCategoryCRUD:
    def get(self, db: Session, category_id: UUID) -> Optional[WizardCategory]:
        return db.query(WizardCategory).filter(WizardCategory.id == category_id).first()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[WizardCategory]:
        return db.query(WizardCategory).order_by(WizardCategory.display_order).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: WizardCategoryCreate) -> WizardCategory:
        db_obj = WizardCategory(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class WizardCRUD:
    def get(self, db: Session, wizard_id: UUID) -> Optional[Wizard]:
        """Get wizard by ID with all related data"""
        return db.query(Wizard).options(
            joinedload(Wizard.steps).joinedload(Step.option_sets).joinedload(OptionSet.options).joinedload(Option.dependencies),
            joinedload(Wizard.category)
        ).filter(Wizard.id == wizard_id).first()

    def get_multi(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        published_only: bool = False,
        category_id: Optional[UUID] = None
    ) -> List[Wizard]:
        """Get multiple wizards with filters"""
        query = db.query(Wizard).options(joinedload(Wizard.category))

        if published_only:
            query = query.filter(Wizard.is_published == True)

        if category_id:
            query = query.filter(Wizard.category_id == category_id)

        query = query.filter(Wizard.is_active == True)
        return query.order_by(Wizard.created_at.desc()).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: WizardCreate, created_by: UUID) -> Wizard:
        """Create new wizard with steps and options"""
        wizard_data = obj_in.model_dump(exclude={"steps"})
        db_wizard = Wizard(**wizard_data, created_by=created_by)
        db.add(db_wizard)
        db.flush()  # Get wizard ID

        # Create steps
        for step_data in obj_in.steps:
            step_dict = step_data.model_dump(exclude={"option_sets"})
            db_step = Step(**step_dict, wizard_id=db_wizard.id)
            db.add(db_step)
            db.flush()

            # Create option sets
            for option_set_data in step_data.option_sets:
                option_set_dict = option_set_data.model_dump(exclude={"options"})
                db_option_set = OptionSet(**option_set_dict, step_id=db_step.id)
                db.add(db_option_set)
                db.flush()

                # Create options
                for option_data in option_set_data.options:
                    db_option = Option(**option_data.model_dump(), option_set_id=db_option_set.id)
                    db.add(db_option)

        db.commit()
        db.refresh(db_wizard)
        return self.get(db, db_wizard.id)

    def update(self, db: Session, db_obj: Wizard, obj_in: WizardUpdate) -> Wizard:
        """Update wizard with nested steps, option_sets, and options"""
        update_data = obj_in.model_dump(exclude_unset=True, exclude={"steps"})

        # Update wizard basic fields
        for field in update_data:
            setattr(db_obj, field, update_data[field])

        # Handle steps update if provided
        if obj_in.steps is not None:
            wizard_id = db_obj.id

            # Delete existing steps (CASCADE will handle option_sets and options)
            db.query(Step).filter(Step.wizard_id == wizard_id).delete()
            db.commit()

            # Refresh the wizard object to clear deleted Step references from memory
            db.refresh(db_obj)

            # Create new steps
            for step_data in obj_in.steps:
                step_dict = step_data.model_dump(exclude={"option_sets"})
                db_step = Step(**step_dict, wizard_id=db_obj.id)
                db.add(db_step)
                db.flush()

                # Create option sets
                for option_set_data in step_data.option_sets:
                    option_set_dict = option_set_data.model_dump(exclude={"options"})
                    db_option_set = OptionSet(**option_set_dict, step_id=db_step.id)
                    db.add(db_option_set)
                    db.flush()

                    # Create options
                    for option_data in option_set_data.options:
                        db_option = Option(**option_data.model_dump(), option_set_id=db_option_set.id)
                        db.add(db_option)

        db_obj.updated_at = datetime.utcnow()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return self.get(db, db_obj.id)

    def publish(self, db: Session, wizard: Wizard, publish: bool = True) -> Wizard:
        """Publish or unpublish wizard"""
        wizard.is_published = publish
        if publish:
            wizard.published_at = datetime.utcnow()
        wizard.updated_at = datetime.utcnow()
        db.add(wizard)
        db.commit()
        db.refresh(wizard)
        return wizard

    def soft_delete(self, db: Session, wizard: Wizard) -> Wizard:
        """Soft delete wizard"""
        wizard.is_active = False
        wizard.is_published = False
        wizard.updated_at = datetime.utcnow()
        db.add(wizard)
        db.commit()
        db.refresh(wizard)
        return wizard

    def increment_session_count(self, db: Session, wizard: Wizard) -> Wizard:
        """Increment total session count"""
        wizard.total_sessions += 1
        db.add(wizard)
        db.commit()
        db.refresh(wizard)
        return wizard

    def increment_completed_count(self, db: Session, wizard: Wizard) -> Wizard:
        """Increment completed session count"""
        wizard.completed_sessions += 1
        db.add(wizard)
        db.commit()
        db.refresh(wizard)
        return wizard

    def count(self, db: Session, created_by: Optional[UUID] = None) -> int:
        """Count wizards"""
        query = db.query(Wizard).filter(Wizard.is_active == True)
        if created_by:
            query = query.filter(Wizard.created_by == created_by)
        return query.count()

    def clone_wizard(
        self,
        db: Session,
        wizard_id: UUID,
        new_name: str,
        created_by: UUID,
        new_description: Optional[str] = None
    ) -> Optional[Wizard]:
        """
        Clone an existing wizard with all its steps, option sets, options, and dependencies.

        Args:
            db: Database session
            wizard_id: UUID of the wizard to clone
            new_name: Name for the new wizard
            created_by: UUID of the user creating the clone
            new_description: Optional description override

        Returns:
            The cloned wizard with all relationships, or None if source wizard not found
        """
        import uuid

        # Get the source wizard with all relationships
        source_wizard = self.get(db, wizard_id)
        if not source_wizard:
            return None

        # Create new wizard (copy basic fields)
        new_wizard = Wizard(
            id=uuid.uuid4(),
            name=new_name,
            description=new_description or source_wizard.description,
            category_id=source_wizard.category_id,
            created_by=created_by,
            icon=source_wizard.icon,
            cover_image=source_wizard.cover_image,
            is_published=False,  # Clones start unpublished
            is_active=True,
            allow_templates=source_wizard.allow_templates,
            require_login=source_wizard.require_login,
            allow_anonymous=source_wizard.allow_anonymous,
            auto_save=source_wizard.auto_save,
            auto_save_interval=source_wizard.auto_save_interval,
            estimated_time=source_wizard.estimated_time,
            difficulty_level=source_wizard.difficulty_level,
            tags=source_wizard.tags,
            lifecycle_state='draft',  # New wizard starts as draft
            version_number=1
        )
        db.add(new_wizard)
        db.flush()

        # Map old IDs to new IDs for relationship reconstruction
        step_id_map = {}
        option_set_id_map = {}
        option_id_map = {}

        # Clone steps
        for source_step in source_wizard.steps:
            new_step = Step(
                id=uuid.uuid4(),
                wizard_id=new_wizard.id,
                name=source_step.name,
                description=source_step.description,
                help_text=source_step.help_text,
                step_order=source_step.step_order,
                is_required=source_step.is_required,
                is_skippable=source_step.is_skippable,
                allow_back_navigation=source_step.allow_back_navigation,
                layout=source_step.layout,
                custom_styles=source_step.custom_styles,
                validation_rules=source_step.validation_rules
            )
            db.add(new_step)
            db.flush()
            step_id_map[source_step.id] = new_step.id

            # Clone option sets for this step
            for source_option_set in source_step.option_sets:
                new_option_set = OptionSet(
                    id=uuid.uuid4(),
                    step_id=new_step.id,
                    name=source_option_set.name,
                    description=source_option_set.description,
                    selection_type=source_option_set.selection_type,
                    is_required=source_option_set.is_required,
                    min_selections=source_option_set.min_selections,
                    max_selections=source_option_set.max_selections,
                    min_value=source_option_set.min_value,
                    max_value=source_option_set.max_value,
                    regex_pattern=source_option_set.regex_pattern,
                    custom_validation=source_option_set.custom_validation,
                    display_order=source_option_set.display_order,
                    placeholder=source_option_set.placeholder,
                    help_text=source_option_set.help_text,
                    step_increment=source_option_set.step_increment
                )
                db.add(new_option_set)
                db.flush()
                option_set_id_map[source_option_set.id] = new_option_set.id

                # Clone options for this option set
                for source_option in source_option_set.options:
                    new_option = Option(
                        id=uuid.uuid4(),
                        option_set_id=new_option_set.id,
                        label=source_option.label,
                        value=source_option.value,
                        description=source_option.description,
                        display_order=source_option.display_order,
                        icon=source_option.icon,
                        image_url=source_option.image_url,
                        is_default=source_option.is_default,
                        is_recommended=source_option.is_recommended,
                        is_active=source_option.is_active,
                        option_metadata=source_option.option_metadata
                    )
                    db.add(new_option)
                    db.flush()
                    option_id_map[source_option.id] = new_option.id

        # Clone option dependencies (now that all options exist)
        for source_step in source_wizard.steps:
            for source_option_set in source_step.option_sets:
                for source_option in source_option_set.options:
                    for source_dependency in source_option.dependencies:
                        new_dependency = OptionDependency(
                            id=uuid.uuid4(),
                            option_id=option_id_map[source_dependency.option_id],
                            depends_on_option_id=option_id_map[source_dependency.depends_on_option_id],
                            dependency_type=source_dependency.dependency_type
                        )
                        db.add(new_dependency)

        db.commit()
        db.refresh(new_wizard)

        # Return the cloned wizard with all relationships loaded
        return self.get(db, new_wizard.id)


class StepCRUD:
    def get(self, db: Session, step_id: UUID) -> Optional[Step]:
        return db.query(Step).options(
            joinedload(Step.option_sets).joinedload(OptionSet.options)
        ).filter(Step.id == step_id).first()

    def get_by_wizard(self, db: Session, wizard_id: UUID) -> List[Step]:
        return db.query(Step).filter(Step.wizard_id == wizard_id).order_by(Step.step_order).all()

    def create(self, db: Session, obj_in: StepCreate, wizard_id: UUID) -> Step:
        step_data = obj_in.model_dump(exclude={"option_sets"})
        db_step = Step(**step_data, wizard_id=wizard_id)
        db.add(db_step)
        db.flush()

        for option_set_data in obj_in.option_sets:
            option_set_dict = option_set_data.model_dump(exclude={"options"})
            db_option_set = OptionSet(**option_set_dict, step_id=db_step.id)
            db.add(db_option_set)
            db.flush()

            for option_data in option_set_data.options:
                db_option = Option(**option_data.model_dump(), option_set_id=db_option_set.id)
                db.add(db_option)

        db.commit()
        db.refresh(db_step)
        return self.get(db, db_step.id)

    def update(self, db: Session, db_obj: Step, obj_in: StepUpdate) -> Step:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        db_obj.updated_at = datetime.utcnow()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, step: Step) -> None:
        db.delete(step)
        db.commit()


class OptionSetCRUD:
    def get(self, db: Session, option_set_id: UUID) -> Optional[OptionSet]:
        return db.query(OptionSet).options(
            joinedload(OptionSet.options)
        ).filter(OptionSet.id == option_set_id).first()

    def create(self, db: Session, obj_in: OptionSetCreate, step_id: UUID) -> OptionSet:
        option_set_data = obj_in.model_dump(exclude={"options"})
        db_option_set = OptionSet(**option_set_data, step_id=step_id)
        db.add(db_option_set)
        db.flush()

        for option_data in obj_in.options:
            db_option = Option(**option_data.model_dump(), option_set_id=db_option_set.id)
            db.add(db_option)

        db.commit()
        db.refresh(db_option_set)
        return self.get(db, db_option_set.id)

    def update(self, db: Session, db_obj: OptionSet, obj_in: OptionSetUpdate) -> OptionSet:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        db_obj.updated_at = datetime.utcnow()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class OptionCRUD:
    def get(self, db: Session, option_id: UUID) -> Optional[Option]:
        return db.query(Option).filter(Option.id == option_id).first()

    def create(self, db: Session, obj_in: OptionCreate, option_set_id: UUID) -> Option:
        db_option = Option(**obj_in.model_dump(), option_set_id=option_set_id)
        db.add(db_option)
        db.commit()
        db.refresh(db_option)
        return db_option

    def update(self, db: Session, db_obj: Option, obj_in: OptionUpdate) -> Option:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        db_obj.updated_at = datetime.utcnow()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class FlowRuleCRUD:
    def get(self, db: Session, rule_id: UUID) -> Optional[FlowRule]:
        return db.query(FlowRule).filter(FlowRule.id == rule_id).first()

    def get_by_wizard(self, db: Session, wizard_id: UUID) -> List[FlowRule]:
        return db.query(FlowRule).filter(
            FlowRule.wizard_id == wizard_id
        ).order_by(FlowRule.priority.desc()).all()

    def create(self, db: Session, obj_in: FlowRuleCreate) -> FlowRule:
        db_obj = FlowRule(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: FlowRule, obj_in: FlowRuleUpdate) -> FlowRule:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        db_obj.updated_at = datetime.utcnow()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: FlowRule) -> None:
        db.delete(db_obj)
        db.commit()


class OptionDependencyCRUD:
    def get(self, db: Session, dependency_id: UUID) -> Optional[OptionDependency]:
        return db.query(OptionDependency).filter(OptionDependency.id == dependency_id).first()

    def get_by_option(self, db: Session, option_id: UUID) -> List[OptionDependency]:
        """Get all dependencies for a specific option"""
        return db.query(OptionDependency).filter(
            OptionDependency.option_id == option_id
        ).all()

    def create(self, db: Session, obj_in: OptionDependencyCreate, option_id: UUID) -> OptionDependency:
        """Create a new option dependency"""
        db_obj = OptionDependency(**obj_in.model_dump(), option_id=option_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: OptionDependency) -> None:
        """Delete an option dependency"""
        db.delete(db_obj)
        db.commit()


category_crud = WizardCategoryCRUD()
wizard_crud = WizardCRUD()
step_crud = StepCRUD()
option_set_crud = OptionSetCRUD()
option_crud = OptionCRUD()
flow_rule_crud = FlowRuleCRUD()
option_dependency_crud = OptionDependencyCRUD()
