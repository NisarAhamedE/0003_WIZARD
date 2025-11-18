from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class SessionResponseData(BaseModel):
    """Response data for a single option set"""
    selected_option_id: Optional[UUID] = None
    selected_option_ids: Optional[List[UUID]] = None
    text: Optional[str] = None
    number: Optional[float] = None
    date: Optional[str] = None
    file_url: Optional[str] = None
    rating: Optional[int] = None
    color: Optional[str] = None


class SessionResponseCreate(BaseModel):
    step_id: UUID
    option_set_id: UUID
    response_data: Dict[str, Any]
    time_spent_seconds: Optional[int] = None


class SessionResponseResponse(BaseModel):
    id: UUID
    session_id: UUID
    step_id: UUID
    option_set_id: UUID
    response_data: Dict[str, Any]
    time_spent_seconds: Optional[int] = None
    answered_at: datetime
    is_valid: bool
    validation_errors: List[str] = []

    class Config:
        from_attributes = True


class SessionBase(BaseModel):
    session_name: Optional[str] = Field(None, max_length=255)
    metadata: Dict[str, Any] = {}
    browser_info: Dict[str, Any] = {}


class SessionCreate(SessionBase):
    wizard_id: UUID


class SessionUpdate(BaseModel):
    session_name: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(in_progress|completed|abandoned|expired)$")
    current_step_id: Optional[UUID] = None
    progress_percentage: Optional[Decimal] = None
    metadata: Optional[Dict[str, Any]] = None


class SessionResponse(SessionBase):
    id: UUID
    wizard_id: UUID
    user_id: Optional[UUID] = None
    status: str
    current_step_id: Optional[UUID] = None
    progress_percentage: Decimal
    started_at: datetime
    last_activity_at: datetime
    completed_at: Optional[datetime] = None
    total_time_seconds: Optional[int] = None
    responses: List[SessionResponseResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    id: UUID
    wizard_id: UUID
    wizard_name: Optional[str] = None  # Add wizard name for display
    session_name: Optional[str] = None
    status: str
    progress_percentage: Decimal
    started_at: datetime
    last_activity_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
