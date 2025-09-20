from typing import Dict, Any

def compute_signals(answers: Dict[str, Any]) -> Dict[str, float]:
    """
    Compute lightweight numeric signals for the LLM to reason with:
    - complexity (size/features)
    - clarityNeed (layout quirks, tight rooms)
    - momentumPressure (timeline urgency)
    - brandLift (agent on-cam comfort + need to pitch premium)
    - locationEfficiency (walkability/commute anchors and remote buyers)
    """
    beds = int(answers.get("beds", 0) or 0)
    baths = float(answers.get("baths", 0) or 0)
    sqft = int(answers.get("interior_size_sqft", 0) or 0)
    tight = 1 if str(answers.get("tight_small_rooms","no")).lower() in ("yes","true","y") else 0
    quirky = 1 if str(answers.get("odd_quirky_flow","no")).lower() in ("yes","true","y") else 0
    vacant = 1 if str(answers.get("occupancy","occupied")).lower()=="vacant" else 0
    remote_buyers = 1 if "remote" in str(answers.get("likely_buyer_profile","")).lower() else 0
    oncam = 1 if str(answers.get("agent_on_camera_comfort","low")).lower() in ("medium","high") else 0

    timeline = str(answers.get("timeline_pressure","normal")).lower()
    pressure = {"urgent":1.0,"fast":0.8,"normal":0.5,"flexible":0.3}.get(timeline,0.5)

    complexity = min(1.0, (beds + baths*0.7 + (sqft/1500.0)))
    clarity_need = min(1.0, 0.5*tight + 0.6*quirky + 0.5*remote_buyers)
    momentum = pressure
    brand_lift = 0.6*oncam + 0.4*max(0.0, (sqft-2000)/2000.0)
    location_eff = 0.6*remote_buyers + 0.4*(1 if answers.get("location_perk") else 0)

    return dict(
        complexity=float(round(complexity,3)),
        clarityNeed=float(round(clarity_need,3)),
        momentumPressure=float(round(momentum,3)),
        brandLift=float(round(brand_lift,3)),
        locationEfficiency=float(round(location_eff,3)),
        vacant=float(vacant)
    )
