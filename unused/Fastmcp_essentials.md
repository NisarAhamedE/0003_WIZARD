# FastMCP Essentials Guide

## What is FastMCP?

**FastMCP** is a Python framework for building Model Context Protocol (MCP) servers that connect AI assistants to your data and tools.

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("My Server")
```

---

## Three Core Components

| Component | Purpose | Analogy |
|-----------|---------|---------|
| **Resource** | Read-only data access | GET endpoint / Documentation |
| **Tool** | Execute actions | POST endpoint / Function call |
| **Prompt** | Guide AI behavior | Standard Operating Procedure |

---

## 1. RESOURCES - Provide Data

**Resources give AI access to your data without changing anything.**

### Simple Example
```python
@mcp.resource("config://settings")
def get_settings() -> str:
    """Return application settings"""
    return '{"theme": "dark", "language": "en"}'
```

### With Parameters
```python
@mcp.resource("user://{user_id}/profile")
def get_user_profile(user_id: str) -> str:
    """Get user profile by ID"""
    profile = {
        "id": user_id,
        "name": "John Doe",
        "email": "john@example.com"
    }
    return json.dumps(profile)
```

**Usage:** AI accesses `user://123/profile` to get user 123's data

---

## 2. TOOLS - Perform Actions

**Tools let AI execute operations that can change state.**

### Basic Tool
```python
@mcp.tool()
def calculate_total(price: float, quantity: int, tax_rate: float = 0.1) -> dict:
    """Calculate order total with tax"""
    subtotal = price * quantity
    tax = subtotal * tax_rate
    total = subtotal + tax
    
    return {
        "subtotal": subtotal,
        "tax": tax,
        "total": total
    }
```

### Async Tool with Progress
```python
from mcp.server.fastmcp import Context
from mcp.server.session import ServerSession
import asyncio

@mcp.tool()
async def process_order(
    order_id: str,
    ctx: Context[ServerSession, None]
) -> dict:
    """Process an order with progress updates"""
    
    await ctx.info(f"Processing order {order_id}")
    
    # Step 1
    await ctx.report_progress(0.33, 1.0, "Validating order")
    await asyncio.sleep(1)
    
    # Step 2
    await ctx.report_progress(0.66, 1.0, "Charging payment")
    await asyncio.sleep(1)
    
    # Step 3
    await ctx.report_progress(1.0, 1.0, "Order complete")
    
    return {
        "success": True,
        "order_id": order_id,
        "status": "completed"
    }
```

**Usage:** AI calls `calculate_total(100, 5, 0.08)` to compute order total

---

## 3. PROMPTS - Guide AI

**Prompts provide templates that guide AI through complex tasks.**

### Basic Prompt
```python
@mcp.prompt()
def analyze_sales() -> str:
    """Guide for sales analysis"""
    return """
    Please analyze sales data:
    
    1. Get current month sales using get_sales_data resource
    2. Compare with previous month
    3. Calculate growth percentage
    4. Identify top 3 products
    5. Suggest improvements
    
    Format output as a summary report.
    """
```

### Parameterized Prompt
```python
@mcp.prompt()
def debug_issue(error_code: str, severity: str = "medium") -> str:
    """Guide for debugging specific issues"""
    return f"""
    DEBUG PROTOCOL - Error Code: {error_code} (Severity: {severity})
    
    Step 1: Check recent logs
    - Use get_logs resource for last 24 hours
    - Filter by error code {error_code}
    
    Step 2: Identify pattern
    - When did errors start?
    - Which users affected?
    - Any common conditions?
    
    Step 3: Investigate root cause
    - Check related systems
    - Review recent deployments
    - Analyze error stack traces
    
    Step 4: Recommend fix
    - Immediate workaround
    - Permanent solution
    - Prevention strategy
    
    Present findings in structured format with priority actions.
    """
```

**Usage:** AI uses this template to systematically debug issues

---

## Complete Example Server

