import asyncio
import os
from mcp import ClientSession
from mcp.client.sse import sse_client

async def list_tools():
    url = "http://localhost:8001/sse"
    print(f"Connecting to {url}...")
    try:
        async with sse_client(url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                print("Available tools:")
                for tool in tools.tools:
                    print(f"- {tool.name}: {tool.description}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(list_tools())
