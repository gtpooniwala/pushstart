import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.task_service import TaskService
from app.models.task import Task

@pytest.mark.asyncio
async def test_sync_tasks():
    # Mock session
    mock_session = AsyncMock()
    # session.add is synchronous
    mock_session.add = MagicMock()
    
    # Mock the result of session.exec()
    mock_exec_result = MagicMock()
    mock_exec_result.all.return_value = [] # Return empty list for local_ids
    mock_session.exec.return_value = mock_exec_result
    
    mock_session.get = AsyncMock(return_value=None)
    
    # Mock todoist_client
    with patch('app.services.task_service.todoist_client') as mock_client:
        # Setup mock return value
        mock_client.list_tasks = AsyncMock(return_value=[
            {
                "id": "123",
                "content": "Test Task",
                "description": "Desc",
                "priority": 1,
                "due": {"string": "tomorrow", "date": "2023-01-01"},
                "order": 1
            }
        ])
        
        service = TaskService(mock_session)
        # Mock get_all_tasks to return the expected task
        service.get_all_tasks = AsyncMock(return_value=[
            Task(id="123", content="Test Task")
        ])
        
        tasks = await service.sync_tasks()
        
        # Verify interactions
        mock_client.list_tasks.assert_called_once()
        assert len(tasks) == 1
        assert tasks[0].id == "123"
        assert tasks[0].content == "Test Task"
        
        # Verify DB interactions
        # Should have called session.add and session.commit
        assert mock_session.add.called
        assert mock_session.commit.called

@pytest.mark.asyncio
async def test_create_task():
    mock_session = AsyncMock()
    mock_session.add = MagicMock() # synchronous
    mock_session.get = AsyncMock(return_value=None) # Ensure task is not found so new one is created
    
    with patch('app.services.task_service.todoist_client') as mock_client:
        mock_client.create_task = AsyncMock(return_value={
            "id": "456",
            "content": "New Task",
            "description": "New Desc",
            "priority": 2,
            "due": None,
            "order": 2
        })
        
        service = TaskService(mock_session)
        task = await service.create_task("New Task", "New Desc")
        
        mock_client.create_task.assert_called_once_with(
            content="New Task",
            description="New Desc",
            due_string=None,
            priority=None
        )
        
        assert task.id == "456"
        assert task.content == "New Task"
        assert mock_session.add.called
        assert mock_session.commit.called
