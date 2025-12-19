import os
import sys
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Path to the server script
# Assuming we are running from backend/
SERVER_SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../mcp/todoist_server/server.py"))

class TodoistClient:
    async def _run_tool(self, tool_name, arguments=None):
        if arguments is None:
            arguments = {}
            
        # Force COLUMNS to prevent rich/logging from wrapping to 1 char width in subprocess
        env = os.environ.copy()
        env["COLUMNS"] = "120"

        server_params = StdioServerParameters(
            command=sys.executable,
            args=[SERVER_SCRIPT],
            env=env
        )
        
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments)
                    
                    # Parse the result
                    if not result.content:
                        return None
                    
                    # If multiple content blocks, it might be a list of items split by FastMCP
                    if len(result.content) > 1:
                        items = []
                        for content in result.content:
                            try:
                                item = json.loads(content.text)
                                items.append(item)
                            except json.JSONDecodeError:
                                items.append(content.text)
                        return items
                    
                    # Single content block
                    text_content = result.content[0].text
                    try:
                        return json.loads(text_content)
                    except json.JSONDecodeError:
                        return text_content
        except Exception as e:
            print(f"MCP Error: {e}")
            raise e

    async def list_tasks(self):
        return await self._run_tool("list_tasks")

    async def create_task(self, content, description=None, due_string=None, priority=None):
        return await self._run_tool("create_task", {
            "content": content,
            "description": description,
            "due_string": due_string,
            "priority": priority
        })

    async def update_task(self, task_id, content=None, description=None, due_string=None, priority=None):
        return await self._run_tool("update_task", {
            "task_id": task_id,
            "content": content,
            "description": description,
            "due_string": due_string,
            "priority": priority
        })

    async def delete_task(self, task_id):
        return await self._run_tool("delete_task", {"task_id": task_id})

    async def close_task(self, task_id):
        return await self._run_tool("close_task", {"task_id": task_id})

# Singleton instance
todoist_client = TodoistClient()
