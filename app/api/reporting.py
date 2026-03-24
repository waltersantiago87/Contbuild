from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, case
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.accounting_entry import AccountingEntry
from app.models.accounting_entry_line import AccountingEntryLine
from app.models.chart_of_account import ChartOfAccount
from app.models.economic_event import EconomicEvent
from app.models.normalized_record import NormalizedRecord
from app.schemas.reporting import TrialBalanceLine, TrialBalanceResponse

router = APIRouter(prefix="/files", tags=["reporting"])


@router.get("/{source_file_id}/trial-balance", response_model=TrialBalanceResponse)
def get_trial_balance(source_file_id: UUID, db: Session = Depends(get_db)):
    rows = (
        db.query(
            ChartOfAccount.code.label("account_code"),
            ChartOfAccount.name.label("account_name"),
            func.coalesce(
                func.sum(
                    case(
                        (AccountingEntryLine.dc == "D", AccountingEntryLine.amount),
                        else_=0,
                    )
                ),
                0,
            ).label("total_debit"),
            func.coalesce(
                func.sum(
                    case(
                        (AccountingEntryLine.dc == "C", AccountingEntryLine.amount),
                        else_=0,
                    )
                ),
                0,
            ).label("total_credit"),
        )
        .join(AccountingEntryLine, AccountingEntryLine.account_id == ChartOfAccount.id)
        .join(AccountingEntry, AccountingEntry.id == AccountingEntryLine.entry_id)
        .join(EconomicEvent, EconomicEvent.id == AccountingEntry.economic_event_id)
        .join(NormalizedRecord, NormalizedRecord.id == EconomicEvent.normalized_record_id)
        .filter(NormalizedRecord.source_file_id == source_file_id)
        .group_by(ChartOfAccount.code, ChartOfAccount.name)
        .order_by(ChartOfAccount.code.asc())
        .all()
    )

    if not rows:
        raise HTTPException(status_code=404, detail="Nenhum lançamento encontrado para este arquivo.")

    lines = [
        TrialBalanceLine(
            account_code=row.account_code,
            account_name=row.account_name,
            total_debit=float(row.total_debit),
            total_credit=float(row.total_credit),
        )
        for row in rows
    ]

    return TrialBalanceResponse(
        source_file_id=str(source_file_id),
        lines=lines,
    )