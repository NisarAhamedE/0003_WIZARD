# Technical Specification - Backend Components

## Overview

This document provides detailed technical specifications for all backend components of the Wizard Action System, including models, schemas, CRUD operations, API endpoints, and services.

---

## 1. Database Models

### 1.1 WizardEvent Model

**File**: `backend/app/models/wizard_event.py`

```python
from sqlalchemy import Column, String, Boolean, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class WizardEvent(Base):
    """
    Represents an event trigger in a wizard that can execute actions.
    Events can be triggered at various points in the wizard lifecycle.
    """
    __tablename__ = "wizard_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wizard_id = Column(UUID(as_uuid=True), ForeignKey("wizards.id", ondelete="CASCADE"), nullable=False)

    # Event identification
    event_trigger = Column(String(50), nullable=False)
    event_name = Column(String(255), nullable=False)
    description = Column(Text)
    is_enabled = Column(Boolean, default=True, nullable=False)

    # Target configuration
    target_type = Column(String(50), nullable=False)  # 'step', 'option_set', 'option', 'wizard'
    target_id = Column(UUID(as_uuid=True))  # ID of the target entity

    # Conditional execution (JSONB array of conditions)
    conditions = Column(JSONB)

    # Error handling configuration (JSONB object)
    error_handling = Column(JSONB)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    wizard = relationship("Wizard", back_populates="events")
    actions = relationship(
        "WizardAction",
        back_populates="event",
        cascade="all, delete-orphan",
        order_by="WizardAction.execution_order"
    )
    execution_logs = relationship("ActionExecutionLog", back_populates="event", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            event_trigger.in_([
                'step.onEntry', 'step.onExit', 'step.onValidate',
                'optionSet.onLoad', 'optionSet.onChange', 'optionSet.onApply',
                'option.onClick', 'option.onSelect', 'option.onDeselect', 'option.onChange',
                'wizard.onStart', 'wizard.onComplete'
            ]),
            name='check_event_trigger'
        ),
        CheckConstraint(
            target_type.in_(['step', 'option_set', 'option', 'wizard']),
            name='check_target_type'
        ),
    )

    def __repr__(self):
        return f"<WizardEvent(id={self.id}, name='{self.event_name}', trigger='{self.event_trigger}')>"
```

### 1.2 WizardAction Model

**File**: `backend/app/models/wizard_action.py`

```python
from sqlalchemy import Column, String, Boolean, Text, Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class WizardAction(Base):
    """
    Represents an action that can be executed when an event is triggered.
    Actions can call APIs, execute MCP operations, transform data, etc.
    """
    __tablename__ = "wizard_actions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey("wizard_events.id", ondelete="CASCADE"), nullable=False)

    # Action identification
    action_name = Column(String(255), nullable=False)
    action_type = Column(String(50), nullable=False)
    execution_order = Column(Integer, default=1, nullable=False)
    is_async = Column(Boolean, default=True, nullable=False)

    # Action configuration (varies by action_type)
    # For api_call: { method, url, headers, body, auth, timeout_ms, response_mapping }
    # For mcp_call: { mcp_server, tool_name, parameters, mcp_config, response_format }
    # For transform_data: { transformation_type, transformation_script, output_schema }
    # For set_field_value: { target_fields, bulk_update }
    # For show_message: { message_type, message, duration_ms, position }
    config = Column(JSONB, nullable=False)

    # Input mapping (map wizard fields/context to action inputs)
    # { variable_name: { source, field_id/field/action_id } }
    input_mapping = Column(JSONB)

    # Output handling configuration
    # { display_type, target_option_set_id, config }
    output_handling = Column(JSONB)

    # Error handling
    on_error = Column(String(20), default='continue', nullable=False)
    retry_count = Column(Integer, default=0, nullable=False)

    # Loading state
    loading_message = Column(Text)
    show_loading_spinner = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    event = relationship("WizardEvent", back_populates="actions")
    execution_logs = relationship("ActionExecutionLog", back_populates="action", cascade="all, delete-orphan")
    dynamic_option_sets = relationship("DynamicOptionSet", back_populates="action")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            action_type.in_([
                'api_call', 'mcp_call', 'transform_data',
                'set_field_value', 'show_message', 'navigate', 'custom_script'
            ]),
            name='check_action_type'
        ),
        CheckConstraint(
            on_error.in_(['continue', 'stop', 'retry']),
            name='check_on_error'
        ),
    )

    def __repr__(self):
        return f"<WizardAction(id={self.id}, name='{self.action_name}', type='{self.action_type}')>"
```

