import json
from unittest.mock import patch
from src.agent.generate import generate_response
from src.policy.rules import PolicyResult, PolicyAction, RiskLevel

@patch("src.agent.generate.requests.post")
def test_generate_response_success(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "reply": "You can bring one carry-on bag.",
                    "evidence_ids": ["train_123"],
                    "claims": [{"claim": "one carry-on", "supported_by_evidence": True}],
                    "needs_human": False,
                    "generation_confidence": 0.9
                })
            }
        }]
    }

    policy = PolicyResult(risk_level=RiskLevel.LOW, policy_action=PolicyAction.ALLOW_SAFE_RESPONSE, reason_codes=[], reason="", requires_human=False)
    res = generate_response("How many bags?", "none", "BAGGAGE_ISSUE", 0.9, policy, [])
    
    assert res["is_fallback"] is False
    assert res["reply"] == "You can bring one carry-on bag."

@patch("src.agent.generate.requests.post")
def test_generate_response_invalid_schema(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "reply": "You can bring one carry-on bag.",
                    # Missing required fields
                })
            }
        }]
    }

    policy = PolicyResult(risk_level=RiskLevel.LOW, policy_action=PolicyAction.ALLOW_SAFE_RESPONSE, reason_codes=[], reason="", requires_human=False)
    res = generate_response("How many bags?", "none", "BAGGAGE_ISSUE", 0.9, policy, [])
    
    assert res["is_fallback"] is True
    assert "Schema parsing error" in res["fallback_reason"]

@patch("src.agent.generate.requests.post")
def test_generate_response_api_error(mock_post):
    mock_post.return_value.raise_for_status.side_effect = Exception("API timeout")
    
    policy = PolicyResult(risk_level=RiskLevel.HIGH, policy_action=PolicyAction.ESCALATE, reason_codes=[], reason="", requires_human=True)
    res = generate_response("Help me", "none", "BAGGAGE_ISSUE", 0.9, policy, [])
    
    assert res["is_fallback"] is True
    assert "Schema parsing error" in res["fallback_reason"]
    assert "escalate" in res["reply"].lower()
