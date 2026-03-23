from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.raw_record import RawRecord
from app.models.source_file import SourceFile
from app.models.normalized_record import NormalizedRecord
from app.schemas.normalization import NormalizationResponse

router = APIRouter(prefix="/files", tags=["normalization"])


@router.post("/{source_file_id}/normalize", response_model=NormalizationResponse, status_code=201)
def normalize_source_file(source_file_id: UUID, db: Session = Depends(get_db)):
    source_file = db.query(SourceFile).filter(SourceFile.id == source_file_id).first()
    if not source_file:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")

    raw_records = (
        db.query(RawRecord)
        .filter(RawRecord.source_file_id == source_file_id)
        .order_by(RawRecord.row_number.asc())
        .all()
    )

    if not raw_records:
        raise HTTPException(status_code=400, detail="Nenhum raw_record encontrado para este arquivo.")

    normalized_rows = 0

    for raw_record in raw_records:
        raw = raw_record.raw_payload_json

        original_amount = float(raw["amount"])
        direction = "outflow" if original_amount < 0 else "inflow"
        normalized_amount = abs(original_amount)

        normalized_payload = {
            "record_type": "bank_transaction",
            "transaction_date": raw["date"],
            "description": raw["description"],
            "amount": normalized_amount,
            "direction": direction,
        }

        normalized_record = NormalizedRecord(
            source_file_id=source_file_id,
            raw_record_id=raw_record.id,
            record_type="bank_transaction",
            normalized_payload_json=normalized_payload,
            normalization_version="v1",
        )

        db.add(normalized_record)
        normalized_rows += 1

    db.commit()

    return NormalizationResponse(
        source_file_id=source_file_id,
        normalized_rows=normalized_rows,
        message="Arquivo normalizado com sucesso."
    )