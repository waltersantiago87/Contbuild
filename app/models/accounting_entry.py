import uuid
from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base


class AccountingEntry(Base):
    __tablename__ = "accounting_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    economic_event_id = Column(UUID(as_uuid=True), ForeignKey("economic_events.id"), nullable=False)
    entry_date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    source = Column(String(50), nullable=False, default="system")
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)