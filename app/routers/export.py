from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
from app.models import get_session, Intake, ExportJob
from app.services.copywriter import generate_copy_pack
from app.services.export_docx import build_proposal_docx
from app.config import settings
import os

router = APIRouter()

class ExportBody(BaseModel):
    intake_id: int
    chosen_tier: str  # "High" | "Medium" | "Low"
    chosen_bias_key: str

@router.post("/docx")
def export_docx(body: ExportBody):
    with get_session() as s:
        intake = s.get(Intake, body.intake_id)
        if not intake or intake.mode != "deep_dive":
            raise HTTPException(status_code=404, detail="Deep Dive intake not found")

        # compose copy (LLM) and export docx
        copy_pack = generate_copy_pack(
            intake.answers, intake.stacks, intake.biases, chosen_bias_key=body.chosen_bias_key
        )
        file_name = build_proposal_docx(
            answers=intake.answers,
            stacks=intake.stacks,
            bias_plans=intake.biases,
            chosen_tier=body.chosen_tier,
            chosen_bias_key=body.chosen_bias_key,
            copy_pack=copy_pack,
        )
        file_path = os.path.join(settings.exports_dir, file_name)

        job = ExportJob(
            intake_id=intake.id,
            chosen_tier=body.chosen_tier,
            chosen_bias_key=body.chosen_bias_key,
            file_path=file_path,
        )
        s.add(job); s.commit(); s.refresh(job)

    # Public URL (Wix downloads this)
    download_url = f"{settings.wix_public_base}/static/exports/{file_name}"
    return {"downloadUrl": download_url, "file": file_name}
