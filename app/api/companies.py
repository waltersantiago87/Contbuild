from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyResponse

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("", response_model=CompanyResponse, status_code=201)
def create_company(payload: CompanyCreate, db: Session = Depends(get_db)):
    existing_company = db.query(Company).filter(Company.cnpj == payload.cnpj).first()
    if existing_company:
        raise HTTPException(status_code=400, detail="CNPJ já cadastrado.")

    company = Company(
        name=payload.name,
        cnpj=payload.cnpj,
        tax_regime=payload.tax_regime,
    )

    db.add(company)
    db.commit()
    db.refresh(company)

    return company


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(company_id: UUID, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada.")

    return company