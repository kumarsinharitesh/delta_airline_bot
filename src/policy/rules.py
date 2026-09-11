import re
from enum import Enum
from pydantic import BaseModel, Field
from typing import List

from src.safety.prompt_injection import detect_prompt_injection, detect_human_request
from src.safety.risk import assess_risk, RiskLevel

class PolicyAction(str, Enum):
    ALLOW_SAFE_RESPONSE = "ALLOW_SAFE_RESPONSE"
    REQUIRE_VERIFICATION = "REQUIRE_VERIFICATION"
    ESCALATE = "ESCALATE"

class ReasonCode(str, Enum):
    PROMPT_INJECTION = "PROMPT_INJECTION"
    EXPLICIT_HUMAN_REQUEST = "EXPLICIT_HUMAN_REQUEST"
    FINANCIAL_ACTION = "FINANCIAL_ACTION"
    PAYMENT_DISPUTE = "PAYMENT_DISPUTE"
    REFUND_AUTHORIZATION = "REFUND_AUTHORIZATION"
    COMPENSATION_REQUEST = "COMPENSATION_REQUEST"
    FRAUD_OR_SECURITY = "FRAUD_OR_SECURITY"
    ACCOUNT_SENSITIVE_CHANGE = "ACCOUNT_SENSITIVE_CHANGE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    REPEATED_UNRESOLVED = "REPEATED_UNRESOLVED"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    SAFE_INFORMATIONAL_REQUEST = "SAFE_INFORMATIONAL_REQUEST"
    SYSTEM_ERROR = "SYSTEM_ERROR"

class PolicyResult(BaseModel):
    risk_level: RiskLevel
    policy_action: PolicyAction
    reason_codes: List[ReasonCode]
    reason: str
    requires_human: bool

def evaluate_policy(
    message: str,
    intent: str,
    confidence: float,
    retrieved_evidence: list = None,
    conversation_context: list = None
) -> PolicyResult:
    """
    Deterministic policy evaluator. Returns a validated PolicyResult.
    """
    try:
        # Check explicit overrides
        if detect_prompt_injection(message):
            return PolicyResult(
                risk_level=RiskLevel.HIGH,
                policy_action=PolicyAction.ESCALATE,
                reason_codes=[ReasonCode.PROMPT_INJECTION],
                reason="Prompt injection or trust boundary violation detected.",
                requires_human=True
            )
            
        if detect_human_request(message):
            return PolicyResult(
                risk_level=RiskLevel.HIGH,
                policy_action=PolicyAction.ESCALATE,
                reason_codes=[ReasonCode.EXPLICIT_HUMAN_REQUEST],
                reason="Customer explicitly requested a human agent.",
                requires_human=True
            )

        fraud_patterns = [r"(?i)fraud", r"(?i)hacked", r"(?i)stolen", r"(?i)unauthorized charge"]
        if any(re.search(p, message) for p in fraud_patterns):
            return PolicyResult(
                risk_level=RiskLevel.HIGH,
                policy_action=PolicyAction.ESCALATE,
                reason_codes=[ReasonCode.FRAUD_OR_SECURITY],
                reason="Fraud or security concern detected.",
                requires_human=True
            )

        # Base risk assessment
        risk = assess_risk(message, intent, confidence)
        
        reasons = []
        action = PolicyAction.ALLOW_SAFE_RESPONSE
        requires_human = False

        if confidence < 0.6:
            reasons.append(ReasonCode.LOW_CONFIDENCE)
            action = PolicyAction.REQUIRE_VERIFICATION
            
        repeated_patterns = [r"(?i)called multiple times", r"(?i)still hasn't been fixed"]
        if any(re.search(p, message) for p in repeated_patterns):
            reasons.append(ReasonCode.REPEATED_UNRESOLVED)
            action = max(action, PolicyAction.REQUIRE_VERIFICATION) # escalated if needed

        if intent == "ACCOUNT_ACCESS":
            reasons.append(ReasonCode.ACCOUNT_SENSITIVE_CHANGE)
            action = PolicyAction.REQUIRE_VERIFICATION
            requires_human = True
            
        elif intent in ["CANCEL_OR_CHANGE_FLIGHT", "SKYMILES_OR_LOYALTY"]:
            reasons.append(ReasonCode.ACCOUNT_SENSITIVE_CHANGE)
            action = max(action, PolicyAction.REQUIRE_VERIFICATION)
            requires_human = True
            
        elif intent == "PAYMENT_OR_CHARGE_DISPUTE":
            reasons.append(ReasonCode.PAYMENT_DISPUTE)
            action = PolicyAction.ESCALATE
            requires_human = True
            
        elif intent == "REFUND_OR_COMPENSATION":
            if risk == RiskLevel.HIGH:
                reasons.append(ReasonCode.REFUND_AUTHORIZATION)
                action = PolicyAction.ESCALATE
                requires_human = True
            else:
                reasons.append(ReasonCode.SAFE_INFORMATIONAL_REQUEST)
                # It's an informational refund request (e.g., "when will it arrive")
                # Wait, if there's retrieved evidence, maybe they can answer it safely? Yes.
                action = PolicyAction.ALLOW_SAFE_RESPONSE
                
        if action == PolicyAction.ALLOW_SAFE_RESPONSE and not reasons:
            reasons.append(ReasonCode.SAFE_INFORMATIONAL_REQUEST)
            
        # If action is ALLOW_SAFE_RESPONSE but the evidence is completely empty or irrelevant, 
        # we might require verification. But in this implementation, we rely on the intent mapping.
        if action == PolicyAction.ALLOW_SAFE_RESPONSE and retrieved_evidence is None:
             # Just an example of handling evidence, though retrieval might be empty.
             pass

        return PolicyResult(
            risk_level=risk,
            policy_action=action,
            reason_codes=reasons,
            reason="Deterministic policy evaluation completed.",
            requires_human=requires_human
        )

    except Exception as e:
        # Fail safe
        return PolicyResult(
            risk_level=RiskLevel.HIGH,
            policy_action=PolicyAction.ESCALATE,
            reason_codes=[ReasonCode.SYSTEM_ERROR],
            reason=f"Policy evaluation failed safely: {str(e)}",
            requires_human=True
        )
