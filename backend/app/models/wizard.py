import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Text, Integer, Numeric, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class WizardCategory(Base):
    __tablename__ = "wizard_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    icon = Column(String(50))
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    wizards = relationship("Wizard", back_populates="category")

    def __repr__(self):
        return f"<WizardCategory(name={self.name})>"


class Wizard(Base):
    __tablename__ = "wizards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category_id = Column(UUID(as_uuid=True), ForeignKey("wizard_categories.id"))
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    icon = Column(String(100))
    cover_image = Column(String(500))

    # Settings
    is_published = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    allow_templates = Column(Boolean, default=True)
    require_login = Column(Boolean, default=True)
    allow_anonymous = Column(Boolean, default=False)
    auto_save = Column(Boolean, default=True)
    auto_save_interval = Column(Integer, default=30)

    # Metadata
    estimated_time = Column(Integer)  # minutes
    difficulty_level = Column(String(20))
    tags = Column(JSONB, default=[])

    # Stats
    total_sessions = Column(Integer, default=0)
    completed_sessions = Column(Integer, default=0)
    average_completion_time = Column(Integer)  # seconds

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime(timezone=True))

    # Lifecycle protection fields
    lifecycle_state = Column(String(20), default='draft')
    first_run_at = Column(DateTime(timezone=True))
    first_stored_run_at = Column(DateTime(timezone=True))
    is_archived = Column(Boolean, default=False)
    archived_at = Column(DateTime(timezone=True))
    version_number = Column(Integer, default=1)
    parent_wizard_id = Column(UUID(as_uuid=True), ForeignKey("wizards.id", ondelete="SET NULL"))

    __table_args__ = (
        CheckConstraint(difficulty_level.in_(['easy', 'medium', 'hard']), name='check_difficulty_level'),
        CheckConstraint(lifecycle_state.in_(['draft', 'in_use', 'published']), name='check_lifecycle_state'),
    )

    # Relationships
    category = relationship("WizardCategory", back_populates="wizards")
    creator = relationship("User", back_populates="wizards")
    steps = relationship("Step", back_populates="wizard", cascade="all, delete-orphan", order_by="Step.step_order")
    flow_rules = relationship("FlowRule", back_populates="wizard", cascade="all, delete-orphan")
    runs = relationship("WizardRun", back_populates="wizard")

    def __repr__(self):
        return f"<Wizard(name={self.name})>"


class Step(Base):
    __tablename__ = "steps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wizard_id = Column(UUID(as_uuid=True), ForeignKey("wizards.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    help_text = Column(Text)

    # Ordering
    step_order = Column(Integer, nullable=False)

    # Configuration
    is_required = Column(Boolean, default=True)
    is_skippable = Column(Boolean, default=False)
    allow_back_navigation = Column(Boolean, default=True)

    # UI Settings
    layout = Column(String(50), default='vertical')
    custom_styles = Column(JSONB, default={})

    # Validation
    validation_rules = Column(JSONB, default={})

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    wizard = relationship("Wizard", back_populates="steps")
    option_sets = relationship("OptionSet", back_populates="step", cascade="all, delete-orphan", order_by="OptionSet.display_order")

    def __repr__(self):
        return f"<Step(name={self.name}, order={self.step_order})>"


class OptionSet(Base):
    __tablename__ = "option_sets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    step_id = Column(UUID(as_uuid=True), ForeignKey("steps.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Selection type
    selection_type = Column(String(50), nullable=False)

    # Validation
    is_required = Column(Boolean, default=True)
    min_selections = Column(Integer, default=0)
    max_selections = Column(Integer)
    min_value = Column(Numeric)
    max_value = Column(Numeric)
    regex_pattern = Column(String(500))
    custom_validation = Column(JSONB, default={})

    # Display
    display_order = Column(Integer, default=0)
    placeholder = Column(Text)
    help_text = Column(Text)

    # For number/slider inputs
    step_increment = Column(Numeric, default=1)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            selection_type.in_([
                'single_select', 'multiple_select', 'text_input', 'number_input',
                'date_input', 'time_input', 'datetime_input', 'file_upload',
                'rating', 'slider', 'color_picker', 'rich_text'
            ]),
            name='check_selection_type'
        ),
    )

    # Relationships
    step = relationship("Step", back_populates="option_sets")
    options = relationship("Option", back_populates="option_set", cascade="all, delete-orphan", order_by="Option.display_order")

    def __repr__(self):
        return f"<OptionSet(name={self.name}, type={self.selection_type})>"


class Option(Base):
    __tablename__ = "options"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    option_set_id = Column(UUID(as_uuid=True), ForeignKey("option_sets.id", ondelete="CASCADE"), nullable=False)
    label = Column(String(255), nullable=False)
    value = Column(String(255), nullable=False)
    description = Column(Text)

    # Display
    display_order = Column(Integer, default=0)
    icon = Column(String(100))
    image_url = Column(String(500))

    # Flags
    is_default = Column(Boolean, default=False)
    is_recommended = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # Metadata
    option_metadata = Column("metadata", JSONB, default={})

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    option_set = relationship("OptionSet", back_populates="options")
    dependencies = relationship("OptionDependency", foreign_keys="OptionDependency.option_id", back_populates="option", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Option(label={self.label}, value={self.value})>"


class OptionDependency(Base):
    __tablename__ = "option_dependencies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    option_id = Column(UUID(as_uuid=True), ForeignKey("options.id", ondelete="CASCADE"), nullable=False)
    depends_on_option_id = Column(UUID(as_uuid=True), ForeignKey("options.id", ondelete="CASCADE"), nullable=False)
    dependency_type = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        CheckConstraint(
            "dependency_type IN ('show_if', 'hide_if', 'require_if', 'disable_if')",
            name='check_dependency_type'
        ),
    )

    # Relationships
    option = relationship("Option", foreign_keys=[option_id], back_populates="dependencies")

    def __repr__(self):
        return f"<OptionDependency(type={self.dependency_type})>"


class FlowRule(Base):
    __tablename__ = "flow_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wizard_id = Column(UUID(as_uuid=True), ForeignKey("wizards.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255))
    description = Column(Text)
    from_step_id = Column(UUID(as_uuid=True), ForeignKey("steps.id", ondelete="CASCADE"), nullable=False)
    to_step_id = Column(UUID(as_uuid=True), ForeignKey("steps.id", ondelete="CASCADE"), nullable=False)
    condition = Column(JSONB, nullable=False)
    priority = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    wizard = relationship("Wizard", back_populates="flow_rules")

    def __repr__(self):
        return f"<FlowRule(name={self.name})>"
