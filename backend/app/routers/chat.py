from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid

from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from app.agent.graph import get_app_graph
from app.agent.tools import SENSITIVE_TOOLS, SAFE_TOOLS
from app.core.db import engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from app.services.task_service import TaskService

router = APIRouter()

# Create a map of tools for easy lookup
TOOL_MAP = {t.name: t for t in SENSITIVE_TOOLS + SAFE_TOOLS}

class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None

class ApproveRequest(BaseModel):
    thread_id: str
    approved_tool_call_ids: Optional[List[str]] = None
    # Backward compatibility
    tool_call_id: Optional[str] = None

class RejectRequest(BaseModel):
    thread_id: str
    tool_call_id: Optional[str] = None
    reason: Optional[str] = "Rejected by user"

class ChatResponse(BaseModel):
    thread_id: str
    messages: List[Dict[str, Any]]
    proposed_actions: List[Dict[str, Any]] = []
    # Backward compatibility (optional, can be removed if frontend is updated simultaneously, 
    # but safer to keep it null or the first action)
    proposed_action: Optional[Dict[str, Any]] = None
    status: str # "ready", "waiting_for_approval"

def _format_messages(messages):
    # Convert LangChain messages to a simple dict format for frontend
    formatted = []
    for m in messages:
        role = "user"
        if isinstance(m, AIMessage):
            role = "assistant"
        elif isinstance(m, ToolMessage):
            role = "tool"
        
        content = m.content
        # Handle list content (common with Anthropic)
        if isinstance(content, list):
            # Extract text parts
            text_parts = [c["text"] for c in content if isinstance(c, dict) and c.get("type") == "text"]
            content = "\n".join(text_parts)
        
        formatted.append({
            "role": role,
            "content": content,
            "tool_calls": getattr(m, "tool_calls", [])
        })
    return formatted

async def _get_proposed_action_with_details(snapshot):
    proposed_actions = []
    status = "ready"
    
    if snapshot.next and "sensitive_tools" in snapshot.next:
        last_message = snapshot.values["messages"][-1]
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            status = "waiting_for_approval"
            
            for tool_call in last_message.tool_calls:
                # Create a copy to avoid modifying the original message in state
                action = tool_call.copy()
                # Enrich with task details if available
                args = action.get("args", {})
                task_id = args.get("task_id")
                if task_id:
                    try:
                        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
                        async with async_session() as session:
                            service = TaskService(session)
                            task = await service.get_task(task_id)
                            if task:
                                action["task_details"] = task.model_dump()
                    except Exception as e:
                        print(f"Failed to fetch task details: {e}")
                proposed_actions.append(action)
                    
    return proposed_actions, status

from sqlalchemy import text

@router.get("/history")
async def get_chat_history():
    try:
        async with engine.connect() as conn:
            # Check if table exists
            result = await conn.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'checkpoints')"
            ))
            exists = result.scalar()
            
            if not exists:
                return {"threads": []}

            # Get threads
            # We could try to get the last write time to sort, but for now just list them
            result = await conn.execute(text(
                "SELECT thread_id FROM checkpoints GROUP BY thread_id"
            ))
            # Simple title generation
            threads = [{"id": row.thread_id, "title": f"Chat {row.thread_id[:8]}..."} for row in result]
            return {"threads": threads}
    except Exception as e:
        print(f"Error fetching history: {e}")
        return {"threads": []}

