from uuid import UUID
from pydantic import BaseModel


class FinancialReportSavedResponse(BaseModel):
    report_id: UUID
    source_file_id: UUID
    report_type: str
    message: str