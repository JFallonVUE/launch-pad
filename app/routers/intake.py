from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List
from app.services.signals import compute_signals
from app.services.llm_decider import decide_stacks_and_biases
from app.models import Intake, get_session

router = APIRouter()

class LightingPayload(BaseModel):
    answers: Dict[str, Any] = Field(..., description="15 answers as per schemas/lighting.json")

class DeepDivePayload(BaseModel):
    answers: Dict[str, Any] = Field(..., description="40–50 answers as per schemas/deep_dive.json")

@router.post("/lighting")
def intake_lighting(payload: LightingPayload):
    answers = payload.answers
    sig = compute_signals(answers)
    stacks, biases = decide_stacks_and_biases(answers, sig, mode="lighting")
    with get_session() as s:
        rec = Intake(mode="lighting", answers=answers, stacks=stacks, biases=biases)
        s.add(rec)
        s.commit()
        s.refresh(rec)
    return {
        "intake_id": rec.id,   # you can ignore for lighting on the Wix side
        "stacks": stacks["stacks"],
        "biases": biases["biasPlans"]
    }

@router.post("/deep-dive")
def intake_deep_dive(payload: DeepDivePayload):
    answers = payload.answers
    sig = compute_signals(answers)
    stacks, biases = decide_stacks_and_biases(answers, sig, mode="deep_dive")
    with get_session() as s:
        rec = Intake(mode="deep_dive", answers=answers, stacks=stacks, biases=biases)
        s.add(rec)
        s.commit()
        s.refresh(rec)
    return {
        "intake_id": rec.id,
        "stacks": stacks["stacks"],
        "biases": biases["biasPlans"]
    }
