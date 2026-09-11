import pytest
from src.policy.rules import PolicyResult, PolicyAction, ReasonCode, RiskLevel
from src.policy.escalation import decide_escalation, EscalationDecision

def test_policy_escalate():
    pr = PolicyResult(risk_level=RiskLevel.HIGH, policy_action=PolicyAction.ESCALATE, reason_codes=[ReasonCode.PAYMENT_DISPUTE], reason="Dispute", requires_human=True)
    res = decide_escalation(pr, intent_confidence=0.9, generation_valid=True)
    assert res.decision == EscalationDecision.ESCALATE
    assert "POLICY_ESCALATE" in res.reason_codes

def test_require_verification_escalate():
    pr = PolicyResult(risk_level=RiskLevel.MEDIUM, policy_action=PolicyAction.REQUIRE_VERIFICATION, reason_codes=[ReasonCode.ACCOUNT_SENSITIVE_CHANGE], reason="Account", requires_human=True)
    res = decide_escalation(pr, intent_confidence=0.9, generation_valid=True)
    assert res.decision == EscalationDecision.ESCALATE
    assert "VERIFICATION_UNSUPPORTED" in res.reason_codes

def test_low_confidence_escalate():
    pr = PolicyResult(risk_level=RiskLevel.LOW, policy_action=PolicyAction.ALLOW_SAFE_RESPONSE, reason_codes=[], reason="Safe", requires_human=False)
    res = decide_escalation(pr, intent_confidence=0.59, generation_valid=True)
    assert res.decision == EscalationDecision.ESCALATE
    assert "LOW_CONFIDENCE" in res.reason_codes

def test_exact_confidence_auto_handle():
    pr = PolicyResult(risk_level=RiskLevel.LOW, policy_action=PolicyAction.ALLOW_SAFE_RESPONSE, reason_codes=[], reason="Safe", requires_human=False)
    res = decide_escalation(pr, intent_confidence=0.60, generation_valid=True)
    assert res.decision == EscalationDecision.AUTO_HANDLE

def test_invalid_generation_escalate():
    pr = PolicyResult(risk_level=RiskLevel.LOW, policy_action=PolicyAction.ALLOW_SAFE_RESPONSE, reason_codes=[], reason="Safe", requires_human=False)
    res = decide_escalation(pr, intent_confidence=0.90, generation_valid=False)
    assert res.decision == EscalationDecision.ESCALATE
    assert "GENERATION_INVALID" in res.reason_codes

def test_validation_failure_escalate():
    pr = PolicyResult(risk_level=RiskLevel.LOW, policy_action=PolicyAction.ALLOW_SAFE_RESPONSE, reason_codes=[], reason="Safe", requires_human=False)
    res = decide_escalation(pr, intent_confidence=0.90, generation_valid=True, validation_failures=["Unsupported financial claim"])
    assert res.decision == EscalationDecision.ESCALATE
    assert "VALIDATION_FAILED: Unsupported financial claim" in res.reason_codes

def test_safe_valid_high_confidence_auto_handle():
    pr = PolicyResult(risk_level=RiskLevel.LOW, policy_action=PolicyAction.ALLOW_SAFE_RESPONSE, reason_codes=[], reason="Safe", requires_human=False)
    res = decide_escalation(pr, intent_confidence=0.90, generation_valid=True)
    assert res.decision == EscalationDecision.AUTO_HANDLE

def test_prompt_injection_escalate():
    pr = PolicyResult(risk_level=RiskLevel.HIGH, policy_action=PolicyAction.ESCALATE, reason_codes=[ReasonCode.PROMPT_INJECTION], reason="Injection", requires_human=True)
    res = decide_escalation(pr, intent_confidence=0.99, generation_valid=True)
    assert res.decision == EscalationDecision.ESCALATE
    assert "POLICY_PROMPT_INJECTION" in res.reason_codes
