import csv
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.raw_record import RawRecord
from app.models.source_file import SourceFile
from app.schemas.ingestion import IngestionResponse

router = APIRouter(prefix="/files", tags=["ingestion"])


@router.post("/{source_file_id}/ingest", response_model=IngestionResponse, status_code=201)
def ingest_source_file(source_file_id: UUID, db: Session = Depends(get_db)):
    source_file = db.query(SourceFile).filter(SourceFile.id == source_file_id).first()
    if not source_file:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")

    file_path = Path(source_file.storage_path)

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo físico não encontrado no disco.")

    if file_path.suffix.lower() != ".csv":
        raise HTTPException(status_code=400, detail="Somente arquivos CSV são suportados nesta etapa.")

    rows_ingested = 0

    with open(file_path, "r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)

        for index, row in enumerate(reader, start=1):
            raw_record = RawRecord(
                source_file_id=source_file.id,
                row_number=index,
                raw_payload_json=row,
            )
            db.add(raw_record)
            rows_ingested += 1

    db.commit()

    return IngestionResponse(
        source_file_id=source_file.id,
        rows_ingested=rows_ingested,
        message="Arquivo ingerido com sucesso."
    )