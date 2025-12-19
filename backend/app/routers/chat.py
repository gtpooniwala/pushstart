from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid

from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from app.agent.graph import app_graph
from app.core.db import engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from app.services.task_service import TaskService

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None

class ApproveRequest(BaseModel):
    thread_id: str
    tool_call_id: str # To verify we are approving the right thing

class RejectRequest(BaseModel):
    thread_id: str
    tool_call_id: str
    reason: Optional[str] = "Rejected by user"

class ChatResponse(BaseModel):
    thread_id: str
    messages: List[Dict[str, Any]]
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
    proposed_action = None
    status = "ready"
    
    if snapshot.next and "sensitive_tools" in snapshot.next:
        last_message = snapshot.values["messages"][-1]
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            proposed_action = last_message.tool_calls[0]
            status = "waiting_for_approval"
            
            # Enrich with task details if available
            args = proposed_action.get("args", {})
            task_id = args.get("task_id")
            if task_id:
                try:
                    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
                    async with async_session() as session:
                        service = TaskService(session)
                        task = await service.get_task(task_id)
                        if task:
                            proposed_action["task_details"] = task.model_dump()
                except Exception as e:
                    print(f"Failed to fetch task details: {e}")
                    
    return proposed_action, status

@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    thread_id = request.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
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
    snapshot = app_graph.get_state(config)
    
    proposed_action, status = await _get_proposed_action_with_details(snapshot)
    
    return ChatResponse(
        thread_id=thread_id,
        messages=_format_messages(snapshot.values["messages"]),
        proposed_action=proposed_action,
        status=status
    )

@router.post("/approve", response_model=ChatResponse)
async def approve_action(request: ApproveRequest):
    config = {"configurable": {"thread_id": request.thread_id}}
    snapshot = app_graph.get_state(config)
    
    if not snapshot.next:
        raise HTTPException(status_code=400, detail="No pending action to approve")
        
    # Resume execution (None input means continue)
    final_state = await app_graph.ainvoke(None, config=config)
    
    # Check if there are more actions or if we are done
    snapshot = app_graph.get_state(config)
    
    proposed_action, status = await _get_proposed_action_with_details(snapshot)
            
    return ChatResponse(
        thread_id=request.thread_id,
        messages=_format_messages(snapshot.values["messages"]),
        proposed_action=proposed_action,
        status=status
    )

@router.post("/reject", response_model=ChatResponse)
async def reject_action(request: RejectRequest):
    config = {"configurable": {"thread_id": request.thread_id}}
    snapshot = app_graph.get_state(config)
    
    if not snapshot.next:
        raise HTTPException(status_code=400, detail="No pending action to reject")
    
    # To reject, we inject a ToolMessage with error/rejection content
    # This simulates the tool running and failing/being cancelled
    
    tool_call_id = request.tool_call_id
    rejection_message = ToolMessage(
        tool_call_id=tool_call_id,
        content=f"Action cancelled by user. Reason: {request.reason}"
    )
    
    # We update the state to include this message
    # And then we resume. The graph will see the ToolMessage and go back to 'chatbot'
    # The chatbot will see the rejection and respond.
    
    # Note: We need to be careful. If we are interrupted BEFORE 'tools', 
    # the 'tools' node hasn't run.
    # If we manually insert a ToolMessage, we are effectively bypassing the 'tools' node.
    # But the graph expects to run 'tools' next.
    # We can use update_state to adding the message as if the tool node produced it.
    # And then we need to tell the graph to skip the 'tools' node execution for this step?
    # Or we can just update the state with the ToolMessage and set 'as_node="tools"' 
    # so the graph thinks the tools node just ran.
    
    app_graph.update_state(
        config, 
        {"messages": [rejection_message]}, 
        as_node="sensitive_tools" 
    )
    
    # Now resume. Since we updated as "tools", the next node should be "chatbot" (based on edge tools->chatbot)
    final_state = await app_graph.ainvoke(None, config=config)
    
    snapshot = app_graph.get_state(config)
    
    return ChatResponse(
        thread_id=request.thread_id,
        messages=_format_messages(snapshot.values["messages"]),
        proposed_action=None,
        status="ready"
    )
