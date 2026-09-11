import os
from pathlib import Path

env_file = Path(".env")
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip()

import json
import logging
import requests
from pydantic import BaseModel, Field, ValidationError
from typing import Optional

try:
    from sarvamai import SarvamAI
    HAS_SDK = True
except ImportError:
    HAS_SDK = False

log = logging.getLogger(__name__)

class IntentClassification(BaseModel):
    primary_intent: str
    secondary_intent: Optional[str] = None
    is_multi_intent: bool
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str

SARVAM_URL = "https://api.sarvam.ai/v1/chat/completions"

# Fallback ERROR response
ERROR_FALLBACK = {
    "primary_intent": "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT",
    "secondary_intent": None,
    "is_multi_intent": False,
    "confidence": 0.0,
    "reason": "Sarvam classification failed validation."
}

def predict_intent(prompt: str, model: str = "sarvam-105b", temperature: float = 0.0) -> dict:
    """Predict intent using Sarvam AI, with structured output enforcing."""
    api_key = os.environ.get("SARVAM_API_KEY")
    if not api_key:
        log.error("SARVAM_API_KEY not found in environment.")
        return ERROR_FALLBACK.copy()

    # Use JSON mode since Sarvam-105b doesn't support json_schema
    schema = {
        "type": "json_object"
    }

    messages = [
        {"role": "user", "content": prompt}
    ]

    raw_content = ""
    actual_model = model

    try:
        if HAS_SDK:
            # Using SDK
            client = SarvamAI(api_subscription_key=api_key)
            # Try with structured output
            try:
                response = client.chat.completions(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    response_format=schema,
                    max_tokens=4000,
                    n=1
                )
                if hasattr(response, 'choices') and len(response.choices) > 0:
                    msg = response.choices[0].message
                    raw_content = getattr(msg, 'content', "") or ""
                elif hasattr(response, 'get'):
                    # Fallback if response is a dict
                    msg = response.get("choices", [{}])[0].get("message", {})
                    raw_content = msg.get("content", "") or ""
                
                # Try getting actual model
                if hasattr(response, 'model'):
                    actual_model = response.model
                elif hasattr(response, 'get'):
                    actual_model = response.get("model", model)
            except Exception as e:
                log.warning(f"SDK structured output failed: {e}. Falling back to requests API.")
                raw_content, actual_model = _predict_requests(messages, model, temperature, schema, api_key)
        else:
            # Fallback to requests if SDK not available
            raw_content, actual_model = _predict_requests(messages, model, temperature, schema, api_key)
            
        if not raw_content:
            log.error("Empty content returned from Sarvam API.")
            return ERROR_FALLBACK.copy()

        # Try to parse the content as JSON
        parsed_json = json.loads(raw_content)
        
        # Validate with Pydantic
        valid_obj = IntentClassification(**parsed_json)
        
        result = valid_obj.dict()
        result["_actual_model"] = actual_model
        result["_raw_response"] = raw_content
        return result

    except json.JSONDecodeError as e:
        log.error(f"Failed to decode JSON from Sarvam response: {e}. Raw: {raw_content}")
        return ERROR_FALLBACK.copy()
    except ValidationError as e:
        log.error(f"Pydantic validation failed for Sarvam response: {e}. Raw: {raw_content}")
        return ERROR_FALLBACK.copy()
    except Exception as e:
        log.error(f"Unexpected error calling Sarvam API: {e}")
        return ERROR_FALLBACK.copy()

def _predict_requests(messages, model, temperature, schema, api_key):
    headers = {
        "api-subscription-key": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "response_format": schema,
        "reasoning_effort": None,
        "max_tokens": 4000,
        "n": 1
    }
    resp = requests.post(SARVAM_URL, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    msg = data["choices"][0]["message"]
    content = msg.get("content", "") or ""
    actual_model = data.get("model", model)
    return content, actual_model

