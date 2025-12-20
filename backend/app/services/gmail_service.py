from app.mcp_client.gmail_client import gmail_client
from typing import List, Dict, Any

class GmailService:
    # No session needed as we are not caching
    def __init__(self):
        pass

    async def list_emails(self, max_results: int = 10, query: str = "") -> List[Dict[str, Any]]:
        """Fetch emails from MCP directly."""
        return await gmail_client.list_emails(max_results, query)

    async def create_draft(self, to: str, subject: str, body: str) -> Dict[str, Any]:
        """Create a draft via MCP."""
        return await gmail_client.create_draft(to, subject, body)
