# Implementation Plan - Wizard Action System Integration

## Executive Summary

This document provides a comprehensive implementation plan for integrating the **Complete Wizard Action System** into the existing Multi-Wizard Platform. The action system will transform the platform from a static form builder into a dynamic, interactive application platform capable of:

- **API Integration**: Call external REST APIs with full configuration
- **MCP Operations**: Execute Model Context Protocol operations for database/tool interactions
- **Data Transformation**: Process and transform data using JavaScript/JMESPath
- **Dynamic Field Population**: Auto-populate fields based on API/MCP responses
- **Rich Output Displays**: Render data in tables, cards, charts, images, documents, and more
- **Event-Driven Architecture**: Trigger actions based on user interactions and wizard lifecycle events

---

## Current System Analysis

### Existing Architecture Strengths

✅ **Complete Wizard Lifecycle System**
- Template Gallery with cloning capability
- Wizard Builder with 12 selection types
- Run Wizard execution engine
- My Runs tracking system
- Store for saved runs

✅ **Robust Technology Stack**
- Backend: FastAPI + PostgreSQL + SQLAlchemy
- Frontend: React + TypeScript + MUI
- Authentication: JWT with role-based access
- State Management: React Query

✅ **12 Selection Types Already Implemented**
- single_select, multiple_select, text_input, number_input
- date_input, time_input, datetime_input
- rating, slider, color_picker, file_upload, rich_text

✅ **Conditional Dependencies Working**
- disable_if, require_if, show_if, hide_if

### Integration Points

The action system will integrate seamlessly with:

1. **Wizard Builder** - Add event/action configuration UI
2. **Wizard Player** - Execute actions during wizard runs
3. **Database Schema** - Add new tables for events, actions, configurations
4. **API Layer** - Add endpoints for event/action management
5. **Frontend Services** - Add action execution engine

---

## System Architecture Overview

### Event-Driven Architecture

```
Wizard Event Triggers
    ↓
Event Conditions Check
    ↓
Action Execution Engine
    ↓
    ├─→ API Call Actions
    ├─→ MCP Call Actions
    ├─→ Transform Data Actions
    ├─→ Set Field Value Actions
    ├─→ Show Message Actions
    └─→ Custom Script Actions
    ↓
Output Renderers
    ↓
    ├─→ Table Renderer
    ├─→ Dropdown Renderer
    ├─→ Card Grid Renderer
    ├─→ Document Renderer
    ├─→ Image Renderer
    ├─→ Code Renderer
    ├─→ Chart Renderer
    └─→ JSON Renderer
```

### Event Trigger Points

**12 Event Triggers Available:**

1. **Step Events** (3)
   - `step.onEntry` - When user enters a step
   - `step.onExit` - Before moving to next step
   - `step.onValidate` - During validation

2. **Option Set Events** (3)
   - `optionSet.onLoad` - When option set is rendered
   - `optionSet.onChange` - When any value changes
   - `optionSet.onApply` - Apply button clicked

3. **Option Events** (4)
   - `option.onClick` - When option is clicked
   - `option.onSelect` - When option is selected
   - `option.onDeselect` - When option is deselected
   - `option.onChange` - When value changes (for inputs)

4. **Global Events** (2)
   - `wizard.onStart` - When wizard execution starts
   - `wizard.onComplete` - When wizard completes

### Action Types

**7 Action Types:**

1. **api_call** - Call external REST APIs
2. **mcp_call** - Execute MCP operations
3. **transform_data** - Transform data using JavaScript/JMESPath
4. **set_field_value** - Update field values
5. **show_message** - Display notifications
6. **navigate** - Navigate between steps
7. **custom_script** - Run custom JavaScript

---

## Database Schema Changes

### New Tables Required (6 tables)

