# Quick Start Guide - Wizard Action System

## Overview

This guide will walk you through setting up and using the Wizard Action System in your Multi-Wizard Platform. By the end of this guide, you'll have created your first interactive wizard with dynamic API integration.

---

## Prerequisites

✅ Multi-Wizard Platform backend running (Port 8000)
✅ Frontend running (Port 3000)
✅ PostgreSQL database (wizarddb)
✅ Admin user account

---

## Phase 1: Database Setup (15 minutes)

### Step 1: Create Migration

```bash
cd backend
python -m alembic revision --autogenerate -m "add_wizard_action_system"
```

### Step 2: Review Migration File

Open the generated migration file in `backend/alembic/versions/` and verify it includes all 6 new tables:
- `wizard_events`
- `wizard_actions`
- `api_configurations`
- `mcp_configurations`
- `action_execution_logs`
- `dynamic_option_sets`

### Step 3: Apply Migration

```bash
python -m alembic upgrade head
```

### Step 4: Verify Tables

```bash
psql -U postgres -d wizarddb -c "\dt wizard_*"
```

You should see the 6 new tables listed.

---

## Phase 2: Backend Setup (1-2 hours)

### Step 1: Create Models

Create the following model files:

**backend/app/models/wizard_event.py**
```python
from sqlalchemy import Column, String, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

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

**backend/app/models/wizard_action.py**
```python
from sqlalchemy import Column, String, Boolean, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class WizardAction(Base):
    __tablename__ = "wizard_actions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey("wizard_events.id", ondelete="CASCADE"))
    action_name = Column(String(255), nullable=False)
    action_type = Column(String(50), nullable=False)
    execution_order = Column(Integer, default=1)
    is_async = Column(Boolean, default=True)
    config = Column(JSONB, nullable=False)
    input_mapping = Column(JSONB)
    output_handling = Column(JSONB)
    on_error = Column(String(20), default='continue')
    retry_count = Column(Integer, default=0)
    loading_message = Column(Text)
    show_loading_spinner = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    event = relationship("WizardEvent", back_populates="actions")
```

### Step 2: Update Wizard Model

Add the relationship to `backend/app/models/wizard.py`:

```python
# Add to Wizard class
events = relationship("WizardEvent", back_populates="wizard", cascade="all, delete-orphan")
```

### Step 3: Create Schemas

**backend/app/schemas/wizard_event.py**
```python
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class WizardEventBase(BaseModel):
    event_trigger: str
    event_name: str
    description: Optional[str] = None
    is_enabled: bool = True
    target_type: str
    target_id: Optional[UUID] = None
    conditions: Optional[dict] = None
    error_handling: Optional[dict] = None

class WizardEventCreate(WizardEventBase):
    wizard_id: UUID

class WizardEvent(WizardEventBase):
    id: UUID
    wizard_id: UUID
    created_at: datetime
    updated_at: datetime
    actions: List["WizardAction"] = []

    class Config:
        from_attributes = True
```

### Step 4: Create API Endpoints

**backend/app/api/v1/wizard_events.py**
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.wizard_event import WizardEvent
from app.schemas.wizard_event import WizardEvent as WizardEventSchema
from app.schemas.wizard_event import WizardEventCreate

router = APIRouter()

@router.post("/wizards/{wizard_id}/events", response_model=WizardEventSchema)
async def create_event(
    wizard_id: UUID,
    event: WizardEventCreate,
    db: Session = Depends(get_db)
):
    """Create a new wizard event"""
    db_event = WizardEvent(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@router.get("/wizards/{wizard_id}/events", response_model=List[WizardEventSchema])
async def get_wizard_events(wizard_id: UUID, db: Session = Depends(get_db)):
    """Get all events for a wizard"""
    events = db.query(WizardEvent).filter(WizardEvent.wizard_id == wizard_id).all()
    return events

@router.get("/wizards/events/{event_id}", response_model=WizardEventSchema)
async def get_event(event_id: UUID, db: Session = Depends(get_db)):
    """Get single event by ID"""
    event = db.query(WizardEvent).filter(WizardEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.delete("/wizards/events/{event_id}")
async def delete_event(event_id: UUID, db: Session = Depends(get_db)):
    """Delete an event"""
    event = db.query(WizardEvent).filter(WizardEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(event)
    db.commit()
    return {"message": "Event deleted"}
```

### Step 5: Register Routes

Update `backend/app/api/v1/__init__.py`:

```python
from .wizard_events import router as events_router

# Add to your main API router
api_router.include_router(events_router, tags=["wizard-events"])
```

---

## Phase 3: Frontend Setup (1-2 hours)

### Step 1: Create TypeScript Types