### 1.3 ApiConfiguration Model

**File**: `backend/app/models/api_configuration.py`

```python
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class ApiConfiguration(Base):
    """
    Reusable API configuration for wizard actions.
    Stores base URL, authentication, headers, etc.
    """
    __tablename__ = "api_configurations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wizard_id = Column(UUID(as_uuid=True), ForeignKey("wizards.id", ondelete="CASCADE"), nullable=False)

    # Configuration details
    config_name = Column(String(255), nullable=False)
    description = Column(Text)

    # API details
    base_url = Column(Text, nullable=False)
    auth_type = Column(String(50), default='none', nullable=False)
    auth_credentials = Column(JSONB)  # Encrypted credentials
    default_headers = Column(JSONB)

    # Settings
    timeout_ms = Column(Integer, default=30000, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    wizard = relationship("Wizard", back_populates="api_configurations")
    created_by_user = relationship("User")

    def __repr__(self):
        return f"<ApiConfiguration(id={self.id}, name='{self.config_name}')>"
```

### 1.4 McpConfiguration Model

**File**: `backend/app/models/mcp_configuration.py`

```python
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class McpConfiguration(Base):
    """
    MCP (Model Context Protocol) server configuration.
    Stores server details and available tools.
    """
    __tablename__ = "mcp_configurations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wizard_id = Column(UUID(as_uuid=True), ForeignKey("wizards.id", ondelete="CASCADE"), nullable=False)

    # Configuration details
    config_name = Column(String(255), nullable=False)
    description = Column(Text)

    # MCP server details
    mcp_server = Column(String(255), nullable=False)
    available_tools = Column(JSONB)  # Array of { tool_name, schema, description }

    # Settings
    timeout_ms = Column(Integer, default=30000, nullable=False)
    max_retries = Column(Integer, default=2, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    wizard = relationship("Wizard", back_populates="mcp_configurations")
    created_by_user = relationship("User")

    def __repr__(self):
        return f"<McpConfiguration(id={self.id}, name='{self.config_name}', server='{self.mcp_server}')>"
```

### 1.5 ActionExecutionLog Model

**File**: `backend/app/models/action_execution_log.py`

```python
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class ActionExecutionLog(Base):
    """
    Logs execution details for actions during wizard runs.
    Used for debugging, analytics, and audit trails.
    """
    __tablename__ = "action_execution_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), ForeignKey("wizard_runs.id", ondelete="CASCADE"), nullable=False)
    action_id = Column(UUID(as_uuid=True), ForeignKey("wizard_actions.id", ondelete="CASCADE"), nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey("wizard_events.id", ondelete="CASCADE"), nullable=False)

    # Execution timing
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)
    duration_ms = Column(Integer)

    # Status
    status = Column(String(20), nullable=False)  # 'success', 'error', 'skipped'

    # Input/Output data
    input_data = Column(JSONB)
    output_data = Column(JSONB)
    error_message = Column(Text)
    error_stack = Column(Text)

    # Retry tracking
    retry_attempt = Column(Integer, default=0, nullable=False)

    # Relationships
    run = relationship("WizardRun", back_populates="action_logs")
    action = relationship("WizardAction", back_populates="execution_logs")
    event = relationship("WizardEvent", back_populates="execution_logs")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            status.in_(['success', 'error', 'skipped']),
            name='check_status'
        ),
    )

    def __repr__(self):
        return f"<ActionExecutionLog(id={self.id}, status='{self.status}', action_id={self.action_id})>"
```

