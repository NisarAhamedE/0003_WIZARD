import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class Template(Base):
    __tablename__ = "templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wizard_id = Column(UUID(as_uuid=True), ForeignKey("wizards.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    source_session_id = Column(UUID(as_uuid=True), ForeignKey("user_sessions.id"))

    # Template info
    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Visibility
    is_public = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # Stats
    times_used = Column(Integer, default=0)
    last_used_at = Column(DateTime(timezone=True))

    # Tags
    tags = Column(JSONB, default=[])

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    wizard = relationship("Wizard", back_populates="templates")
    user = relationship("User", back_populates="templates")
    responses = relationship("TemplateResponse", back_populates="template", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Template(name={self.name})>"


class TemplateResponse(Base):
    __tablename__ = "template_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("templates.id", ondelete="CASCADE"), nullable=False)
    step_id = Column(UUID(as_uuid=True), ForeignKey("steps.id"), nullable=False)
    option_set_id = Column(UUID(as_uuid=True), ForeignKey("option_sets.id"), nullable=False)

    # Stored response
    response_data = Column(JSONB, nullable=False)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    template = relationship("Template", back_populates="responses")

    def __repr__(self):
        return f"<TemplateResponse(template_id={self.template_id})>"
