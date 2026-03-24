import uuid
from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base


class EconomicEvent(Base):
    __tablename__ = "economic_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    normalized_record_id = Column(UUID(as_uuid=True), ForeignKey("normalized_records.id"), nullable=True)
    event_type = Column(String(100), nullable=False)
    event_date = Column(Date, nullable=False)
    total_amount = Column(Numeric(18, 2), nullable=False)
    currency = Column(String(10), nullable=False, default="BRL")
    related_entity = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    source_ref = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)