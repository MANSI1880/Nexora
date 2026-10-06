from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database.connection import get_db
from app.models.user import User
from app.auth.dependencies import get_current_user
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketResponse
from app.services import ticket as ticket_service

router = APIRouter(prefix="/api/tickets", tags=["tickets"])

@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket_endpoint(
    ticket_in: TicketCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await ticket_service.create_ticket(db, ticket_in, current_user.id)

@router.get("", response_model=List[TicketResponse])
async def get_tickets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role in ["admin", "it_support"]:
        return await ticket_service.get_all_tickets(db)
    return await ticket_service.get_user_tickets(db, current_user.id)

@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_ticket = await ticket_service.get_ticket_by_id(db, ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    if current_user.role not in ["admin", "it_support"] and db_ticket.user_id != current_user.id:
        await ticket_service.create_audit_log(db, "unauthorized_ticket_access", current_user.id, f"Attempted to access ticket {ticket_id}")
        await db.commit()
        raise HTTPException(status_code=403, detail="Not authorized to view this ticket")
        
    return db_ticket

@router.put("/{ticket_id}", response_model=TicketResponse)
async def update_ticket_endpoint(
    ticket_id: int,
    ticket_update: TicketUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_ticket = await ticket_service.get_ticket_by_id(db, ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    if current_user.role not in ["admin", "it_support"] and db_ticket.user_id != current_user.id:
        await ticket_service.create_audit_log(db, "unauthorized_ticket_access", current_user.id, f"Attempted to update ticket {ticket_id}")
        await db.commit()
        raise HTTPException(status_code=403, detail="Not authorized to update this ticket")
        
    return await ticket_service.update_ticket(db, db_ticket, ticket_update, current_user.id)
