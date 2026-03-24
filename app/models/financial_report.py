import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.core.database import Base


class FinancialReport(Base):
    __tablename__ = "financial_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    source_file_id = Column(UUID(as_uuid=True), ForeignKey("source_files.id"), nullable=False)
    report_type = Column(String(50), nullable=False)
    payload_json = Column(JSONB, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)