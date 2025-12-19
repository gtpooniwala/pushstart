import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add mcp root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock TodoistAPI before importing server
with patch('todoist_api_python.api.TodoistAPI') as MockAPI:
    from todoist_server.server import list_tasks, create_task, update_task, close_task, api

def test_list_tasks():
    # Setup mock
    mock_task = MagicMock()
    mock_task.to_dict.return_value = {"id": "1", "content": "Test"}
    api.get_tasks.return_value = [mock_task]
    
    # Call tool
    result = list_tasks()
    
    # Verify
    api.get_tasks.assert_called_once()
    assert len(result) == 1
    assert result[0]["id"] == "1"

def test_create_task():
    mock_task = MagicMock()
    mock_task.to_dict.return_value = {"id": "2", "content": "New"}
    api.add_task.return_value = mock_task
    
    result = create_task("New", "Desc")
    
    api.add_task.assert_called_once_with(
        content="New",
        description="Desc",
        due_string=None,
        priority=None
    )
    assert result["id"] == "2"

def test_close_task():
    api.complete_task.return_value = True
    
    result = close_task("123")
    
    api.complete_task.assert_called_once_with(task_id="123")
    assert result["success"] is True
