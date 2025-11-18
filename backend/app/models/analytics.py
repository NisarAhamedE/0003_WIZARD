import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from app.database import Base


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Context
    session_id = Column(UUID(as_uuid=True), ForeignKey("user_sessions.id", ondelete="SET NULL"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    wizard_id = Column(UUID(as_uuid=True), ForeignKey("wizards.id", ondelete="SET NULL"))
    step_id = Column(UUID(as_uuid=True), ForeignKey("steps.id", ondelete="SET NULL"))

    # Event info
    event_type = Column(String(100), nullable=False)
    event_name = Column(String(255), nullable=False)
    event_data = Column(JSONB, default={})

    # Timing
    occurred_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Client info
    ip_address = Column(INET)
    user_agent = Column(Text)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    def __repr__(self):
        return f"<AnalyticsEvent(type={self.event_type}, name={self.event_name})>"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Who
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))

    # What
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(UUID(as_uuid=True))

    # Details
    old_values = Column(JSONB)
    new_values = Column(JSONB)

    # Context
    ip_address = Column(INET)
    user_agent = Column(Text)

    # When
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    def __repr__(self):
        return f"<AuditLog(action={self.action}, resource={self.resource_type})>"


class SystemSetting(Base):
    __tablename__ = "system_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(JSONB, nullable=False)
    description = Column(Text)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SystemSetting(key={self.key})>"
