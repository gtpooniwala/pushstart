from typing import Annotated, List, Optional, Dict, Any
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    # We can track the proposed action explicitly if needed, 
    # but usually the last message being a tool_call is enough.
    # However, for the UI, having an explicit field might be easier.
    proposed_action: Optional[Dict[str, Any]]