### 1.6 DynamicOptionSet Model

**File**: `backend/app/models/dynamic_option_set.py`

```python
from sqlalchemy import Column, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class DynamicOptionSet(Base):
    """
    Option sets created dynamically by actions.
    Used to display API/MCP response data in various formats.
    """
    __tablename__ = "dynamic_option_sets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wizard_id = Column(UUID(as_uuid=True), ForeignKey("wizards.id", ondelete="CASCADE"), nullable=False)
    step_id = Column(UUID(as_uuid=True), ForeignKey("wizard_steps.id", ondelete="CASCADE"), nullable=False)
    action_id = Column(UUID(as_uuid=True), ForeignKey("wizard_actions.id", ondelete="CASCADE"), nullable=False)

    # Option set properties
    name = Column(String(255), nullable=False)
    selection_type = Column(String(50), default='dynamic_table', nullable=False)

    # Display configuration
    display_config = Column(JSONB, nullable=False)

    # Data source
    data_source = Column(String(50))  # 'api_response', 'mcp_response', 'transform_result'
    data_source_action_id = Column(UUID(as_uuid=True), ForeignKey("wizard_actions.id"))

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    wizard = relationship("Wizard")
    step = relationship("WizardStep")
    action = relationship("WizardAction", foreign_keys=[action_id], back_populates="dynamic_option_sets")
    source_action = relationship("WizardAction", foreign_keys=[data_source_action_id])

    # Constraints
    __table_args__ = (
        CheckConstraint(
            selection_type.in_([
                'dynamic_table', 'dynamic_dropdown', 'dynamic_card_grid',
                'dynamic_list', 'dynamic_document', 'dynamic_image',
                'dynamic_code', 'dynamic_json', 'dynamic_chart'
            ]),
            name='check_selection_type'
        ),
    )

    def __repr__(self):
        return f"<DynamicOptionSet(id={self.id}, name='{self.name}', type='{self.selection_type}')>"
```

---

## 2. Pydantic Schemas

### 2.1 WizardEvent Schemas

**File**: `backend/app/schemas/wizard_event.py`

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

# Event Condition
class EventCondition(BaseModel):
    field_id: str = Field(..., description="Field ID to check")
    operator: str = Field(..., pattern="^(equals|not_equals|contains|greater_than|less_than|is_empty|is_not_empty)$")
    value: Any = Field(None, description="Value to compare against")
    logic: str = Field(default="AND", pattern="^(AND|OR)$")

# Error Handling Config
class ErrorHandlingConfig(BaseModel):
    on_error: str = Field(default="continue", pattern="^(continue|stop|retry)$")
    retry_count: Optional[int] = Field(default=0, ge=0, le=5)
    retry_delay_ms: Optional[int] = Field(default=1000, ge=0, le=10000)
    show_error_to_user: bool = Field(default=True)
    log_errors: bool = Field(default=True)

# Base schema
class WizardEventBase(BaseModel):
    event_trigger: str = Field(..., description="Event trigger point")
    event_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_enabled: bool = Field(default=True)
    target_type: str = Field(..., pattern="^(step|option_set|option|wizard)$")
    target_id: Optional[UUID] = None
    conditions: Optional[List[EventCondition]] = None
    error_handling: Optional[ErrorHandlingConfig] = None

    @field_validator('event_trigger')
    @classmethod
    def validate_event_trigger(cls, v):
        valid_triggers = [
            'step.onEntry', 'step.onExit', 'step.onValidate',
            'optionSet.onLoad', 'optionSet.onChange', 'optionSet.onApply',
            'option.onClick', 'option.onSelect', 'option.onDeselect', 'option.onChange',
            'wizard.onStart', 'wizard.onComplete'
        ]
        if v not in valid_triggers:
            raise ValueError(f"Invalid event trigger. Must be one of: {', '.join(valid_triggers)}")
        return v

# Create schema
class WizardEventCreate(WizardEventBase):
    wizard_id: UUID

