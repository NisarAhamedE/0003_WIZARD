Complete Wizard Action System - Enhanced Specification
Overview
This enhancement adds a powerful Event-Driven Action System to the Wizard Builder, enabling dynamic, interactive wizards that can:

Call external APIs
Execute MCP (Model Context Protocol) operations
Transform and display data dynamically
Populate fields based on API responses
Create truly interactive, data-driven workflows


Table of Contents

Event System Architecture
Action Types & Configurations
Wizard Builder Enhancements
Action Executor Engine
Output Renderers
Database Schema
API Specification
Implementation Examples
Integration with Existing System


1. Event System Architecture
Event Hierarchy
typescriptinterface WizardEventSystem {
  stepEvents: StepEvent[];
  optionSetEvents: OptionSetEvent[];
  optionEvents: OptionEvent[];
}

// Event trigger points
enum EventTrigger {
  // Step Events
  STEP_ON_ENTRY = 'step.onEntry',       // When user enters a step
  STEP_ON_EXIT = 'step.onExit',         // Before moving to next step
  STEP_ON_VALIDATE = 'step.onValidate', // During validation
  
  // Option Set Events
  OPTIONSET_ON_LOAD = 'optionSet.onLoad',     // When option set is rendered
  OPTIONSET_ON_CHANGE = 'optionSet.onChange', // When any value changes
  OPTIONSET_ON_APPLY = 'optionSet.onApply',   // Apply button clicked
  
  // Option Events (Individual Options)
  OPTION_ON_CLICK = 'option.onClick',       // When option is clicked
  OPTION_ON_SELECT = 'option.onSelect',     // When option is selected
  OPTION_ON_DESELECT = 'option.onDeselect', // When option is deselected
  OPTION_ON_CHANGE = 'option.onChange',     // When value changes (for inputs)
  
  // Global Events
  WIZARD_ON_START = 'wizard.onStart',     // When wizard execution starts
  WIZARD_ON_COMPLETE = 'wizard.onComplete' // When wizard completes
}
Event Structure
typescriptinterface WizardEvent {
  id: string;
  event_trigger: EventTrigger;
  event_name: string;
  description?: string;
  is_enabled: boolean;
  
  // What triggers this event
  trigger_config: TriggerConfig;
  
  // What actions to execute
  actions: Action[];
  
  // Conditional execution
  conditions?: EventCondition[];
  
  // Error handling
  error_handling: ErrorHandlingConfig;
}

interface TriggerConfig {
  trigger_type: EventTrigger;
  target_id: string; // step_id, option_set_id, or option_id
  target_type: 'step' | 'option_set' | 'option' | 'wizard';
}

interface EventCondition {
  field_id: string;
  operator: 'equals' | 'not_equals' | 'contains' | 'greater_than' | 'less_than' | 'is_empty' | 'is_not_empty';
  value: any;
  logic: 'AND' | 'OR';
}

2. Action Types & Configurations
Action Structure
typescriptinterface Action {
  id: string;
  action_name: string;
  action_type: ActionType;
  execution_order: number; // Multiple actions execute in order
  is_async: boolean;
  
  // Action configuration
  config: ActionConfig;
  
  // Input mapping
  input_mapping: InputMapping;
  
  // Output handling
  output_handling: OutputHandling;
  
  // Error handling
  on_error: 'continue' | 'stop' | 'retry';
  retry_count?: number;
  
  // Loading state
  loading_message?: string;
  show_loading_spinner: boolean;
}

enum ActionType {
  API_CALL = 'api_call',
  MCP_CALL = 'mcp_call',
  TRANSFORM_DATA = 'transform_data',
  SET_FIELD_VALUE = 'set_field_value',
  SHOW_MESSAGE = 'show_message',
  NAVIGATE = 'navigate',
  CUSTOM_SCRIPT = 'custom_script'
}
1. API Call Action
typescriptinterface ApiCallAction extends Action {
  config: {
    method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
    url: string; // Supports templating: "https://api.example.com/users/${userId}"
    headers: Record<string, string>;
    query_params: Record<string, any>;
    body?: any;
    timeout_ms: number;
    
    // Authentication
    auth: {
      type: 'none' | 'bearer' | 'basic' | 'api_key' | 'oauth2';
      credentials: Record<string, string>;
    };
    
    // Response handling
    response_mapping: {
      success_path: string; // JSONPath: "$.data.items"
      error_path: string;   // JSONPath: "$.error.message"
    };
  };
}

// Example API Call Action
{
  action_name: "Fetch User Profile",
  action_type: "api_call",
  execution_order: 1,
  is_async: true,
  config: {
    method: "GET",
    url: "https://api.example.com/users/${userId}",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer ${access_token}"
    },
    auth: {
      type: "bearer",
      credentials: { token_field: "access_token" }
    },
    response_mapping: {
      success_path: "$.data.user",
      error_path: "$.error.message"
    }
  },
  input_mapping: {
    userId: { source: "option_set", field_id: "user_id_field" },
    access_token: { source: "context", field: "auth.token" }
  },
  output_handling: {
    display_type: "table",
    target_option_set_id: "user_details_display"
  }
}
2. MCP (Model Context Protocol) Action
typescriptinterface McpCallAction extends Action {
  config: {
    mcp_server: string; // MCP server identifier
    tool_name: string;  // Tool to invoke
    parameters: Record<string, any>;
    
    // MCP-specific settings
    mcp_config: {
      timeout_ms: number;
      max_retries: number;
      streaming: boolean; // For streaming responses
    };
    
    // Response parsing
    response_format: 'json' | 'text' | 'stream';
    response_schema?: object; // JSON Schema for validation
  };
}

// Example MCP Call Action
{
  action_name: "Query Database via MCP",
  action_type: "mcp_call",
  execution_order: 1,
  is_async: true,
  config: {
    mcp_server: "database_server",
    tool_name: "execute_query",
    parameters: {
      query: "SELECT * FROM products WHERE category = :category",
      params: { category: "${selected_category}" }
    },
    mcp_config: {
      timeout_ms: 30000,
      max_retries: 2,
      streaming: false
    },
    response_format: "json",
    response_schema: {
      type: "array",
      items: {
        type: "object",
        properties: {
          id: { type: "string" },
          name: { type: "string" },
          price: { type: "number" }
        }
      }
    }
  },
  input_mapping: {
    selected_category: { 
      source: "option_set", 
      field_id: "category_dropdown" 
    }
  },
  output_handling: {
    display_type: "table",
    columns: ["id", "name", "price"],
    target_option_set_id: "product_results"
  }
}
3. Transform Data Action
typescriptinterface TransformDataAction extends Action {
  config: {
    transformation_type: 'jmespath' | 'javascript' | 'python';
    transformation_script: string;
    
    // For JavaScript/Python
    script_context: Record<string, any>;
    
    // Output schema
    output_schema?: object;
  };
}

// Example Transform Action
{
  action_name: "Calculate Total Price",
  action_type: "transform_data",
  execution_order: 2,
  config: {
    transformation_type: "javascript",
    transformation_script: `
      const items = input.selectedItems;
      const total = items.reduce((sum, item) => sum + item.price * item.quantity, 0);
      const tax = total * 0.1;
      const shipping = total > 100 ? 0 : 15;
      
      return {
        subtotal: total,
        tax: tax,
        shipping: shipping,
        total: total + tax + shipping
      };
    `
  },
  input_mapping: {
    selectedItems: { 
      source: "context", 
      field: "cart.items" 
    }
  },
  output_handling: {
    display_type: "custom",
    target_option_set_id: "price_summary"
  }
}
4. Set Field Value Action
typescriptinterface SetFieldValueAction extends Action {
  config: {
    target_fields: Array<{
      option_set_id: string;
      field_path: string; // For nested fields
      value_source: 'static' | 'dynamic' | 'computed';
      value: any;
    }>;
    
    // Populate multiple fields at once
    bulk_update: boolean;
  };
}

