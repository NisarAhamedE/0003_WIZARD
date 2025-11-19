"""
Wizard Run Schemas

Pydantic schemas for request/response validation of wizard runs.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal


# ============================================================================
# Wizard Run Schemas
# ============================================================================

class WizardRunBase(BaseModel):
    """Base wizard run schema with common fields."""
    run_name: Optional[str] = Field(None, max_length=255)
    run_description: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None


class WizardRunCreate(BaseModel):
    """Schema for creating a new wizard run."""
    wizard_id: UUID
    run_name: Optional[str] = Field(None, max_length=255)
    run_description: Optional[str] = None


class WizardRunUpdate(BaseModel):
    """Schema for updating a wizard run."""
    run_name: Optional[str] = Field(None, max_length=255)
    run_description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(in_progress|completed|abandoned)$")
    current_step_index: Optional[int] = Field(None, ge=0)
    is_stored: Optional[bool] = None
    is_favorite: Optional[bool] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    calculated_price: Optional[Decimal] = None

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v and v not in ['in_progress', 'completed', 'abandoned']:
            raise ValueError('status must be in_progress, completed, or abandoned')
        return v


class WizardRunResponse(WizardRunBase):
    """Schema for wizard run responses."""
    id: UUID
    wizard_id: UUID
    user_id: Optional[UUID]
    status: str
    current_step_index: int
    total_steps: Optional[int]
    progress_percentage: Decimal
    started_at: datetime
    completed_at: Optional[datetime]
    last_accessed_at: datetime
    calculated_price: Optional[Decimal]
    is_stored: bool
    is_favorite: bool
    metadata: Optional[Dict[str, Any]] = Field(None, validation_alias="run_metadata", serialization_alias="metadata")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "json_encoders": {
            UUID: str,
            datetime: lambda v: v.isoformat(),
            Decimal: float,
        }
    }


class WizardRunListResponse(BaseModel):
    """Schema for paginated list of wizard runs."""
    runs: List[WizardRunResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class WizardRunCompleteRequest(BaseModel):
    """Schema for completing a wizard run."""
    run_name: Optional[str] = None
    run_description: Optional[str] = None
    save_to_store: bool = False
    tags: Optional[List[str]] = None


# ============================================================================
# Step Response Schemas
# ============================================================================

class WizardRunStepResponseBase(BaseModel):
    """Base step response schema."""
    step_id: UUID
    step_index: int
    step_name: Optional[str] = None


class WizardRunStepResponseCreate(WizardRunStepResponseBase):
    """Schema for creating a step response."""
    run_id: UUID


class WizardRunStepResponseUpdate(BaseModel):
    """Schema for updating a step response."""
    completed: Optional[bool] = None
    time_spent_seconds: Optional[int] = Field(None, ge=0)


class WizardRunStepResponseDetail(WizardRunStepResponseBase):
    """Schema for detailed step response."""
    id: UUID
    run_id: UUID
    completed: bool
    completed_at: Optional[datetime]
    time_spent_seconds: int

    model_config = {
        "from_attributes": True,
        "json_encoders": {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }
    }


# ============================================================================
# Option Set Response Schemas
# ============================================================================

class WizardRunOptionSetResponseBase(BaseModel):
    """Base option set response schema."""
    option_set_id: UUID
    option_set_name: Optional[str] = None
    selection_type: Optional[str] = None
    response_value: Dict[str, Any]  # Flexible JSONB storage
    selected_options: Optional[List[UUID]] = Field(default_factory=list)


class WizardRunOptionSetResponseCreate(WizardRunOptionSetResponseBase):
    """Schema for creating an option set response."""
    run_id: UUID
    step_response_id: UUID


class WizardRunOptionSetResponseUpdate(BaseModel):
    """Schema for updating an option set response."""
    response_value: Optional[Dict[str, Any]] = None
    selected_options: Optional[List[UUID]] = None


class WizardRunOptionSetResponseDetail(WizardRunOptionSetResponseBase):
    """Schema for detailed option set response."""
    id: UUID
    run_id: UUID
    step_response_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "json_encoders": {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }
    }


# ============================================================================
# File Upload Schemas
# ============================================================================

class WizardRunFileUploadBase(BaseModel):
    """Base file upload schema."""
    file_name: str = Field(..., max_length=255)
    file_path: str
    file_size: Optional[int] = Field(None, ge=0)
    file_type: Optional[str] = Field(None, max_length=100)


class WizardRunFileUploadCreate(WizardRunFileUploadBase):
    """Schema for creating a file upload record."""
    run_id: UUID
    option_set_response_id: UUID


class WizardRunFileUploadResponse(WizardRunFileUploadBase):
    """Schema for file upload responses."""
    id: UUID
    run_id: UUID
    option_set_response_id: UUID
    uploaded_at: datetime

    model_config = {
        "from_attributes": True,
        "json_encoders": {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }
    }


# ============================================================================
# Share Schemas
# ============================================================================

class WizardRunShareCreate(BaseModel):
    """Schema for creating a share link."""
    run_id: UUID
    share_type: str = Field(default='view', pattern="^(view|edit|clone)$")
    expires_at: Optional[datetime] = None

    @field_validator('share_type')
    @classmethod
    def validate_share_type(cls, v):
        if v not in ['view', 'edit', 'clone']:
            raise ValueError('share_type must be view, edit, or clone')
        return v


class WizardRunShareResponse(BaseModel):
    """Schema for share responses."""
    id: UUID
    run_id: UUID
    share_token: str
    shared_by: UUID
    share_type: str
    expires_at: Optional[datetime]
    created_at: datetime
    access_count: int
    last_accessed_at: Optional[datetime]
    is_active: bool

    model_config = {
        "from_attributes": True,
        "json_encoders": {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }
    }


# ============================================================================
# Comparison Schemas
# ============================================================================

class WizardRunComparisonCreate(BaseModel):
    """Schema for creating a run comparison."""
    comparison_name: Optional[str] = Field(None, max_length=255)
    run_ids: List[UUID] = Field(..., min_length=2)
    metadata: Optional[Dict[str, Any]] = None


class WizardRunComparisonResponse(BaseModel):
    """Schema for comparison responses."""
    id: UUID
    comparison_name: Optional[str]
    run_ids: List[UUID]
    created_by: UUID
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = Field(None, validation_alias="comparison_metadata", serialization_alias="metadata")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "json_encoders": {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }
    }


# ============================================================================
# Combined/Complex Schemas
# ============================================================================

class WizardRunDetailResponse(WizardRunResponse):
    """Schema for detailed wizard run with all responses."""
    step_responses: List[WizardRunStepResponseDetail] = Field(default_factory=list)
    option_set_responses: List[WizardRunOptionSetResponseDetail] = Field(default_factory=list)
    file_uploads: List[WizardRunFileUploadResponse] = Field(default_factory=list)


class WizardRunProgressUpdate(BaseModel):
    """Schema for updating wizard run progress."""
    current_step_index: int = Field(..., ge=0)
    step_responses: Optional[List[Dict[str, Any]]] = None
    option_set_responses: Optional[List[Dict[str, Any]]] = None


class WizardRunExportRequest(BaseModel):
    """Schema for exporting wizard run."""
    run_id: UUID
    format: str = Field(default='json', pattern="^(json|pdf|csv)$")
    include_metadata: bool = True
    include_files: bool = False

    @field_validator('format')
    @classmethod
    def validate_format(cls, v):
        if v not in ['json', 'pdf', 'csv']:
            raise ValueError('format must be json, pdf, or csv')
        return v


class WizardRunStats(BaseModel):
    """Schema for wizard run statistics."""
    total_runs: int
    completed_runs: int
    in_progress_runs: int
    abandoned_runs: int
    stored_runs: int
    average_completion_time: Optional[float] = None
    average_progress: float

    model_config = {
        "from_attributes": True
    }
