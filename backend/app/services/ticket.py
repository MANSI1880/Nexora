from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
import datetime

from app.models.ticket import Ticket
from app.models.audit_log import AuditLog
from app.schemas.ticket import TicketCreate, TicketUpdate

async def create_audit_log(db: AsyncSession, action: str, user_id: int | None = None, details: str | None = None):
    log = AuditLog(user_id=user_id, action=action, details=details, timestamp=datetime.datetime.utcnow())
    db.add(log)

async def create_ticket(db: AsyncSession, ticket_in: TicketCreate, user_id: int) -> Ticket:
    db_ticket = Ticket(
        title=ticket_in.title,
        description=ticket_in.description,
        priority=ticket_in.priority or "MEDIUM",
        user_id=user_id,
        status="OPEN"
    )
    db.add(db_ticket)
    await db.commit()
    await db.refresh(db_ticket)
    
    await create_audit_log(db, "ticket_created", user_id=user_id, details=f"Ticket {db_ticket.id} created.")
    await db.commit()
    return db_ticket

async def get_ticket_by_id(db: AsyncSession, ticket_id: int) -> Ticket | None:
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    return result.scalars().first()

async def get_user_tickets(db: AsyncSession, user_id: int):
    result = await db.execute(select(Ticket).where(Ticket.user_id == user_id))
    return result.scalars().all()

async def get_all_tickets(db: AsyncSession):
    result = await db.execute(select(Ticket))
    return result.scalars().all()

async def update_ticket(db: AsyncSession, db_ticket: Ticket, ticket_update: TicketUpdate, user_id: int) -> Ticket:
    if ticket_update.status:
        db_ticket.status = ticket_update.status
    if ticket_update.priority:
        db_ticket.priority = ticket_update.priority
        
    db.add(db_ticket)
    await create_audit_log(db, "ticket_updated", user_id=user_id, details=f"Ticket {db_ticket.id} updated.")
    await db.commit()
    await db.refresh(db_ticket)
    return db_ticket
