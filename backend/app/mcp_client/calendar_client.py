import os
import sys
import json
from mcp import ClientSession
from mcp.client.sse import sse_client

# URL of the MCP server
CALENDAR_MCP_SERVER_URL = os.getenv("CALENDAR_MCP_SERVER_URL", "http://localhost:8002/sse")

class CalendarClient:
    async def _run_tool(self, tool_name, arguments=None):
        if arguments is None:
            arguments = {}
            
        try:
            async with sse_client(CALENDAR_MCP_SERVER_URL) as (read, write):
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
            print(f"Calendar MCP Error: {e}")
            # Return error dict so agent can see it
            return {"error": str(e)}

    async def list_events(self, days=7):
        return await self._run_tool("list_events", {"days": days})

    async def create_event(self, summary, start_time, end_time, description=""):
        return await self._run_tool("create_event", {
            "summary": summary,
            "start_time": start_time,
            "end_time": end_time,
            "description": description
        })

    async def find_free_blocks(self, duration_minutes=60, days=3):
        return await self._run_tool("find_free_blocks", {
            "duration_minutes": duration_minutes,
            "days": days
        })

calendar_client = CalendarClient()
