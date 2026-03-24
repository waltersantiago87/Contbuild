from pydantic import BaseModel


class TrialBalanceLine(BaseModel):
    account_code: str
    account_name: str
    total_debit: float
    total_credit: float


class TrialBalanceResponse(BaseModel):
    source_file_id: str
    lines: list[TrialBalanceLine]