```python
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.session import ServerSession
import json
import asyncio

mcp = FastMCP("Task Manager")

# RESOURCE: Get task list
@mcp.resource("tasks://list")
def get_tasks() -> str:
    """Get all tasks"""
    tasks = [
        {"id": 1, "title": "Write docs", "status": "done"},
        {"id": 2, "title": "Review code", "status": "pending"},
        {"id": 3, "title": "Deploy app", "status": "pending"}
    ]
    return json.dumps(tasks, indent=2)

# RESOURCE: Get specific task
@mcp.resource("tasks://{task_id}")
def get_task(task_id: str) -> str:
    """Get task by ID"""
    task = {
        "id": task_id,
        "title": "Sample Task",
        "status": "pending",
        "created": "2025-11-17"
    }
    return json.dumps(task, indent=2)

# TOOL: Create new task
@mcp.tool()
def create_task(title: str, priority: str = "normal") -> dict:
    """Create a new task"""
    task_id = 4  # Would generate in real app
    
    return {
        "success": True,
        "task_id": task_id,
        "title": title,
        "priority": priority,
        "status": "pending"
    }

# TOOL: Update task status (with async)
@mcp.tool()
async def update_task_status(
    task_id: int,
    new_status: str,
    ctx: Context[ServerSession, None]
) -> dict:
    """Update task status with validation"""
    
    await ctx.info(f"Updating task {task_id}")
    
    # Validate
    await ctx.report_progress(0.5, 1.0, "Validating status")
    await asyncio.sleep(0.5)
    
    valid_statuses = ["pending", "in_progress", "done", "cancelled"]
    if new_status not in valid_statuses:
        return {
            "success": False,
            "error": f"Invalid status. Must be one of: {valid_statuses}"
        }
    
    # Update
    await ctx.report_progress(1.0, 1.0, "Status updated")
    
    return {
        "success": True,
        "task_id": task_id,
        "new_status": new_status
    }

# PROMPT: Daily review workflow
@mcp.prompt()
def daily_task_review() -> str:
    """Guide for daily task review"""
    return """
    DAILY TASK REVIEW WORKFLOW
    
    1. GET OVERVIEW
       - Use tasks://list resource to get all tasks
       - Count tasks by status
       - Calculate completion rate
    
    2. IDENTIFY PRIORITIES
       - Find overdue tasks
       - List high-priority pending tasks
       - Check blocked tasks
    
    3. SUGGEST ACTIONS
       - Which tasks to focus on today?
       - Any tasks to delegate?
       - Tasks that can be cancelled?
    
    4. GENERATE REPORT
       Format as:
       - Summary (2-3 sentences)
       - Priority tasks (top 5)
       - Recommendations
    
    Use create_task if new tasks are needed.
    Use update_task_status to mark completed tasks.
    """

# PROMPT: Task completion assistant
@mcp.prompt()
def complete_task_workflow(task_id: int) -> str:
    """Guide for completing a task"""
    return f"""
    TASK COMPLETION WORKFLOW
    
    Task ID: {task_id}
    
    Steps:
    1. Retrieve task details using tasks://{task_id}
    2. Verify task requirements are met
    3. Update status using update_task_status({task_id}, "done")
    4. Confirm completion
    
    If task cannot be completed:
    - Update status to "cancelled" with reason
    - Document why it cannot be completed
    - Suggest alternative actions
    """

if __name__ == "__main__":
    print("🚀 Task Manager MCP Server")
    print("\nResources:")
    print("  - tasks://list")
    print("  - tasks://{task_id}")
    print("\nTools:")
    print("  - create_task(title, priority)")
    print("  - update_task_status(task_id, new_status)")
    print("\nPrompts:")
    print("  - daily_task_review()")
    print("  - complete_task_workflow(task_id)")
    print("\nStarting server...\n")
    
    mcp.run()
```

---

## Running Your Server

### Start the Server
```bash
python server.py
```

### Connect to Claude Desktop

Edit config file:
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "task-manager": {
      "command": "python",
      "args": ["/full/path/to/server.py"]
    }
  }
}
```

Restart Claude Desktop and start using your server!

---

## Quick Comparison

### Resource vs Tool vs Prompt

```python
# RESOURCE: Just returns data (no side effects)
@mcp.resource("data://info")
def get_info() -> str:
    return json.dumps({"message": "Hello"})

# TOOL: Performs action (can change things)
@mcp.tool()
def send_email(to: str, subject: str) -> dict:
    # Actually sends email
    return {"sent": True}

# PROMPT: Instructs AI how to use resources/tools
@mcp.prompt()
def email_workflow() -> str:
    return "1. Get contacts\n2. Draft email\n3. Send using send_email"
```

### When to Use What?

**Use RESOURCE when:**
- Showing configuration
- Displaying data
- Providing reference info
- No changes needed

**Use TOOL when:**
- Creating records
- Updating database
- Calling APIs
- Making changes

**Use PROMPT when:**
- Multi-step workflows
- Best practices
- Analysis templates
- Decision frameworks

---

## Installation

```bash
# Install FastMCP
pip install mcp

# Or standalone FastMCP 2.0
pip install fastmcp
```

---

## Key Takeaways

✅ **Resources** = Read-only data (like GET requests)  
✅ **Tools** = Actions that can modify state (like POST requests)  
✅ **Prompts** = Instructions for AI on how to do complex tasks  

**Think of it as:**
- 📚 Resources = Your library of information
- 🔨 Tools = Your toolbox of actions
- 📋 Prompts = Your instruction manuals

---

## Learn More

- **FastMCP Docs:** https://gofastmcp.com
- **MCP Specification:** https://modelcontextprotocol.io
- **Python SDK:** https://github.com/modelcontextprotocol/python-sdk

---

**Ready to build? Start with the complete example above! 🚀**