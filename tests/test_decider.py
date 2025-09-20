import json, os
from app.services.signals import compute_signals
from app.services.llm_decider import decide_stacks_and_biases

def _assert_stack(bundles):
    tiers = [s["tier"] for s in bundles["stacks"]]
    assert set(tiers)=={"High","Medium","Low"}
    for s in bundles["stacks"]:
        assert len(s["services"])>=1
        for it in s["services"]:
            assert "service_id" in it

def test_fixture_vacant_dated_sfr():
    answers = json.load(open("examples/fixture_vacant_dated_sfr.json"))
    sig = compute_signals(answers)
    stacks, biases = decide_stacks_and_biases(answers, sig, mode="deep_dive")
    _assert_stack(stacks)
    keys = [b["key"] for b in biases["biasPlans"]]
    assert any(k in keys for k in ("mere-exposure","loss-aversion"))

def test_fixture_large_view_home():
    answers = json.load(open("examples/fixture_large_view_home.json"))
    sig = compute_signals(answers)
    stacks, biases = decide_stacks_and_biases(answers, sig, mode="deep_dive")
    _assert_stack(stacks)
    keys = [b["key"] for b in biases["biasPlans"]]
    assert any(k in keys for k in ("anchoring","novelty","authority"))

def test_fixture_tight_room_condo():
    answers = json.load(open("examples/fixture_tight_room_condo.json"))
    sig = compute_signals(answers)
    stacks, biases = decide_stacks_and_biases(answers, sig, mode="deep_dive")
    _assert_stack(stacks)
    svc_ids = [s["service_id"] for s in stacks["stacks"][2]["services"]]  # Low usually contains plan
    assert "F2D" in svc_ids or any(s["service_id"]=="Z3D" for s in stacks["stacks"][0]["services"])
