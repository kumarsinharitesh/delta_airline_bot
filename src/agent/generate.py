import os
import json
import requests
import logging
from pathlib import Path

env_file = Path(".env")
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip()

from pydantic import BaseModel, ValidationError
from typing import List, Dict, Any, Optional
from src.policy.rules import PolicyResult, PolicyAction
from src.agent.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from src.agent.validate import validate_generation, get_safe_fallback

log = logging.getLogger(__name__)

class Claim(BaseModel):
    claim: str
    supported_by_evidence: bool

class ResponseOutput(BaseModel):
    reply: str
    evidence_ids: List[str]
    claims: List[Claim]
    needs_human: bool
    generation_confidence: float

def generate_response(
    customer_message: str,
    conversation_context: str,
    intent: str,
    confidence: float,
    policy_result: PolicyResult,
    retrieved_evidence: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Orchestrates grounded response generation using Sarvam-105b via REST API.
    Enforces deterministic safety via post-generation validation.
    """
    # 1. Orchestrate Retrieval Exposure
    formatted_evidence = "None"
    if retrieved_evidence:
        # User requested: "For ESCALATE: use minimal/no historical evidence unless specifically useful..."
        if policy_result.policy_action == PolicyAction.ESCALATE:
            formatted_evidence = "No historical evidence available for this escalated issue."
        else:
            evidence_blocks = []
            for ev in retrieved_evidence:
                ev_id = ev.get("example_id", "unknown")
                c_text = ev.get("customer_text", "")
                s_text = ev.get("support_response", "")
                r_status = ev.get("resolution_status", "")
                
                block = f"[HISTORICAL_SUPPORT_RESPONSE]\nEvidence ID: {ev_id}\nCustomer: {c_text}\nSupport: {s_text}\nResolution status: {r_status}\n[/HISTORICAL_SUPPORT_RESPONSE]"
                evidence_blocks.append(block)
            formatted_evidence = "\n\n".join(evidence_blocks)

    # 2. Build Prompts
    user_prompt = USER_PROMPT_TEMPLATE.format(
        customer_message=customer_message,
        conversation_context=conversation_context,
        intent=intent,
        confidence=confidence,
        policy_action=policy_result.policy_action.value,
        retrieved_evidence=formatted_evidence
    )

    # 3. Request LLM Execution
    api_key = os.environ.get("SARVAM_API_KEY")
    headers = {
        "api-subscription-key": api_key,
        "Content-Type": "application/json"
    }
    
    schema_instructions = {
        "type": "object",
        "properties": {
            "reply": {"type": "string"},
            "evidence_ids": {"type": "array", "items": {"type": "string"}},
            "claims": {"type": "array", "items": {"type": "object", "properties": {"claim": {"type": "string"}, "supported_by_evidence": {"type": "boolean"}}}},
            "needs_human": {"type": "boolean"},
            "generation_confidence": {"type": "number"}
        },
        "required": ["reply", "evidence_ids", "claims", "needs_human", "generation_confidence"]
    }

    # Add strict schema request to system prompt
    final_system_prompt = SYSTEM_PROMPT + f"\n\nJSON SCHEMA:\n{json.dumps(schema_instructions, indent=2)}\nONLY output valid JSON matching this schema."

    payload = {
        "model": "sarvam-105b",
        "messages": [
            {"role": "system", "content": final_system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.0,
        "max_tokens": 4000,
        "reasoning_effort": None,
        "response_format": {"type": "json_object"}
    }

    raw_response_text = ""
    try:
        resp = requests.post("https://api.sarvam.ai/v1/chat/completions", headers=headers, json=payload, timeout=60)
        data = resp.json()
        if resp.status_code != 200:
            log.error(f"API Error: {data}")
            raise Exception(f"API Error {resp.status_code}")
            
        raw_response_text = data["choices"][0]["message"].get("content", "") or ""
        
        if not raw_response_text:
            log.warning(f"Empty content returned. Full response: {json.dumps(data)}")
        
        # Clean markdown code blocks if present
        if raw_response_text.startswith("```json"):
            raw_response_text = raw_response_text[7:-3].strip()
        elif raw_response_text.startswith("```"):
            raw_response_text = raw_response_text[3:-3].strip()

        # Parse JSON
        generated_json = json.loads(raw_response_text)
        
        # Validate Pydantic schema
        ResponseOutput(**generated_json)

    except Exception as e:
        log.warning(f"Generation parsing failed: {e}")
        return {
            "reply": get_safe_fallback(policy_result.policy_action),
            "is_fallback": True,
            "fallback_reason": f"Schema parsing error: {str(e)}",
            "raw_output": raw_response_text,
            "evidence_used": []
        }

    # 4. Post-Generation Safety Validation
    val_res = validate_generation(generated_json, policy_result, retrieved_evidence)
    
    if not val_res["is_valid"]:
        return {
            "reply": val_res["fallback_reply"],
            "is_fallback": True,
            "fallback_reason": val_res["reason"],
            "raw_output": generated_json,
            "evidence_used": []
        }

    # Successful grounded response
    return {
        "reply": generated_json["reply"],
        "is_fallback": False,
        "fallback_reason": "",
        "raw_output": generated_json,
        "evidence_used": generated_json.get("evidence_ids", [])
    }