#### 1. wizard_events
```sql
CREATE TABLE wizard_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wizard_id UUID REFERENCES wizards(id) ON DELETE CASCADE,
    event_trigger VARCHAR(50) NOT NULL,
    event_name VARCHAR(255) NOT NULL,
    description TEXT,
    is_enabled BOOLEAN DEFAULT TRUE,

    -- Target configuration
    target_type VARCHAR(50) NOT NULL,
    target_id UUID,

    -- Conditional execution
    conditions JSONB,

    -- Error handling
    error_handling JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. wizard_actions
```sql
CREATE TABLE wizard_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID REFERENCES wizard_events(id) ON DELETE CASCADE,
    action_name VARCHAR(255) NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    execution_order INTEGER DEFAULT 1,
    is_async BOOLEAN DEFAULT TRUE,

    -- Action configuration (varies by type)
    config JSONB NOT NULL,

    -- Input mapping
    input_mapping JSONB,

    -- Output handling
    output_handling JSONB,

    -- Error handling
    on_error VARCHAR(20) DEFAULT 'continue',
    retry_count INTEGER DEFAULT 0,

    -- Loading state
    loading_message TEXT,
    show_loading_spinner BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. api_configurations
```sql
CREATE TABLE api_configurations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wizard_id UUID REFERENCES wizards(id) ON DELETE CASCADE,
    config_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- API details
    base_url TEXT NOT NULL,
    auth_type VARCHAR(50) DEFAULT 'none',
    auth_credentials JSONB,
    default_headers JSONB,

    -- Settings
    timeout_ms INTEGER DEFAULT 30000,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);
```

#### 4. mcp_configurations
```sql
CREATE TABLE mcp_configurations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wizard_id UUID REFERENCES wizards(id) ON DELETE CASCADE,
    config_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- MCP server details
    mcp_server VARCHAR(255) NOT NULL,
    available_tools JSONB,

    -- Settings
    timeout_ms INTEGER DEFAULT 30000,
    max_retries INTEGER DEFAULT 2,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);
```

#### 5. action_execution_logs
```sql
CREATE TABLE action_execution_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id UUID REFERENCES wizard_runs(id) ON DELETE CASCADE,
    action_id UUID REFERENCES wizard_actions(id) ON DELETE CASCADE,
    event_id UUID REFERENCES wizard_events(id) ON DELETE CASCADE,

    -- Execution details
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_ms INTEGER,

    -- Status
    status VARCHAR(20) NOT NULL,

    -- Input/Output
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    error_stack TEXT,

    -- Retry tracking
    retry_attempt INTEGER DEFAULT 0
);
```

#### 6. dynamic_option_sets
```sql
CREATE TABLE dynamic_option_sets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wizard_id UUID REFERENCES wizards(id) ON DELETE CASCADE,
    step_id UUID REFERENCES wizard_steps(id) ON DELETE CASCADE,
    action_id UUID REFERENCES wizard_actions(id) ON DELETE CASCADE,

    -- Option set properties
    name VARCHAR(255) NOT NULL,
    selection_type VARCHAR(50) DEFAULT 'dynamic_table',

    -- Display configuration
    display_config JSONB NOT NULL,

    -- Data source
    data_source VARCHAR(50),
    data_source_action_id UUID REFERENCES wizard_actions(id),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Migration Strategy

1. **Create migration script**: `alembic revision --autogenerate -m "add_wizard_action_system"`
2. **Test in development**: Apply migration to dev database
3. **Backup production**: Before applying to production
4. **Apply migration**: `alembic upgrade head`

---

## Backend Implementation Plan

### Phase 1: Models & Schemas (Week 1)

#### 1.1 SQLAlchemy Models

**Files to Create:**
- `backend/app/models/wizard_event.py`
- `backend/app/models/wizard_action.py`
- `backend/app/models/api_configuration.py`
- `backend/app/models/mcp_configuration.py`
- `backend/app/models/action_execution_log.py`
- `backend/app/models/dynamic_option_set.py`

**Key Implementation:**
```python
# backend/app/models/wizard_event.py
class WizardEvent(Base):
    __tablename__ = "wizard_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wizard_id = Column(UUID(as_uuid=True), ForeignKey("wizards.id", ondelete="CASCADE"))
    event_trigger = Column(String(50), nullable=False)
    event_name = Column(String(255), nullable=False)
    description = Column(Text)
    is_enabled = Column(Boolean, default=True)

    target_type = Column(String(50), nullable=False)
    target_id = Column(UUID(as_uuid=True))

    conditions = Column(JSONB)
    error_handling = Column(JSONB)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    wizard = relationship("Wizard", back_populates="events")
    actions = relationship("WizardAction", back_populates="event", cascade="all, delete-orphan")
