import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Text, Integer, Numeric, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wizard_id = Column(UUID(as_uuid=True), ForeignKey("wizards.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))  # NULL for anonymous
    session_name = Column(String(255))

    # Status
    status = Column(String(50), nullable=False, default='in_progress')

    # Progress
    current_step_id = Column(UUID(as_uuid=True), ForeignKey("steps.id"))
    progress_percentage = Column(Numeric(5, 2), default=0)

    # Timing
    started_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_activity_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at = Column(DateTime(timezone=True))

    # Metadata
    session_metadata = Column("metadata", JSONB, default={})
    browser_info = Column(JSONB, default={})

    # Summary
    total_time_seconds = Column(Integer)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            status.in_(['in_progress', 'completed', 'abandoned', 'expired']),
            name='check_session_status'
        ),
    )

    # Relationships
    wizard = relationship("Wizard", back_populates="sessions")
    user = relationship("User", back_populates="sessions")
    responses = relationship("SessionResponse", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<UserSession(name={self.session_name}, status={self.status})>"


class SessionResponse(Base):
    __tablename__ = "session_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("user_sessions.id", ondelete="CASCADE"), nullable=False)
    step_id = Column(UUID(as_uuid=True), ForeignKey("steps.id"), nullable=False)
    option_set_id = Column(UUID(as_uuid=True), ForeignKey("option_sets.id"), nullable=False)

    # Response data
    response_data = Column(JSONB, nullable=False)

    # Timing
    time_spent_seconds = Column(Integer)
    answered_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Validation
    is_valid = Column(Boolean, default=True)
    validation_errors = Column(JSONB, default=[])

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    session = relationship("UserSession", back_populates="responses")

    def __repr__(self):
        return f"<SessionResponse(session_id={self.session_id}, option_set_id={self.option_set_id})>"
