"""
Demo UI backend server for the Delta Airlines Customer Support Agent prototype.
Uses only Python standard library — no Flask/FastAPI required.

Run with:
    python src/app.py

Opens on: http://localhost:8000

IMPORTANT: This is a DEMO/REVIEW interface only.
It calls the existing locked pipeline without modifying any evaluation logic.
"""

import json
import logging
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

# Ensure project root is on the path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Load .env
env_file = ROOT / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip()

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s")
log = logging.getLogger("demo-ui")

# --- Import pipeline components (read-only, no modifications) ---
from src.safety.prompt_injection import detect_prompt_injection, detect_human_request
from src.llm.sarvam_client import predict_intent
from src.policy.rules import evaluate_policy
from src.policy.escalation import decide_escalation
from src.retrieval.retrieve import retrieve
from src.agent.generate import generate_response

STATIC_DIR = ROOT / "static"

# Load intent prompt template once
INTENT_PROMPT_TEMPLATE = (ROOT / "src" / "llm" / "prompts" / "sarvam_intent_v1.txt").read_text(encoding="utf-8")


def run_pipeline(customer_message: str, history: list = None, attachment: dict = None) -> dict:
    """
    Runs the full locked pipeline and returns a structured result dict.
    Does NOT expose API keys, chain-of-thought, or reasoning_content.
    Supports multi-turn conversational context and file attachments.
    """
    if history is None:
        history = []

    # Build conversation context from prior turns (last 4 turns)
    context_parts = []
    for turn in history[-4:]:
        role = turn.get("role", "customer").capitalize()
        text = str(turn.get("text", "")).strip()
        if text:
            context_parts.append(f"{role}: {text}")
    conversation_context = " | ".join(context_parts)

    # If attachment is provided, incorporate its presence into processing text
    attachment_note = ""
    if attachment and isinstance(attachment, dict) and attachment.get("name"):
        attachment_note = f"[Attached file: {attachment.get('name')}]"
        effective_message = f"{customer_message} {attachment_note}".strip()
    else:
        effective_message = customer_message

    result = {
        "customer_message": customer_message,
        "attachment": attachment if (attachment and attachment.get("name")) else None,
        "safety_flags": [],
        "intent": None,
        "intent_confidence": None,
        "policy_action": None,
        "policy_reason": None,
        "retrieval_used": False,
        "retrieved_count": 0,
        "reply": None,
        "is_fallback": False,
        "generation_valid": True,
        "final_decision": None,
        "escalation_reason": None,
        "error": None,
    }

    try:
        # ── Step 1: Safety checks ──────────────────────────────────────────────
        if detect_prompt_injection(customer_message):
            result["safety_flags"].append("PROMPT_INJECTION_DETECTED")
        if detect_human_request(customer_message):
            result["safety_flags"].append("EXPLICIT_HUMAN_REQUEST")

        # ── Step 2: Intent classification ──────────────────────────────────────
        # Ground classification in conversation context if follow-up
        if conversation_context:
            text_to_classify = f"{conversation_context} | CUSTOMER: {customer_message}"
        else:
            text_to_classify = f"CUSTOMER: {customer_message}"
        intent_prompt = INTENT_PROMPT_TEMPLATE + f"\n\nMessage to classify:\n{text_to_classify}\n"
        intent_data = predict_intent(intent_prompt)
        intent = intent_data.get("primary_intent", "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT")
        confidence = float(intent_data.get("confidence", 0.5))
        result["intent"] = intent
        result["intent_confidence"] = round(confidence, 3)

        # ── Step 3: Policy evaluation ──────────────────────────────────────────
        policy_result = evaluate_policy(customer_message, intent, confidence)
        result["policy_action"] = policy_result.policy_action.value
        result["policy_reason"] = policy_result.reason

        # ── Step 4: Conditional retrieval ─────────────────────────────────────
        retrieved_evidence = []
        from src.policy.rules import PolicyAction
        if policy_result.policy_action == PolicyAction.ALLOW_SAFE_RESPONSE:
            ret = retrieve(customer_message, intent=intent, top_k=3)
            retrieved_evidence = ret.get("results", [])
            result["retrieval_used"] = len(retrieved_evidence) > 0
            result["retrieved_count"] = len(retrieved_evidence)

        # ── Step 5: Generation ────────────────────────────────────────────────
        gen_result = generate_response(
            customer_message=effective_message,
            conversation_context=conversation_context,
            intent=intent,
            confidence=confidence,
            policy_result=policy_result,
            retrieved_evidence=retrieved_evidence,
        )
        result["reply"] = gen_result.get("reply", "")
        result["is_fallback"] = gen_result.get("is_fallback", False)
        generation_valid = not result["is_fallback"]

        # ── Step 6: Escalation decision ───────────────────────────────────────
        esc = decide_escalation(
            policy_result=policy_result,
            intent_confidence=confidence,
            generation_valid=generation_valid,
            validation_failures=[],
        )
        result["final_decision"] = esc.decision.value
        if esc.decision.value == "ESCALATE":
            result["escalation_reason"] = esc.reason

    except Exception as e:
        log.exception("Pipeline error")
        result["error"] = f"Pipeline error: {str(e)}"
        result["reply"] = (
            "We're sorry, something went wrong. Please try again or contact support directly."
        )
        result["final_decision"] = "ESCALATE"
        result["escalation_reason"] = "SYSTEM_ERROR"

    return result


class DemoHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler serving static files and the /chat API."""

    def log_message(self, format, *args):  # suppress default noisy logging
        log.info("%s - %s", self.address_string(), format % args)

    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _serve_static(self, path: str):
        file_path = STATIC_DIR / path.lstrip("/")
        if not file_path.exists() or not file_path.is_file():
            self.send_error(404, "Not Found")
            return
        ext = file_path.suffix.lower()
        content_types = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".png": "image/png",
            ".ico": "image/x-icon",
        }
        ct = content_types.get(ext, "application/octet-stream")
        body = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            self._serve_static("index.html")
        elif path.startswith("/static/"):
            self._serve_static(path[len("/static/"):])
        else:
            # Try to serve from static/ directly
            self._serve_static(path)

    def do_POST(self):
        if self.path != "/chat":
            self.send_error(404, "Not Found")
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
            message = str(data.get("message", "")).strip()
            history = data.get("history", [])
            attachment = data.get("attachment")
            if not isinstance(history, list):
                history = []
        except Exception:
            self._send_json({"error": "Invalid JSON body"}, 400)
            return

        if not message and not attachment:
            self._send_json({"error": "Message cannot be empty"}, 400)
            return

        if not message and attachment:
            message = f"Please check my attached document: {attachment.get('name', 'file')}"

        if len(message) > 2000:
            self._send_json({"error": "Message too long (max 2000 chars)"}, 400)
            return

        log.info("Received message: %.80s... (history: %d, attachment: %s)", message, len(history), bool(attachment))
        result = run_pipeline(message, history=history, attachment=attachment)
        self._send_json(result)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def main():
    port = 8000
    server = HTTPServer(("localhost", port), DemoHandler)
    log.info("=" * 60)
    log.info("Delta Support Agent — DEMO UI")
    log.info("Open in browser: http://localhost:%d", port)
    log.info("This is a prototype demo. Do not use in production.")
    log.info("=" * 60)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("Server stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
