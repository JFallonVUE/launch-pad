from fastapi import APIRouter
import json, os

router = APIRouter()

def _load(name: str):
    with open(os.path.join("schemas", name), "r") as f:
        return json.load(f)

@router.get("/schemas")
def get_schemas():
    return {
        "lighting": _load("lighting.json"),
        "deep_dive": _load("deep_dive.json"),
        "stacks": _load("stacks.json"),
        "bias_plan": _load("bias_plan.json"),
        "export_request": _load("export_request.json")
    }
