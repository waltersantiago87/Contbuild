import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.core.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    task_type = Column(String(100), nullable=False)
    status = Column(String(30), nullable=False, default="PENDING")
    attempt = Column(Integer, nullable=False, default=0)
    priority = Column(Integer, nullable=False, default=0)
    celery_task_id = Column(String(255), nullable=True)
    input_ref = Column(Text, nullable=True)
    output_ref = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    error_code = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    error_details_json = Column(JSONB, nullable=True)
    metrics_json = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)