@router.get("/{thread_id}", response_model=ChatResponse)
async def get_chat_state(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    app_graph = await get_app_graph()
    snapshot = await app_graph.aget_state(config)
    
    if not snapshot.values:
        # New thread or empty
        return ChatResponse(
            thread_id=thread_id,
            messages=[],
            status="ready"
        )

    proposed_actions, status = await _get_proposed_action_with_details(snapshot)
    
    return ChatResponse(
        thread_id=thread_id,
        messages=_format_messages(snapshot.values["messages"]),
        proposed_actions=proposed_actions,
        proposed_action=proposed_actions[0] if proposed_actions else None,
        status=status
    )

@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    thread_id = request.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    # Get the graph
    app_graph = await get_app_graph()
    
    # Check for pending interruptions (sensitive tools waiting for approval)
    # If the user sends a new message instead of approving/rejecting, we must cancel the pending tools
    # to avoid "tool_use ids found without tool_result" errors from the LLM.
    snapshot = await app_graph.aget_state(config)
    if snapshot.next and "sensitive_tools" in snapshot.next:
        if snapshot.values and "messages" in snapshot.values:
            last_message = snapshot.values["messages"][-1]
            if isinstance(last_message, AIMessage) and last_message.tool_calls:
                # Auto-reject pending tools because user sent a new message
                tool_outputs = []
                for tool_call in last_message.tool_calls:
                    tool_outputs.append(ToolMessage(
                        tool_call_id=tool_call["id"],
                        content="Action cancelled by user (new message received).",
                        name=tool_call["name"]
                    ))
                
                await app_graph.aupdate_state(
                    config,
                    {"messages": tool_outputs},
                    as_node="sensitive_tools"
                )
    
    # Run the graph
    # If this is a new thread or continuing, we pass the new message
    input_message = HumanMessage(content=request.message)
    
    # We use stream=False (invoke) for simplicity, but we need to handle the interruption
    # app_graph.invoke returns the FINAL state. 
    # If interrupted, it returns the state at the interruption point.
    
    final_state = await app_graph.ainvoke(
        {"messages": [input_message]}, 
        config=config
    )
    
    # Check if we are interrupted
    snapshot = await app_graph.aget_state(config)
    
    proposed_actions, status = await _get_proposed_action_with_details(snapshot)
    
    return ChatResponse(
        thread_id=thread_id,
        messages=_format_messages(snapshot.values["messages"]),
        proposed_actions=proposed_actions,
        proposed_action=proposed_actions[0] if proposed_actions else None,
        status=status
    )

@router.post("/approve", response_model=ChatResponse)
async def approve_action(request: ApproveRequest):
    config = {"configurable": {"thread_id": request.thread_id}}
    
    app_graph = await get_app_graph()
    snapshot = await app_graph.aget_state(config)
    
    if not snapshot.next:
        raise HTTPException(status_code=400, detail="No pending action to approve")
        
    last_message = snapshot.values["messages"][-1]
    if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
         raise HTTPException(status_code=400, detail="No tool calls found in last message")

    # Determine which tools to run
    approved_ids = request.approved_tool_call_ids
    if approved_ids is None and request.tool_call_id:
        approved_ids = [request.tool_call_id]
    
    # If approved_ids is None here, it means "Approve All"
    approve_all = approved_ids is None

    tool_outputs = []
    
    for tool_call in last_message.tool_calls:
        tc_id = tool_call["id"]
        if approve_all or (approved_ids and tc_id in approved_ids):
            # Execute tool
            tool_name = tool_call["name"]
            tool = TOOL_MAP.get(tool_name)
            if tool:
                try:
                    # We need to await the tool execution
                    result = await tool.ainvoke(tool_call["args"])
                    
                    # Serialize result to JSON for better frontend handling
                    import json
                    content_str = str(result)
                    try:
                        if hasattr(result, "model_dump"):
                            content_str = json.dumps(result.model_dump(), default=str)
                        elif isinstance(result, list):
                            # Handle list of models or dicts
                            serialized_list = []
                            for item in result:
                                if hasattr(item, "model_dump"):
                                    serialized_list.append(item.model_dump())
                                else:
                                    serialized_list.append(item)
                            content_str = json.dumps(serialized_list, default=str)
                        elif isinstance(result, dict):
                            content_str = json.dumps(result, default=str)
                    except Exception as e:
                        print(f"Serialization error: {e}")
                        # Fallback to string representation
                        pass

                    tool_outputs.append(ToolMessage(
                        tool_call_id=tc_id,
                        content=content_str,
                        name=tool_name
                    ))
                except Exception as e:
                    tool_outputs.append(ToolMessage(
                        tool_call_id=tc_id,
                        content=f"Error executing tool: {str(e)}",
                        name=tool_name,
                        status="error"
                    ))
            else:
                 tool_outputs.append(ToolMessage(
                    tool_call_id=tc_id,
                    content=f"Tool {tool_name} not found",
                    name=tool_name,
                    status="error"
                ))
        else:
            # Rejected
            tool_outputs.append(ToolMessage(
                tool_call_id=tc_id,
                content="Action cancelled by user.",
                name=tool_call["name"]
            ))

    # Update state with ALL outputs
    await app_graph.aupdate_state(
        config, 
        {"messages": tool_outputs}, 
        as_node="sensitive_tools" 
    )
    
    # Resume execution
    final_state = await app_graph.ainvoke(None, config=config)
    
    # Check if there are more actions or if we are done
    snapshot = await app_graph.aget_state(config)
    
    proposed_actions, status = await _get_proposed_action_with_details(snapshot)
            
    return ChatResponse(
        thread_id=request.thread_id,
        messages=_format_messages(snapshot.values["messages"]),
        proposed_actions=proposed_actions,
        proposed_action=proposed_actions[0] if proposed_actions else None,
        status=status
    )

@router.post("/reject", response_model=ChatResponse)
async def reject_action(request: RejectRequest):
    config = {"configurable": {"thread_id": request.thread_id}}
    
    app_graph = await get_app_graph()
    snapshot = await app_graph.aget_state(config)
    
    if not snapshot.next:
        raise HTTPException(status_code=400, detail="No pending action to reject")
    
    last_message = snapshot.values["messages"][-1]
    if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
         raise HTTPException(status_code=400, detail="No tool calls found in last message")

    # Reject ALL pending actions if specific ID is not provided or just reject everything for safety
    # If the user wants to reject specific ones, they should use the approve endpoint with the ones they WANT.
    # So reject endpoint is "Cancel All".
    
    tool_outputs = []
    for tool_call in last_message.tool_calls:
        tool_outputs.append(ToolMessage(
            tool_call_id=tool_call["id"],
            content=f"Action cancelled by user. Reason: {request.reason}",
            name=tool_call["name"]
        ))
    
    await app_graph.aupdate_state(
        config, 
        {"messages": tool_outputs}, 
        as_node="sensitive_tools" 
    )
    
    # Now resume.
    final_state = await app_graph.ainvoke(None, config=config)
    
    snapshot = await app_graph.aget_state(config)
    
    proposed_actions, status = await _get_proposed_action_with_details(snapshot)

    return ChatResponse(
        thread_id=request.thread_id,
        messages=_format_messages(snapshot.values["messages"]),
        proposed_actions=proposed_actions,
        proposed_action=proposed_actions[0] if proposed_actions else None,
        status=status
    )