```

#### 1.2 Pydantic Schemas

**Files to Create:**
- `backend/app/schemas/wizard_event.py`
- `backend/app/schemas/wizard_action.py`
- `backend/app/schemas/api_configuration.py`
- `backend/app/schemas/mcp_configuration.py`

**Key Implementation:**
```python
# backend/app/schemas/wizard_event.py
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class WizardEventBase(BaseModel):
    event_trigger: str = Field(..., pattern="^(step|optionSet|option|wizard)\\.(on[A-Z][a-z]+)$")
    event_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_enabled: bool = True
    target_type: str = Field(..., pattern="^(step|option_set|option|wizard)$")
    target_id: Optional[UUID] = None
    conditions: Optional[dict] = None
    error_handling: Optional[dict] = None

class WizardEventCreate(WizardEventBase):
    wizard_id: UUID

class WizardEventUpdate(BaseModel):
    event_name: Optional[str] = None
    description: Optional[str] = None
    is_enabled: Optional[bool] = None
    conditions: Optional[dict] = None
    error_handling: Optional[dict] = None

class WizardEvent(WizardEventBase):
    id: UUID
    wizard_id: UUID
    created_at: datetime
    updated_at: datetime
    actions: List["WizardAction"] = []

    class Config:
        from_attributes = True
```

### Phase 2: CRUD Operations (Week 1-2)

**Files to Create:**
- `backend/app/crud/wizard_event.py`
- `backend/app/crud/wizard_action.py`
- `backend/app/crud/api_configuration.py`
- `backend/app/crud/mcp_configuration.py`

**Key Operations:**
- Create/Read/Update/Delete for all entities
- Get events by wizard ID
- Get events by target (step/option_set/option)
- Get actions by event ID
- Reorder actions
- Test API/MCP configurations

### Phase 3: API Endpoints (Week 2)

**Files to Create:**
- `backend/app/api/v1/wizard_events.py`
- `backend/app/api/v1/wizard_actions.py`
- `backend/app/api/v1/api_configurations.py`
- `backend/app/api/v1/mcp_configurations.py`

**Endpoints to Create:**
```python
# Events
POST   /api/v1/wizards/{wizard_id}/events
GET    /api/v1/wizards/{wizard_id}/events
GET    /api/v1/wizards/events/{event_id}
PUT    /api/v1/wizards/events/{event_id}
DELETE /api/v1/wizards/events/{event_id}

# Actions
GET    /api/v1/wizards/events/{event_id}/actions
POST   /api/v1/wizards/events/{event_id}/actions
PUT    /api/v1/wizards/events/{event_id}/actions/{action_id}
DELETE /api/v1/wizards/events/{event_id}/actions/{action_id}
POST   /api/v1/wizards/events/{event_id}/actions/reorder

# Testing
POST   /api/v1/wizards/actions/test
POST   /api/v1/wizards/actions/{action_id}/test

# API Configurations
POST   /api/v1/wizards/{wizard_id}/api-configs
GET    /api/v1/wizards/{wizard_id}/api-configs
GET    /api/v1/wizards/api-configs/{config_id}
PUT    /api/v1/wizards/api-configs/{config_id}
DELETE /api/v1/wizards/api-configs/{config_id}
POST   /api/v1/wizards/api-configs/{config_id}/test

# MCP Configurations
POST   /api/v1/wizards/{wizard_id}/mcp-configs
GET    /api/v1/wizards/{wizard_id}/mcp-configs
GET    /api/v1/wizards/mcp-configs/{config_id}
PUT    /api/v1/wizards/mcp-configs/{config_id}
DELETE /api/v1/wizards/mcp-configs/{config_id}
GET    /api/v1/mcp/servers
GET    /api/v1/mcp/servers/{server}/tools