# Update schema
class WizardEventUpdate(BaseModel):
    event_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_enabled: Optional[bool] = None
    conditions: Optional[List[EventCondition]] = None
    error_handling: Optional[ErrorHandlingConfig] = None

# Response schema
class WizardEvent(WizardEventBase):
    id: UUID
    wizard_id: UUID
    created_at: datetime
    updated_at: datetime
    actions: List["WizardAction"] = []

    class Config:
        from_attributes = True

# List response
class WizardEventList(BaseModel):
    events: List[WizardEvent]
    total: int
```

### 2.2 WizardAction Schemas

**File**: `backend/app/schemas/wizard_action.py`

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

# Input Mapping
class InputMappingConfig(BaseModel):
    source: str = Field(..., pattern="^(option_set|context|action_output|static|event_data)$")
    field_id: Optional[str] = None
    field: Optional[str] = None  # For context/event_data
    action_id: Optional[UUID] = None  # For action_output
    value: Optional[Any] = None  # For static

# Output Handling Config
class OutputHandlingConfig(BaseModel):
    display_type: str = Field(
        ...,
        pattern="^(table|dropdown|card_grid|list|document|image|code|json|chart|custom|hidden)$"
    )
    target_option_set_id: Optional[UUID] = None
    config: Optional[Dict[str, Any]] = None

# Base schema
class WizardActionBase(BaseModel):
    action_name: str = Field(..., min_length=1, max_length=255)
    action_type: str = Field(..., pattern="^(api_call|mcp_call|transform_data|set_field_value|show_message|navigate|custom_script)$")
    execution_order: int = Field(default=1, ge=1)
    is_async: bool = Field(default=True)
    config: Dict[str, Any] = Field(..., description="Action-specific configuration")
    input_mapping: Optional[Dict[str, InputMappingConfig]] = None
    output_handling: Optional[OutputHandlingConfig] = None
    on_error: str = Field(default="continue", pattern="^(continue|stop|retry)$")
    retry_count: int = Field(default=0, ge=0, le=5)
    loading_message: Optional[str] = None
    show_loading_spinner: bool = Field(default=True)

# Create schema
class WizardActionCreate(WizardActionBase):
    event_id: UUID

# Update schema
class WizardActionUpdate(BaseModel):
    action_name: Optional[str] = Field(None, min_length=1, max_length=255)
    execution_order: Optional[int] = Field(None, ge=1)
    is_async: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None
    input_mapping: Optional[Dict[str, InputMappingConfig]] = None
    output_handling: Optional[OutputHandlingConfig] = None
    on_error: Optional[str] = Field(None, pattern="^(continue|stop|retry)$")
    retry_count: Optional[int] = Field(None, ge=0, le=5)
    loading_message: Optional[str] = None
    show_loading_spinner: Optional[bool] = None

# Response schema
class WizardAction(WizardActionBase):
    id: UUID
    event_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# List response
class WizardActionList(BaseModel):
    actions: List[WizardAction]
    total: int

# Reorder request
class WizardActionReorder(BaseModel):
    action_orders: Dict[UUID, int] = Field(..., description="Map of action_id to new execution_order")
```

---

## 3. CRUD Operations

### 3.1 WizardEvent CRUD

**File**: `backend/app/crud/wizard_event.py`

