from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class SourceFileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    filename: str
    storage_path: str
    mime_type: str | None = None
    size_bytes: int | None = None
    file_hash: str | None = None
    uploaded_by: str | None = None
    uploaded_at: datetime