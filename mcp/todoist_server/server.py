from mcp.server.fastmcp import FastMCP
from todoist_api_python.api import TodoistAPI
import os
from dotenv import load_dotenv
import dataclasses
from typing import Optional

# Load .env from project root (2 levels up from this file)
# mcp/todoist_server/server.py -> mcp/todoist_server -> mcp -> root
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
load_dotenv(os.path.join(root_dir, ".env"))

# Initialize with a dummy token if not present to avoid crash on import, 
# but operations will fail.
api_token = os.getenv("TODOIST_API_TOKEN", "dummy_token")
api = TodoistAPI(api_token)

mcp = FastMCP("todoist")

@mcp.tool()
def list_tasks():
    """List all active tasks."""
    # Let exceptions propagate so they are reported as tool errors
    tasks_collection = api.get_tasks()
    
    all_tasks = []
    try:
        # Handle both direct list of tasks and paginated results
        # If it's a list, iterating yields tasks.
        # If it's a paginator, iterating yields pages (lists of tasks).
        for item in tasks_collection:
            if isinstance(item, list):
                all_tasks.extend(item)
            else:
                all_tasks.append(item)
    except Exception:
        return []

    results = []
    for task in all_tasks:
        if hasattr(task, 'to_dict'):
            results.append(task.to_dict())
        elif dataclasses.is_dataclass(task):
            results.append(dataclasses.asdict(task))
        else:
            # Fallback for unexpected types
            results.append(str(task))
    return results

@mcp.tool()
def get_task(task_id: str):
    """Get a single task by ID."""
    try:
        task = api.get_task(task_id=task_id)
        return task.to_dict()
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def create_task(content: str, description: Optional[str] = None, due_string: Optional[str] = None, priority: Optional[int] = None):
    """Create a new task."""
    try:
        task = api.add_task(
            content=content, 
            description=description, 
            due_string=due_string,
            priority=priority
        )
        return task.to_dict()
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def update_task(task_id: str, content: Optional[str] = None, description: Optional[str] = None, due_string: Optional[str] = None, priority: Optional[int] = None):
    """Update an existing task."""
    try:
        # Filter out None values
        kwargs = {}
        if content is not None: kwargs['content'] = content
        if description is not None: kwargs['description'] = description
        if due_string is not None: kwargs['due_string'] = due_string
        if priority is not None: kwargs['priority'] = priority
        
        is_success = api.update_task(task_id=task_id, **kwargs)
        return {"success": is_success, "id": task_id}
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def delete_task(task_id: str):
    """Delete a task."""
    try:
        is_success = api.delete_task(task_id=task_id)
        return {"success": is_success, "id": task_id}
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def close_task(task_id: str):
    """Complete (close) a task."""
    try:
        is_success = api.complete_task(task_id=task_id)
        return {"success": is_success, "id": task_id}
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()
