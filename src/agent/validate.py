import re
from typing import List, Dict, Any
from src.policy.rules import PolicyAction, PolicyResult

def validate_generation(generated_json: Dict[str, Any], policy_result: PolicyResult, retrieved_evidence: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Validates the generated response against deterministic policy constraints.
    Returns {"is_valid": True/False, "fallback_reply": str, "reason": str}
    """
    if not isinstance(generated_json, dict) or "reply" not in generated_json:
        return {"is_valid": False, "fallback_reply": get_safe_fallback(policy_result.policy_action), "reason": "Malformed output"}

    reply = generated_json["reply"]
    if not reply or not isinstance(reply, str):
        return {"is_valid": False, "fallback_reply": get_safe_fallback(policy_result.policy_action), "reason": "Empty or non-string reply"}

    # A. Unsupported financial claims
    # E.g. "Your refund has been processed", "We refunded $200", "Payment reversed"
    financial_claim_patterns = [
        r"(?i)refund (has been|was|is) (processed|issued|approved)",
        r"(?i)we (have )?refunded",
        r"(?i)payment (has been|was|is) reversed",
        r"(?i)compensation (has been|was|is) approved",
        r"(?i)issued a (.*) refund",
        r"(?i)refunded \$",
        r"(?i)refund has already been processed",
        r"(?i)should have received your refund",
        r"(?i)payment seems to have been reversed",
    ]
    
    # We do NOT allow these claims at all right now because deterministic evidence does not explicitly contain "Current customer X was refunded".
    # Even if historical evidence says it, it's rejected for the current user.
    for pattern in financial_claim_patterns:
        if re.search(pattern, reply):
            return {"is_valid": False, "fallback_reply": get_safe_fallback(policy_result.policy_action), "reason": "Unsupported financial claim"}

    # B. Unauthorized actions based on policy
    # If policy is ESCALATE or REQUIRE_VERIFICATION, we strictly forbid "processed", "approved", "issued"
    unauthorized_action_patterns = [
        r"(?i)i have processed",
        r"(?i)has been approved",
        r"(?i)i have issued",
        r"(?i)i have completed",
    ]
    if policy_result.policy_action in [PolicyAction.ESCALATE, PolicyAction.REQUIRE_VERIFICATION]:
        for pattern in unauthorized_action_patterns:
            if re.search(pattern, reply):
                return {"is_valid": False, "fallback_reply": get_safe_fallback(policy_result.policy_action), "reason": "Unauthorized action claim"}

    # C. Prompt leakage
    leakage_patterns = [
        r"(?i)system prompt",
        r"(?i)developer instructions",
        r"(?i)ALLOW_SAFE_RESPONSE",
        r"(?i)REQUIRE_VERIFICATION",
        r"(?i)policy action is",
        r"(?i)risk level is",
        r"(?i)reason code",
    ]
    for pattern in leakage_patterns:
        if re.search(pattern, reply):
            return {"is_valid": False, "fallback_reply": get_safe_fallback(policy_result.policy_action), "reason": "Prompt leakage"}

    # D. False human-action claims
    false_human_patterns = [
        r"(?i)a human agent has already processed",
        r"(?i)our support team has completed",
        r"(?i)agent has already",
    ]
    for pattern in false_human_patterns:
        if re.search(pattern, reply):
            return {"is_valid": False, "fallback_reply": get_safe_fallback(policy_result.policy_action), "reason": "False human-action claim"}

    return {"is_valid": True, "fallback_reply": "", "reason": ""}

def get_safe_fallback(policy_action: PolicyAction) -> str:
    if policy_action == PolicyAction.ESCALATE:
        return "I apologize, but this issue requires a human specialist. I will escalate your case to our support team for further assistance."
    elif policy_action == PolicyAction.REQUIRE_VERIFICATION:
        return "I need a bit more information to assist you securely. Please provide your booking reference or necessary verification details."
    else:
        return "I'm sorry, but I'm unable to provide a reliable answer to that right now. Please contact Delta support for assistance."
