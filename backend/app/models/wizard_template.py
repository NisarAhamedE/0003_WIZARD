"""
Wizard Template Models

Models for the Wizard Template Gallery system.
"""
from sqlalchemy import Column, String, Integer, Boolean, DECIMAL, TIMESTAMP, Text, ARRAY, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.database import Base


class WizardTemplate(Base):
    """
    Wizard Template model for storing reusable wizard configurations.
    Can be system templates or user-created templates.
    """
    __tablename__ = "wizard_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_name = Column(String(255), nullable=False)
    template_description = Column(Text)
    category = Column(String(100))
    icon = Column(String(50))
    difficulty_level = Column(String(20))
    estimated_time = Column(Integer)  # in minutes
    tags = Column(ARRAY(Text))
    preview_image = Column(Text)
    step_count = Column(Integer)
    option_set_count = Column(Integer)
    is_system_template = Column(Boolean, default=False)
    created_by = Column(String(50), default='system')
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    usage_count = Column(Integer, default=0)
    average_rating = Column(DECIMAL(3, 2), default=0)
    wizard_structure = Column(JSONB, nullable=False)  # Complete wizard configuration
    is_active = Column(Boolean, default=True)

    # Relationships
    ratings = relationship("WizardTemplateRating", back_populates="template", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            difficulty_level.in_(['easy', 'medium', 'hard']),
            name='check_difficulty'
        ),
    )

    def __repr__(self):
        return f"<WizardTemplate(id={self.id}, name={self.template_name}, category={self.category})>"


class WizardTemplateRating(Base):
    """
    Wizard Template Rating model for user ratings and reviews.
    """
    __tablename__ = "wizard_template_ratings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey('wizard_templates.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    rating = Column(Integer, nullable=False)
    review_text = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    template = relationship("WizardTemplate", back_populates="ratings")
    user = relationship("User", back_populates="template_ratings")

    # Constraints
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
        # Unique constraint: one rating per user per template
        # Using tuple syntax for unique constraint
    )

    def __repr__(self):
        return f"<WizardTemplateRating(template_id={self.template_id}, user_id={self.user_id}, rating={self.rating})>"
