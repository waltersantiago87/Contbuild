from fastapi import FastAPI
from app.api.companies import router as companies_router
from app.api.files import router as files_router
from app.api.ingestion import router as ingestion_router
from app.api.normalization import router as normalization_router

app = FastAPI(title="Contabilidade API")

app.include_router(companies_router)
app.include_router(files_router)
app.include_router(ingestion_router)
app.include_router(normalization_router)


@app.get("/")
def root():
    return {"message": "API de contabilidade no ar"}
