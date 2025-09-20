from typing import Dict, Any
from app.config import settings
from app.services.kb_store import KBStore

COMPLIANCE_BLOCK = (
    "Compliance notes:\n"
    "- Schools/safety: reference only factual items (school names, distances, third-party links); no claims or ratings.\n"
    "- Post-production: limited to non-material item removals and sky/grass enhancement; no structural changes or misrepresentation.\n"
    "- Copy tone: neutral, descriptive, MLS-safe."
)

def generate_copy_pack(answers: Dict[str, Any], stacks: Dict[str, Any], biases: Dict[str, Any], chosen_bias_key: str) -> Dict[str, Any]:
    """
    Generates all Listing Lingo sections. Uses OpenAI if available; otherwise produces a concise deterministic pack.
    """
    from openai import OpenAI
    client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
    bias = KBStore.instance().bias_by_key.get(chosen_bias_key, {})
    prompt = {
        "task":"Create MLS-safe, bias-tuned copy for real-estate listing.",
        "answers":answers,
        "chosen_stack": next((s for s in stacks["stacks"] if s["tier"]==answers.get("chosen_tier","High")), stacks["stacks"][0]),
        "chosen_bias": bias,
        "guardrails": COMPLIANCE_BLOCK,
        "sections": [
            "I. Core Listing & Print",
            "II. Digital & Social",
            "III. Direct Outreach",
            "Phase I: Core Asset Creation (Pre-Launch)",
            "Phase II: Release & Distribution (Go-Live)",
            "Operational Checklists",
            "Week-1 cadence windows only (Morning 9–11a, Lunch 12–2p, Evening 5–8p)",
            "KPIs"
        ]
    }
    if client:
        resp = client.chat.completions.create(
            model=settings.model,
            response_format={"type":"json_object"},
            temperature=0.4,
            messages=[
                {"role":"system","content":"You are an expert real-estate copywriter. Respect all compliance notes. Output strictly JSON."},
                {"role":"user","content":str(prompt)}
            ]
        )
        import json
        return json.loads(resp.choices[0].message.content)
    # offline small pack
    return {
        "core_listing_print":{
            "mls_description":"Sunlit spaces, connected flow, and everyday ease. See floor plan + 3D for layout clarity.",
            "flyer_headline":"Light, Flow, Location",
            "flyer_short":"Open living to updated kitchen; restful bedrooms; private outdoor space.",
            "bulleted_specs":["3 bed / 2 bath","~1,650± sf","2D Plan + Zillow 3D link","Upgrades: newer roof, HVAC"]
        },
        "digital_social":{
            "just_listed":["Just Listed: tour the 3D + plan","See how the layout lives day to day"],
            "open_house":["Open Sat 12–2 — start with the 3D","Walkthrough video: hooks first, then flow"],
            "feature_highlights":["Functional kitchen triangle","Outdoor living zone","Primary privacy"],
            "under_contract_sold":["Under contract — floor plan clarity helped buyers choose fast"],
            "video_scripts":{"walkthrough":"60–120s beats: Hook → 5 features → CTA","reels":"15–45s: Hook; 3 shots; CTA"},
            "spw_copy":"Single-property site anchors all assets (photos, plan, 3D, video).",
            "ads":["Plan + 3D = fewer surprises","Save this for later","Book your showing"]
        },
        "direct_outreach":{
            "email_blast":"Tour the floor plan + 3D first, then book your time.",
            "inquiry_templates":{"sms":"Link to plan & 3D, then avail window","email":"Factual info + links; invite to open house"},
            "oh_followup":"Thanks for visiting — here are the plan, 3D, and video for review."
        },
        "phases":{
            "phase_i_prelaunch":["Home prep checklist","Hero thumbnail plan","Script beats & shot list"],
            "phase_ii_golive":["MLS go-live with plan/3D","Reels sequence M/L/E windows","Email + ad set A/B"]
        },
        "checklists":{
            "homeowner_prep":["Declutter surfaces","Bulb check & blinds","Curb tidy"],
            "run_of_show":["Front→main→private→outdoor","Plan capture before video"],
            "gallery_order":["Curb→living→kitchen→primary→outdoor"],
            "plan_3d":["Label rooms; note tight areas","2D plan placement in gallery"],
            "thumbnail_retouch":["Clean sky/grass","Remove small distractions only"]
        },
        "week1_cadence":[
            "Morning 9–11a: Just Listed post + ad set",
            "Lunch 12–2p: Quick Snap reel",
            "Evening 5–8p: Feature highlight"
        ],
        "kpis":["Saves/Views ratio","3D dwell time","Click-through to showing link"],
        "compliance": COMPLIANCE_BLOCK
    }
