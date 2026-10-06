import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, default="OPEN", nullable=False)  # OPEN, IN_PROGRESS, PENDING_APPROVAL, RESOLVED, CLOSED
    priority = Column(String, default="MEDIUM", nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User")