```python
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.models.wizard_event import WizardEvent
from app.schemas.wizard_event import WizardEventCreate, WizardEventUpdate

class CRUDWizardEvent:
    def create(self, db: Session, obj_in: WizardEventCreate) -> WizardEvent:
        """Create a new wizard event"""
        db_obj = WizardEvent(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, event_id: UUID) -> Optional[WizardEvent]:
        """Get event by ID"""
        return db.query(WizardEvent).filter(WizardEvent.id == event_id).first()

    def get_by_wizard(self, db: Session, wizard_id: UUID) -> List[WizardEvent]:
        """Get all events for a wizard"""
        return db.query(WizardEvent)\
            .filter(WizardEvent.wizard_id == wizard_id)\
            .order_by(WizardEvent.created_at)\
            .all()

    def get_by_trigger(
        self,
        db: Session,
        wizard_id: UUID,
        trigger: str,
        target_id: Optional[UUID] = None
    ) -> List[WizardEvent]:
        """Get events by trigger type and optional target"""
        query = db.query(WizardEvent)\
            .filter(
                WizardEvent.wizard_id == wizard_id,
                WizardEvent.event_trigger == trigger,
                WizardEvent.is_enabled == True
            )

        if target_id:
            query = query.filter(WizardEvent.target_id == target_id)

        return query.all()

    def update(self, db: Session, event_id: UUID, obj_in: WizardEventUpdate) -> Optional[WizardEvent]:
        """Update event"""
        db_obj = self.get(db, event_id)
        if not db_obj:
            return None

        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, event_id: UUID) -> bool:
        """Delete event"""
        db_obj = self.get(db, event_id)
        if not db_obj:
            return False

        db.delete(db_obj)
        db.commit()
        return True

    def toggle_enabled(self, db: Session, event_id: UUID) -> Optional[WizardEvent]:
        """Toggle event enabled status"""
        db_obj = self.get(db, event_id)
        if not db_obj:
            return None

        db_obj.is_enabled = not db_obj.is_enabled
        db.commit()
        db.refresh(db_obj)
        return db_obj

wizard_event = CRUDWizardEvent()
```

### 3.2 WizardAction CRUD

**File**: `backend/app/crud/wizard_action.py`

```python
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from uuid import UUID
from app.models.wizard_action import WizardAction
from app.schemas.wizard_action import WizardActionCreate, WizardActionUpdate

class CRUDWizardAction:
    def create(self, db: Session, obj_in: WizardActionCreate) -> WizardAction:
        """Create a new action"""
        db_obj = WizardAction(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, action_id: UUID) -> Optional[WizardAction]:
        """Get action by ID"""
        return db.query(WizardAction).filter(WizardAction.id == action_id).first()

    def get_by_event(self, db: Session, event_id: UUID) -> List[WizardAction]:
        """Get all actions for an event, ordered by execution_order"""
        return db.query(WizardAction)\
            .filter(WizardAction.event_id == event_id)\
            .order_by(WizardAction.execution_order)\
            .all()

    def update(self, db: Session, action_id: UUID, obj_in: WizardActionUpdate) -> Optional[WizardAction]:
        """Update action"""
        db_obj = self.get(db, action_id)
        if not db_obj:
            return None

        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, action_id: UUID) -> bool:
        """Delete action"""
        db_obj = self.get(db, action_id)
        if not db_obj:
            return False

        db.delete(db_obj)
        db.commit()
        return True

    def reorder(self, db: Session, action_orders: Dict[UUID, int]) -> List[WizardAction]:
        """Reorder actions"""
        actions = []
        for action_id, order in action_orders.items():
            db_obj = self.get(db, action_id)
            if db_obj:
                db_obj.execution_order = order
                actions.append(db_obj)

        db.commit()
        for action in actions:
            db.refresh(action)

        return sorted(actions, key=lambda a: a.execution_order)

wizard_action = CRUDWizardAction()
```

---

## 4. Service Layer

### 4.1 Action Executor Service

**File**: `backend/app/services/action_executor.py`

