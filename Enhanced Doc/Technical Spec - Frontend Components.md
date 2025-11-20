# Technical Specification - Frontend Components

## Overview

This document provides detailed technical specifications for all frontend components of the Wizard Action System, including TypeScript types, services, UI components, output renderers, and integration with the Wizard Player.

---

## 1. TypeScript Types & Interfaces

### 1.1 Event Types

**File**: `frontend/src/types/wizardEvent.types.ts`

```typescript
// Event Triggers
export enum EventTrigger {
  // Step Events
  STEP_ON_ENTRY = 'step.onEntry',
  STEP_ON_EXIT = 'step.onExit',
  STEP_ON_VALIDATE = 'step.onValidate',

  // Option Set Events
  OPTIONSET_ON_LOAD = 'optionSet.onLoad',
  OPTIONSET_ON_CHANGE = 'optionSet.onChange',
  OPTIONSET_ON_APPLY = 'optionSet.onApply',

  // Option Events
  OPTION_ON_CLICK = 'option.onClick',
  OPTION_ON_SELECT = 'option.onSelect',
  OPTION_ON_DESELECT = 'option.onDeselect',
  OPTION_ON_CHANGE = 'option.onChange',

  // Global Events
  WIZARD_ON_START = 'wizard.onStart',
  WIZARD_ON_COMPLETE = 'wizard.onComplete'
}

// Event Condition
export interface EventCondition {
  field_id: string;
  operator: 'equals' | 'not_equals' | 'contains' | 'greater_than' | 'less_than' | 'is_empty' | 'is_not_empty';
  value: any;
  logic: 'AND' | 'OR';
}

// Error Handling Config
export interface ErrorHandlingConfig {
  on_error: 'continue' | 'stop' | 'retry';
  retry_count?: number;
  retry_delay_ms?: number;
  show_error_to_user: boolean;
  log_errors: boolean;
}

// Wizard Event
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

// Create/Update interfaces
export interface WizardEventCreate {
  wizard_id: string;
  event_trigger: EventTrigger;
  event_name: string;
  description?: string;
  is_enabled: boolean;
  target_type: 'step' | 'option_set' | 'option' | 'wizard';
  target_id?: string;
  conditions?: EventCondition[];
  error_handling?: ErrorHandlingConfig;
}

export interface WizardEventUpdate {
  event_name?: string;
  description?: string;
  is_enabled?: boolean;
  conditions?: EventCondition[];
  error_handling?: ErrorHandlingConfig;
}
```

### 1.2 Action Types

**File**: `frontend/src/types/wizardAction.types.ts`