// Example Set Field Action
{
  action_name: "Populate Address Fields",
  action_type: "set_field_value",
  execution_order: 3,
  config: {
    target_fields: [
      {
        option_set_id: "street_address",
        value_source: "dynamic",
        value: "${api_response.address.street}"
      },
      {
        option_set_id: "city",
        value_source: "dynamic",
        value: "${api_response.address.city}"
      },
      {
        option_set_id: "zipcode",
        value_source: "dynamic",
        value: "${api_response.address.zip}"
      }
    ],
    bulk_update: true
  },
  input_mapping: {
    api_response: { source: "action_output", action_id: "fetch_user_profile" }
  }
}
5. Show Message Action
typescriptinterface ShowMessageAction extends Action {
  config: {
    message_type: 'success' | 'error' | 'warning' | 'info';
    message: string; // Supports templating
    duration_ms?: number;
    position: 'top' | 'bottom' | 'center';
    is_dismissible: boolean;
  };
}

3. Wizard Builder Enhancements
New UI Components in Builder
A. Action Builder Panel
typescript<ActionBuilderPanel>
  {/* Event Selection */}
  <Box>
    <Typography variant="h6">Event Configuration</Typography>
    
    <FormControl fullWidth>
      <InputLabel>Event Trigger</InputLabel>
      <Select
        value={selectedEvent}
        onChange={handleEventChange}
      >
        <MenuItem value="step.onEntry">Step: On Entry</MenuItem>
        <MenuItem value="step.onExit">Step: On Exit</MenuItem>
        <MenuItem value="optionSet.onApply">Option Set: On Apply</MenuItem>
        <MenuItem value="option.onClick">Option: On Click</MenuItem>
        {/* ... more triggers */}
      </Select>
    </FormControl>
    
    <TextField
      fullWidth
      label="Event Name"
      value={eventName}
      placeholder="e.g., Load User Data"
      margin="normal"
    />
    
    <TextField
      fullWidth
      multiline
      rows={2}
      label="Description"
      value={eventDescription}
      margin="normal"
    />
  </Box>

  {/* Conditions (Optional) */}
  <Box sx={{ mt: 3 }}>
    <Typography variant="h6">Conditions (Optional)</Typography>
    <Typography variant="caption" color="text.secondary">
      Execute actions only when these conditions are met
    </Typography>
    
    {conditions.map((condition, idx) => (
      <ConditionBuilder
        key={idx}
        condition={condition}
        onChange={(updated) => updateCondition(idx, updated)}
        onRemove={() => removeCondition(idx)}
      />
    ))}
    
    <Button onClick={addCondition} startIcon={<AddIcon />}>
      Add Condition
    </Button>
  </Box>

  {/* Actions List */}
  <Box sx={{ mt: 3 }}>
    <Typography variant="h6">Actions</Typography>
    <Typography variant="caption" color="text.secondary">
      Actions execute in order. Drag to reorder.
    </Typography>
    
    <DragDropContext onDragEnd={handleReorderActions}>
      <Droppable droppableId="actions">
        {(provided) => (
          <Box {...provided.droppableProps} ref={provided.innerRef}>
            {actions.map((action, idx) => (
              <Draggable key={action.id} draggableId={action.id} index={idx}>
                {(provided) => (
                  <ActionCard
                    ref={provided.innerRef}
                    {...provided.draggableProps}
                    action={action}
                    dragHandleProps={provided.dragHandleProps}
                    onEdit={() => openActionEditor(action)}
                    onDelete={() => deleteAction(action.id)}
                  />
                )}
              </Draggable>
            ))}
            {provided.placeholder}
          </Box>
        )}
      </Droppable>
    </DragDropContext>
    
    <Button 
      variant="outlined" 
      startIcon={<AddIcon />}
      onClick={openActionTypeSelector}
    >
      Add Action
    </Button>
  </Box>

  {/* Error Handling */}
  <Box sx={{ mt: 3 }}>
    <Typography variant="h6">Error Handling</Typography>
    
    <FormControl fullWidth>
      <InputLabel>On Error</InputLabel>
      <Select value={onError}>
        <MenuItem value="continue">Continue to Next Action</MenuItem>
        <MenuItem value="stop">Stop All Actions</MenuItem>
        <MenuItem value="retry">Retry Action</MenuItem>
      </Select>
    </FormControl>
    
    {onError === 'retry' && (
      <TextField
        type="number"
        label="Retry Count"
        value={retryCount}
        InputProps={{ inputProps: { min: 1, max: 5 } }}
        margin="normal"
      />
    )}
  </Box>
</ActionBuilderPanel>
B. Action Type Selector
typescript<ActionTypeSelectorDialog open={showSelector}>
  <DialogTitle>Choose Action Type</DialogTitle>
  <DialogContent>
    <Grid container spacing={2}>
      <Grid item xs={6}>
        <ActionTypeCard
          icon={<ApiIcon />}
          title="API Call"
          description="Call external REST APIs"
          onClick={() => selectActionType('api_call')}
        />
      </Grid>
      
      <Grid item xs={6}>
        <ActionTypeCard
          icon={<StorageIcon />}
          title="MCP Call"
          description="Execute MCP operations"
          onClick={() => selectActionType('mcp_call')}
        />
      </Grid>
      
      <Grid item xs={6}>
        <ActionTypeCard
          icon={<TransformIcon />}
          title="Transform Data"
          description="Process and transform data"
          onClick={() => selectActionType('transform_data')}
        />
      </Grid>
      
      <Grid item xs={6}>
        <ActionTypeCard
          icon={<EditIcon />}
          title="Set Field Value"
          description="Update field values"
          onClick={() => selectActionType('set_field_value')}
        />
      </Grid>
      
      <Grid item xs={6}>
        <ActionTypeCard
          icon={<MessageIcon />}
          title="Show Message"
          description="Display notifications"
          onClick={() => selectActionType('show_message')}
        />
      </Grid>
      
      <Grid item xs={6}>
        <ActionTypeCard
          icon={<CodeIcon />}
          title="Custom Script"
          description="Run custom JavaScript"
          onClick={() => selectActionType('custom_script')}
        />
      </Grid>
    </Grid>
  </DialogContent>
