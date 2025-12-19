from typing import Literal, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage
import os
import asyncio

# Try to import PostgresSaver
try:
    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
    from psycopg_pool import AsyncConnectionPool
    HAS_POSTGRES_CHECKPOINT = True
except ImportError:
    HAS_POSTGRES_CHECKPOINT = False

from app.core.llm import LLMFactory
from app.agent.state import AgentState
from app.agent.tools import ALL_TOOLS, SAFE_TOOLS, SENSITIVE_TOOLS

# Initialize LLM and bind tools
llm = LLMFactory.get_llm()
llm_with_tools = llm.bind_tools(ALL_TOOLS)

def chatbot(state: AgentState):
    """
    The main chatbot node. It invokes the LLM.
    """
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState) -> Literal["safe_tools", "sensitive_tools", "__end__"]:
    """
    Determine if we should go to the tools node or end.
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    if last_message.tool_calls:
        # Check the first tool call to decide routing
        tool_name = last_message.tool_calls[0]["name"]
        if any(t.name == tool_name for t in SAFE_TOOLS):
            return "safe_tools"
        return "sensitive_tools"
    return "__end__"

# Define the graph
workflow = StateGraph(AgentState)

workflow.add_node("chatbot", chatbot)
workflow.add_node("safe_tools", ToolNode(SAFE_TOOLS))
workflow.add_node("sensitive_tools", ToolNode(SENSITIVE_TOOLS))

workflow.add_edge(START, "chatbot")

# Conditional edge from chatbot
workflow.add_conditional_edges(
    "chatbot",
    should_continue,
)

# From tools, go back to chatbot to generate a confirmation message
workflow.add_edge("safe_tools", "chatbot")
workflow.add_edge("sensitive_tools", "chatbot")

# Global variables
app_graph = None
_pool = None

async def get_app_graph():
    global app_graph, _pool
    if app_graph is not None:
        return app_graph

    # Default to MemorySaver
    checkpointer = MemorySaver()

    if HAS_POSTGRES_CHECKPOINT:
        db_url = os.getenv("DATABASE_URL", "postgresql://pushstart:pushstart_password@localhost:5432/pushstart_db")
        # Adjust for psycopg
        if db_url.startswith("postgresql+asyncpg://"):
            db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
        
        try:
            # Create a connection pool
            _pool = AsyncConnectionPool(conninfo=db_url, min_size=1, max_size=20, kwargs={"autocommit": True})
            await _pool.open()
            
            checkpointer = AsyncPostgresSaver(_pool)
            await checkpointer.setup()
            print("Initialized Postgres Checkpointer")
        except Exception as e:
            print(f"Failed to initialize Postgres Checkpointer, falling back to MemorySaver: {e}")
            checkpointer = MemorySaver()

    app_graph = workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["sensitive_tools"]
    )
    return app_graph

async def close_graph():
    global _pool
    if _pool:
        await _pool.close()
