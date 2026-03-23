from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.company import Company
from app.models.source_file import SourceFile
from app.schemas.file import SourceFileResponse  # ← FALTAVA ISSO

router = APIRouter(prefix="/companies", tags=["files"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/{company_id}/files", response_model=SourceFileResponse, status_code=201)
def upload_file(
    company_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # 1. Verifica se a empresa existe
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada.")

    # 2. Gera nome único para o arquivo
    unique_filename = f"{uuid4()}_{file.filename}"
    storage_path = UPLOAD_DIR / unique_filename

    # 3. Lê o conteúdo do arquivo
    content = file.file.read()

    # 4. Salva o arquivo no disco
    with open(storage_path, "wb") as buffer:
        buffer.write(content)

    # 5. Salva no banco
    source_file = SourceFile(
        company_id=company_id,
        filename=file.filename,
        storage_path=str(storage_path),
        mime_type=file.content_type,
        size_bytes=len(content),
        uploaded_by=None,
    )

    db.add(source_file)
    db.commit()
    db.refresh(source_file)

    # 6. Retorna resposta
    return source_file
