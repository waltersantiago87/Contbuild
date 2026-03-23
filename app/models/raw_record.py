import uuid
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.core.database import Base

class RawRecord(Base):
    __tablename__ = "raw_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_file_id = Column(UUID(as_uuid=True), ForeignKey("source_files.id"), nullable=False)
    row_number = Column(Integer, nullable=True)
    raw_payload_json = Column(JSONB, nullable=False)
    extracted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)