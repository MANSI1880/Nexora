from app.database.base import Base
from app.models.user import User
from app.models.ticket import Ticket
from app.models.audit_log import AuditLog
from app.models.approval import Approval

# This ensures all models are loaded when Base.metadata is imported by Alembic
__all__ = ["Base", "User", "Ticket", "AuditLog", "Approval"]
