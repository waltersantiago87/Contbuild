from uuid import UUID
from pydantic import BaseModel


class EventBuilderResponse(BaseModel):
    source_file_id: UUID
    events_created: int
    message: str