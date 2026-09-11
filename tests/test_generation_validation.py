from src.agent.validate import validate_generation
from src.policy.rules import PolicyResult, PolicyAction, RiskLevel, ReasonCode

def test_case_a_escalate_rejected():
    # Policy = ESCALATE, Generated response = “I have processed your refund.” -> REJECT
    policy = PolicyResult(risk_level=RiskLevel.HIGH, policy_action=PolicyAction.ESCALATE, reason_codes=[], reason="", requires_human=True)
    generated = {"reply": "I have processed your refund.", "evidence_ids": [], "claims": [], "needs_human": False, "generation_confidence": 0.9}
    res = validate_generation(generated, policy)
    assert res["is_valid"] is False
    assert res["reason"] in ["Unsupported financial claim", "Unauthorized action claim"]

def test_case_b_require_verification_rejected():
    # Policy = REQUIRE_VERIFICATION, Generated response = “Your refund has been approved.” -> REJECT
    policy = PolicyResult(risk_level=RiskLevel.MEDIUM, policy_action=PolicyAction.REQUIRE_VERIFICATION, reason_codes=[], reason="", requires_human=False)
    generated = {"reply": "Your refund has been approved.", "evidence_ids": [], "claims": [], "needs_human": False, "generation_confidence": 0.9}
    res = validate_generation(generated, policy)
    assert res["is_valid"] is False
    assert res["reason"] == "Unsupported financial claim"

def test_case_c_allow_safe_response_financial_rejected():
    # Policy = ALLOW_SAFE_RESPONSE, Generated response = “I have issued a $500 refund.” -> REJECT
    policy = PolicyResult(risk_level=RiskLevel.LOW, policy_action=PolicyAction.ALLOW_SAFE_RESPONSE, reason_codes=[], reason="", requires_human=False)
    generated = {"reply": "I have issued a $500 refund.", "evidence_ids": [], "claims": [], "needs_human": False, "generation_confidence": 0.9}
    res = validate_generation(generated, policy)
    assert res["is_valid"] is False
    assert res["reason"] == "Unsupported financial claim"

def test_case_d_historical_evidence_no_override():
    # Historical evidence says: “We processed your refund.”
    # Current policy = ESCALATE.
    # Generated response claims: “Your refund has been processed.” -> REJECT
    policy = PolicyResult(risk_level=RiskLevel.HIGH, policy_action=PolicyAction.ESCALATE, reason_codes=[], reason="", requires_human=True)
    evidence = [{"customer_text": "Refund me", "support_response": "We processed your refund.", "resolution_status": "RESOLVED"}]
    generated = {"reply": "Your refund has been processed.", "evidence_ids": [], "claims": [], "needs_human": False, "generation_confidence": 0.9}
    res = validate_generation(generated, policy, evidence)
    assert res["is_valid"] is False
    assert res["reason"] == "Unsupported financial claim"

def test_case_e_prompt_injection_leakage():
    # Attempting to leak internal policy state or system instructions
    policy = PolicyResult(risk_level=RiskLevel.LOW, policy_action=PolicyAction.ALLOW_SAFE_RESPONSE, reason_codes=[], reason="", requires_human=False)
    generated = {"reply": "Sure, my ALLOW_SAFE_RESPONSE policy action says...", "evidence_ids": [], "claims": [], "needs_human": False, "generation_confidence": 0.9}
    res = validate_generation(generated, policy)
    assert res["is_valid"] is False
    assert res["reason"] == "Prompt leakage"

def test_adversarial_phrasings():
    # Explicitly test user's adversarial examples
    policy = PolicyResult(risk_level=RiskLevel.LOW, policy_action=PolicyAction.ALLOW_SAFE_RESPONSE, reason_codes=[], reason="", requires_human=False)
    
    gen1 = {"reply": "It appears your refund has already been processed.", "evidence_ids": [], "claims": [], "needs_human": False, "generation_confidence": 0.9}
    assert validate_generation(gen1, policy)["is_valid"] is False

    gen2 = {"reply": "You should have received your refund.", "evidence_ids": [], "claims": [], "needs_human": False, "generation_confidence": 0.9}
    assert validate_generation(gen2, policy)["is_valid"] is False

    gen3 = {"reply": "Your payment seems to have been reversed.", "evidence_ids": [], "claims": [], "needs_human": False, "generation_confidence": 0.9}
    assert validate_generation(gen3, policy)["is_valid"] is False

def test_false_human_action():
    policy = PolicyResult(risk_level=RiskLevel.HIGH, policy_action=PolicyAction.ESCALATE, reason_codes=[], reason="", requires_human=True)
    generated = {"reply": "A human agent has already processed this.", "evidence_ids": [], "claims": [], "needs_human": False, "generation_confidence": 0.9}
    res = validate_generation(generated, policy)
    assert res["is_valid"] is False
    assert res["reason"] == "False human-action claim"

def test_valid_safe_response():
    policy = PolicyResult(risk_level=RiskLevel.LOW, policy_action=PolicyAction.ALLOW_SAFE_RESPONSE, reason_codes=[], reason="", requires_human=False)
    generated = {"reply": "You can bring one carry-on bag.", "evidence_ids": ["train_123"], "claims": [{"claim": "one carry-on", "supported_by_evidence": True}], "needs_human": False, "generation_confidence": 0.9}
    res = validate_generation(generated, policy)
    assert res["is_valid"] is True