**frontend/src/types/wizardEvent.types.ts**
```typescript
export enum EventTrigger {
  STEP_ON_ENTRY = 'step.onEntry',
  STEP_ON_EXIT = 'step.onExit',
  OPTIONSET_ON_APPLY = 'optionSet.onApply',
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
  conditions?: any;
  error_handling?: any;
  actions: WizardAction[];
  created_at: string;
  updated_at: string;
}

export interface WizardAction {
  id: string;
  event_id: string;
  action_name: string;
  action_type: 'api_call' | 'mcp_call' | 'transform_data' | 'set_field_value' | 'show_message';
  execution_order: number;
  config: any;
  input_mapping?: any;
  output_handling?: any;
  on_error: 'continue' | 'stop' | 'retry';
  created_at: string;
}
```

### Step 2: Create Service

**frontend/src/services/wizardEvent.service.ts**
```typescript
import api from './api';
import { WizardEvent } from '../types/wizardEvent.types';

export const wizardEventService = {
  getWizardEvents: async (wizardId: string): Promise<WizardEvent[]> => {
    const response = await api.get(`/wizards/${wizardId}/events`);
    return response.data;
  },

  createEvent: async (event: any): Promise<WizardEvent> => {
    const response = await api.post(`/wizards/${event.wizard_id}/events`, event);
    return response.data;
  },

  deleteEvent: async (eventId: string): Promise<void> => {
    await api.delete(`/wizards/events/${eventId}`);
  }
};
```

### Step 3: Update Wizard Builder

Add Events section to `frontend/src/pages/admin/WizardBuilderPage.tsx`:

```typescript
import { useState, useEffect } from 'react';
import { wizardEventService } from '../../services/wizardEvent.service';
import { WizardEvent } from '../../types/wizardEvent.types';

// Inside WizardBuilderPage component:
const [events, setEvents] = useState<WizardEvent[]>([]);

useEffect(() => {
  if (wizard?.id) {
    loadEvents();
  }
}, [wizard?.id]);

const loadEvents = async () => {
  try {
    const data = await wizardEventService.getWizardEvents(wizard.id);
    setEvents(data);
  } catch (error) {
    console.error('Failed to load events:', error);
  }
};

// Add to render:
<Accordion>
  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
    <Typography variant="h6">⚡ Events & Actions</Typography>
    <Chip label={`${events.length} events`} size="small" sx={{ ml: 2 }} />
  </AccordionSummary>
  <AccordionDetails>
    <Alert severity="info" sx={{ mb: 2 }}>
      Configure events and actions to make your wizard dynamic and interactive.
    </Alert>

    <List>
      {events.map(event => (
        <ListItem key={event.id}>
          <ListItemText
            primary={event.event_name}
            secondary={`${event.event_trigger} | ${event.actions.length} actions`}
          />
          <IconButton onClick={() => handleDeleteEvent(event.id)}>
            <DeleteIcon />
          </IconButton>
        </ListItem>
      ))}
    </List>

    <Button
      variant="outlined"
      startIcon={<AddIcon />}
      onClick={() => setShowEventDialog(true)}
    >
      Add Event
    </Button>
  </AccordionDetails>
</Accordion>
```

---

## Phase 4: Create Your First Interactive Wizard (30 minutes)

### Example: Weather Lookup Wizard

Let's create a wizard that fetches weather data from an API based on user input.

### Step 1: Create Base Wizard

1. Go to Wizard Builder (`/admin/wizard-builder`)
2. Create new wizard:
   - Name: "Weather Lookup"
   - Description: "Get current weather for any city"
   - Category: "Utility"

### Step 2: Add Steps

**Step 1: City Input**
- Title: "Enter City"
- Description: "Which city's weather would you like to check?"
- Add Option Set:
  - Name: "City Name"
  - Selection Type: `text_input`
  - Placeholder: "e.g., London, New York, Tokyo"
  - Required: Yes

**Step 2: Weather Results**
- Title: "Weather Information"
- Description: "Current weather conditions"
- (Dynamic data will be displayed here)

### Step 3: Add Event & Action

1. Click "Events & Actions" section
2. Click "Add Event"
3. Configure Event:
   - Event Name: "Fetch Weather Data"
   - Event Trigger: `Step: On Entry`
   - Target Type: `Step`
   - Target Step: "Weather Results" (Step 2)
   - Enabled: Yes

4. Add Action to Event:
   - Action Name: "Get Weather from API"
   - Action Type: `api_call`
   - Execution Order: 1

5. Configure API Call:
   ```json
   {
     "method": "GET",
     "url": "https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=YOUR_API_KEY&units=metric",
     "timeout_ms": 10000,
     "auth": {
       "type": "none"
     },
     "response_mapping": {
       "success_path": "$.data"
     }
   }
   ```

6. Configure Input Mapping:
   ```json
   {
     "city": {
       "source": "option_set",
       "field_id": "city_name_field_id"
     }
   }
   ```

7. Configure Output Handling:
   ```json
   {
     "display_type": "table",
     "config": {
       "columns": [
         { "field": "name", "label": "City" },
         { "field": "main.temp", "label": "Temperature (°C)", "format": "number" },
         { "field": "weather[0].description", "label": "Conditions" },
         { "field": "main.humidity", "label": "Humidity (%)", "format": "number" }
       ],
       "show_actions": false
     }
   }
   ```

