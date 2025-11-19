# Wizard Builder - Implementation & Features Documentation

## Overview

The Wizard Builder is a comprehensive administrative interface that allows administrators to create, configure, and manage step-by-step wizards in the Multi-Wizard Platform. It provides a powerful drag-and-drop interface for building complex, multi-step forms with conditional logic and dependencies.

**Location**: [frontend/src/pages/admin/WizardBuilderPage.tsx](frontend/src/pages/admin/WizardBuilderPage.tsx)
**Lines of Code**: 1,103 lines
**Role Required**: Admin or Super Admin

---

## Table of Contents

1. [Core Features](#core-features)
2. [Architecture](#architecture)
3. [Wizard Configuration](#wizard-configuration)
4. [Step Management](#step-management)
5. [Option Sets & Selection Types](#option-sets--selection-types)
6. [Conditional Dependencies](#conditional-dependencies)
7. [User Interface Components](#user-interface-components)
8. [API Integration](#api-integration)
9. [Validation & Error Handling](#validation--error-handling)
10. [Usage Examples](#usage-examples)

---

## Core Features

### 1. **Wizard Management**
- Create new wizards from scratch
- Edit existing wizards
- Clone wizards for quick templating
- Delete wizards (with confirmation)
- Publish/unpublish wizards
- Real-time preview

### 2. **Step Builder**
- Add unlimited steps to a wizard
- Reorder steps with drag handles
- Configure step properties:
  - Name and description
  - Help text for guidance
  - Required/optional flags
  - Skippable configuration
  - Step ordering

### 3. **Option Sets (Input Fields)**
- Add multiple option sets per step
- Support for 12 different input types
- Configure validation rules
- Set placeholder text and help text
- Mark fields as required/optional
- Min/max selection limits

### 4. **Conditional Logic**
- Show/hide fields based on selections
- Enable/disable fields conditionally
- Make fields required conditionally
- Cross-field dependencies
- Complex dependency chains

### 5. **Publishing & Configuration**
- Publish/draft mode
- Login requirements
- Template creation allowed
- Auto-save functionality
- Difficulty levels (Easy, Medium, Hard)
- Estimated completion time
- Tagging system

---

## Architecture

### Component Structure

```
WizardBuilderPage (Main Component)
├── Wizard List View
│   ├── Existing Wizards Grid
│   ├── Clone/Edit/Delete Actions
│   └── Create New Wizard Button
│
└── Wizard Editor View
    ├── Basic Information Section
    │   ├── Name, Description
    │   ├── Category Selection
    │   ├── Settings (Publish, Login, etc.)
    │   └── Metadata (Tags, Difficulty, Time)
    │
    ├── Steps Section (Repeatable)
    │   ├── Step Configuration
    │   ├── Option Sets (Repeatable)
    │   │   ├── Selection Type
    │   │   ├── Validation Rules
    │   │   └── Options (for select types)
    │   │       ├── Option Label & Value
    │   │       ├── Default Selection
    │   │       └── Dependencies
    │   └── Add Step Button
    │
    └── Action Buttons
        ├── Save Wizard
        ├── Cancel
        └── Delete (if editing)
```

### State Management

```typescript
interface WizardData {
  name: string;
  description?: string;
  category_id?: string;
  icon?: string;
  is_published: boolean;
  allow_templates: boolean;
  require_login: boolean;
  auto_save: boolean;
  estimated_time?: number;
  difficulty_level?: 'easy' | 'medium' | 'hard';
  tags: string[];
  steps: StepData[];
}

interface StepData {
  name: string;
  description?: string;
  help_text?: string;
  step_order: number;
  is_required: boolean;
  is_skippable: boolean;
  option_sets: OptionSetData[];
}

interface OptionSetData {
  name: string;
  description?: string;
  selection_type: string;
  is_required: boolean;
  min_selections: number;
  max_selections?: number;
  placeholder?: string;
  help_text?: string;
  options: OptionData[];
}
```

---

## Wizard Configuration

### Basic Information

**Fields:**
- **Name** (Required): The wizard's display name
- **Description**: Detailed explanation of the wizard's purpose
- **Category**: Classification for organization
- **Icon**: Visual identifier (emoji or icon name)

### Settings & Permissions

**Publish Settings:**
- **Is Published**: Control wizard visibility to users
- **Require Login**: Mandate authentication before access
- **Allow Templates**: Enable users to save sessions as templates
- **Auto Save**: Automatic session progress saving

**Metadata:**
- **Difficulty Level**: Easy, Medium, or Hard
- **Estimated Time**: Completion time in minutes
- **Tags**: Searchable keywords (comma-separated)

### Configuration Example

```typescript
{
  name: "Laptop Configuration Wizard",
  description: "Configure your perfect laptop",
  category_id: "electronics-uuid",
  icon: "💻",
  is_published: true,
  allow_templates: true,
  require_login: false,
  auto_save: true,
  estimated_time: 15,
  difficulty_level: "easy",
  tags: ["laptop", "electronics", "configuration"]
}
```

---

## Step Management

### Step Properties

Each step represents a page in the wizard flow and can contain multiple option sets (input fields).

**Configuration:**
- **Name**: Step title shown to users
- **Description**: Additional context or instructions
- **Help Text**: Inline guidance for users
- **Step Order**: Position in wizard sequence (auto-managed)
- **Is Required**: Must be completed to proceed
- **Is Skippable**: Can be bypassed by users

### Step Operations

1. **Add Step**: Click "Add Step" button
2. **Remove Step**: Click delete icon on step accordion
3. **Reorder Steps**: Use drag handle (automatic renumbering)
4. **Configure Step**: Expand accordion to edit properties

### Example Step Configuration

```typescript
{
  name: "Choose Processor",
  description: "Select your preferred CPU",
  help_text: "Higher GHz means better performance",
  step_order: 1,
  is_required: true,
  is_skippable: false,
  option_sets: [...]
}
```

---

## Option Sets & Selection Types

### Supported Input Types

The Wizard Builder supports **12 different selection types** for maximum flexibility:

#### 1. **Single Select** (`single_select`)
- Radio buttons for single choice
- Use case: Select one option from a list
- Example: Choose laptop brand (Dell, HP, Lenovo)

#### 2. **Multiple Select** (`multiple_select`)
- Checkboxes for multiple choices
- Configuration: Min/max selections
- Example: Select software packages

#### 3. **Text Input** (`text_input`)
- Multi-line text entry
- Configuration: Placeholder, validation
- Example: Special requirements or notes

#### 4. **Number Input** (`number_input`)
- Numeric input with validation
- Configuration: Min/max value, step increment
- Example: Quantity, budget amount

#### 5. **Date Input** (`date_input`)
- Calendar date picker
- Example: Delivery date, event date

#### 6. **Time Input** (`time_input`)
- Time picker (HH:MM)
- Example: Appointment time, meeting time

#### 7. **DateTime Input** (`datetime_input`)
- Combined date and time picker
- Example: Event scheduling

#### 8. **Rating** (`rating`)
- Star rating (1-5 stars)
- Example: Priority level, satisfaction rating

#### 9. **Slider** (`slider`)
- Range slider for numeric values
- Configuration: Min/max value, step increment
- Example: Budget range, performance level

#### 10. **Color Picker** (`color_picker`)
- Color selection tool
- Example: Product color, theme color

#### 11. **File Upload** (`file_upload`)
- File attachment capability
- Configuration: Allowed file types, size limits
- Example: Document upload, image attachment

#### 12. **Rich Text** (`rich_text`)
- Formatted text editor
- Example: Detailed descriptions, documentation

### Option Set Configuration

```typescript
{
  name: "Processor Speed",
  description: "Select CPU speed",
  selection_type: "single_select",
  is_required: true,
  min_selections: 1,
  max_selections: 1,
  placeholder: "Choose processor...",
  help_text: "Higher GHz = Better performance",
  options: [
    {
      label: "2.4 GHz - Basic",
      value: "2.4ghz",
      description: "Good for everyday tasks",
      is_default: true
    },
    {
      label: "3.2 GHz - Performance",
      value: "3.2ghz",
      description: "Better for multitasking"
    },
    {
      label: "4.0 GHz - Premium",
      value: "4.0ghz",
      description: "Best for gaming and heavy workloads"
    }
  ]
}
```

---

## Conditional Dependencies

### Dependency System

The Wizard Builder includes a sophisticated dependency management system powered by the **OptionDependencyManager** component.

### Dependency Types

#### 1. **Show If** (`show_if`)
- Shows an option/field only when a specific option is selected
- Use case: Show "Gaming GPU" only if "Gaming" purpose is selected

#### 2. **Hide If** (`hide_if`)
- Hides an option/field when a specific option is selected
- Use case: Hide "Budget options" if "Premium" tier is selected

#### 3. **Require If** (`require_if`)
- Makes a field required based on another selection
- Use case: Require "Company Name" if "Business" user type is selected

#### 4. **Disable If** (`disable_if`)
- Disables a field when a specific option is selected
- Use case: Disable "Color choice" if "Standard color" is selected

### How Dependencies Work

Dependencies are defined at the **option level** within option sets:

```typescript
{
  label: "Gaming GPU",
  value: "rtx_4090",
  dependencies: [
    {
      depends_on_option_id: "gaming-purpose-option-id",
      dependency_type: "show_if"
    }
  ]
}
```

### Dependency Manager UI

The **OptionDependencyManager** component provides:
- Visual dependency configuration
- Dropdown to select dependency type
- Selection of which option triggers the dependency
- Real-time preview of dependency effects
- Support for multiple dependencies per option

**Component Location**: [frontend/src/components/OptionDependencyManager.tsx](frontend/src/components/OptionDependencyManager.tsx)

---

## User Interface Components

### Main Sections

#### 1. **Wizard List View**
- Grid layout of existing wizards
- Card-based design with key information:
  - Wizard name and description
  - Published status badge
  - Step count
  - Session statistics
  - Action buttons (Edit, Clone, Delete)

#### 2. **Wizard Editor View**
- Tabbed/accordion interface
- Collapsible sections for better organization
- Real-time validation feedback
- Auto-save indicators
- Responsive design for all screen sizes

### Interactive Elements

**Drag & Drop:**
- Reorder steps using drag handles
- Visual feedback during dragging
- Automatic order recalculation

**Accordions:**
- Collapsible step sections
- Expand/collapse all functionality
- Clean, organized interface

**Dynamic Forms:**
- Add/remove steps dynamically
- Add/remove option sets on the fly
- Add/remove options within option sets

### Visual Indicators

**Status Badges:**
- Published (Green)
- Draft (Orange)
- Required fields (Red asterisk)

**Helper Icons:**
- Info tooltips
- Validation warnings
- Success confirmations

---

## API Integration

### Backend Endpoints Used

```typescript
// Wizard CRUD Operations
POST   /api/v1/wizards/              // Create new wizard
GET    /api/v1/wizards/              // List all wizards
GET    /api/v1/wizards/:id           // Get wizard details
PUT    /api/v1/wizards/:id           // Update wizard
DELETE /api/v1/wizards/:id           // Delete wizard

// Category Management
GET    /api/v1/wizards/categories    // List categories

// Dependencies
POST   /api/v1/wizards/options/:id/dependencies  // Add dependency
DELETE /api/v1/wizards/dependencies/:id          // Remove dependency
```

### React Query Integration

```typescript
// Fetch wizards list
const { data: wizards } = useQuery({
  queryKey: ['wizards'],
  queryFn: () => wizardService.getWizards()
});

// Create/Update wizard
const createMutation = useMutation({
  mutationFn: (data: WizardData) => wizardService.createWizard(data),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['wizards'] });
    // Show success message
  }
});
```

### Data Flow

```
User Input → Component State → Validation → API Request → Backend → Database
                    ↓                                          ↓
              UI Updates ← Success/Error Message ← Response ←─┘
```

---

## Validation & Error Handling

### Client-Side Validation

**Required Fields:**
- Wizard name
- At least one step
- At least one option set per step
- Option set name and selection type

**Business Rules:**
- Min selections ≤ Max selections
- Step order must be sequential
- Tags must be comma-separated
- Estimated time must be positive

### Server-Side Validation

**Schema Validation:**
- Pydantic models validate all data types
- Enum validation for selection types
- UUID validation for IDs
- Regex pattern validation

**Database Constraints:**
- Foreign key integrity
- Unique constraints
- Not null constraints

### Error Display

**User-Friendly Messages:**
```typescript
"Please add at least one step to your wizard"
"Option set name is required"
"Min selections cannot exceed max selections"
```

**Error Positioning:**
- Inline validation next to fields
- Summary alerts at top of form
- Toast notifications for API errors

---

## Usage Examples

### Example 1: Simple Survey Wizard

```typescript
{
  name: "Customer Satisfaction Survey",
  description: "Help us improve our service",
  is_published: true,
  require_login: false,
  difficulty_level: "easy",
  estimated_time: 5,
  steps: [
    {
      name: "Overall Satisfaction",
      is_required: true,
      option_sets: [
        {
          name: "How satisfied are you?",
          selection_type: "rating",
          is_required: true,
          options: []
        },
        {
          name: "Additional Comments",
          selection_type: "text_input",
          is_required: false,
          placeholder: "Share your thoughts..."
        }
      ]
    }
  ]
}
```

### Example 2: Product Configuration Wizard

```typescript
{
  name: "Laptop Builder",
  description: "Build your custom laptop",
  is_published: true,
  require_login: true,
  allow_templates: true,
  difficulty_level: "medium",
  estimated_time: 15,
  steps: [
    {
      name: "Choose Purpose",
      step_order: 1,
      option_sets: [
        {
          name: "Primary Use",
          selection_type: "single_select",
          is_required: true,
          options: [
            { label: "Gaming", value: "gaming", id: "purpose-gaming" },
            { label: "Business", value: "business", id: "purpose-business" },
            { label: "Student", value: "student", id: "purpose-student" }
          ]
        }
      ]
    },
    {
      name: "Select Components",
      step_order: 2,
      option_sets: [
        {
          name: "Graphics Card",
          selection_type: "single_select",
          options: [
            {
              label: "RTX 4090 - Gaming",
              value: "rtx4090",
              dependencies: [{
                depends_on_option_id: "purpose-gaming",
                dependency_type: "show_if"
              }]
            },
            {
              label: "Integrated Graphics",
              value: "integrated",
              dependencies: [{
                depends_on_option_id: "purpose-gaming",
                dependency_type: "hide_if"
              }]
            }
          ]
        }
      ]
    }
  ]
}
```

### Example 3: Event Registration Form

```typescript
{
  name: "Conference Registration",
  description: "Register for our annual conference",
  is_published: true,
  require_login: true,
  steps: [
    {
      name: "Personal Information",
      option_sets: [
        {
          name: "Full Name",
          selection_type: "text_input",
          is_required: true
        },
        {
          name: "Attendance Date",
          selection_type: "date_input",
          is_required: true
        },
        {
          name: "Session Time",
          selection_type: "time_input",
          is_required: true
        }
      ]
    },
    {
      name: "Preferences",
      option_sets: [
        {
          name: "Dietary Restrictions",
          selection_type: "multiple_select",
          options: [
            { label: "Vegetarian", value: "vegetarian" },
            { label: "Vegan", value: "vegan" },
            { label: "Gluten-Free", value: "gluten_free" },
            { label: "None", value: "none" }
          ]
        },
        {
          name: "T-Shirt Size",
          selection_type: "single_select",
          options: [
            { label: "Small", value: "s" },
            { label: "Medium", value: "m" },
            { label: "Large", value: "l" },
            { label: "X-Large", value: "xl" }
          ]
        }
      ]
    }
  ]
}
```

---

## Best Practices

### Wizard Design

1. **Keep Steps Focused**: Each step should have a clear, single purpose
2. **Logical Flow**: Order steps in a natural progression
3. **Provide Context**: Use descriptions and help text liberally
4. **Set Defaults**: Mark sensible options as default
5. **Use Dependencies**: Show/hide fields to reduce complexity

### Performance Optimization

1. **Lazy Loading**: Load wizard details only when editing
2. **Debounced Saves**: Prevent excessive API calls
3. **Optimistic Updates**: Update UI before API confirmation
4. **Query Invalidation**: Refresh data after mutations

### Accessibility

1. **Keyboard Navigation**: All actions keyboard-accessible
2. **ARIA Labels**: Screen reader support
3. **Focus Management**: Proper focus handling
4. **Color Contrast**: WCAG AA compliant

### Security

1. **Role-Based Access**: Admin/Super Admin only
2. **Input Sanitization**: XSS prevention
3. **CSRF Protection**: Token validation
4. **Audit Logging**: Track all changes

---

## Technical Stack

**Frontend:**
- React 18+ with TypeScript
- Material-UI (MUI) v5 components
- React Query for data fetching
- React Hook Form for form management
- Zod for schema validation

**Backend:**
- FastAPI with Python 3.11+
- SQLAlchemy 2.0 ORM
- Pydantic v2 for validation
- PostgreSQL database

**State Management:**
- React useState for local state
- React Query for server state
- Context API for global state

---

## Future Enhancements

### Planned Features

1. **Visual Flow Designer**: Drag-and-drop flowchart interface
2. **Template Library**: Pre-built wizard templates
3. **Advanced Validation**: Custom JavaScript validation rules
4. **Branching Logic**: Conditional step navigation
5. **Integration Hub**: Connect to external APIs
6. **Analytics Dashboard**: Track wizard performance metrics
7. **A/B Testing**: Test different wizard configurations
8. **Multi-language Support**: Internationalization
9. **Version Control**: Track wizard changes over time
10. **Bulk Operations**: Import/export wizards

---

## Troubleshooting

### Common Issues

**Issue**: Wizard won't save
**Solution**: Check required fields and validation errors

**Issue**: Dependencies not working
**Solution**: Ensure option IDs are correctly referenced

**Issue**: Steps not reordering
**Solution**: Verify drag handle is being used

**Issue**: Options not appearing
**Solution**: Check selection type allows options (single/multiple select)

### Debug Mode

Enable detailed logging:
```typescript
console.log('Wizard State:', wizard);
console.log('Validation Errors:', validationErrors);
```

---

## Conclusion

The Wizard Builder is a powerful, flexible tool for creating sophisticated multi-step forms without writing code. Its intuitive interface, comprehensive feature set, and robust validation make it suitable for everything from simple surveys to complex product configurators.

For additional support or feature requests, please refer to the project's GitHub repository or contact the development team.

---

**Document Version**: 1.0
**Last Updated**: November 2025
**Maintained By**: Multi-Wizard Platform Team
