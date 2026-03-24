from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.accounting_entry import AccountingEntry
from app.models.accounting_entry_line import AccountingEntryLine
from app.models.chart_of_account import ChartOfAccount
from app.models.economic_event import EconomicEvent
from app.models.normalized_record import NormalizedRecord
from app.schemas.posting import PostingResponse

router = APIRouter(prefix="/files", tags=["posting"])


def get_account_by_code(db: Session, code: str) -> ChartOfAccount:
    account = db.query(ChartOfAccount).filter(ChartOfAccount.code == code).first()
    if not account:
        raise HTTPException(status_code=500, detail=f"Conta contábil {code} não encontrada.")
    return account


def resolve_accounts(db: Session, event_type: str):
    bank_account = get_account_by_code(db, "1.1.1.01")

    if event_type == "supplier_payment":
        debit_account = get_account_by_code(db, "2.1.1.01")
        credit_account = bank_account
        return debit_account, credit_account

    if event_type == "bank_fee":
        debit_account = get_account_by_code(db, "4.1.1.01")
        credit_account = bank_account
        return debit_account, credit_account

    if event_type == "customer_receipt":
        debit_account = bank_account
        credit_account = get_account_by_code(db, "3.1.1.01")
        return debit_account, credit_account

    if event_type == "operational_expense":
        debit_account = get_account_by_code(db, "4.1.1.02")
        credit_account = bank_account
        return debit_account, credit_account

    if event_type == "service_revenue":
        debit_account = bank_account
        credit_account = get_account_by_code(db, "3.1.1.01")
        return debit_account, credit_account

    raise HTTPException(status_code=400, detail=f"Sem regra contábil para event_type={event_type}")


@router.post("/{source_file_id}/post-entries", response_model=PostingResponse, status_code=201)
def post_entries(source_file_id: UUID, db: Session = Depends(get_db)):
    events = (
        db.query(EconomicEvent)
        .join(NormalizedRecord, EconomicEvent.normalized_record_id == NormalizedRecord.id)
        .filter(NormalizedRecord.source_file_id == source_file_id)
        .order_by(EconomicEvent.created_at.asc())
        .all()
    )

    if not events:
        raise HTTPException(status_code=400, detail="Nenhum economic_event encontrado para este arquivo.")

    entries_created = 0
    lines_created = 0

    for event in events:
        debit_account, credit_account = resolve_accounts(db, event.event_type)

        entry = AccountingEntry(
            company_id=event.company_id,
            economic_event_id=event.id,
            entry_date=event.event_date,
            description=event.description,
            source="system",
            version=1,
        )
        db.add(entry)
        db.flush()

        debit_line = AccountingEntryLine(
            entry_id=entry.id,
            account_id=debit_account.id,
            dc="D",
            amount=event.total_amount,
            history=event.description,
        )
        credit_line = AccountingEntryLine(
            entry_id=entry.id,
            account_id=credit_account.id,
            dc="C",
            amount=event.total_amount,
            history=event.description,
        )

        db.add(debit_line)
        db.add(credit_line)

        entries_created += 1
        lines_created += 2

    db.commit()

    return PostingResponse(
        source_file_id=source_file_id,
        entries_created=entries_created,
        lines_created=lines_created,
        message="Lançamentos contábeis criados com sucesso."
    )