```typescript
// Action Types
export enum ActionType {
  API_CALL = 'api_call',
  MCP_CALL = 'mcp_call',
  TRANSFORM_DATA = 'transform_data',
  SET_FIELD_VALUE = 'set_field_value',
  SHOW_MESSAGE = 'show_message',
  NAVIGATE = 'navigate',
  CUSTOM_SCRIPT = 'custom_script'
}

// Input Mapping
export interface InputMappingConfig {
  source: 'option_set' | 'context' | 'action_output' | 'static' | 'event_data';
  field_id?: string;
  field?: string;
  action_id?: string;
  value?: any;
}

// Output Handling
export enum OutputDisplayType {
  TABLE = 'table',
  DROPDOWN = 'dropdown',
  CARD_GRID = 'card_grid',
  LIST = 'list',
  DOCUMENT = 'document',
  IMAGE = 'image',
  CODE = 'code',
  JSON = 'json',
  CHART = 'chart',
  CUSTOM = 'custom',
  HIDDEN = 'hidden'
}

export interface OutputHandlingConfig {
  display_type: OutputDisplayType;
  target_option_set_id?: string;
  config?: Record<string, any>;
}

// Base Action
export interface WizardAction {
  id: string;
  event_id: string;
  action_name: string;
  action_type: ActionType;
  execution_order: number;
  is_async: boolean;
  config: ActionConfig;
  input_mapping?: Record<string, InputMappingConfig>;
  output_handling?: OutputHandlingConfig;
  on_error: 'continue' | 'stop' | 'retry';
  retry_count: number;
  loading_message?: string;
  show_loading_spinner: boolean;
  created_at: string;
  updated_at: string;
}

// Action Configs (union type)
export type ActionConfig =
  | ApiCallActionConfig
  | McpCallActionConfig
  | TransformDataActionConfig
  | SetFieldValueActionConfig
  | ShowMessageActionConfig
  | NavigateActionConfig
  | CustomScriptActionConfig;

// API Call Action Config
export interface ApiCallActionConfig {
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  url: string;
  headers?: Record<string, string>;
  query_params?: Record<string, any>;
  body?: any;
  timeout_ms: number;
  auth: {
    type: 'none' | 'bearer' | 'basic' | 'api_key' | 'oauth2';
    credentials?: Record<string, string>;
  };
  response_mapping: {
    success_path?: string;
    error_path?: string;
  };
}

// MCP Call Action Config
export interface McpCallActionConfig {
  mcp_server: string;
  tool_name: string;
  parameters: Record<string, any>;
  mcp_config: {
    timeout_ms: number;
    max_retries: number;
    streaming: boolean;
  };
  response_format: 'json' | 'text' | 'stream';
  response_schema?: object;
}

// Transform Data Action Config
export interface TransformDataActionConfig {
  transformation_type: 'jmespath' | 'javascript' | 'python';
  transformation_script: string;
  script_context?: Record<string, any>;
  output_schema?: object;
}

// Set Field Value Action Config
export interface SetFieldValueActionConfig {
  target_fields: Array<{
    option_set_id: string;
    field_path?: string;
    value_source: 'static' | 'dynamic' | 'computed';
    value: any;
  }>;
  bulk_update: boolean;
}

// Show Message Action Config
export interface ShowMessageActionConfig {
  message_type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration_ms?: number;
  position: 'top' | 'bottom' | 'center';
  is_dismissible: boolean;
}

// Navigate Action Config
export interface NavigateActionConfig {
  target_step_id: string;
  navigation_type: 'next' | 'previous' | 'jump' | 'complete';
}

// Custom Script Action Config
export interface CustomScriptActionConfig {
  script: string;
  script_context?: Record<string, any>;
}

// Create/Update interfaces
export interface WizardActionCreate {
  event_id: string;
  action_name: string;
  action_type: ActionType;
  execution_order: number;
  is_async: boolean;
  config: ActionConfig;
  input_mapping?: Record<string, InputMappingConfig>;
  output_handling?: OutputHandlingConfig;
  on_error: 'continue' | 'stop' | 'retry';
  retry_count: number;
  loading_message?: string;
  show_loading_spinner: boolean;
}

export interface WizardActionUpdate {
  action_name?: string;
  execution_order?: number;
  is_async?: boolean;
  config?: ActionConfig;
  input_mapping?: Record<string, InputMappingConfig>;
  output_handling?: OutputHandlingConfig;
  on_error?: 'continue' | 'stop' | 'retry';
  retry_count?: number;
  loading_message?: string;
  show_loading_spinner?: boolean;
}

// Action Execution Result
export interface ActionResult {
  action_id: string;
  success: boolean;
  data?: any;
  error?: string;
}

export interface ActionExecutionResult {
  success: boolean;
  results: ActionResult[];
}
```

### 1.3 Output Renderer Types

**File**: `frontend/src/types/outputRenderer.types.ts`

