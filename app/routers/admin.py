from fastapi import APIRouter
from app.services.ingest_docx import rebuild_from_sources
from app.services.kb_store import KBStore

router = APIRouter()

@router.post("/reload-kb")
def reload_kb():
    rebuilt = rebuild_from_sources()
    KBStore.instance().warm(force=True)
    return {"reloaded": rebuilt}