</ActionTypeSelectorDialog>
C. API Call Action Editor
typescript<ApiCallActionEditor action={editingAction}>
  <Tabs value={activeTab} onChange={handleTabChange}>
    <Tab label="Basic" />
    <Tab label="Headers" />
    <Tab label="Body" />
    <Tab label="Input Mapping" />
    <Tab label="Output Handling" />
    <Tab label="Testing" />
  </Tabs>

  {/* Basic Tab */}
  <TabPanel value={activeTab} index={0}>
    <TextField
      fullWidth
      label="Action Name"
      value={actionName}
      margin="normal"
    />
    
    <FormControl fullWidth margin="normal">
      <InputLabel>HTTP Method</InputLabel>
      <Select value={method}>
        <MenuItem value="GET">GET</MenuItem>
        <MenuItem value="POST">POST</MenuItem>
        <MenuItem value="PUT">PUT</MenuItem>
        <MenuItem value="DELETE">DELETE</MenuItem>
      </Select>
    </FormControl>
    
    <TextField
      fullWidth
      label="URL"
      value={url}
      placeholder="https://api.example.com/endpoint"
      helperText="Use ${variableName} for dynamic values"
      margin="normal"
    />
    
    <TextField
      fullWidth
      type="number"
      label="Timeout (ms)"
      value={timeout}
      InputProps={{ inputProps: { min: 1000, max: 60000 } }}
      margin="normal"
    />
  </TabPanel>

  {/* Headers Tab */}
  <TabPanel value={activeTab} index={1}>
    <Typography variant="h6" gutterBottom>Request Headers</Typography>
    
    {headers.map((header, idx) => (
      <Box key={idx} sx={{ display: 'flex', gap: 1, mb: 1 }}>
        <TextField
          label="Header Name"
          value={header.name}
          onChange={(e) => updateHeader(idx, 'name', e.target.value)}
          sx={{ flex: 1 }}
        />
        <TextField
          label="Header Value"
          value={header.value}
          onChange={(e) => updateHeader(idx, 'value', e.target.value)}
          sx={{ flex: 2 }}
          helperText="Use ${variable} for dynamic values"
        />
        <IconButton onClick={() => removeHeader(idx)}>
          <DeleteIcon />
        </IconButton>
      </Box>
    ))}
    
    <Button onClick={addHeader} startIcon={<AddIcon />}>
      Add Header
    </Button>
    
    <Divider sx={{ my: 2 }} />
    
    <Typography variant="h6" gutterBottom>Authentication</Typography>
    
    <FormControl fullWidth>
      <InputLabel>Auth Type</InputLabel>
      <Select value={authType}>
        <MenuItem value="none">None</MenuItem>
        <MenuItem value="bearer">Bearer Token</MenuItem>
        <MenuItem value="basic">Basic Auth</MenuItem>
        <MenuItem value="api_key">API Key</MenuItem>
      </Select>
    </FormControl>
    
    {authType === 'bearer' && (
      <TextField
        fullWidth
        label="Token"
        value={token}
        type="password"
        margin="normal"
        helperText="Use ${token_variable} for dynamic tokens"
      />
    )}
  </TabPanel>

  {/* Body Tab (for POST/PUT) */}
  <TabPanel value={activeTab} index={2}>
    <FormControl fullWidth margin="normal">
      <InputLabel>Body Type</InputLabel>
      <Select value={bodyType}>
        <MenuItem value="json">JSON</MenuItem>
        <MenuItem value="form-data">Form Data</MenuItem>
        <MenuItem value="x-www-form-urlencoded">URL Encoded</MenuItem>
        <MenuItem value="raw">Raw</MenuItem>
      </Select>
    </FormControl>
    
    <Box sx={{ mt: 2 }}>
      <Typography variant="subtitle2" gutterBottom>
        Request Body
      </Typography>
      <CodeEditor
        value={requestBody}
        language="json"
        onChange={setRequestBody}
        height="300px"
        placeholder={`{
  "key": "value",
  "dynamic": "\${variable_name}"
}`}
      />
    </Box>
    
    <Alert severity="info" sx={{ mt: 2 }}>
      <AlertTitle>Using Variables</AlertTitle>
      Reference wizard fields using: <code>$&#123;option_set_id&#125;</code>
      <br />
      Reference context values using: <code>$&#123;context.field.path&#125;</code>
      <br />
      Reference previous action outputs: <code>$&#123;action:action_name.path&#125;</code>
    </Alert>
  </TabPanel>

  {/* Input Mapping Tab */}
  <TabPanel value={activeTab} index={3}>
    <Typography variant="h6" gutterBottom>Input Mapping</Typography>
    <Typography variant="body2" color="text.secondary" paragraph>
      Map wizard fields to variables used in the API call
    </Typography>
    
    {inputMappings.map((mapping, idx) => (
      <Card key={idx} sx={{ mb: 2, p: 2 }}>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'start' }}>
          <TextField
            label="Variable Name"
            value={mapping.variable}
            onChange={(e) => updateMapping(idx, 'variable', e.target.value)}
            placeholder="userId"
            sx={{ flex: 1 }}
          />
          
          <FormControl sx={{ flex: 1 }}>
            <InputLabel>Source Type</InputLabel>
            <Select
              value={mapping.sourceType}
              onChange={(e) => updateMapping(idx, 'sourceType', e.target.value)}
            >
              <MenuItem value="option_set">Option Set</MenuItem>
              <MenuItem value="context">Context</MenuItem>
              <MenuItem value="action_output">Action Output</MenuItem>
              <MenuItem value="static">Static Value</MenuItem>
            </Select>
          </FormControl>
          
          {mapping.sourceType === 'option_set' && (
            <FormControl sx={{ flex: 1 }}>
              <InputLabel>Field</InputLabel>
              <Select
                value={mapping.fieldId}
                onChange={(e) => updateMapping(idx, 'fieldId', e.target.value)}
              >
                {availableFields.map(field => (
                  <MenuItem key={field.id} value={field.id}>
                    {field.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          )}
          
          {mapping.sourceType === 'static' && (
            <TextField
              label="Static Value"
              value={mapping.value}
              onChange={(e) => updateMapping(idx, 'value', e.target.value)}
              sx={{ flex: 1 }}
            />
          )}
          
          <IconButton onClick={() => removeMapping(idx)} color="error">
            <DeleteIcon />
          </IconButton>
        </Box>
      </Card>
    ))}
    
    <Button onClick={addMapping} startIcon={<AddIcon />} variant="outlined">
      Add Input Mapping
    </Button>
  </TabPanel>

  {/* Output Handling Tab */}
  <TabPanel value={activeTab} index={4}>
    <Typography variant="h6" gutterBottom>Output Handling</Typography>
    
    <TextField
      fullWidth
      label="Success Response Path (JSONPath)"
      value={successPath}
      placeholder="$.data.items"
      helperText="JSONPath to extract success data from response"
      margin="normal"
    />
    
    <TextField
      fullWidth
      label="Error Response Path (JSONPath)"
      value={errorPath}
      placeholder="$.error.message"
      helperText="JSONPath to extract error message"
      margin="normal"
    />
    
    <Divider sx={{ my: 2 }} />
    
    <Typography variant="subtitle1" gutterBottom>
      Display Configuration
    </Typography>
    
    <FormControl fullWidth margin="normal">
      <InputLabel>Display Type</InputLabel>
      <Select 
        value={displayType}
        onChange={(e) => setDisplayType(e.target.value)}
      >
        <MenuItem value="table">Table</MenuItem>
        <MenuItem value="dropdown">Dropdown/Select</MenuItem>
        <MenuItem value="card_grid">Card Grid</MenuItem>
        <MenuItem value="list">List</MenuItem>
        <MenuItem value="json">JSON Viewer</MenuItem>
        <MenuItem value="custom">Custom Template</MenuItem>
        <MenuItem value="hidden">Hidden (No Display)</MenuItem>
      </Select>
    </FormControl>
    
    {displayType === 'table' && (
      <TableDisplayConfig
        columns={tableColumns}
        onColumnsChange={setTableColumns}
        responseData={testResponseData}
      />
    )}
    
    {displayType === 'dropdown' && (
      <DropdownDisplayConfig
        labelField={dropdownLabelField}
        valueField={dropdownValueField}
        onConfigChange={updateDropdownConfig}
      />
    )}
    
    <FormControl fullWidth margin="normal">
      <InputLabel>Target Option Set</InputLabel>
      <Select value={targetOptionSetId}>
        <MenuItem value="">Create New Option Set</MenuItem>
        {availableOptionSets.map(os => (
          <MenuItem key={os.id} value={os.id}>
            {os.name}
          </MenuItem>
        ))}
      </Select>
      <FormHelperText>
        Where to display the API response
      </FormHelperText>
    </FormControl>
  </TabPanel>

  {/* Testing Tab */}
  <TabPanel value={activeTab} index={5}>
    <Typography variant="h6" gutterBottom>Test API Call</Typography>
    
    <Alert severity="info" sx={{ mb: 2 }}>
      Test your API configuration with sample data before saving
    </Alert>
    
    <Typography variant="subtitle2" gutterBottom>
      Sample Input Data (JSON)
    </Typography>
    <CodeEditor
      value={testInputData}
      language="json"
      onChange={setTestInputData}
      height="150px"
      placeholder={`{
  "userId": "123",
  "category": "electronics"
}`}
    />
    
    <Button
      variant="contained"
      onClick={handleTestApiCall}
      disabled={isTestingApi}
      startIcon={isTestingApi ? <CircularProgress size={20} /> : <PlayArrowIcon />}
      sx={{ mt: 2 }}
    >
      {isTestingApi ? 'Testing...' : 'Test API Call'}
    </Button>
    
    {testResult && (
      <Box sx={{ mt: 3 }}>
        <Typography variant="subtitle2" gutterBottom>
          Test Result
        </Typography>
        
        <Alert 
          severity={testResult.success ? 'success' : 'error'}
          sx={{ mb: 2 }}
        >
          {testResult.success 
            ? `Success! Status: ${testResult.statusCode}`
            : `Error: ${testResult.error}`
          }
        </Alert>
        
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography>Response Data</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <CodeEditor
              value={JSON.stringify(testResult.data, null, 2)}
              language="json"
              readOnly
              height="300px"
            />
          </AccordionDetails>
        </Accordion>
        
        {displayType !== 'hidden' && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Preview Display
            </Typography>
            <OutputRenderer
              type={displayType}
              data={testResult.data}
              config={outputConfig}
            />
          </Box>
        )}
      </Box>
    )}
  </TabPanel>
</ApiCallActionEditor>
D. Apply Button Option Set
New selection type for Option Sets:
typescriptinterface ApplyButtonOptionSet extends OptionSet {
  selection_type: 'apply_button';
  
  // Button configuration
  button_config: {
    button_text: string;
    button_variant: 'contained' | 'outlined' | 'text';
    button_color: 'primary' | 'secondary' | 'success' | 'error';
    button_icon?: string;
    loading_text?: string;
    success_text?: string;
    disabled_text?: string;
  };
  
  // Apply button triggers actions
  actions: Action[];
}

// In Wizard Builder
<FormControl fullWidth margin="normal">
  <InputLabel>Selection Type</InputLabel>
  <Select value={selectionType}>
    {/* ... existing types */}
    <MenuItem value="apply_button">
      <Box sx={{ display: 'flex', alignItems: 'center' }}>
        <TouchAppIcon sx={{ mr: 1 }} />
        Apply Button (Execute Actions)
      </Box>
    </MenuItem>
  </Select>
</FormControl>

{selectionType === 'apply_button' && (
  <ApplyButtonConfig
    config={buttonConfig}
    actions={buttonActions}
    onConfigChange={setButtonConfig}
    onActionsChange={setButtonActions}
  />
)}

4. Action Executor Engine
Core Execution Engine
typescriptclass ActionExecutor {
  private context: WizardExecutionContext;
  private actionResults: Map<string, any> = new Map();
  
  constructor(context: WizardExecutionContext) {
    this.context = context;
  }
  
  /**
   * Execute a list of actions in sequence
   */
  async executeActions(
    actions: Action[],
    eventData: EventData
  ): Promise<ActionExecutionResult> {
    const results: ActionResult[] = [];
    
    // Sort actions by execution order
    const sortedActions = [...actions].sort(
      (a, b) => a.execution_order - b.execution_order
    );
    
    for (const action of sortedActions) {
      try {
        // Check if action should execute based on conditions
        if (!this.shouldExecuteAction(action, eventData)) {
          continue;
        }
        
        // Show loading state
        if (action.show_loading_spinner) {
          this.showLoadingState(action);
        }
        
        // Resolve input values
        const inputValues = await this.resolveInputMapping(
          action.input_mapping,
          eventData
        );
        
        // Execute the action
        const result = await this.executeAction(action, inputValues);
        
        // Store result for downstream actions
        this.actionResults.set(action.id, result);
        
        // Handle output
        await this.handleActionOutput(action, result);
        
        results.push({
          action_id: action.id,
          success: true,
          data: result
        });
        
      } catch (error) {
        const errorResult = await this.handleActionError(
          action,
          error,
          eventData
        );
        
        results.push(errorResult);
        
        if (action.on_error === 'stop') {
          break;
        }
      } finally {
        this.hideLoadingState(action);
      }
    }
    
    return {
      success: results.every(r => r.success),
      results
    };
  }
  
  /**
   * Execute individual action based on type
   */
  private async executeAction(
    action: Action,
    inputValues: Record<string, any>
  ): Promise<any> {
    switch (action.action_type) {
      case ActionType.API_CALL:
        return this.executeApiCall(action as ApiCallAction, inputValues);
      
      case ActionType.MCP_CALL:
        return this.executeMcpCall(action as McpCallAction, inputValues);
      
      case ActionType.TRANSFORM_DATA:
        return this.executeTransform(action as TransformDataAction, inputValues);
      
      case ActionType.SET_FIELD_VALUE:
        return this.executeSetFieldValue(action as SetFieldValueAction, inputValues);
      
      case ActionType.SHOW_MESSAGE:
        return this.executeShowMessage(action as ShowMessageAction, inputValues);
      
      default:
        throw new Error(`Unknown action type: ${action.action_type}`);
    }
  }
  
  /**
   * Execute API Call
   */
  private async executeApiCall(
    action: ApiCallAction,
    inputValues: Record<string, any>
  ): Promise<any> {
    const config = action.config;
    
    // Replace template variables in URL
    const url = this.replaceTemplateVariables(config.url, inputValues);
    
    // Build headers
    const headers = this.buildHeaders(config.headers, inputValues);
    
    // Build request body
    const body = config.body 
      ? this.replaceTemplateVariables(
          JSON.stringify(config.body),
          inputValues
        )
      : undefined;
    
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
    
    // Extract success data using JSONPath
    const successData = config.response_mapping.success_path
      ? this.extractJsonPath(data, config.response_mapping.success_path)
      : data;
    
    return successData;
  }
  
  /**
   * Execute MCP Call
   */
  private async executeMcpCall(
    action: McpCallAction,
    inputValues: Record<string, any>
  ): Promise<any> {
    const config = action.config;
    
    // Replace template variables in parameters
    const parameters = this.replaceTemplateVariables(
      JSON.stringify(config.parameters),
      inputValues
    );
    
    // Call MCP service
    const response = await mcpService.callTool(
      config.mcp_server,
      config.tool_name,
      JSON.parse(parameters)
    );
    
    // Validate response against schema if provided
    if (config.response_schema) {
      this.validateJsonSchema(response, config.response_schema);
    }
    
    return response;
  }
  
  /**
   * Transform data using script
   */
  private executeTransform(
    action: TransformDataAction,
    inputValues: Record<string, any>
  ): any {
    const config = action.config;
    
    switch (config.transformation_type) {
      case 'javascript':
        return this.executeJavaScriptTransform(
          config.transformation_script,
          inputValues
        );
      
      case 'jmespath':
        return this.executeJmesPathTransform(
          config.transformation_script,
          inputValues
        );
      
      default:
        throw new Error(`Unsupported transformation type: ${config.transformation_type}`);
    }
  }
  
  /**
   * Execute JavaScript transformation safely
   */
  private executeJavaScriptTransform(
    script: string,
    input: Record<string, any>
  ): any {
    // Create safe execution context
    const context = {
      input,
      console: {
        log: (...args: any[]) => console.log('[Transform]', ...args)
      },
      // Add safe utility functions
      JSON,
      Math,
      Date
    };
    
    // Execute in isolated context
    const func = new Function(
      'context',
      `with (context) { ${script} }`
    );
    
    return func(context);
  }
  
  /**
   * Resolve input mapping from various sources
   */
  private async resolveInputMapping(
    mapping: InputMapping,
    eventData: EventData
  ): Promise<Record<string, any>> {
    const resolved: Record<string, any> = {};
    
    for (const [key, mapConfig] of Object.entries(mapping)) {
      switch (mapConfig.source) {
        case 'option_set':
          resolved[key] = this.context.getFieldValue(mapConfig.field_id);
          break;
        
        case 'context':
          resolved[key] = this.getNestedValue(
            this.context.data,
            mapConfig.field
          );
          break;
        
        case 'action_output':
          resolved[key] = this.actionResults.get(mapConfig.action_id);
          break;
        
        case 'static':
          resolved[key] = mapConfig.value;
          break;
        
        case 'event_data':
          resolved[key] = eventData[mapConfig.field];
          break;
      }
    }
    
    return resolved;
  }
  
  /**
   * Handle action output based on configuration
   */
  private async handleActionOutput(
    action: Action,
    result: any
  ): Promise<void> {
    const outputConfig = action.output_handling;
    
    if (!outputConfig || outputConfig.display_type === 'hidden') {
      return;
    }
    
    // Get or create target option set
    const targetOptionSet = outputConfig.target_option_set_id
      ? this.context.getOptionSet(outputConfig.target_option_set_id)
      : await this.createDynamicOptionSet(action, outputConfig);
    
    // Render output based on display type
    await this.renderOutput(
      targetOptionSet,
      result,
      outputConfig
    );
  }
  
  /**
   * Replace template variables in string
   */
  private replaceTemplateVariables(
    template: string,
    values: Record<string, any>
  ): string {
    return template.replace(/\$\{([^}]+)\}/g, (match, key) => {
      const value = this.getNestedValue(values, key);
      return value !== undefined ? String(value) : match;
    });
  }
  
  /**
   * Extract value using JSONPath
   */
  private extractJsonPath(data: any, path: string): any {
    // Use JSONPath library (e.g., jsonpath-plus)
    return JSONPath({ path, json: data });
  }
  
  /**
   * Get nested value from object using dot notation
   */
  private getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((acc, part) => acc?.[part], obj);
  }
}

