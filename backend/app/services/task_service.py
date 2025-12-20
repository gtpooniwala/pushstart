from sqlmodel import select, delete
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.task import Task
from app.mcp_client.todoist_client import todoist_client
from typing import List, Dict, Any

class TaskService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_tasks(self) -> List[Task]:
        result = await self.session.exec(select(Task).order_by(Task.order))
        return result.all()

    async def list_tasks(self) -> List[Task]:
        """Alias for get_all_tasks to match tool interface."""
        return await self.get_all_tasks()

    async def get_task(self, task_id: str) -> Task | None:
        return await self.session.get(Task, task_id)

    async def sync_tasks(self) -> List[Task]:
        """
        Full sync:
        1. Fetch all tasks from Todoist via MCP.
        2. Upsert all fetched tasks to DB.
        3. Delete tasks from DB that are not in the fetched list.
        """
        # 1. Fetch from MCP
        mcp_tasks = await todoist_client.list_tasks()
        if not isinstance(mcp_tasks, list):
            # Error or empty
            return []

        # 2. Upsert
        active_ids = set()
        for t_data in mcp_tasks:
            task_id = t_data.get("id")
            if not task_id:
                continue
            
            active_ids.add(task_id)
            
            # Map MCP dict to Task model
            # Note: 'due' in Todoist is a dict, we flatten it slightly for our model
            due = t_data.get("due")
            due_string = due.get("string") if due else None
            due_date = due.get("date") if due else None
            
            task = await self.session.get(Task, task_id)
            if not task:
                task = Task(id=task_id, content=t_data.get("content"))
            
            # Update fields
            task.content = t_data.get("content")
            task.description = t_data.get("description")
            task.project_id = t_data.get("project_id")
            task.section_id = t_data.get("section_id")
            task.parent_id = t_data.get("parent_id")
            task.priority = t_data.get("priority", 1)
            task.due_string = due_string
            task.due_date = due_date
            task.labels = t_data.get("labels")
            task.order = t_data.get("order")
            task.url = t_data.get("url")
            task.raw_data = t_data
            
            self.session.add(task)
        
        # 3. Delete stale tasks
        # We fetch all IDs from DB first? Or just delete where ID not in active_ids
        # Delete where ID not in active_ids is efficient if supported, 
        # but SQLModel/SQLAlchemy async delete with 'not in' can be tricky.
        # Let's fetch all local IDs first.
        
        local_tasks = await self.session.exec(select(Task.id))
        local_ids = set(local_tasks.all())
        
        to_delete = local_ids - active_ids
        if to_delete:
            # Batch delete
            statement = delete(Task).where(Task.id.in_(to_delete))
            await self.session.exec(statement)
            
        await self.session.commit()
        
        # Return fresh list
        return await self.get_all_tasks()

    async def update_local_task(self, task_data: Dict[str, Any]):
        """Update or Insert a single task from MCP data (e.g. after create/update)"""
        task_id = task_data.get("id")
        if not task_id:
            return

        due = task_data.get("due")
        due_string = due.get("string") if due else None
        due_date = due.get("date") if due else None

        task = await self.session.get(Task, task_id)
        if not task:
            task = Task(id=task_id, content=task_data.get("content"))
        
        task.content = task_data.get("content")
        task.description = task_data.get("description")
        task.project_id = task_data.get("project_id")
        task.section_id = task_data.get("section_id")
        task.parent_id = task_data.get("parent_id")
        task.priority = task_data.get("priority", 1)
        task.due_string = due_string
        task.due_date = due_date
        task.labels = task_data.get("labels")
        task.order = task_data.get("order")
        task.url = task_data.get("url")
        task.raw_data = task_data
        
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def delete_local_task(self, task_id: str):
        task = await self.session.get(Task, task_id)
        if task:
            await self.session.delete(task)
            await self.session.commit()

    # --- Unified Write Methods (MCP + Local Cache) ---

    async def create_task(self, content: str, description: str = None, due_string: str = None, priority: int = None) -> Task:
        """Create in Todoist -> Update Local Cache"""
        # 1. Create in Todoist
        new_task_data = await todoist_client.create_task(
            content=content,
            description=description,
            due_string=due_string,
            priority=priority
        )
        if not isinstance(new_task_data, dict):
            raise Exception(f"Failed to create task: {new_task_data}")
            
        # 2. Update local DB
        return await self.update_local_task(new_task_data)

    async def update_task(self, task_id: str, content: str = None, description: str = None, due_string: str = None, priority: int = None) -> Task:
        """Update in Todoist -> Update Local Cache"""
        # 1. Update in Todoist
        updated_task_data = await todoist_client.update_task(
            task_id=task_id,
            content=content,
            description=description,
            due_string=due_string,
            priority=priority
        )
        if not isinstance(updated_task_data, dict):
            raise Exception(f"Failed to update task: {updated_task_data}")

        # 2. Update local DB
        return await self.update_local_task(updated_task_data)

    async def delete_task(self, task_id: str):
        """Delete in Todoist -> Delete from Local Cache"""
        # 1. Delete in Todoist
        await todoist_client.delete_task(task_id)
        # 2. Delete from local DB
        await self.delete_local_task(task_id)

    async def close_task(self, task_id: str):
        """Close in Todoist -> Delete from Local Cache (since it's completed)"""
        # 1. Close in Todoist
        result = await todoist_client.close_task(task_id)
        
        # Check for error
        if isinstance(result, str) and result.startswith("Error:"):
             raise Exception(f"Failed to close task in Todoist: {result}")
             
        # 2. Delete from local DB
        await self.delete_local_task(task_id)

