from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, create_engine, Session
from app.config import settings

class Intake(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    mode: str  # "lighting" or "deep_dive"
    answers: Dict[str, Any]
    stacks: Dict[str, Any]
    biases: Dict[str, Any]

class ExportJob(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    intake_id: int
    chosen_tier: str
    chosen_bias_key: str
    file_path: str

_engine = create_engine(settings.db_url, echo=False)

def init_db():
    SQLModel.metadata.create_all(_engine)

def get_session():
    return Session(_engine)