```python
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from uuid import UUID
import json
from datetime import datetime

from app.models.wizard_action import WizardAction
from app.models.wizard_event import WizardEvent
from app.models.action_execution_log import ActionExecutionLog
from app.services.api_caller import ApiCaller
from app.services.mcp_caller import McpCaller
from app.services.data_transformer import DataTransformer

class ActionExecutor:
    """
    Executes wizard actions based on event triggers.
    Handles action sequencing, input mapping, output handling, and error management.
    """

    def __init__(self, db: Session, run_id: UUID):
        self.db = db
        self.run_id = run_id
        self.action_results: Dict[UUID, Any] = {}
        self.api_caller = ApiCaller()
        self.mcp_caller = McpCaller()
        self.data_transformer = DataTransformer()

    async def execute_event(self, event: WizardEvent, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute all actions for an event.

        Args:
            event: WizardEvent to execute
            context: Execution context (step data, user selections, etc.)

        Returns:
            Dict with execution results
        """
        # Check if event should execute based on conditions
        if not self._should_execute_event(event, context):
            return {"skipped": True, "reason": "conditions not met"}

        results = []

        # Execute actions in order
        for action in sorted(event.actions, key=lambda a: a.execution_order):
            result = await self._execute_action(action, context)
            results.append(result)

            # Handle errors
            if not result["success"]:
                if action.on_error == "stop":
                    break
                elif action.on_error == "retry":
                    result = await self._retry_action(action, context)
                    results[-1] = result

        return {
            "success": all(r["success"] for r in results),
            "results": results
        }

    async def _execute_action(self, action: WizardAction, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single action"""
        start_time = datetime.utcnow()

        try:
            # Resolve input values
            input_values = self._resolve_input_mapping(action.input_mapping, context)

            # Execute based on action type
            if action.action_type == "api_call":
                result = await self.api_caller.execute(action.config, input_values)
            elif action.action_type == "mcp_call":
                result = await self.mcp_caller.execute(action.config, input_values)
            elif action.action_type == "transform_data":
                result = self.data_transformer.execute(action.config, input_values)
            elif action.action_type == "set_field_value":
                result = await self._execute_set_field_value(action.config, input_values)
            elif action.action_type == "show_message":
                result = {"message": action.config.get("message"), "type": action.config.get("message_type")}
            else:
                raise ValueError(f"Unknown action type: {action.action_type}")

            # Store result for downstream actions
            self.action_results[action.id] = result

            # Log success
            self._log_execution(action, input_values, result, "success", start_time)

            return {"success": True, "data": result}

        except Exception as e:
            # Log error
            self._log_execution(action, input_values, None, "error", start_time, str(e))

            return {"success": False, "error": str(e)}

    def _resolve_input_mapping(self, input_mapping: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve input mapping from various sources"""
        if not input_mapping:
            return {}

        resolved = {}

        for key, mapping_config in input_mapping.items():
            source = mapping_config.get("source")

            if source == "option_set":
                field_id = mapping_config.get("field_id")
                resolved[key] = context.get("responses", {}).get(field_id)

            elif source == "context":
                field = mapping_config.get("field")
                resolved[key] = self._get_nested_value(context, field)

            elif source == "action_output":
                action_id = UUID(mapping_config.get("action_id"))
                resolved[key] = self.action_results.get(action_id)

            elif source == "static":
                resolved[key] = mapping_config.get("value")

            elif source == "event_data":
                field = mapping_config.get("field")
                resolved[key] = context.get(field)

        return resolved

    def _should_execute_event(self, event: WizardEvent, context: Dict[str, Any]) -> bool:
        """Check if event conditions are met"""
        if not event.conditions:
            return True

        # Implement condition checking logic
        # AND/OR logic based on condition.logic
        return True

    def _get_nested_value(self, obj: Dict[str, Any], path: str) -> Any:
        """Get nested value from dict using dot notation"""
        keys = path.split('.')
        value = obj
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value

    def _log_execution(
        self,
        action: WizardAction,
        input_data: Dict[str, Any],
        output_data: Any,
        status: str,
        start_time: datetime,
        error_message: str = None
    ):
        """Log action execution"""
        end_time = datetime.utcnow()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)

        log = ActionExecutionLog(
            run_id=self.run_id,
            action_id=action.id,
            event_id=action.event_id,
            started_at=start_time,
            completed_at=end_time,
            duration_ms=duration_ms,
            status=status,
            input_data=input_data,
            output_data=output_data,
            error_message=error_message
        )

        self.db.add(log)
        self.db.commit()
```

---

**Document Status**: Part 1 - Models, Schemas, CRUD, and Core Services
**Next Document**: Technical Spec - Frontend Components
