from uuid import UUID
from pydantic import BaseModel


class NormalizationResponse(BaseModel):
    source_file_id: UUID
    normalized_rows: int
    message: str