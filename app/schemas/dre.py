from pydantic import BaseModel


class DreAccountLine(BaseModel):
    account_code: str
    account_name: str
    amount: float


class DreGroupLine(BaseModel):
    group: str
    amount: float
    accounts: list[DreAccountLine]


class DreSummary(BaseModel):
    total_revenue: float
    total_expenses: float
    net_result: float


class DreResponse(BaseModel):
    source_file_id: str
    summary: DreSummary
    groups: list[DreGroupLine]