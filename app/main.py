from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.routers import intake, export, admin, schemas, health
from app.services.ingest_docx import ensure_kb_materialized
from app.services.kb_store import KBStore
from app.models import init_db

app = FastAPI(title="LaunchPad AI Decision Engine", version="1.0.0")

# CORS for Wix domain(s)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static exports
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routers
app.include_router(health.router)
app.include_router(schemas.router)
app.include_router(intake.router, prefix="/intake")
app.include_router(export.router, prefix="/export")
app.include_router(admin.router, prefix="/admin")

@app.on_event("startup")
def startup():
    init_db()
    # Build KB JSON from DOCX/XLSX if present, then index embeddings
    ensure_kb_materialized()
    KBStore.instance().warm()
