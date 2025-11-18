from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


class TemplateResponseData(BaseModel):
    step_id: UUID
    option_set_id: UUID
    response_data: Dict[str, Any]


class TemplateBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    is_public: bool = False
    tags: List[str] = []


class TemplateCreate(TemplateBase):
    wizard_id: UUID
    source_session_id: Optional[UUID] = None
    responses: List[TemplateResponseData] = []


class TemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    is_public: Optional[bool] = None
    tags: Optional[List[str]] = None


class TemplateResponseSchema(BaseModel):
    id: UUID
    template_id: UUID
    step_id: UUID
    option_set_id: UUID
    response_data: Dict[str, Any]

    class Config:
        from_attributes = True


class TemplateResponse(TemplateBase):
    id: UUID
    wizard_id: UUID
    user_id: UUID
    source_session_id: Optional[UUID] = None
    is_active: bool
    times_used: int
    last_used_at: Optional[datetime] = None
    responses: List[TemplateResponseSchema] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    id: UUID
    wizard_id: UUID
    user_id: UUID
    name: str
    description: Optional[str] = None
    is_public: bool
    tags: List[str] = []
    times_used: int
    last_used_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
