import pytest
import os
import sys
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# Add backend to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.mcp_client.todoist_client import todoist_client

# Load env vars
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
load_dotenv(os.path.join(root_dir, ".env"))

@pytest.mark.asyncio
async def test_mcp_client_direct():
    """Test the MCP client directly."""
    print("\nTesting MCP Client directly...")
    
    # test get list of tasks
    try:
        tasks = await todoist_client.list_tasks()
        print(f"MCP Client returned: {tasks}")
        assert isinstance(tasks, list), f"Expected list, got {type(tasks)}: {tasks}"
    except Exception as e:
        pytest.fail(f"MCP Client failed: {e}")
    
    # Test creating a task
    try:
        new_task = await todoist_client.create_task(
            content="Test Task from MCP Client",
            description="This is a test task created during integration testing.",
            due_string="tomorrow",
            priority=4
        )
        print(f"Created Task: {new_task}")
        assert isinstance(new_task, dict), f"Expected dict, got {type(new_task)}: {new_task}"
    except Exception as e:
        pytest.fail(f"Task creation failed: {e}")

    # test editing the created task
    try:
        update_result = await todoist_client.update_task(
            task_id=new_task['id'],
            content="Updated Test Task from MCP Client"
        )
        print(f"Update Result: {update_result}")
        
        # Verify update by fetching tasks
        tasks = await todoist_client.list_tasks()
        updated_task = next((t for t in tasks if t['id'] == new_task['id']), None)
        assert updated_task is not None, "Task not found after update"
        assert updated_task['content'] == "Updated Test Task from MCP Client", "Task content not updated correctly."
    except Exception as e:
        pytest.fail(f"Task update failed: {e}")

    # test marking the created task as completed
    try:
        close_result = await todoist_client.close_task(new_task['id'])
        print(f"Close Result: {close_result}")
        
        # Verify completion by fetching tasks (should be gone from active list or marked completed if we could fetch all)
        # Todoist list_tasks only returns active tasks by default.
        tasks = await todoist_client.list_tasks()
        closed_task = next((t for t in tasks if t['id'] == new_task['id']), None)
        assert closed_task is None, "Task should not be in active list after closing."
    except Exception as e:
        pytest.fail(f"Task completion failed: {e}")
        
    # test deleting the created task
    # Note: Task is already closed, so we might need to reopen it or just delete it (Todoist allows deleting completed tasks)
    # But since we can't easily find the ID if it's not in the list, we rely on the ID we have.
    try:
        delete_result = await todoist_client.delete_task(new_task['id'])
        print(f"Deleted Task Result: {delete_result}")
        # The server returns a dict with success
        if isinstance(delete_result, dict):
             assert delete_result.get('success') is True or delete_result.get('success') is None # Todoist API might return None on void
        else:
             # Fallback if it returns raw boolean
             assert delete_result is True or delete_result is None
    except Exception as e:
        pytest.fail(f"Task deletion failed: {e}")


def test_api_endpoint():
    """Test the FastAPI endpoint."""
    client = TestClient(app)
    response = client.get("/tasks/")
    print(f"\nAPI Response: {response.status_code} - {response.text}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
