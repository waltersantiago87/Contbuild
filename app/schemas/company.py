from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class CompanyCreate(BaseModel):
    name: str
    cnpj: str
    tax_regime: str | None = None


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    cnpj: str
    tax_regime: str | None = None
    created_at: datetime