from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, case
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.accounting_entry import AccountingEntry
from app.models.accounting_entry_line import AccountingEntryLine
from app.models.chart_of_account import ChartOfAccount
from app.models.economic_event import EconomicEvent
from app.models.financial_report import FinancialReport
from app.models.normalized_record import NormalizedRecord
from app.models.source_file import SourceFile
from app.schemas.report_storage import FinancialReportSavedResponse

router = APIRouter(prefix="/files", tags=["report-storage"])


@router.post("/{source_file_id}/dre/save", response_model=FinancialReportSavedResponse, status_code=201)
def save_dre_report(source_file_id: UUID, db: Session = Depends(get_db)):
    source_file = db.query(SourceFile).filter(SourceFile.id == source_file_id).first()
    if not source_file:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")

    rows = (
        db.query(
            ChartOfAccount.dre_group.label("dre_group"),
            ChartOfAccount.code.label("account_code"),
            ChartOfAccount.name.label("account_name"),
            func.coalesce(
                func.sum(
                    case(
                        (AccountingEntryLine.dc == "C", AccountingEntryLine.amount),
                        else_=-AccountingEntryLine.amount,
                    )
                ),
                0,
            ).label("raw_amount"),
        )
        .join(AccountingEntryLine, AccountingEntryLine.account_id == ChartOfAccount.id)
        .join(AccountingEntry, AccountingEntry.id == AccountingEntryLine.entry_id)
        .join(EconomicEvent, EconomicEvent.id == AccountingEntry.economic_event_id)
        .join(NormalizedRecord, NormalizedRecord.id == EconomicEvent.normalized_record_id)
        .filter(NormalizedRecord.source_file_id == source_file_id)
        .filter(ChartOfAccount.dre_group.isnot(None))
        .group_by(
            ChartOfAccount.dre_group,
            ChartOfAccount.code,
            ChartOfAccount.name,
        )
        .order_by(ChartOfAccount.dre_group.asc(), ChartOfAccount.code.asc())
        .all()
    )

    if not rows:
        raise HTTPException(status_code=404, detail="Nenhum dado de DRE encontrado para este arquivo.")

    grouped: dict[str, list[dict]] = {}
    total_revenue = 0.0
    total_expenses = 0.0

    for row in rows:
        group = row.dre_group
        amount = float(row.raw_amount)

        if group in ("receita", "despesa"):
            amount = abs(amount)

        grouped.setdefault(group, []).append(
            {
                "account_code": row.account_code,
                "account_name": row.account_name,
                "amount": amount,
            }
        )

    groups = []
    for group_name, accounts in grouped.items():
        group_total = sum(account["amount"] for account in accounts)

        groups.append(
            {
                "group": group_name,
                "amount": group_total,
                "accounts": accounts,
            }
        )

        if group_name == "receita":
            total_revenue += group_total
        elif group_name == "despesa":
            total_expenses += group_total

    net_result = total_revenue - total_expenses

    payload = {
        "source_file_id": str(source_file_id),
        "summary": {
            "total_revenue": total_revenue,
            "total_expenses": total_expenses,
            "net_result": net_result,
        },
        "groups": sorted(groups, key=lambda g: g["group"]),
    }

    report = FinancialReport(
        company_id=source_file.company_id,
        source_file_id=source_file_id,
        report_type="dre",
        payload_json=payload,
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return FinancialReportSavedResponse(
        report_id=report.id,
        source_file_id=source_file_id,
        report_type="dre",
        message="DRE salva com sucesso.",
    )