```typescript
// Table Config
export interface TableColumn {
  field: string;
  label: string;
  icon?: string;
  sortable?: boolean;
  format?: 'text' | 'number' | 'currency' | 'date' | 'boolean' | 'link';
  width?: string | number;
}

export interface TableConfig {
  columns: TableColumn[];
  rows_per_page?: number;
  show_actions: boolean;
  allow_select: boolean;
  searchable: boolean;
  sortable: boolean;
}

// Dropdown Config
export interface DropdownConfig {
  label: string;
  value_field: string;
  label_field: string;
  description_field?: string;
  icon_field?: string;
  show_icon: boolean;
  multiple: boolean;
  searchable: boolean;
  onChange?: (value: any) => void;
}

// Card Grid Config
export interface CardGridConfig {
  title_field: string;
  subtitle_field?: string;
  description_field?: string;
  image_field?: string;
  show_image: boolean;
  image_height?: number;
  custom_fields: Array<{
    name: string;
    label: string;
  }>;
  show_actions: boolean;
  onSelect?: (item: any) => void;
  onView?: (item: any) => void;
}

// List Config
export interface ListConfig {
  primary_field: string;
  secondary_field?: string;
  icon_field?: string;
  avatar_field?: string;
  show_dividers: boolean;
  dense: boolean;
  onClick?: (item: any) => void;
}

// Document Config
export interface DocumentConfig {
  title_field: string;
  content_field: string;
  content_type: 'html' | 'markdown' | 'text';
  show_title: boolean;
  show_metadata: boolean;
  metadata_fields: string[];
  show_download: boolean;
}

// Image Config
export interface ImageConfig {
  url_field: string;
  title_field?: string;
  alt_field?: string;
  caption_field?: string;
  width?: string | number;
  height?: string | number;
  border_radius?: number;
  object_fit?: 'contain' | 'cover' | 'fill' | 'none' | 'scale-down';
  show_title: boolean;
  show_caption: boolean;
}

// Code Config
export interface CodeConfig {
  code_field: string;
  language: string;
  show_language: boolean;
  show_line_numbers: boolean;
  wrap_lines: boolean;
  theme: 'light' | 'dark';
}

// JSON Config
export interface JsonConfig {
  collapsed_depth?: number;
  sortable: boolean;
  theme: 'light' | 'dark';
}

// Chart Config
export interface ChartDataset {
  label: string;
  data_field: string;
  background_color?: string;
  border_color?: string;
  border_width?: number;
}

export interface ChartConfig {
  chart_type: 'line' | 'bar' | 'pie' | 'doughnut' | 'radar' | 'scatter';
  label_field: string;
  datasets: ChartDataset[];
  options?: any; // Chart.js options
}

// Output Config (union type)
export type OutputConfig =
  | TableConfig
  | DropdownConfig
  | CardGridConfig
  | ListConfig
  | DocumentConfig
  | ImageConfig
  | CodeConfig
  | JsonConfig
  | ChartConfig;
```

---

## 2. Service Layer

### 2.1 Event Service

**File**: `frontend/src/services/wizardEvent.service.ts`

```typescript
import api from './api';
import { WizardEvent, WizardEventCreate, WizardEventUpdate } from '../types/wizardEvent.types';

export const wizardEventService = {
  /**
   * Get all events for a wizard
   */
  getWizardEvents: async (wizardId: string): Promise<WizardEvent[]> => {
    const response = await api.get(`/wizards/${wizardId}/events`);
    return response.data.events || response.data;
  },

  /**
   * Get single event by ID
   */
  getEvent: async (eventId: string): Promise<WizardEvent> => {
    const response = await api.get(`/wizards/events/${eventId}`);
    return response.data;
  },

  /**
   * Get events by trigger and target
   */
  getEventsByTrigger: async (
    wizardId: string,
    trigger: string,
    targetId?: string
  ): Promise<WizardEvent[]> => {
    const params: any = { trigger };
    if (targetId) params.target_id = targetId;

    const response = await api.get(`/wizards/${wizardId}/events/by-trigger`, { params });
    return response.data.events || response.data;
  },

  /**
   * Create new event
   */
  createEvent: async (event: WizardEventCreate): Promise<WizardEvent> => {
    const response = await api.post(`/wizards/${event.wizard_id}/events`, event);
    return response.data;
  },

  /**
   * Update event
   */
  updateEvent: async (eventId: string, event: WizardEventUpdate): Promise<WizardEvent> => {
    const response = await api.put(`/wizards/events/${eventId}`, event);
    return response.data;
  },

  /**
   * Delete event
   */
  deleteEvent: async (eventId: string): Promise<void> => {
    await api.delete(`/wizards/events/${eventId}`);
  },

  /**
   * Toggle event enabled status
   */
  toggleEventEnabled: async (eventId: string): Promise<WizardEvent> => {
    const response = await api.patch(`/wizards/events/${eventId}/toggle`);
    return response.data;
  }
};
```

### 2.2 Action Service

**File**: `frontend/src/services/wizardAction.service.ts`

