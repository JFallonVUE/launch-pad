from typing import Dict, Any, Tuple
from app.services.kb_store import KBStore
from app.config import settings

def _deterministic_rules(answers: Dict[str, Any]) -> Dict[str, Any]:
    """
    Hard guardrails (illegal combos or must-haves).
    Returns an advisory dict the LLM must honor; enforced again after LLM output.
    """
    rules = {"must_include": set(), "forbid": set()}
    vacant = str(answers.get("occupancy","occupied")).lower()=="vacant"
    tight = str(answers.get("tight_small_rooms","no")).lower() in ("yes","true","y")
    remote = "remote" in str(answers.get("likely_buyer_profile","")).lower()
    busy_street = "busy" in str(answers.get("signature_feature","")).lower() and "exterior" in str(answers.get("signature_feature","")).lower()

    if vacant:
        rules["must_include"].add("VS1")  # at least some virtual staging; validator will flex to VS3/VS4/VSP
    if tight or remote:
        rules["must_include"].add("F2D")  # 2D Floor Plan
    if remote:
        rules["must_include"].add("Z3D")  # Zillow 3D for platform-native lift
    if busy_street:
        rules["must_include"].add("EXO")  # Exterior Only special use

    # Compliance constraints: post-production limits
    # (We simply document; export/copywriter also carry strict instructions)
    return rules

def _enforce_validator(stacks: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
    must = rules.get("must_include", set())
    forbid = rules.get("forbid", set())
    def fix_stack(stack):
        svcs = {s["service_id"] for s in stack["services"]}
        # add missing must-haves from KB (pick cheapest variants where logical)
        kb = KBStore.instance()
        sid_map = kb.service_by_id
        for req in must:
            if req not in svcs and req in sid_map:
                stack["services"].append({"service_id": req, "name": sid_map[req]["name"]})
        # strip forbidden
        stack["services"] = [s for s in stack["services"] if s["service_id"] not in forbid]
        return stack
    stacks["stacks"] = [fix_stack(s) for s in stacks["stacks"]]
    return stacks

def decide_stacks_and_biases(answers: Dict[str, Any], signals: Dict[str, float], mode: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Uses RAG (+ deterministic guardrails) + OpenAI JSON-mode to return:
    stacks: High/Medium/Low bundles with rationale
    biasPlans: 3 plans with key/definition/why/execution bullets
    """
    kb = KBStore.instance()
    # Retrieve context
    q = " ".join(f"{k}:{v}" for k,v in {**answers, **signals}.items())
    hits = kb.search(q, k=8)

    # Build system + user prompt
    sys = (
        "You are a marketing decision engine for real-estate listings. "
        "Select 3 stacks (High/Medium/Low) of VUE services using service_ids that exist in the catalog. "
        "Also select top 3 behavioral bias plans from the bias library.\n"
        "Constraints:\n"
        "- Two modes only: Lighting (15 Q) → JSON results only; Deep Dive (40–50 Q) → same + supports export.\n"
        "- No budget questions; always propose three stacks (H/M/L).\n"
        "- Compliance: Schools/safety language strictly factual (names, distances, links). "
        "Post-production limited to non-material item removals and sky/grass. Keep copy neutral.\n"
        "- Favor layout clarity (2D plans, 3D tours) when tight rooms/quirky flow/remote buyers.\n"
        "- Vacant → virtual staging allowed; occupied → do NOT include virtual staging unless explicitly permitted.\n"
        "Return strictly the JSON schema shown next."
    )

    # Collate grounding snippets
    svc_ctx = []
    bias_ctx = []
    for h in hits:
        if h["type"]=="service":
            s = h["item"]
            svc_ctx.append(f"[{s['service_id']}] {s['name']} — {s.get('description','')}")
        else:
            b = h["item"]
            bias_ctx.append(f"[{b['key']}] {b['name']}: {b['definition']}")

    user = {
        "mode": mode,
        "answers": answers,
        "signals": signals,
        "grounding": {
            "services": svc_ctx[:6],
            "biases": bias_ctx[:6]
        },
        "return_schema_example": {
            "stacks":[
                {"tier":"High","services":[{"service_id":"VLX"},{"service_id":"MPT"}],"rationale":"..."},
                {"tier":"Medium","services":[{"service_id":"VPP"},{"service_id":"Z3D"}],"rationale":"..."},
                {"tier":"Low","services":[{"service_id":"P25"},{"service_id":"F2D"}],"rationale":"..."}
            ],
            "biasPlans":[
                {"key":"fluency","definition":"...","why":"...","executionBullets":["...","..."]},
                {"key":"anchoring","definition":"...","why":"...","executionBullets":["...","..."]},
                {"key":"mere-exposure","definition":"...","why":"...","executionBullets":["...","..."]}
            ]
        }
    }

    # Call OpenAI for structured output
    from openai import OpenAI
    client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
    if client:
        resp = client.chat.completions.create(
            model=settings.model,
            response_format={"type":"json_object"},
            temperature=0.2,
            messages=[
                {"role":"system","content":sys},
                {"role":"user","content":str(user)}
            ]
        )
        raw = resp.choices[0].message.content
        import json
        result = json.loads(raw)
    else:
        # Offline fallback for dev/unit tests without API key
        result = user["return_schema_example"]

    # Deterministic guardrails & validator
    rules = _deterministic_rules(answers)
    stacks = _enforce_validator({"stacks": result["stacks"]}, rules)

    # Bias: keep top 3 unique keys that exist in KB
    bias_map = KBStore.instance().bias_by_key
    bias_plans = []
    for bp in result["biasPlans"]:
        key = bp.get("key","").lower()
        if key in bias_map and key not in [b["key"] for b in bias_plans]:
            bias_plans.append({
                "key": key,
                "definition": bias_map[key]["definition"],
                "why": bp.get("why","Selected to fit goals & audience."),
                "executionBullets": bp.get("executionBullets", [])[:3]
            })
        if len(bias_plans)==3: break
    if not bias_plans:
        # sensible defaults
        for key in ["mere-exposure","anchoring","fluency"]:
            if key in bias_map:
                bias_plans.append({"key":key,"definition":bias_map[key]["definition"],"why":"Default","executionBullets":["Post in morning window","Retarget with reels","MLS+Zillow 3D"]})
            if len(bias_plans)==3: break

    return stacks, {"biasPlans": bias_plans}
