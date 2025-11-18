from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from enum import Enum


# Dependency Type Enum
class DependencyType(str, Enum):
    SHOW_IF = "show_if"
    HIDE_IF = "hide_if"
    REQUIRE_IF = "require_if"
    DISABLE_IF = "disable_if"


# Option Dependency Schemas
class OptionDependencyBase(BaseModel):
    depends_on_option_id: UUID
    dependency_type: DependencyType


class OptionDependencyCreate(OptionDependencyBase):
    pass


class OptionDependencyResponse(OptionDependencyBase):
    id: UUID
    option_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Category Schemas
class WizardCategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)
    display_order: int = 0


class WizardCategoryCreate(WizardCategoryBase):
    pass


class WizardCategoryResponse(WizardCategoryBase):
    id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Option Schemas
class OptionBase(BaseModel):
    label: str = Field(..., max_length=255)
    value: str = Field(..., max_length=255)
    description: Optional[str] = None
    display_order: int = 0
    icon: Optional[str] = None
    image_url: Optional[str] = None
    is_default: bool = False
    is_recommended: bool = False
    is_active: bool = True
    option_metadata: Dict[str, Any] = Field(default={}, serialization_alias="metadata")


class OptionCreate(OptionBase):
    pass


class OptionUpdate(BaseModel):
    label: Optional[str] = Field(None, max_length=255)
    value: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    display_order: Optional[int] = None
    icon: Optional[str] = None
    image_url: Optional[str] = None
    is_default: Optional[bool] = None
    is_recommended: Optional[bool] = None
    is_active: Optional[bool] = None


class OptionResponse(OptionBase):
    id: UUID
    option_set_id: UUID
    dependencies: List['OptionDependencyResponse'] = []
    created_at: datetime

    class Config:
        from_attributes = True
        by_alias = True


# OptionSet Schemas
class OptionSetBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    selection_type: str = Field(..., pattern="^(single_select|multiple_select|text_input|number_input|date_input|time_input|datetime_input|file_upload|rating|slider|color_picker|rich_text)$")
    is_required: bool = True
    min_selections: int = 0
    max_selections: Optional[int] = None
    min_value: Optional[Decimal] = None
    max_value: Optional[Decimal] = None
    regex_pattern: Optional[str] = None
    custom_validation: Dict[str, Any] = {}
    display_order: int = 0
    placeholder: Optional[str] = None
    help_text: Optional[str] = None
    step_increment: Decimal = Decimal("1")


class OptionSetCreate(OptionSetBase):
    options: List[OptionCreate] = []


class OptionSetUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    selection_type: Optional[str] = None
    is_required: Optional[bool] = None
    min_selections: Optional[int] = None
    max_selections: Optional[int] = None
    display_order: Optional[int] = None
    placeholder: Optional[str] = None
    help_text: Optional[str] = None


class OptionSetResponse(OptionSetBase):
    id: UUID
    step_id: UUID
    options: List[OptionResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


# Step Schemas
class StepBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    help_text: Optional[str] = None
    step_order: int
    is_required: bool = True
    is_skippable: bool = False
    allow_back_navigation: bool = True
    layout: str = "vertical"
    custom_styles: Dict[str, Any] = {}
    validation_rules: Dict[str, Any] = {}


class StepCreate(StepBase):
    option_sets: List[OptionSetCreate] = []


class StepUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    help_text: Optional[str] = None
    step_order: Optional[int] = None
    is_required: Optional[bool] = None
    is_skippable: Optional[bool] = None
    allow_back_navigation: Optional[bool] = None
    layout: Optional[str] = None


class StepResponse(StepBase):
    id: UUID
    wizard_id: UUID
    option_sets: List[OptionSetResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


# Wizard Schemas
class WizardBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    icon: Optional[str] = None
    cover_image: Optional[str] = None
    is_published: bool = False
    allow_templates: bool = True
    require_login: bool = True
    allow_anonymous: bool = False
    auto_save: bool = True
    auto_save_interval: int = 30
    estimated_time: Optional[int] = None
    difficulty_level: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")
    tags: List[str] = []


class WizardCreate(WizardBase):
    steps: List[StepCreate] = []


class WizardUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    icon: Optional[str] = None
    cover_image: Optional[str] = None
    is_published: Optional[bool] = None
    allow_templates: Optional[bool] = None
    require_login: Optional[bool] = None
    auto_save: Optional[bool] = None
    estimated_time: Optional[int] = None
    difficulty_level: Optional[str] = None
    tags: Optional[List[str]] = None
    steps: Optional[List["StepCreate"]] = None  # Allow updating steps


class WizardResponse(WizardBase):
    id: UUID
    created_by: UUID
    is_active: bool
    total_sessions: int
    completed_sessions: int
    average_completion_time: Optional[int] = None
    steps: List[StepResponse] = []
    category: Optional[WizardCategoryResponse] = None
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WizardListResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    cover_image: Optional[str] = None
    is_published: bool
    estimated_time: Optional[int] = None
    difficulty_level: Optional[str] = None
    tags: List[str] = []
    total_sessions: int
    completed_sessions: int
    category: Optional[WizardCategoryResponse] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Flow Rule Schemas
class FlowRuleBase(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    from_step_id: UUID
    to_step_id: UUID
    condition: Dict[str, Any]
    priority: int = 0
    is_active: bool = True


class FlowRuleCreate(FlowRuleBase):
    wizard_id: UUID


class FlowRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    from_step_id: Optional[UUID] = None
    to_step_id: Optional[UUID] = None
    condition: Optional[Dict[str, Any]] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None


class FlowRuleResponse(FlowRuleBase):
    id: UUID
    wizard_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
