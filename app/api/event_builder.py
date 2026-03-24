from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.economic_event import EconomicEvent
from app.models.normalized_record import NormalizedRecord
from app.models.source_file import SourceFile
from app.schemas.event_builder import EventBuilderResponse

router = APIRouter(prefix="/files", tags=["event-builder"])


def infer_event_type(description: str, direction: str) -> tuple[str, str | None]:
    desc = description.upper()

    if "TARIFA" in desc or "BANCO" in desc:
        return "bank_fee", "Banco"

    if "FORNECEDOR" in desc and direction == "outflow":
        return "supplier_payment", "Fornecedor XPTO"

    if "CLIENTE" in desc and direction == "inflow":
        return "customer_receipt", "Cliente"

    if direction == "outflow":
        return "operational_expense", None

    if direction == "inflow":
        return "service_revenue", None

    return "unclassified_event", None


@router.post("/{source_file_id}/build-events", response_model=EventBuilderResponse, status_code=201)
def build_events(source_file_id: UUID, db: Session = Depends(get_db)):
    source_file = db.query(SourceFile).filter(SourceFile.id == source_file_id).first()
    if not source_file:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")

    normalized_records = (
        db.query(NormalizedRecord)
        .filter(NormalizedRecord.source_file_id == source_file_id)
        .order_by(NormalizedRecord.created_at.asc())
        .all()
    )

    if not normalized_records:
        raise HTTPException(status_code=400, detail="Nenhum normalized_record encontrado para este arquivo.")

    events_created = 0

    for normalized_record in normalized_records:
        payload = normalized_record.normalized_payload_json

        event_type, related_entity = infer_event_type(
            payload["description"],
            payload["direction"]
        )

        event = EconomicEvent(
            company_id=source_file.company_id,
            normalized_record_id=normalized_record.id,
            event_type=event_type,
            event_date=datetime.strptime(payload["transaction_date"], "%Y-%m-%d").date(),
            total_amount=payload["amount"],
            currency="BRL",
            related_entity=related_entity,
            description=payload["description"],
            source_ref=f"normalized_record:{normalized_record.id}",
        )

        db.add(event)
        events_created += 1

    db.commit()

    return EventBuilderResponse(
        source_file_id=source_file_id,
        events_created=events_created,
        message="Eventos econômicos criados com sucesso."
    )