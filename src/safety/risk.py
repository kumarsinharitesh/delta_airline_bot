import re
from enum import Enum
from src.safety.prompt_injection import detect_prompt_injection, detect_human_request

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

def assess_risk(message: str, intent: str, confidence: float) -> RiskLevel:
    """
    Deterministically assess the risk level of the interaction based on the intent and message contents.
    """
    
    if detect_prompt_injection(message):
        return RiskLevel.HIGH
        
    if detect_human_request(message):
        return RiskLevel.HIGH
        
    if confidence < 0.6:
        # Low confidence implies we shouldn't fully trust the automated resolution without verification
        return RiskLevel.MEDIUM

    # Intents that are inherently high-risk because they involve financial or secure actions
    if intent in ["ACCOUNT_ACCESS", "PAYMENT_OR_CHARGE_DISPUTE"]:
        return RiskLevel.HIGH
        
    if intent == "REFUND_OR_COMPENSATION":
        # Check if it's just asking about refund status vs demanding an actual refund
        # Informational request: "when will my refund arrive?"
        # Action request: "refund me now"
        informational_patterns = [
            r"(?i)where is my refund",
            r"(?i)when will.*refund",
            r"(?i)refund status",
            r"(?i)how long.*refund",
        ]
        is_informational = any(re.search(p, message) for p in informational_patterns)
        if is_informational:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.HIGH

    if intent == "CANCEL_OR_CHANGE_FLIGHT":
        return RiskLevel.MEDIUM

    # Security/Fraud triggers across any intent
    fraud_patterns = [
        r"(?i)fraud",
        r"(?i)hacked",
        r"(?i)stolen",
        r"(?i)unauthorized charge"
    ]
    if any(re.search(p, message) for p in fraud_patterns):
        return RiskLevel.HIGH
        
    # Unresolved or repeated issues
    repeated_patterns = [
        r"(?i)called multiple times",
        r"(?i)still hasn't been fixed",
        r"(?i)tried to resolve this",
        r"(?i)waiting for days",
    ]
    if any(re.search(p, message) for p in repeated_patterns):
        return RiskLevel.MEDIUM

    return RiskLevel.LOW
