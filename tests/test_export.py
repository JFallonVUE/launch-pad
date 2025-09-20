from app.services.export_docx import build_proposal_docx

def test_export_smoke(tmp_path, monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "exports_dir", str(tmp_path))
    answers = {"chosen_tier":"High"}
    stacks = {"stacks":[
        {"tier":"High","services":[{"service_id":"VLX","name":"VUE LUXE","rationale":"Complexity coverage"}],"rationale":"Premium coverage"},
        {"tier":"Medium","services":[{"service_id":"VPP","name":"VUE PRIME+","rationale":"Luxe finish"}],"rationale":"Strong middle"},
        {"tier":"Low","services":[{"service_id":"P25","name":"PHOTO 25","rationale":"Lean"}],"rationale":"Budget-aware"}
    ]}
    bias_plans = {"biasPlans":[{"key":"fluency","definition":"...","why":"...","executionBullets":["..."]}]}
    copy_pack = {
        "core_listing_print":{"mls_description":"...","flyer_headline":"...","flyer_short":"...","bulleted_specs":["A","B"]},
        "digital_social":{"just_listed":["A"],"open_house":["B"],"feature_highlights":["C"],"under_contract_sold":["D"],"video_scripts":{"walkthrough":"...", "reels":"..."}, "ads":["E"]},
        "direct_outreach":{"email_blast":"...","inquiry_templates":{"sms":"...","email":"..."},"oh_followup":"..."},
        "phases":{"phase_i_prelaunch":["X"],"phase_ii_golive":["Y"]},
        "checklists":{"homeowner_prep":["x"],"run_of_show":["y"]},
        "week1_cadence":["Morning 9–11a: ..."],
        "kpis":["Saves/Views"],
        "compliance":"..."
    }
    fn = build_proposal_docx(answers, stacks, bias_plans, "High", "fluency", copy_pack)
    p = tmp_path / fn
    assert p.exists()