# Runtime Execution
POST   /api/v1/wizard-runs/{run_id}/execute-event
GET    /api/v1/wizard-runs/{run_id}/action-logs
GET    /api/v1/wizard-runs/{run_id}/action-logs/{log_id}
```

### Phase 4: Action Execution Engine (Week 3)

**Files to Create:**
- `backend/app/services/action_executor.py`
- `backend/app/services/api_caller.py`
- `backend/app/services/mcp_caller.py`
- `backend/app/services/data_transformer.py`

**Key Implementation:**
```python
# backend/app/services/action_executor.py
class ActionExecutor:
    def __init__(self, db: Session, run_id: UUID):
        self.db = db
        self.run_id = run_id
        self.action_results = {}

    async def execute_event(self, event: WizardEvent, context: dict):
        """Execute all actions for an event"""
        if not self.should_execute_event(event, context):
            return {"skipped": True, "reason": "conditions not met"}

        results = []
        for action in sorted(event.actions, key=lambda a: a.execution_order):
            result = await self.execute_action(action, context)
            results.append(result)

            if not result["success"] and action.on_error == "stop":
                break

        return {"success": True, "results": results}

    async def execute_action(self, action: WizardAction, context: dict):
        """Execute a single action"""
        try:
            # Resolve input values
            input_values = self.resolve_input_mapping(action.input_mapping, context)

            # Execute based on action type
            if action.action_type == "api_call":
                result = await self.execute_api_call(action, input_values)
            elif action.action_type == "mcp_call":
                result = await self.execute_mcp_call(action, input_values)
            elif action.action_type == "transform_data":
                result = self.execute_transform(action, input_values)
            elif action.action_type == "set_field_value":
                result = await self.execute_set_field_value(action, input_values)
            elif action.action_type == "show_message":
                result = self.execute_show_message(action, input_values)
            else:
                raise ValueError(f"Unknown action type: {action.action_type}")

            # Store result for downstream actions
            self.action_results[action.id] = result

            # Handle output
            await self.handle_output(action, result)

            # Log execution
            await self.log_execution(action, input_values, result, "success")

            return {"success": True, "data": result}

        except Exception as e:
            await self.log_execution(action, input_values, None, "error", str(e))

            if action.on_error == "retry" and action.retry_count > 0:
                return await self.retry_action(action, context)

            return {"success": False, "error": str(e)}
```

---

## Frontend Implementation Plan

### Phase 5: TypeScript Types (Week 3)

**Files to Create:**
- `frontend/src/types/wizardEvent.types.ts`
- `frontend/src/types/wizardAction.types.ts`
- `frontend/src/types/apiConfiguration.types.ts`
- `frontend/src/types/mcpConfiguration.types.ts`

**Key Types:**
```typescript
// frontend/src/types/wizardEvent.types.ts
export enum EventTrigger {
  STEP_ON_ENTRY = 'step.onEntry',
  STEP_ON_EXIT = 'step.onExit',
  STEP_ON_VALIDATE = 'step.onValidate',
  OPTIONSET_ON_LOAD = 'optionSet.onLoad',
  OPTIONSET_ON_CHANGE = 'optionSet.onChange',
  OPTIONSET_ON_APPLY = 'optionSet.onApply',
  OPTION_ON_CLICK = 'option.onClick',
  OPTION_ON_SELECT = 'option.onSelect',
  OPTION_ON_DESELECT = 'option.onDeselect',
  OPTION_ON_CHANGE = 'option.onChange',
  WIZARD_ON_START = 'wizard.onStart',
  WIZARD_ON_COMPLETE = 'wizard.onComplete'
}

export interface WizardEvent {
  id: string;
  wizard_id: string;
  event_trigger: EventTrigger;
  event_name: string;
  description?: string;
  is_enabled: boolean;
  target_type: 'step' | 'option_set' | 'option' | 'wizard';
  target_id?: string;
  conditions?: EventCondition[];
  error_handling?: ErrorHandlingConfig;
  actions: WizardAction[];
  created_at: string;
  updated_at: string;
}

