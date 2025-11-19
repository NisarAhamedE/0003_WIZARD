"""
Wizard Template Schemas

Pydantic schemas for request/response validation of wizard templates.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class WizardTemplateBase(BaseModel):
    """Base wizard template schema with common fields."""
    template_name: str = Field(..., min_length=1, max_length=255)
    template_description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    icon: Optional[str] = Field(None, max_length=50)
    difficulty_level: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    estimated_time: Optional[int] = Field(None, ge=0)  # in minutes
    tags: Optional[List[str]] = Field(default_factory=list)
    preview_image: Optional[str] = None
    wizard_structure: Dict[str, Any] = Field(...)  # Complete wizard configuration

    @field_validator('difficulty_level')
    @classmethod
    def validate_difficulty(cls, v):
        if v and v not in ['easy', 'medium', 'hard']:
            raise ValueError('difficulty_level must be easy, medium, or hard')
        return v


class WizardTemplateCreate(WizardTemplateBase):
    """Schema for creating a new wizard template."""
    is_system_template: bool = False
    created_by: str = Field(default='system', max_length=50)


class WizardTemplateUpdate(BaseModel):
    """Schema for updating a wizard template."""
    template_name: Optional[str] = Field(None, min_length=1, max_length=255)
    template_description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    icon: Optional[str] = Field(None, max_length=50)
    difficulty_level: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    estimated_time: Optional[int] = Field(None, ge=0)
    tags: Optional[List[str]] = None
    preview_image: Optional[str] = None
    wizard_structure: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class WizardTemplateResponse(WizardTemplateBase):
    """Schema for wizard template responses."""
    id: UUID
    step_count: Optional[int] = None
    option_set_count: Optional[int] = None
    is_system_template: bool
    created_by: str
    created_at: datetime
    updated_at: datetime
    usage_count: int
    average_rating: Decimal
    is_active: bool

    model_config = {
        "from_attributes": True,
        "json_encoders": {
            UUID: str,
            datetime: lambda v: v.isoformat(),
            Decimal: float,
        }
    }


class WizardTemplateListResponse(BaseModel):
    """Schema for paginated list of wizard templates."""
    templates: List[WizardTemplateResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class WizardTemplateRatingBase(BaseModel):
    """Base wizard template rating schema."""
    rating: int = Field(..., ge=1, le=5)
    review_text: Optional[str] = None


class WizardTemplateRatingCreate(WizardTemplateRatingBase):
    """Schema for creating a template rating."""
    template_id: UUID


class WizardTemplateRatingUpdate(BaseModel):
    """Schema for updating a template rating."""
    rating: Optional[int] = Field(None, ge=1, le=5)
    review_text: Optional[str] = None


class WizardTemplateRatingResponse(WizardTemplateRatingBase):
    """Schema for template rating responses."""
    id: UUID
    template_id: UUID
    user_id: UUID
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "json_encoders": {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }
    }


class WizardTemplateStats(BaseModel):
    """Schema for template statistics."""
    template_id: UUID
    usage_count: int
    average_rating: Decimal
    total_ratings: int
    rating_distribution: Dict[int, int]  # {1: count, 2: count, ...}

    model_config = {
        "from_attributes": True,
        "json_encoders": {
            UUID: str,
            Decimal: float,
        }
    }


class WizardTemplateCloneRequest(BaseModel):
    """Schema for cloning a template to create a wizard."""
    template_id: UUID
    wizard_name: str = Field(..., min_length=1, max_length=255)
    wizard_description: Optional[str] = None
    customizations: Optional[Dict[str, Any]] = None  # Optional modifications to template


class WizardTemplateCloneResponse(BaseModel):
    """Schema for template clone response."""
    wizard_id: UUID
    message: str

    model_config = {
        "from_attributes": True,
        "json_encoders": {
            UUID: str,
        }
    }
