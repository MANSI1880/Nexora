from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

from app.database.connection import get_db
from app.models.user import User
from app.auth.dependencies import get_current_user
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.ticket import TicketCreate
from app.services import ticket as ticket_service
from app.agents.orchestrator import process_chat_request

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Call the AI orchestrator. It expects a message string.
    # process_chat_request is synchronous, so we should run it in a threadpool to not block the event loop
    loop = asyncio.get_running_loop()
    ai_result = await loop.run_in_executor(None, process_chat_request, request.message)
    
    # Check if the AI wants to create a ticket (e.g. status requires it or action is present)
    if ai_result.get("status") in ["pending_approval", "needs_escalation"] or ai_result.get("action") is not None:
        title = f"Request: {ai_result.get('intent', 'general')}"
        description = f"User message: {request.message}\nAction: {ai_result.get('action')}\nAI Response: {ai_result.get('response')}"
        
        ticket_in = TicketCreate(title=title, description=description, priority="MEDIUM")
        new_ticket = await ticket_service.create_ticket(db, ticket_in, current_user.id)
        
        # Log specifically for AI creation
        await ticket_service.create_audit_log(db, "ai_ticket_created", current_user.id, f"AI created ticket {new_ticket.id}")
        await db.commit()
        
        ai_result["ticket_id"] = str(new_ticket.id)
        
    return ChatResponse(**ai_result)