5. Output Renderers
Dynamic Output Display Components
typescript/**
 * Master Output Renderer
 */
const OutputRenderer: React.FC<{
  type: OutputDisplayType;
  data: any;
  config: OutputConfig;
}> = ({ type, data, config }) => {
  switch (type) {
    case 'table':
      return <TableRenderer data={data} config={config} />;
    
    case 'dropdown':
      return <DropdownRenderer data={data} config={config} />;
    
    case 'card_grid':
      return <CardGridRenderer data={data} config={config} />;
    
    case 'list':
      return <ListRenderer data={data} config={config} />;
    
    case 'document':
      return <DocumentRenderer data={data} config={config} />;
    
    case 'image':
      return <ImageRenderer data={data} config={config} />;
    
    case 'code':
      return <CodeRenderer data={data} config={config} />;
    
    case 'json':
      return <JsonRenderer data={data} config={config} />;
    
    case 'chart':
      return <ChartRenderer data={data} config={config} />;
    
    case 'custom':
      return <CustomRenderer data={data} config={config} />;
    
    default:
      return <Typography>Unsupported display type: {type}</Typography>;
  }
};
1. Table Renderer
typescriptconst TableRenderer: React.FC<{
  data: any[];
  config: TableConfig;
}> = ({ data, config }) => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(config.rows_per_page || 10);
  
  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            {config.columns.map(col => (
              <TableCell key={col.field}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  {col.icon && <Icon sx={{ mr: 1 }}>{col.icon}</Icon>}
                  {col.label}
                  {col.sortable && <SortIcon />}
                </Box>
              </TableCell>
            ))}
            {config.show_actions && (
              <TableCell>Actions</TableCell>
            )}
          </TableRow>
        </TableHead>
        
        <TableBody>
          {data
            .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
            .map((row, idx) => (
              <TableRow key={idx} hover>
                {config.columns.map(col => (
                  <TableCell key={col.field}>
                    {formatCellValue(row[col.field], col.format)}
                  </TableCell>
                ))}
                {config.show_actions && (
                  <TableCell>
                    <IconButton size="small" onClick={() => handleView(row)}>
                      <VisibilityIcon />
                    </IconButton>
                    {config.allow_select && (
                      <IconButton 
                        size="small" 
                        color="primary"
                        onClick={() => handleSelect(row)}
                      >
                        <CheckCircleIcon />
                      </IconButton>
                    )}
                  </TableCell>
                )}
              </TableRow>
            ))}
        </TableBody>
      </Table>
      
      <TablePagination
        component="div"
        count={data.length}
        page={page}
        onPageChange={(e, newPage) => setPage(newPage)}
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={(e) => setRowsPerPage(parseInt(e.target.value))}
      />
    </TableContainer>
  );
};

