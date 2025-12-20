import os
import sys
import json
from mcp import ClientSession
from mcp.client.sse import sse_client

# URL of the MCP server
GMAIL_MCP_SERVER_URL = os.getenv("GMAIL_MCP_SERVER_URL", "http://localhost:8003/sse")

class GmailClient:
    async def _run_tool(self, tool_name, arguments=None):
        if arguments is None:
            arguments = {}
            
        try:
            async with sse_client(GMAIL_MCP_SERVER_URL) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments)
                    
                    if not result.content:
                        return None
                    
                    if len(result.content) > 1:
                        items = []
                        for content in result.content:
                            try:
                                item = json.loads(content.text)
                                items.append(item)
                            except json.JSONDecodeError:
                                items.append(content.text)
                        return items
                    
                    text_content = result.content[0].text
                    try:
                        data = json.loads(text_content)
                        # Handle case where MCP returns a single dict for a list-returning tool
                        if tool_name in ["list_emails"] and isinstance(data, dict) and "error" not in data:
                            return [data]
                        return data
                    except json.JSONDecodeError:
                        return text_content
        except Exception as e:
            print(f"Gmail MCP Error: {e}")
            return {"error": str(e)}

    async def list_emails(self, max_results: int = 10, query: str = ""):
        return await self._run_tool("list_emails", {"max_results": max_results, "query": query})

    async def create_draft(self, to: str, subject: str, body: str):
        return await self._run_tool("create_draft", {"to": to, "subject": subject, "body": body})

gmail_client = GmailClient()
