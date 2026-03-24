from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.companies import router as companies_router
from app.api.files import router as files_router
from app.api.ingestion import router as ingestion_router
from app.api.normalization import router as normalization_router
from app.api.event_builder import router as event_builder_router
from app.api.posting import router as posting_router
from app.api.reporting import router as reporting_router
from app.api.dre import router as dre_router
from app.api.report_storage import router as report_storage_router

app = FastAPI(title="Contabilidade API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(companies_router)
app.include_router(files_router)
app.include_router(ingestion_router)
app.include_router(normalization_router)
app.include_router(event_builder_router)
app.include_router(posting_router)
app.include_router(reporting_router)
app.include_router(dre_router)
app.include_router(report_storage_router)


@app.get("/")
def root():
    return {"message": "API de contabilidade no ar"}
