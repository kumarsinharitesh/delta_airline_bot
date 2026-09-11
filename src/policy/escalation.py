from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from src.policy.rules import PolicyResult, PolicyAction

class EscalationDecision(str, Enum):
    AUTO_HANDLE = "AUTO_HANDLE"
    ESCALATE = "ESCALATE"

class EscalationResult(BaseModel):
    decision: EscalationDecision
    reason_codes: List[str]
    reason: str

def decide_escalation(
    policy_result: PolicyResult,
    intent_confidence: float,
    generation_valid: bool,
    validation_failures: List[str] = None
) -> EscalationResult:
    """
    Deterministically decides whether a customer request should be auto-handled or escalated.
    """
    reasons = []
    
    # 1. Policy triggers
    if policy_result.policy_action == PolicyAction.ESCALATE:
        reasons.append("POLICY_ESCALATE")
    
    # 2. Verification requirement
    if policy_result.policy_action == PolicyAction.REQUIRE_VERIFICATION:
        reasons.append("VERIFICATION_UNSUPPORTED")
        
    # 3. Confidence threshold
    if intent_confidence < 0.60:
        reasons.append("LOW_CONFIDENCE")
        
    # 4 & 5. Generation validity and post-generation validation
    if not generation_valid:
        reasons.append("GENERATION_INVALID")
        
    if validation_failures:
        for failure in validation_failures:
            reasons.append(f"VALIDATION_FAILED: {failure}")
            
    # Include underlying safety/policy reason codes
    for rc in policy_result.reason_codes:
        reasons.append(f"POLICY_{rc.value}")
        
    if reasons and (
        policy_result.policy_action != PolicyAction.ALLOW_SAFE_RESPONSE or 
        intent_confidence < 0.60 or 
        not generation_valid or 
        validation_failures
    ):
        return EscalationResult(
            decision=EscalationDecision.ESCALATE,
            reason_codes=reasons,
            reason="Escalated due to: " + ", ".join(reasons)
        )
        
    # All checks passed
    return EscalationResult(
        decision=EscalationDecision.AUTO_HANDLE,
        reason_codes=["SAFE_INFORMATIONAL_REQUEST"],
        reason="The request is informational, low risk, and the generated response passed validation."
    )