```typescript
import api from './api';
import { WizardAction, WizardActionCreate, WizardActionUpdate } from '../types/wizardAction.types';

export const wizardActionService = {
  /**
   * Get all actions for an event
   */
  getEventActions: async (eventId: string): Promise<WizardAction[]> => {
    const response = await api.get(`/wizards/events/${eventId}/actions`);
    return response.data.actions || response.data;
  },

  /**
   * Get single action by ID
   */
  getAction: async (actionId: string): Promise<WizardAction> => {
    const response = await api.get(`/wizards/actions/${actionId}`);
    return response.data;
  },

  /**
   * Create new action
   */
  createAction: async (action: WizardActionCreate): Promise<WizardAction> => {
    const response = await api.post(`/wizards/events/${action.event_id}/actions`, action);
    return response.data;
  },

  /**
   * Update action
   */
  updateAction: async (actionId: string, action: WizardActionUpdate): Promise<WizardAction> => {
    const response = await api.put(`/wizards/actions/${actionId}`, action);
    return response.data;
  },

  /**
   * Delete action
   */
  deleteAction: async (actionId: string): Promise<void> => {
    await api.delete(`/wizards/actions/${actionId}`);
  },

  /**
   * Reorder actions
   */
  reorderActions: async (eventId: string, actionOrders: Record<string, number>): Promise<WizardAction[]> => {
    const response = await api.post(`/wizards/events/${eventId}/actions/reorder`, {
      action_orders: actionOrders
    });
    return response.data.actions || response.data;
  },

  /**
   * Test action with sample data
   */
  testAction: async (actionId: string, testData: any): Promise<any> => {
    const response = await api.post(`/wizards/actions/${actionId}/test`, { test_data: testData });
    return response.data;
  }
};
```

### 2.3 Action Executor Service

**File**: `frontend/src/services/actionExecutor.service.ts`

```typescript
import api from './api';
import { WizardAction, ActionExecutionResult } from '../types/wizardAction.types';

export const actionExecutorService = {
  /**
   * Execute event actions during wizard run
   */
  executeEvent: async (runId: string, eventId: string, context: any): Promise<ActionExecutionResult> => {
    const response = await api.post(`/wizard-runs/${runId}/execute-event`, {
      event_id: eventId,
      context
    });
    return response.data;
  },

  /**
   * Get action execution logs for a run
   */
  getActionLogs: async (runId: string): Promise<any[]> => {
    const response = await api.get(`/wizard-runs/${runId}/action-logs`);
    return response.data.logs || response.data;
  },

  /**
   * Get specific action log
   */
  getActionLog: async (runId: string, logId: string): Promise<any> => {
    const response = await api.get(`/wizard-runs/${runId}/action-logs/${logId}`);
    return response.data;
  }
};
```

---

## 3. Action Executor Engine

### 3.1 Main Executor Class

**File**: `frontend/src/lib/ActionExecutor.ts`

