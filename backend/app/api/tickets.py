from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database.connection import get_db
from app.models.user import User
from app.auth.dependencies import get_current_user, require_role
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    if current_user.role not in ["admin", "it_support"] and db_ticket.user_id != current_user.id:
        await ticket_service.create_audit_log(db, "unauthorized_ticket_access", current_user.id, f"Attempted to access ticket {ticket_id}")
        await db.commit()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    if current_user.role not in ["admin", "it_support"] and db_ticket.user_id != current_user.id:
        await ticket_service.create_audit_log(db, "unauthorized_ticket_access", current_user.id, f"Attempted to update ticket {ticket_id}")
        await db.commit()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    # Regular users cannot change status or priority
    if current_user.role not in ["admin", "it_support"]:
        if ticket_update.status is not None or ticket_update.priority is not None:
            await ticket_service.create_audit_log(
                db,
                "unauthorized_status_change",
                current_user.id,
                f"Attempted to modify status/priority on ticket {ticket_id}"
            )
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only IT Support or Admin can alter ticket status or priority"
            )

    return await ticket_service.update_ticket(db, db_ticket, ticket_update, current_user.id)

@router.post("/{ticket_id}/approve", response_model=TicketResponse)
async def approve_ticket_endpoint(
    ticket_id: int,
    current_user: User = Depends(require_role(["admin", "it_support"])),
    db: AsyncSession = Depends(get_db)
):
    try:
        db_ticket = await ticket_service.get_ticket_by_id(db, ticket_id, for_update=True, nowait=True)
    except Exception as exc:
        err_msg = str(exc).lower()
        if "lock" in err_msg or "conflict" in err_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ticket is currently being processed by another transaction"
            )
        raise
    if not db_ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    # Prevent requester from approving their own ticket
    if db_ticket.user_id == current_user.id:
        await ticket_service.create_audit_log(
            db,
            "unauthorized_self_approval",
            current_user.id,
            f"User attempted to approve their own ticket {ticket_id}"
        )
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requesters cannot approve their own tickets"
        )

    # Validate status transition: ticket must be PENDING_APPROVAL
    if db_ticket.status != "PENDING_APPROVAL":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ticket cannot be approved in '{db_ticket.status}' status"
        )

    updated_ticket, _ = await ticket_service.process_ticket_approval(
        db, db_ticket, current_user.id, approved=True
    )
    return updated_ticket

@router.post("/{ticket_id}/reject", response_model=TicketResponse)
async def reject_ticket_endpoint(
    ticket_id: int,
    current_user: User = Depends(require_role(["admin", "it_support"])),
    db: AsyncSession = Depends(get_db)
):
    try:
        db_ticket = await ticket_service.get_ticket_by_id(db, ticket_id, for_update=True, nowait=True)
    except Exception as exc:
        err_msg = str(exc).lower()
        if "lock" in err_msg or "conflict" in err_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ticket is currently being processed by another transaction"
            )
        raise
    if not db_ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    # Prevent requester from rejecting their own ticket
    if db_ticket.user_id == current_user.id:
        await ticket_service.create_audit_log(
            db,
            "unauthorized_self_rejection",
            current_user.id,
            f"User attempted to reject their own ticket {ticket_id}"
        )
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requesters cannot reject their own tickets"
        )

    # Validate status transition: ticket must be PENDING_APPROVAL
    if db_ticket.status != "PENDING_APPROVAL":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ticket cannot be rejected in '{db_ticket.status}' status"
        )

    updated_ticket, _ = await ticket_service.process_ticket_approval(
        db, db_ticket, current_user.id, approved=False
    )
    return updated_ticket
