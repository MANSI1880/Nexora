from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from datetime import datetime, timezone

from app.models.ticket import Ticket
from app.models.approval import Approval
from app.models.audit_log import AuditLog
from app.schemas.ticket import TicketCreate, TicketUpdate

async def create_audit_log(db: AsyncSession, action: str, user_id: int | None = None, details: str | None = None):
    log = AuditLog(user_id=user_id, action=action, details=details, timestamp=datetime.now(timezone.utc).replace(tzinfo=None))
    db.add(log)

async def create_ticket(db: AsyncSession, ticket_in: TicketCreate, user_id: int, status: str = "OPEN") -> Ticket:
    db_ticket = Ticket(
        title=ticket_in.title,
        description=ticket_in.description,
        priority=ticket_in.priority or "MEDIUM",
        user_id=user_id,
        status=status
    )
    db.add(db_ticket)
    await db.commit()
    await db.refresh(db_ticket)

    await create_audit_log(db, "ticket_created", user_id=user_id, details=f"Ticket {db_ticket.id} created with status {status}.")
    await db.commit()
    return db_ticket

async def get_ticket_by_id(db: AsyncSession, ticket_id: int, for_update: bool = False, nowait: bool = False) -> Ticket | None:
    stmt = select(Ticket).where(Ticket.id == ticket_id)
    if for_update:
        stmt = stmt.with_for_update(nowait=nowait)
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_user_tickets(db: AsyncSession, user_id: int):
    result = await db.execute(select(Ticket).where(Ticket.user_id == user_id))
    return result.scalars().all()

async def get_all_tickets(db: AsyncSession):
    result = await db.execute(select(Ticket))
    return result.scalars().all()

async def update_ticket(db: AsyncSession, db_ticket: Ticket, ticket_update: TicketUpdate, user_id: int) -> Ticket:
    changes = []
    if ticket_update.title and ticket_update.title != db_ticket.title:
        changes.append(f"title: '{db_ticket.title}' -> '{ticket_update.title}'")
        db_ticket.title = ticket_update.title
    if ticket_update.description and ticket_update.description != db_ticket.description:
        changes.append("description updated")
        db_ticket.description = ticket_update.description
    if ticket_update.status and ticket_update.status != db_ticket.status:
        changes.append(f"status: '{db_ticket.status}' -> '{ticket_update.status}'")
        db_ticket.status = ticket_update.status
    if ticket_update.priority and ticket_update.priority != db_ticket.priority:
        changes.append(f"priority: '{db_ticket.priority}' -> '{ticket_update.priority}'")
        db_ticket.priority = ticket_update.priority

    db.add(db_ticket)
    details_msg = f"Ticket {db_ticket.id} updated: {', '.join(changes)}" if changes else f"Ticket {db_ticket.id} updated."
    await create_audit_log(db, "ticket_updated", user_id=user_id, details=details_msg)
    await db.commit()
    await db.refresh(db_ticket)
    return db_ticket

async def get_approval_by_ticket_id(db: AsyncSession, ticket_id: int) -> Approval | None:
    result = await db.execute(select(Approval).where(Approval.ticket_id == ticket_id))
    return result.scalars().first()

async def process_ticket_approval(
    db: AsyncSession,
    db_ticket: Ticket,
    approver_id: int,
    approved: bool
) -> tuple[Ticket, Approval]:
    new_ticket_status = "APPROVED" if approved else "REJECTED"
    approval_status = "APPROVED" if approved else "DENIED"

    db_ticket.status = new_ticket_status
    db.add(db_ticket)

    existing_approval = await get_approval_by_ticket_id(db, db_ticket.id)
    if existing_approval:
        existing_approval.status = approval_status
        existing_approval.approver_id = approver_id
        existing_approval.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        db.add(existing_approval)
        approval_record = existing_approval
    else:
        approval_record = Approval(
            ticket_id=db_ticket.id,
            approver_id=approver_id,
            status=approval_status
        )
        db.add(approval_record)

    action_name = "ticket_approved" if approved else "ticket_rejected"
    await create_audit_log(
        db,
        action_name,
        user_id=approver_id,
        details=f"Ticket {db_ticket.id} {action_name.split('_')[1]} by user {approver_id}. Ticket status transitioned to {new_ticket_status}."
    )
    await db.commit()
    await db.refresh(db_ticket)
    await db.refresh(approval_record)
    return db_ticket, approval_record
