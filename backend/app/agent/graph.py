from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage

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
        # In a more complex scenario, we might need to handle mixed batches,
        # but for now we assume the LLM usually does one type or we treat mixed as sensitive.
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

# Compile the graph with a checkpointer for state persistence (in-memory for now)
checkpointer = MemorySaver()

# We interrupt before 'sensitive_tools' to allow for Human-in-the-loop approval
app_graph = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["sensitive_tools"]
)