export enum ActionType {
  API_CALL = 'api_call',
  MCP_CALL = 'mcp_call',
  TRANSFORM_DATA = 'transform_data',
  SET_FIELD_VALUE = 'set_field_value',
  SHOW_MESSAGE = 'show_message',
  NAVIGATE = 'navigate',
  CUSTOM_SCRIPT = 'custom_script'
}

export interface WizardAction {
  id: string;
  event_id: string;
  action_name: string;
  action_type: ActionType;
  execution_order: number;
  is_async: boolean;
  config: ActionConfig;
  input_mapping?: InputMapping;
  output_handling?: OutputHandling;
  on_error: 'continue' | 'stop' | 'retry';
  retry_count?: number;
  loading_message?: string;
  show_loading_spinner: boolean;
  created_at: string;
  updated_at: string;
}
```

### Phase 6: Services (Week 4)

**Files to Create:**
- `frontend/src/services/wizardEvent.service.ts`
- `frontend/src/services/wizardAction.service.ts`
- `frontend/src/services/apiConfiguration.service.ts`
- `frontend/src/services/mcpConfiguration.service.ts`
- `frontend/src/services/actionExecutor.service.ts`

**Key Service Methods:**
```typescript
// frontend/src/services/wizardEvent.service.ts
export const wizardEventService = {
  // Get all events for a wizard
  getWizardEvents: async (wizardId: string): Promise<WizardEvent[]> => {
    const response = await api.get(`/wizards/${wizardId}/events`);
    return response.data;
  },

  // Create event
  createEvent: async (event: WizardEventCreate): Promise<WizardEvent> => {
    const response = await api.post(`/wizards/${event.wizard_id}/events`, event);
    return response.data;
  },

  // Update event
  updateEvent: async (eventId: string, event: WizardEventUpdate): Promise<WizardEvent> => {
    const response = await api.put(`/wizards/events/${eventId}`, event);
    return response.data;
  },

  // Delete event
  deleteEvent: async (eventId: string): Promise<void> => {
    await api.delete(`/wizards/events/${eventId}`);
  }
};
```

### Phase 7: Action Executor Engine (Week 4-5)

**Files to Create:**
- `frontend/src/lib/ActionExecutor.ts`
- `frontend/src/lib/TemplateEngine.ts`
- `frontend/src/lib/JSONPathExtractor.ts`

**Key Implementation:**
```typescript
// frontend/src/lib/ActionExecutor.ts
export class ActionExecutor {
  private context: WizardExecutionContext;
  private actionResults: Map<string, any> = new Map();

  constructor(context: WizardExecutionContext) {
    this.context = context;
  }

  async executeActions(actions: WizardAction[], eventData: any): Promise<ActionExecutionResult> {
    const results: ActionResult[] = [];

    // Sort by execution order
    const sortedActions = [...actions].sort((a, b) => a.execution_order - b.execution_order);

    for (const action of sortedActions) {
      try {
        // Show loading
        if (action.show_loading_spinner) {
          this.showLoading(action);
        }

        // Resolve inputs
        const inputValues = this.resolveInputMapping(action.input_mapping, eventData);

        // Execute action
        const result = await this.executeAction(action, inputValues);

        // Store result
        this.actionResults.set(action.id, result);

        // Handle output
        await this.handleOutput(action, result);

        results.push({ action_id: action.id, success: true, data: result });

      } catch (error) {
        results.push({ action_id: action.id, success: false, error: error.message });

        if (action.on_error === 'stop') {
          break;
        }
      } finally {
        this.hideLoading(action);
      }
    }

    return {
      success: results.every(r => r.success),
      results
    };
  }

  private async executeAction(action: WizardAction, inputValues: Record<string, any>): Promise<any> {
    switch (action.action_type) {
      case ActionType.API_CALL:
        return this.executeApiCall(action, inputValues);
      case ActionType.MCP_CALL:
        return this.executeMcpCall(action, inputValues);
      case ActionType.TRANSFORM_DATA:
        return this.executeTransform(action, inputValues);
      case ActionType.SET_FIELD_VALUE:
        return this.executeSetFieldValue(action, inputValues);
      case ActionType.SHOW_MESSAGE:
        return this.executeShowMessage(action, inputValues);
      default:
        throw new Error(`Unknown action type: ${action.action_type}`);
    }
  }