### Step 4: Test the Wizard

1. Publish the wizard
2. Go to Run Wizard (`/wizards`)
3. Start "Weather Lookup"
4. Enter a city name (e.g., "London")
5. Click Next
6. See the weather data displayed in a table!

---

## Phase 5: Advanced Example - Database Query (45 minutes)

### Example: Product Catalog with MCP

This example shows how to query a database using MCP and display results.

### Step 1: Setup MCP Configuration

1. Create MCP Configuration:
   ```json
   {
     "config_name": "PostgreSQL - Products DB",
     "mcp_server": "postgresql_server",
     "available_tools": ["execute_query"],
     "timeout_ms": 30000,
     "max_retries": 2
   }
   ```

### Step 2: Create Wizard

1. Name: "Product Catalog Browser"
2. Add Steps:
   - Step 1: Category Selection
   - Step 2: Product Results

### Step 3: Add Category Dropdown

In Step 1, add Option Set:
- Name: "Product Category"
- Selection Type: `single_select`
- Options:
  - Electronics
  - Clothing
  - Books
  - Home & Garden

### Step 4: Add MCP Event

1. Event Name: "Load Products by Category"
2. Event Trigger: `Step: On Entry`
3. Target: Step 2

4. Add MCP Action:
   ```json
   {
     "action_name": "Query Products",
     "action_type": "mcp_call",
     "config": {
       "mcp_server": "postgresql_server",
       "tool_name": "execute_query",
       "parameters": {
         "query": "SELECT id, name, price, description FROM products WHERE category = :category ORDER BY name LIMIT 50",
         "params": {
           "category": "${selected_category}"
         }
       },
       "mcp_config": {
         "timeout_ms": 30000,
         "streaming": false
       },
       "response_format": "json"
     },
     "input_mapping": {
       "selected_category": {
         "source": "option_set",
         "field_id": "category_dropdown_id"
       }
     },
     "output_handling": {
       "display_type": "card_grid",
       "config": {
         "title_field": "name",
         "subtitle_field": "price",
         "description_field": "description",
         "show_actions": true
       }
     }
   }
   ```

### Step 5: Test

1. Publish wizard
2. Run wizard
3. Select category
4. See products displayed as cards!

---

## Common Use Cases

### 1. Form Auto-Fill from API

**Scenario**: Automatically populate address fields when user enters zip code

**Event**: `Option: On Change` (zip code field)
**Action**: API Call to address lookup service
**Output**: Set multiple field values (street, city, state)

### 2. Validation with External Service

**Scenario**: Validate email address before proceeding

**Event**: `Step: On Exit`
**Action**: API Call to email validation service
**Output**: Show error message if invalid

### 3. Dynamic Price Calculation

**Scenario**: Calculate total price based on selections

**Event**: `Option Set: On Change`
**Action**: Transform Data (JavaScript calculation)
**Output**: Update price display field

### 4. Conditional Step Navigation

**Scenario**: Skip certain steps based on user selections

**Event**: `Step: On Exit`
**Action**: Navigate action with conditions
**Output**: Jump to appropriate step

### 5. Multi-Step Data Aggregation

**Scenario**: Fetch data from multiple APIs and combine

**Event**: `Step: On Entry`
**Actions**:
  1. API Call to Service A
  2. API Call to Service B
  3. Transform Data (merge results)
  4. Display combined data

---

## Troubleshooting

### Issue: Events not triggering

**Solution**:
1. Check event is enabled
2. Verify target_id matches the step/option_set ID
3. Check browser console for errors
4. Review action execution logs

### Issue: API call failing

**Solution**:
1. Test API endpoint in Postman/curl
2. Check CORS settings
3. Verify API key/authentication
4. Review timeout settings

### Issue: Template variables not resolving

**Solution**:
1. Check input mapping source is correct
2. Verify field IDs match wizard configuration
3. Use browser console to debug context values
4. Test with static values first

### Issue: Output not displaying

**Solution**:
1. Check JSONPath expression in response_mapping
2. Verify output_handling display_type is set
3. Review API response structure
4. Test with sample data in action tester

---

## Next Steps

✅ Explore all 7 action types
✅ Implement error handling strategies
✅ Create reusable API configurations
✅ Build custom output renderers
✅ Add conditional logic with event conditions
✅ Monitor action execution logs for analytics

---

## Resources

- **Full Implementation Plan**: `Implementation Plan - Wizard Action System.md`
- **Backend Technical Spec**: `Technical Spec - Backend Components.md`
- **Frontend Technical Spec**: `Technical Spec - Frontend Components.md`
- **API Documentation**: `/api/docs` (FastAPI auto-generated)
- **Example Wizards**: Check `examples/` folder (coming soon)

---

## Support

If you encounter issues:
1. Check troubleshooting section above
2. Review action execution logs in database
3. Enable debug logging in backend
4. Check browser console for frontend errors
5. Review the detailed technical specifications

---

**Document Version**: 1.0
**Last Updated**: 2025-11-19
**Status**: Ready for Implementation
