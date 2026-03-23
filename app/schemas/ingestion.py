from uuid import UUID
from pydantic import BaseModel


class IngestionResponse(BaseModel):
    source_file_id: UUID
    rows_ingested: int
    message: str