```typescript
import { WizardAction, ActionResult, ActionExecutionResult, ActionType } from '../types/wizardAction.types';
import { TemplateEngine } from './TemplateEngine';
import { JSONPathExtractor } from './JSONPathExtractor';

export interface WizardExecutionContext {
  runId: string;
  wizardId: string;
  currentStep: any;
  responses: Record<string, any>;
  userData?: any;
  [key: string]: any;
}

export class ActionExecutor {
  private context: WizardExecutionContext;
  private actionResults: Map<string, any> = new Map();
  private templateEngine: TemplateEngine;
  private jsonPathExtractor: JSONPathExtractor;
  private loadingHandlers: Map<string, () => void> = new Map();

  constructor(context: WizardExecutionContext) {
    this.context = context;
    this.templateEngine = new TemplateEngine();
    this.jsonPathExtractor = new JSONPathExtractor();
  }

  /**
   * Execute multiple actions in sequence
   */
  async executeActions(actions: WizardAction[], eventData: any): Promise<ActionExecutionResult> {
    const results: ActionResult[] = [];

    // Sort actions by execution order
    const sortedActions = [...actions].sort((a, b) => a.execution_order - b.execution_order);

    for (const action of sortedActions) {
      try {
        // Show loading state
        if (action.show_loading_spinner) {
          this.showLoading(action);
        }

        // Resolve input values
        const inputValues = this.resolveInputMapping(action.input_mapping || {}, eventData);

        // Execute the action
        const result = await this.executeAction(action, inputValues);

        // Store result for downstream actions
        this.actionResults.set(action.id, result);

        // Handle output
        if (action.output_handling) {
          await this.handleOutput(action, result);
        }

        results.push({
          action_id: action.id,
          success: true,
          data: result
        });

      } catch (error: any) {
        results.push({
          action_id: action.id,
          success: false,
          error: error.message
        });

        // Handle errors based on action configuration
        if (action.on_error === 'stop') {
          break;
        } else if (action.on_error === 'retry' && action.retry_count > 0) {
          // Retry logic here
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

  /**
   * Execute a single action
   */
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

      case ActionType.NAVIGATE:
        return this.executeNavigate(action, inputValues);

      case ActionType.CUSTOM_SCRIPT:
        return this.executeCustomScript(action, inputValues);

      default:
        throw new Error(`Unknown action type: ${action.action_type}`);
    }
  }

  /**
   * Execute API Call action
   */
  private async executeApiCall(action: WizardAction, inputValues: Record<string, any>): Promise<any> {
    const config = action.config as any;

    // Replace template variables in URL
    const url = this.templateEngine.render(config.url, inputValues);

    // Build headers
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...config.headers
    };

    // Replace template variables in headers
    Object.keys(headers).forEach(key => {
      headers[key] = this.templateEngine.render(headers[key], inputValues);
    });

    // Build request body
    let body: string | undefined;
    if (config.body && (config.method === 'POST' || config.method === 'PUT' || config.method === 'PATCH')) {
      const bodyObj = this.templateEngine.renderObject(config.body, inputValues);
      body = JSON.stringify(bodyObj);
    }

    // Make API call
    const response = await fetch(url, {
      method: config.method,
      headers,
      body,
      signal: AbortSignal.timeout(config.timeout_ms || 30000)
    });

    if (!response.ok) {
      throw new Error(`API call failed: ${response.statusText}`);
    }

    const data = await response.json();

    // Extract data using JSONPath if specified
    if (config.response_mapping?.success_path) {
      return this.jsonPathExtractor.extract(data, config.response_mapping.success_path);
    }

    return data;
  }

  /**
   * Execute MCP Call action
   */
  private async executeMcpCall(action: WizardAction, inputValues: Record<string, any>): Promise<any> {
    const config = action.config as any;

    // Replace template variables in parameters
    const parameters = this.templateEngine.renderObject(config.parameters, inputValues);

    // Call backend MCP endpoint
    const response = await fetch(`/api/v1/mcp/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        server: config.mcp_server,
        tool: config.tool_name,
        parameters
      })
    });

    if (!response.ok) {
      throw new Error(`MCP call failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Execute Transform Data action
   */
  private executeTransform(action: WizardAction, inputValues: Record<string, any>): any {
    const config = action.config as any;

    if (config.transformation_type === 'javascript') {
      return this.executeJavaScriptTransform(config.transformation_script, inputValues);
    } else if (config.transformation_type === 'jmespath') {
      return this.executeJMESPathTransform(config.transformation_script, inputValues);
    }

    throw new Error(`Unsupported transformation type: ${config.transformation_type}`);
  }

  /**
   * Execute JavaScript transformation safely
   */
  private executeJavaScriptTransform(script: string, input: Record<string, any>): any {
    // Create safe execution context
    const context = {
      input,
      console: {
        log: (...args: any[]) => console.log('[Transform]', ...args)
      },
      JSON,
      Math,
      Date,
      Array,
      Object
    };

    // Execute script
    const func = new Function('context', `with (context) { return (function() { ${script} })(); }`);
    return func(context);
  }

  /**
   * Execute Set Field Value action
   */
  private async executeSetFieldValue(action: WizardAction, inputValues: Record<string, any>): Promise<any> {
    const config = action.config as any;

    const updates: Record<string, any> = {};

    for (const targetField of config.target_fields) {
      const value = this.templateEngine.render(String(targetField.value), inputValues);
      updates[targetField.option_set_id] = value;

      // Trigger field update in wizard context
      if (this.context.responses) {
        this.context.responses[targetField.option_set_id] = value;
      }
    }

    return updates;
  }

  /**
   * Execute Show Message action
   */
  private executeShowMessage(action: WizardAction, inputValues: Record<string, any>): any {
    const config = action.config as any;

    const message = this.templateEngine.render(config.message, inputValues);

    // Return message info (will be handled by wizard player)
    return {
      type: config.message_type,
      message,
      duration: config.duration_ms,
      position: config.position
    };
  }

  /**
   * Resolve input mapping from various sources
   */
  private resolveInputMapping(
    inputMapping: Record<string, any>,
    eventData: any
  ): Record<string, any> {
    const resolved: Record<string, any> = {};

    for (const [key, mapping] of Object.entries(inputMapping)) {
      const source = mapping.source;

      if (source === 'option_set') {
        resolved[key] = this.context.responses?.[mapping.field_id];
      } else if (source === 'context') {
        resolved[key] = this.getNestedValue(this.context, mapping.field);
      } else if (source === 'action_output') {
        resolved[key] = this.actionResults.get(mapping.action_id);
      } else if (source === 'static') {
        resolved[key] = mapping.value;
      } else if (source === 'event_data') {
        resolved[key] = eventData[mapping.field];
      }
    }

    return resolved;
  }

  /**
   * Get nested value from object using dot notation
   */
  private getNestedValue(obj: any, path: string): any {
    const keys = path.split('.');
    let value = obj;
    for (const key of keys) {
      if (value && typeof value === 'object') {
        value = value[key];
      } else {
        return undefined;
      }
    }
    return value;
  }

  /**
   * Handle action output
   */
  private async handleOutput(action: WizardAction, result: any): Promise<void> {
    // Output handling logic will be implemented by OutputRenderer components
    // This method can emit events or update context for the wizard player
  }

  /**
   * Show loading state
   */
  private showLoading(action: WizardAction): void {
    // Emit loading event or update context
    const handler = this.loadingHandlers.get(action.id);
    if (handler) handler();
  }

  /**
   * Hide loading state
   */
  private hideLoading(action: WizardAction): void {
    // Clear loading state
  }

  /**
   * Register loading handler
   */
  public registerLoadingHandler(actionId: string, handler: () => void): void {
    this.loadingHandlers.set(actionId, handler);
  }
}
```

### 3.2 Template Engine

**File**: `frontend/src/lib/TemplateEngine.ts`

```typescript
export class TemplateEngine {
  /**
   * Render template string with variable substitution
   * Supports ${variable} syntax
   */
  render(template: string, variables: Record<string, any>): string {
    return template.replace(/\$\{([^}]+)\}/g, (match, key) => {
      const value = this.getNestedValue(variables, key.trim());
      return value !== undefined ? String(value) : match;
    });
  }

  /**
   * Render object recursively with variable substitution
   */
  renderObject(obj: any, variables: Record<string, any>): any {
    if (typeof obj === 'string') {
      return this.render(obj, variables);
    } else if (Array.isArray(obj)) {
      return obj.map(item => this.renderObject(item, variables));
    } else if (obj !== null && typeof obj === 'object') {
      const result: Record<string, any> = {};
      for (const [key, value] of Object.entries(obj)) {
        result[key] = this.renderObject(value, variables);
      }
      return result;
    }
    return obj;
  }

  /**
   * Get nested value using dot notation
   */
  private getNestedValue(obj: any, path: string): any {
    const keys = path.split('.');
    let value = obj;
    for (const key of keys) {
      if (value && typeof value === 'object') {
        value = value[key];
      } else {
        return undefined;
      }
    }
    return value;
  }
}
```

### 3.3 JSONPath Extractor

**File**: `frontend/src/lib/JSONPathExtractor.ts`

```typescript
import { JSONPath } from 'jsonpath-plus';

export class JSONPathExtractor {
  /**
   * Extract data from object using JSONPath expression
   */
  extract(data: any, path: string): any {
    try {
      const result = JSONPath({ path, json: data });
      return result.length === 1 ? result[0] : result;
    } catch (error) {
      console.error('JSONPath extraction failed:', error);
      return null;
    }
  }

  /**
   * Check if path exists in data
   */
  exists(data: any, path: string): boolean {
    try {
      const result = JSONPath({ path, json: data });
      return result.length > 0;
    } catch {
      return false;
    }
  }
}
```

---

## 4. UI Components - Wizard Builder

### 4.1 Event Builder Panel

**File**: `frontend/src/components/WizardBuilder/EventBuilderPanel.tsx`

```typescript
import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Switch,
  FormControlLabel,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import AddIcon from '@mui/icons-material/Add';
import { WizardEvent, EventTrigger } from '../../types/wizardEvent.types';
import { ActionList } from './ActionList';

interface EventBuilderPanelProps {
  event: WizardEvent | null;
  wizardId: string;
  steps: any[];
  onSave: (event: WizardEvent) => void;
  onCancel: () => void;
}

export const EventBuilderPanel: React.FC<EventBuilderPanelProps> = ({
  event,
  wizardId,
  steps,
  onSave,
  onCancel
}) => {
  const [formData, setFormData] = useState<Partial<WizardEvent>>(
    event || {
      wizard_id: wizardId,
      event_trigger: EventTrigger.STEP_ON_ENTRY,
      event_name: '',
      is_enabled: true,
      target_type: 'step',
      actions: []
    }
  );

  const handleSave = () => {
    onSave(formData as WizardEvent);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        {event ? 'Edit Event' : 'Create Event'}
      </Typography>

      {/* Event Configuration */}
      <Box sx={{ mt: 3 }}>
        <TextField
          fullWidth
          label="Event Name"
          value={formData.event_name}
          onChange={(e) => setFormData({ ...formData, event_name: e.target.value })}
          margin="normal"
          required
        />

        <FormControl fullWidth margin="normal">
          <InputLabel>Event Trigger</InputLabel>
          <Select
            value={formData.event_trigger}
            onChange={(e) => setFormData({ ...formData, event_trigger: e.target.value as EventTrigger })}
          >
            <MenuItem value={EventTrigger.STEP_ON_ENTRY}>Step: On Entry</MenuItem>
            <MenuItem value={EventTrigger.STEP_ON_EXIT}>Step: On Exit</MenuItem>
            <MenuItem value={EventTrigger.STEP_ON_VALIDATE}>Step: On Validate</MenuItem>
            <MenuItem value={EventTrigger.OPTIONSET_ON_LOAD}>Option Set: On Load</MenuItem>
            <MenuItem value={EventTrigger.OPTIONSET_ON_CHANGE}>Option Set: On Change</MenuItem>
            <MenuItem value={EventTrigger.OPTIONSET_ON_APPLY}>Option Set: On Apply</MenuItem>
            <MenuItem value={EventTrigger.OPTION_ON_CLICK}>Option: On Click</MenuItem>
            <MenuItem value={EventTrigger.OPTION_ON_SELECT}>Option: On Select</MenuItem>
            <MenuItem value={EventTrigger.WIZARD_ON_START}>Wizard: On Start</MenuItem>
            <MenuItem value={EventTrigger.WIZARD_ON_COMPLETE}>Wizard: On Complete</MenuItem>
          </Select>
        </FormControl>

        <FormControl fullWidth margin="normal">
          <InputLabel>Target Type</InputLabel>
          <Select
            value={formData.target_type}
            onChange={(e) => setFormData({ ...formData, target_type: e.target.value as any })}
          >
            <MenuItem value="step">Step</MenuItem>
            <MenuItem value="option_set">Option Set</MenuItem>
            <MenuItem value="option">Option</MenuItem>
            <MenuItem value="wizard">Wizard</MenuItem>
          </Select>
        </FormControl>

        {formData.target_type === 'step' && (
          <FormControl fullWidth margin="normal">
            <InputLabel>Target Step</InputLabel>
            <Select
              value={formData.target_id || ''}
              onChange={(e) => setFormData({ ...formData, target_id: e.target.value })}
            >
              {steps.map(step => (
                <MenuItem key={step.id} value={step.id}>
                  {step.title}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        )}

        <TextField
          fullWidth
          multiline
          rows={3}
          label="Description"
          value={formData.description || ''}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          margin="normal"
        />

        <FormControlLabel
          control={
            <Switch
              checked={formData.is_enabled}
              onChange={(e) => setFormData({ ...formData, is_enabled: e.target.checked })}
            />
          }
          label="Enabled"
        />
      </Box>

      {/* Actions Section */}
      <Box sx={{ mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Actions
        </Typography>
        <Alert severity="info" sx={{ mb: 2 }}>
          Actions execute in order when this event is triggered
        </Alert>

        <ActionList
          actions={formData.actions || []}
          onChange={(actions) => setFormData({ ...formData, actions })}
        />
      </Box>

      {/* Save/Cancel Buttons */}
      <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
        <Button variant="contained" onClick={handleSave}>
          Save Event
        </Button>
        <Button variant="outlined" onClick={onCancel}>
          Cancel
        </Button>
      </Box>
    </Box>
  );
};
```

---

**Document Status**: Part 1 - Types, Services, and Core Components
**Next Document**: Technical Spec - Output Renderers & Integration