  private async executeApiCall(action: WizardAction, inputValues: Record<string, any>): Promise<any> {
    const config = action.config as ApiCallActionConfig;

    // Replace template variables
    const url = this.replaceTemplates(config.url, inputValues);
    const headers = this.buildHeaders(config.headers, inputValues);
    const body = config.body ? this.replaceTemplates(JSON.stringify(config.body), inputValues) : undefined;

    // Make API call
    const response = await fetch(url, {
      method: config.method,
      headers,
      body,
      signal: AbortSignal.timeout(config.timeout_ms)
    });

    if (!response.ok) {
      throw new Error(`API call failed: ${response.statusText}`);
    }

    const data = await response.json();

    // Extract using JSONPath
    return config.response_mapping.success_path
      ? this.extractJsonPath(data, config.response_mapping.success_path)
      : data;
  }
}
```

### Phase 8: Wizard Builder UI Components (Week 5-6)

**Files to Create:**
- `frontend/src/components/WizardBuilder/EventBuilderPanel.tsx`
- `frontend/src/components/WizardBuilder/ActionTypeSelectorDialog.tsx`
- `frontend/src/components/WizardBuilder/ActionEditors/ApiCallActionEditor.tsx`
- `frontend/src/components/WizardBuilder/ActionEditors/McpCallActionEditor.tsx`
- `frontend/src/components/WizardBuilder/ActionEditors/TransformDataActionEditor.tsx`
- `frontend/src/components/WizardBuilder/ActionEditors/SetFieldValueActionEditor.tsx`
- `frontend/src/components/WizardBuilder/ActionCard.tsx`
- `frontend/src/components/WizardBuilder/ConditionBuilder.tsx`
- `frontend/src/components/WizardBuilder/InputMappingBuilder.tsx`
- `frontend/src/components/WizardBuilder/OutputConfigBuilder.tsx`

### Phase 9: Output Renderers (Week 6-7)

**Files to Create:**
- `frontend/src/components/OutputRenderers/OutputRenderer.tsx`
- `frontend/src/components/OutputRenderers/TableRenderer.tsx`
- `frontend/src/components/OutputRenderers/DropdownRenderer.tsx`
- `frontend/src/components/OutputRenderers/CardGridRenderer.tsx`
- `frontend/src/components/OutputRenderers/ListRenderer.tsx`
- `frontend/src/components/OutputRenderers/DocumentRenderer.tsx`
- `frontend/src/components/OutputRenderers/ImageRenderer.tsx`
- `frontend/src/components/OutputRenderers/CodeRenderer.tsx`
- `frontend/src/components/OutputRenderers/JsonRenderer.tsx`
- `frontend/src/components/OutputRenderers/ChartRenderer.tsx`

### Phase 10: Wizard Player Integration (Week 7)

**Files to Modify:**
- `frontend/src/pages/WizardPlayerPage.tsx`

**Key Changes:**
```typescript
// Add event execution on step entry
useEffect(() => {
  const executeStepEntryEvents = async () => {
    const events = wizard.events?.filter(
      e => e.event_trigger === EventTrigger.STEP_ON_ENTRY &&
           e.target_id === currentStep.id &&
           e.is_enabled
    ) || [];

    for (const event of events) {
      await actionExecutor.executeActions(event.actions, {
        step: currentStep,
        runId: run.id,
        wizardId: wizard.id
      });
    }
  };

  executeStepEntryEvents();
}, [currentStep.id]);