interface TableConfig {
  columns: Array<{
    field: string;
    label: string;
    icon?: string;
    sortable?: boolean;
    format?: 'text' | 'number' | 'currency' | 'date' | 'boolean' | 'link';
  }>;
  rows_per_page?: number;
  show_actions: boolean;
  allow_select: boolean;
  searchable: boolean;
}
2. Dropdown/Select Renderer
typescriptconst DropdownRenderer: React.FC<{
  data: any[];
  config: DropdownConfig;
}> = ({ data, config }) => {
  const [selectedValue, setSelectedValue] = useState<any>(null);
  
  return (
    <FormControl fullWidth>
      <InputLabel>{config.label}</InputLabel>
      <Select
        value={selectedValue}
        onChange={(e) => {
          setSelectedValue(e.target.value);
          config.onChange?.(e.target.value);
        }}
      >
        {data.map((item, idx) => (
          <MenuItem 
            key={idx} 
            value={item[config.value_field]}
          >
            {config.show_icon && item[config.icon_field] && (
              <ListItemIcon>
                {item[config.icon_field]}
              </ListItemIcon>
            )}
            <ListItemText
              primary={item[config.label_field]}
              secondary={config.description_field && item[config.description_field]}
            />
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};

interface DropdownConfig {
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
3. Card Grid Renderer
typescriptconst CardGridRenderer: React.FC<{
  data: any[];
  config: CardGridConfig;
}> = ({ data, config }) => {
  return (
    <Grid container spacing={2}>
      {data.map((item, idx) => (
        <Grid item xs={12} sm={6} md={4} key={idx}>
          <Card>
            {config.show_image && item[config.image_field] && (
              <CardMedia
                component="img"
                height={config.image_height || 140}
                image={item[config.image_field]}
                alt={item[config.title_field]}
              />
            )}
            
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {item[config.title_field]}
              </Typography>
              
              {config.subtitle_field && (
                <Typography variant="body2" color="text.secondary">
                  {item[config.subtitle_field]}
                </Typography>
              )}
              
              {config.description_field && (
                <Typography variant="body2" sx={{ mt: 1 }}>
                  {item[config.description_field]}
                </Typography>
              )}
              
              {config.custom_fields.map(field => (
                <Box key={field.name} sx={{ mt: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    {field.label}:
                  </Typography>
                  <Typography variant="body2">
                    {item[field.name]}
                  </Typography>
                </Box>
              ))}
            </CardContent>
            
            {config.show_actions && (
              <CardActions>
                <Button 
                  size="small" 
                  onClick={() => config.onSelect?.(item)}
                >
                  Select
                </Button>
                <Button 
                  size="small"
                  onClick={() => config.onView?.(item)}
                >
                  Details
                </Button>
              </CardActions>
            )}
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};
4. Document Renderer
typescriptconst DocumentRenderer: React.FC<{
  data: any;
  config: DocumentConfig;
}> = ({ data, config }) => {
  return (
    <Paper sx={{ p: 3 }}>
      {config.show_title && (
        <Typography variant="h5" gutterBottom>
          {data[config.title_field]}
        </Typography>
      )}
      
      {config.show_metadata && (
        <Box sx={{ mb: 2 }}>
          {config.metadata_fields.map(field => (
            <Chip
              key={field}
              label={`${field}: ${data[field]}`}
              size="small"
              sx={{ mr: 1 }}
            />
          ))}
        </Box>
      )}
      
      <Divider sx={{ my: 2 }} />
      
      {config.content_type === 'html' ? (
        <div dangerouslySetInnerHTML={{ __html: data[config.content_field] }} />
      ) : config.content_type === 'markdown' ? (
        <ReactMarkdown>{data[config.content_field]}</ReactMarkdown>
      ) : (
        <Typography style={{ whiteSpace: 'pre-wrap' }}>
          {data[config.content_field]}
        </Typography>
      )}
      
      {config.show_download && (
        <Button
          variant="outlined"
          startIcon={<DownloadIcon />}
          onClick={() => handleDownload(data)}
          sx={{ mt: 2 }}
        >
          Download Document
        </Button>
      )}
    </Paper>
  );
};
5. Image Renderer
typescriptconst ImageRenderer: React.FC<{
  data: any;
  config: ImageConfig;
}> = ({ data, config }) => {
  const imageUrl = typeof data === 'string' ? data : data[config.url_field];
  
  return (
    <Box>
      {config.show_title && data[config.title_field] && (
        <Typography variant="h6" gutterBottom>
          {data[config.title_field]}
        </Typography>
      )}
      
      <Box
        component="img"
        src={imageUrl}
        alt={data[config.alt_field] || 'Image'}
        sx={{
          width: config.width || '100%',
          height: config.height || 'auto',
          maxWidth: '100%',
          borderRadius: config.border_radius || 1,
          objectFit: config.object_fit || 'cover'
        }}
      />
      
      {config.show_caption && data[config.caption_field] && (
        <Typography 
          variant="caption" 
          display="block" 
          sx={{ mt: 1, textAlign: 'center' }}
        >
          {data[config.caption_field]}
        </Typography>
      )}
    </Box>
  );
};
6. Code Renderer
typescriptconst CodeRenderer: React.FC<{
  data: any;
  config: CodeConfig;
}> = ({ data, config }) => {
  const [copied, setCopied] = useState(false);
  
  const codeString = typeof data === 'string' 
    ? data 
    : data[config.code_field];
  
  const handleCopy = () => {
    navigator.clipboard.writeText(codeString);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  
  return (
    <Box sx={{ position: 'relative' }}>
      {config.show_language && (
        <Chip 
          label={config.language} 
          size="small"
          sx={{ position: 'absolute', top: 8, left: 8, zIndex: 1 }}
        />
      )}
      
      <IconButton
        onClick={handleCopy}
        sx={{ position: 'absolute', top: 8, right: 8, zIndex: 1 }}
      >
        {copied ? <CheckIcon /> : <ContentCopyIcon />}
      </IconButton>
      
      <SyntaxHighlighter
        language={config.language}
        style={config.theme === 'dark' ? vscDarkPlus : vs}
        showLineNumbers={config.show_line_numbers}
        wrapLines={config.wrap_lines}
      >
        {codeString}
      </SyntaxHighlighter>
    </Box>
  );
};
7. Chart Renderer
typescriptconst ChartRenderer: React.FC<{
  data: any[];
  config: ChartConfig;
}> = ({ data, config }) => {
  const chartData = {
    labels: data.map(item => item[config.label_field]),
    datasets: config.datasets.map(dataset => ({
      label: dataset.label,
      data: data.map(item => item[dataset.data_field]),
      backgroundColor: dataset.background_color,
      borderColor: dataset.border_color,
      borderWidth: dataset.border_width
    }))
  };
  
  switch (config.chart_type) {
    case 'line':
      return <Line data={chartData} options={config.options} />;
    case 'bar':
      return <Bar data={chartData} options={config.options} />;
    case 'pie':
      return <Pie data={chartData} options={config.options} />;
    case 'doughnut':
      return <Doughnut data={chartData} options={config.options} />;
    default:
      return <Typography>Unsupported chart type</Typography>;
  }
};

6. Database Schema
sql-- ============================================
-- WIZARD EVENTS
-- ============================================
CREATE TABLE wizard_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wizard_id UUID REFERENCES wizards(id) ON DELETE CASCADE,
    event_trigger VARCHAR(50) NOT NULL,
    event_name VARCHAR(255) NOT NULL,
    description TEXT,
    is_enabled BOOLEAN DEFAULT TRUE,
    
    -- Target configuration
    target_type VARCHAR(50) NOT NULL, -- 'step', 'option_set', 'option', 'wizard'
    target_id UUID, -- References step_id, option_set_id, or option_id
    
    -- Conditional execution
    conditions JSONB, -- Array of conditions
    
    -- Error handling
    error_handling JSONB, -- { on_error, retry_count, etc. }
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT check_event_trigger CHECK (
        event_trigger IN (
            'step.onEntry', 'step.onExit', 'step.onValidate',
            'optionSet.onLoad', 'optionSet.onChange', 'optionSet.onApply',
            'option.onClick', 'option.onSelect', 'option.onDeselect', 'option.onChange',
            'wizard.onStart', 'wizard.onComplete'
        )
    ),
    CONSTRAINT check_target_type CHECK (target_type IN ('step', 'option_set', 'option', 'wizard'))
);

-- ============================================
-- WIZARD ACTIONS
-- ============================================
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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT check_action_type CHECK (
        action_type IN (
            'api_call', 'mcp_call', 'transform_data',
            'set_field_value', 'show_message', 'navigate', 'custom_script'
        )
    ),
    CONSTRAINT check_on_error CHECK (on_error IN ('continue', 'stop', 'retry'))
);

-- ============================================
-- API CONFIGURATIONS (for reusability)
-- ============================================
CREATE TABLE api_configurations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wizard_id UUID REFERENCES wizards(id) ON DELETE CASCADE,
    config_name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- API details
    base_url TEXT NOT NULL,
    auth_type VARCHAR(50) DEFAULT 'none',
    auth_credentials JSONB, -- Encrypted credentials
    default_headers JSONB,
    
    -- Settings
    timeout_ms INTEGER DEFAULT 30000,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    
    CONSTRAINT check_auth_type CHECK (
        auth_type IN ('none', 'bearer', 'basic', 'api_key', 'oauth2')
    )
);

-- ============================================
-- MCP CONFIGURATIONS
-- ============================================
CREATE TABLE mcp_configurations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wizard_id UUID REFERENCES wizards(id) ON DELETE CASCADE,
    config_name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- MCP server details
    mcp_server VARCHAR(255) NOT NULL,
    available_tools JSONB, -- Array of tool names and schemas
    
    -- Settings
    timeout_ms INTEGER DEFAULT 30000,
    max_retries INTEGER DEFAULT 2,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

-- ============================================
-- ACTION EXECUTION LOGS
-- ============================================
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
    status VARCHAR(20) NOT NULL, -- 'success', 'error', 'skipped'
    
    -- Input/Output
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    error_stack TEXT,
    
    -- Retry tracking
    retry_attempt INTEGER DEFAULT 0,
    
    CONSTRAINT check_status CHECK (status IN ('success', 'error', 'skipped'))
);

-- ============================================
-- DYNAMIC OPTION SETS (Created by Actions)
-- ============================================
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
    data_source VARCHAR(50), -- 'api_response', 'mcp_response', 'transform_result'
    data_source_action_id UUID REFERENCES wizard_actions(id),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT check_selection_type CHECK (
        selection_type IN (
            'dynamic_table', 'dynamic_dropdown', 'dynamic_card_grid',
            'dynamic_list', 'dynamic_document', 'dynamic_image',
            'dynamic_code', 'dynamic_json', 'dynamic_chart'
        )
    )
);

-- ============================================
-- INDEXES
-- ============================================
CREATE INDEX idx_wizard_events_wizard ON wizard_events(wizard_id);
CREATE INDEX idx_wizard_events_target ON wizard_events(target_type, target_id);
CREATE INDEX idx_wizard_events_trigger ON wizard_events(event_trigger);

CREATE INDEX idx_wizard_actions_event ON wizard_actions(event_id);
CREATE INDEX idx_wizard_actions_type ON wizard_actions(action_type);
CREATE INDEX idx_wizard_actions_order ON wizard_actions(execution_order);

CREATE INDEX idx_action_logs_run ON action_execution_logs(run_id);
CREATE INDEX idx_action_logs_action ON action_execution_logs(action_id);
CREATE INDEX idx_action_logs_status ON action_execution_logs(status);
CREATE INDEX idx_action_logs_started ON action_execution_logs(started_at DESC);

CREATE INDEX idx_dynamic_option_sets_wizard ON dynamic_option_sets(wizard_id);
CREATE INDEX idx_dynamic_option_sets_step ON dynamic_option_sets(step_id);
CREATE INDEX idx_dynamic_option_sets_action ON dynamic_option_sets(action_id);

7. API Specification
typescript// ============================================
// WIZARD EVENTS API
// ============================================
POST   /api/v1/wizards/:wizardId/events                // Create event
GET    /api/v1/wizards/:wizardId/events                // List all events
GET    /api/v1/wizards/:wizardId/events/:eventId       // Get event details
PUT    /api/v1/wizards/:wizardId/events/:eventId       // Update event
DELETE /api/v1/wizards/:wizardId/events/:eventId       // Delete event

// Event actions
GET    /api/v1/wizards/events/:eventId/actions         // List event actions
POST   /api/v1/wizards/events/:eventId/actions         // Add action to event
PUT    /api/v1/wizards/events/:eventId/actions/:actionId  // Update action
DELETE /api/v1/wizards/events/:eventId/actions/:actionId  // Delete action
POST   /api/v1/wizards/events/:eventId/actions/reorder    // Reorder actions

// ============================================
// ACTION TESTING API
// ============================================
POST   /api/v1/wizards/actions/test                    // Test action with sample data
POST   /api/v1/wizards/actions/:actionId/test          // Test specific action

// ============================================
// API CONFIGURATIONS API
// ============================================
POST   /api/v1/wizards/:wizardId/api-configs           // Create API config
GET    /api/v1/wizards/:wizardId/api-configs           // List API configs
GET    /api/v1/wizards/api-configs/:configId           // Get API config
PUT    /api/v1/wizards/api-configs/:configId           // Update API config
DELETE /api/v1/wizards/api-configs/:configId           // Delete API config
POST   /api/v1/wizards/api-configs/:configId/test      // Test API config

// ============================================
// MCP CONFIGURATIONS API
// ============================================
POST   /api/v1/wizards/:wizardId/mcp-configs           // Create MCP config
GET    /api/v1/wizards/:wizardId/mcp-configs           // List MCP configs
GET    /api/v1/wizards/mcp-configs/:configId           // Get MCP config
PUT    /api/v1/wizards/mcp-configs/:configId           // Update MCP config
DELETE /api/v1/wizards/mcp-configs/:configId           // Delete MCP config
GET    /api/v1/mcp/servers                             // List available MCP servers
GET    /api/v1/mcp/servers/:server/tools               // List tools for MCP server

// ============================================
// ACTION EXECUTION API (Runtime)
// ============================================
POST   /api/v1/wizard-runs/:runId/execute-event        // Execute event actions
GET    /api/v1/wizard-runs/:runId/action-logs          // Get action execution logs
GET    /api/v1/wizard-runs/:runId/action-logs/:logId   // Get specific log

// ============================================
// DYNAMIC DATA API (Runtime)
// ============================================
GET    /api/v1/wizard-runs/:runId/dynamic-data/:optionSetId  // Get dynamic data
POST   /api/v1/wizard-runs/:runId/refresh-data/:optionSetId  // Refresh dynamic data

8. Implementation Examples
Example 1: Database Query with MCP
Scenario: Query products from database when category is selected
typescript// Event Configuration
{
  event_trigger: "option.onSelect",
  event_name: "Load Products by Category",
  target_type: "option",
  target_id: "category_option_id",
  
  actions: [
    {
      action_name: "Query Database",
      action_type: "mcp_call",
      execution_order: 1,
      config: {
        mcp_server: "postgresql_server",
        tool_name: "execute_query",
        parameters: {
          query: "SELECT id, name, price, stock FROM products WHERE category_id = :category_id ORDER BY name",
          params: {
            category_id: "${selected_category_id}"
          }
        },
        mcp_config: {
          timeout_ms: 30000,
          streaming: false
        }
      },
      input_mapping: {
        selected_category_id: {
          source: "option_set",
          field_id: "category_dropdown"
        }
      },
      output_handling: {
        display_type: "table",
        columns: [
          { field: "id", label: "Product ID" },
          { field: "name", label: "Product Name" },
          { field: "price", label: "Price", format: "currency" },
          { field: "stock", label: "In Stock" }
        ],
        show_actions: true,
        allow_select: true,
        target_option_set_id: null // Create new
      }
    }
  ]
}
Example 2: API Call with Transformation
Scenario: Fetch user data from API, transform it, and populate fields
typescript// Event Configuration
{
  event_trigger: "step.onEntry",
  event_name: "Load User Profile",
  target_type: "step",
  target_id: "profile_step_id",
  
  actions: [
    // Action 1: Fetch user data
    {
      action_name: "Fetch User Profile",
      action_type: "api_call",
      execution_order: 1,
      config: {
        method: "GET",
        url: "https://api.example.com/users/${userId}",
        headers: {
          "Authorization": "Bearer ${access_token}"
        },
        response_mapping: {
          success_path: "$.data.user"
        }
      },
      input_mapping: {
        userId: { source: "context", field: "auth.user_id" },
        access_token: { source: "context", field: "auth.token" }
      }
    },
    
    // Action 2: Transform address
    {
      action_name: "Format Address",
      action_type: "transform_data",
      execution_order: 2,
      config: {
        transformation_type: "javascript",
        transformation_script: `
          const user = input.user;
          return {
            fullAddress: \`\${user.address.street}, \${user.address.city}, \${user.address.state} \${user.address.zip}\`,
            cityState: \`\${user.address.city}, \${user.address.state}\`
          };
        `
      },
      input_mapping: {
        user: { source: "action_output", action_id: "fetch_user_profile_id" }
      }
    },
    
    // Action 3: Populate fields
    {
      action_name: "Populate Form Fields",
      action_type: "set_field_value",
      execution_order: 3,
      config: {
        target_fields: [
          {
            option_set_id: "name_field",
            value_source: "dynamic",
            value: "${user.name}"
          },
          {
            option_set_id: "email_field",
            value_source: "dynamic",
            value: "${user.email}"
          },
          {
            option_set_id: "address_field",
            value_source: "dynamic",
            value: "${formatted.fullAddress}"
          }
        ],
        bulk_update: true
      },
      input_mapping: {
        user: { source: "action_output", action_id: "fetch_user_profile_id" },
        formatted: { source: "action_output", action_id: "format_address_id" }
      }
    }
  ]
}
Example 3: Apply Button with Multiple Actions
Scenario: "Search" button that calls API and displays results
typescript// Option Set Configuration
{
  name: "Search Products",
  selection_type: "apply_button",
  button_config: {
    button_text: "Search",
    button_variant: "contained",
    button_color: "primary",
    button_icon: "SearchIcon",
    loading_text: "Searching...",
    success_text: "Search Complete"
  },
  
  // Event triggered on button click
  events: [
    {
      event_trigger: "optionSet.onApply",
      event_name: "Execute Search",
      
      actions: [
        // Validate search input
        {
          action_name: "Validate Search Query",
          action_type: "custom_script",
          execution_order: 1,
          config: {
            script: `
              const query = input.searchQuery;
              if (!query || query.trim().length < 3) {
                throw new Error("Search query must be at least 3 characters");
              }
              return { valid: true, query: query.trim() };
            `
          },
          input_mapping: {
            searchQuery: {
              source: "option_set",
              field_id: "search_input_field"
            }
          }
        },
        
        // Call search API
        {
          action_name: "Search Products API",
          action_type: "api_call",
          execution_order: 2,
          config: {
            method: "GET",
            url: "https://api.example.com/products/search",
            query_params: {
              q: "${validatedQuery}",
              limit: 50
            },
            response_mapping: {
              success_path: "$.results"
            }
          },
          input_mapping: {
            validatedQuery: {
              source: "action_output",
              action_id: "validate_search_id",
              field: "query"
            }
          },
          output_handling: {
            display_type: "card_grid",
            config: {
              title_field: "name",
              subtitle_field: "category",
              description_field: "description",
              image_field: "thumbnail",
              show_image: true,
              show_actions: true
            }
          }
        },
        
        // Show success message
        {
          action_name: "Show Success Message",
          action_type: "show_message",
          execution_order: 3,
          config: {
            message_type: "success",
            message: "Found ${resultCount} products matching '${query}'",
            duration_ms: 3000,
            position: "top"
          },
          input_mapping: {
            resultCount: {
              source: "action_output",
              action_id: "search_products_id",
              field: "length"
            },
            query: {
              source: "action_output",
              action_id: "validate_search_id",
              field: "query"
            }
          }
        }
      ]
    }
  ]
}
Example 4: Step OnExit Validation with API
Scenario: Validate email before leaving step
typescript{
  event_trigger: "step.onExit",
  event_name: "Validate Email Address",
  target_type: "step",
  target_id: "contact_info_step_id",
  
  actions: [
    {
      action_name: "Check Email Validity",
      action_type: "api_call",
      execution_order: 1,
      config: {
        method: "POST",
        url: "https://api.emailvalidation.com/validate",
        body: {
          email: "${email_address}"
        },
        response_mapping: {
          success_path: "$.valid"
        }
      },
      input_mapping: {
        email_address: {
          source: "option_set",
          field_id: "email_field"
        }
      }
    },
    
    {
      action_name: "Handle Validation Result",
      action_type: "custom_script",
      execution_order: 2,
      config: {
        script: `
          if (!input.isValid) {
            throw new Error("Email address is invalid. Please check and try again.");
          }
          return { validated: true };
        `
      },
      input_mapping: {
        isValid: {
          source: "action_output",
          action_id: "check_email_id"
        }
      }
    }
  ]
}

9. Integration with Existing System
Enhanced Wizard Builder Steps
Update existing WizardBuilderPage.tsx to include event/action management:
typescriptconst WizardBuilderPage = () => {
  // ... existing state ...
  const [events, setEvents] = useState<WizardEvent[]>([]);
  const [showEventBuilder, setShowEventBuilder] = useState(false);
  const [editingEvent, setEditingEvent] = useState<WizardEvent | null>(null);
  
  return (
    <Box>
      {/* ... existing wizard builder UI ... */}
      
      {/* NEW: Events & Actions Tab */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">
            ⚡ Events & Actions
          </Typography>
          <Chip 
            label={`${events.length} events`}
            size="small"
            color="primary"
            sx={{ ml: 2 }}
          />
        </AccordionSummary>
        
        <AccordionDetails>
          <Alert severity="info" sx={{ mb: 2 }}>
            Configure events and actions to make your wizard dynamic and interactive.
            Events trigger actions like API calls, data transformations, and field updates.
          </Alert>
          
          {/* Events List */}
          <List>
            {events.map(event => (
              <EventListItem
                key={event.id}
                event={event}
                onEdit={() => openEventBuilder(event)}
                onDelete={() => deleteEvent(event.id)}
                onToggle={() => toggleEventEnabled(event.id)}
              />
            ))}
          </List>
          
          <Button
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={() => setShowEventBuilder(true)}
          >
            Add Event
          </Button>
        </AccordionDetails>
      </Accordion>
      
      {/* Event Builder Dialog */}
      <EventBuilderDialog
        open={showEventBuilder}
        event={editingEvent}
        wizard={wizard}
        onSave={handleSaveEvent}
        onClose={() => {
          setShowEventBuilder(false);
          setEditingEvent(null);
        }}
      />
    </Box>
  );
};
Enhanced Run Wizard with Event Handling
Update RunWizardPage.tsx to execute events:
typescriptconst RunWizardPage = () => {
  const actionExecutor = useRef(new ActionExecutor(context));
  
  // Execute step onEntry event
  useEffect(() => {
    const executeStepEntry = async () => {
      const stepEvents = wizard.events.filter(
        e => e.event_trigger === 'step.onEntry' && e.target_id === currentStep.id
      );
      
      for (const event of stepEvents) {
        if (event.is_enabled) {
          await actionExecutor.current.executeActions(
            event.actions,
            { step: currentStep, runId: run.id }
          );
        }
      }
    };
    
    executeStepEntry();
  }, [currentStep.id]);
  
  // Handle apply button click
  const handleApplyButtonClick = async (optionSetId: string) => {
    const optionSet = currentStep.option_sets.find(os => os.id === optionSetId);
    
    if (optionSet?.selection_type === 'apply_button') {
      setIsExecutingAction(true);
      
      try {
        const result = await actionExecutor.current.executeActions(
          optionSet.actions,
          { 
            optionSet,
            step: currentStep,
            runId: run.id 
          }
        );
        
        if (result.success) {
          showSuccess('Action completed successfully');
        }
      } catch (error) {
        showError(error.message);
      } finally {
        setIsExecutingAction(false);
      }
    }
  };
  
  return (
    <Box>
      {/* ... existing run wizard UI ... */}
      
      {/* Render option sets including apply buttons */}
      {currentStep.option_sets.map(optionSet => (
        optionSet.selection_type === 'apply_button' ? (
          <Button
            key={optionSet.id}
            variant={optionSet.button_config.button_variant}
            color={optionSet.button_config.button_color}
            startIcon={
              isExecutingAction ? 
              <CircularProgress size={20} /> :
              <Icon>{optionSet.button_config.button_icon}</Icon>
            }
            onClick={() => handleApplyButtonClick(optionSet.id)}
            disabled={isExecutingAction}
            fullWidth
            sx={{ my: 2 }}
          >
            {isExecutingAction 
              ? optionSet.button_config.loading_text 
              : optionSet.button_config.button_text
            }
          </Button>
        ) : (
          <OptionSetRenderer
            key={optionSet.id}
            optionSet={optionSet}
            value={responses[optionSet.id]}
            onChange={(value) => handleOptionSetChange(optionSet.id, value)}
          />
        )
      ))}
    </Box>
  );
};

10. Complete Feature Summary
For Wizard Builders (Admins)

Event Configuration

✅ Choose from 12+ event triggers
✅ Set conditions for execution
✅ Configure error handling


Action Types

✅ API calls with full configuration
✅ MCP calls for database/tool operations
✅ Data transformations
✅ Field value updates
✅ User notifications
✅ Custom scripts


Visual Builder

✅ Drag-and-drop action ordering
✅ Visual input mapping
✅ Live API testing
✅ Response preview


Output Configuration

✅ 10+ display types
✅ Customizable layouts
✅ Dynamic field creation



For Wizard Users

Dynamic Data

✅ Real-time API integration
✅ Auto-populated fields
✅ Interactive tables and dropdowns


Interactive Actions

✅ Apply buttons for custom operations
✅ Loading states and progress indicators
✅ Success/error messages


Rich Display

✅ Tables, cards, lists
✅ Images and documents
✅ Charts and visualizations
✅ Code syntax highlighting




Implementation Roadmap
Phase 1: Core Event System (Week 1-2)

Database schema for events/actions
Event executor engine
Basic API call actions
Simple output renderers (table, dropdown)

Phase 2: Wizard Builder Integration (Week 3-4)

Event builder UI
Action type selector
API call action editor
Input/output mapping UI

Phase 3: Advanced Actions (Week 5-6)

MCP call actions
Transform data actions
Set field value actions
Apply button option set

Phase 4: Output Renderers (Week 7-8)

All display types
Card grid, list, document
Image, code, chart renderers
Custom templates

Phase 5: Testing & Polish (Week 9-10)

Action testing interface
Error handling refinement
Performance optimization
Documentation


This comprehensive action system transforms the wizard from a simple form builder into a powerful, interactive application platform capable of orchestrating complex workflows, integrating with external systems, and delivering rich, dynamic user experiences!