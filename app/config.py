import os
from pydantic import BaseModel
from typing import List

class Settings(BaseModel):
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    model: str = os.getenv("MODEL", "gpt-4.1-mini")
    embed_model: str = os.getenv("EMBED_MODEL", "text-embedding-3-small")
    db_url: str = os.getenv("DB_URL", "sqlite:///./launchpad.db")
    exports_dir: str = os.getenv("EXPORTS_DIR", "app/static/exports")
    allowed_origins: List[str] = (
        os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,https://*.wixsite.com,https://*.wixstudio.io")
        .split(",")
    )
    wix_public_base: str = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000")

settings = Settings()
os.makedirs(settings.exports_dir, exist_ok=True)