// Add apply button handler
const handleApplyButton = async (optionSetId: string) => {
  const optionSet = currentStep.option_sets.find(os => os.id === optionSetId);

  if (optionSet?.selection_type === 'apply_button') {
    setIsExecutingAction(true);

    try {
      const events = wizard.events?.filter(
        e => e.event_trigger === EventTrigger.OPTIONSET_ON_APPLY &&
             e.target_id === optionSetId &&
             e.is_enabled
      ) || [];

      for (const event of events) {
        await actionExecutor.executeActions(event.actions, {
          optionSet,
          step: currentStep,
          runId: run.id
        });
      }

      showSuccess('Action completed successfully');
    } catch (error) {
      showError(error.message);
    } finally {
      setIsExecutingAction(false);
    }
  }
};
```

---

## Implementation Timeline

### Week 1: Foundation
- ✅ Database schema design
- ✅ Create Alembic migration
- ✅ SQLAlchemy models
- ✅ Pydantic schemas
- ✅ Basic CRUD operations

### Week 2: Backend API
- ✅ Event management endpoints
- ✅ Action management endpoints
- ✅ API configuration endpoints
- ✅ MCP configuration endpoints
- ✅ Testing endpoints

### Week 3: Action Execution Engine
- ✅ Backend action executor
- ✅ API caller service
- ✅ MCP caller service
- ✅ Data transformer service
- ✅ TypeScript types
- ✅ Frontend action executor

### Week 4: Services & Testing
- ✅ Frontend services
- ✅ Template engine
- ✅ JSONPath extractor
- ✅ Action testing interface
- ✅ End-to-end testing

### Week 5-6: Wizard Builder UI
- ✅ Event builder panel
- ✅ Action type selector
- ✅ API call action editor (full featured)
- ✅ MCP call action editor
- ✅ Transform/Set Field editors
- ✅ Condition builder
- ✅ Input/output mapping builders

### Week 7: Output Renderers
- ✅ Table renderer
- ✅ Dropdown renderer
- ✅ Card grid renderer
- ✅ Document/Image/Code renderers
- ✅ Chart renderer
- ✅ JSON renderer

### Week 8: Integration & Polish
- ✅ Wizard player integration
- ✅ Apply button implementation
- ✅ Error handling refinement
- ✅ Loading states
- ✅ Success/error messages

### Week 9: Testing & Documentation
- ✅ Unit tests
- ✅ Integration tests
- ✅ User acceptance testing
- ✅ Documentation
- ✅ Example wizards

### Week 10: Launch Preparation
- ✅ Performance optimization
- ✅ Security review
- ✅ Production deployment
- ✅ User training materials

---

## Risk Assessment & Mitigation

### Technical Risks

**Risk 1: API Call Security**
- **Mitigation**: Implement API key encryption, CORS validation, rate limiting
- **Priority**: High

**Risk 2: JavaScript Execution Safety**
- **Mitigation**: Use sandboxed execution context, limit available APIs
- **Priority**: High

**Risk 3: Performance with Large Datasets**
- **Mitigation**: Implement pagination, lazy loading, data streaming
- **Priority**: Medium

**Risk 4: MCP Server Availability**
- **Mitigation**: Add fallback mechanisms, caching, timeout handling
- **Priority**: Medium

### Business Risks

**Risk 1: User Adoption Complexity**
- **Mitigation**: Create comprehensive tutorials, example wizards, video guides
- **Priority**: Medium

**Risk 2: Breaking Changes to Existing Wizards**
- **Mitigation**: Backward compatibility layer, migration scripts
- **Priority**: High

---

## Success Metrics

### Technical Metrics
- ✅ All API endpoints return < 200ms (95th percentile)
- ✅ Action execution success rate > 98%
- ✅ Zero security vulnerabilities
- ✅ Test coverage > 85%

### User Metrics
- ✅ 50+ wizards using action system within 3 months
- ✅ Average 5+ actions per wizard
- ✅ 90%+ user satisfaction rating
- ✅ < 5% error rate in production

---

## Next Steps

1. **Review & Approve Plan** - Stakeholder review (1 day)
2. **Database Migration** - Create and test schema (2 days)
3. **Begin Phase 1** - Start backend models & schemas (Week 1)
4. **Daily Standups** - Track progress and blockers
5. **Weekly Demos** - Show progress to stakeholders

---

**Document Version**: 1.0
**Created**: 2025-11-19
**Last Updated**: 2025-11-19
**Status**: Ready for Implementation
