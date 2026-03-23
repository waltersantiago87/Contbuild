import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.core.database import Base

class NormalizedRecord(Base):
    __tablename__ = "normalized_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_file_id = Column(UUID(as_uuid=True), ForeignKey("source_files.id"), nullable=False)
    raw_record_id = Column(UUID(as_uuid=True), ForeignKey("raw_records.id"), nullable=True)
    record_type = Column(String(50), nullable=False)
    normalized_payload_json = Column(JSONB, nullable=False)
    normalization_version = Column(String(30), nullable=False, default="v1")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)