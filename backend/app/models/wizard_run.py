"""
Wizard Run Models

Models for the Run Wizard and Store Wizard systems.
"""
from sqlalchemy import Column, String, Integer, Boolean, DECIMAL, TIMESTAMP, Text, ARRAY, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.database import Base


class WizardRun(Base):
    """
    Wizard Run model for tracking user execution of wizards.
    Represents both in-progress and completed wizard sessions.
    """
    __tablename__ = "wizard_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wizard_id = Column(UUID(as_uuid=True), ForeignKey('wizards.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'))
    run_name = Column(String(255))
    run_description = Column(Text)
    status = Column(String(20), default='in_progress')
    current_step_index = Column(Integer, default=0)
    total_steps = Column(Integer)
    progress_percentage = Column(DECIMAL(5, 2), default=0)
    started_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(TIMESTAMP(timezone=True))
    last_accessed_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    calculated_price = Column(DECIMAL(10, 2))
    is_stored = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)
    tags = Column(ARRAY(Text))
    run_metadata = Column("metadata", JSONB)  # Renamed to avoid SQLAlchemy conflict

    # Relationships
    wizard = relationship("Wizard", back_populates="runs")
    user = relationship("User", back_populates="wizard_runs")
    step_responses = relationship("WizardRunStepResponse", back_populates="run", cascade="all, delete-orphan")
    option_set_responses = relationship("WizardRunOptionSetResponse", back_populates="run", cascade="all, delete-orphan")
    file_uploads = relationship("WizardRunFileUpload", back_populates="run", cascade="all, delete-orphan")
    shares = relationship("WizardRunShare", back_populates="run", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            status.in_(['in_progress', 'completed', 'abandoned']),
            name='check_status'
        ),
    )

    def __repr__(self):
        return f"<WizardRun(id={self.id}, wizard_id={self.wizard_id}, status={self.status})>"


class WizardRunStepResponse(Base):
    """
    Wizard Run Step Response model for tracking step-level completion.
    """
    __tablename__ = "wizard_run_step_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), ForeignKey('wizard_runs.id', ondelete='CASCADE'), nullable=False)
    step_id = Column(UUID(as_uuid=True), ForeignKey('steps.id', ondelete='CASCADE'), nullable=False)
    step_index = Column(Integer, nullable=False)
    step_name = Column(String(255))
    completed = Column(Boolean, default=False)
    completed_at = Column(TIMESTAMP(timezone=True))
    time_spent_seconds = Column(Integer, default=0)

    # Relationships
    run = relationship("WizardRun", back_populates="step_responses")
    step = relationship("Step")
    option_set_responses = relationship("WizardRunOptionSetResponse", back_populates="step_response", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<WizardRunStepResponse(run_id={self.run_id}, step_id={self.step_id}, completed={self.completed})>"


class WizardRunOptionSetResponse(Base):
    """
    Wizard Run Option Set Response model for storing user selections.
    """
    __tablename__ = "wizard_run_option_set_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), ForeignKey('wizard_runs.id', ondelete='CASCADE'), nullable=False)
    step_response_id = Column(UUID(as_uuid=True), ForeignKey('wizard_run_step_responses.id', ondelete='CASCADE'), nullable=False)
    option_set_id = Column(UUID(as_uuid=True), ForeignKey('option_sets.id', ondelete='CASCADE'), nullable=False)
    option_set_name = Column(String(255))
    selection_type = Column(String(50))
    response_value = Column(JSONB, nullable=False)  # Flexible storage for any response type
    selected_options = Column(ARRAY(UUID(as_uuid=True)))  # For single/multiple select types
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    run = relationship("WizardRun", back_populates="option_set_responses")
    step_response = relationship("WizardRunStepResponse", back_populates="option_set_responses")
    option_set = relationship("OptionSet")
    file_uploads = relationship("WizardRunFileUpload", back_populates="option_set_response", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<WizardRunOptionSetResponse(run_id={self.run_id}, option_set_id={self.option_set_id})>"


class WizardRunFileUpload(Base):
    """
    Wizard Run File Upload model for tracking uploaded files.
    """
    __tablename__ = "wizard_run_file_uploads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), ForeignKey('wizard_runs.id', ondelete='CASCADE'), nullable=False)
    option_set_response_id = Column(UUID(as_uuid=True), ForeignKey('wizard_run_option_set_responses.id', ondelete='CASCADE'), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(100))
    uploaded_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    run = relationship("WizardRun", back_populates="file_uploads")
    option_set_response = relationship("WizardRunOptionSetResponse", back_populates="file_uploads")

    def __repr__(self):
        return f"<WizardRunFileUpload(id={self.id}, file_name={self.file_name})>"


class WizardRunShare(Base):
    """
    Wizard Run Share model for sharing completed wizard runs.
    """
    __tablename__ = "wizard_run_shares"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), ForeignKey('wizard_runs.id', ondelete='CASCADE'), nullable=False)
    share_token = Column(String(255), unique=True, nullable=False)
    shared_by = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    share_type = Column(String(20), default='view')
    expires_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    access_count = Column(Integer, default=0)
    last_accessed_at = Column(TIMESTAMP(timezone=True))
    is_active = Column(Boolean, default=True)

    # Relationships
    run = relationship("WizardRun", back_populates="shares")
    user = relationship("User", back_populates="shared_runs")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            share_type.in_(['view', 'edit', 'clone']),
            name='check_share_type'
        ),
    )

    def __repr__(self):
        return f"<WizardRunShare(id={self.id}, run_id={self.run_id}, share_type={self.share_type})>"


class WizardRunComparison(Base):
    """
    Wizard Run Comparison model for comparing multiple wizard runs.
    """
    __tablename__ = "wizard_run_comparisons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    comparison_name = Column(String(255))
    run_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    comparison_metadata = Column("metadata", JSONB)  # Renamed to avoid SQLAlchemy conflict

    # Relationships
    user = relationship("User", back_populates="run_comparisons")

    def __repr__(self):
        return f"<WizardRunComparison(id={self.id}, comparison_name={self.comparison_name})>"
