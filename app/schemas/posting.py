from uuid import UUID
from pydantic import BaseModel


class PostingResponse(BaseModel):
    source_file_id: UUID
    entries_created: int
    lines_created: int
    message: str