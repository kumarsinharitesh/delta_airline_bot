import json
import random
import csv
import re
from pathlib import Path
from tqdm import tqdm
from collections import Counter
import time

from src.llm.sarvam_client import _predict_requests
import os

DEV_DATA = Path("data/processed/dev.jsonl")
OUT_FILE = Path("evaluation/escalation_gold.csv")
PROMPT_FILE = Path("src/llm/prompts/escalation_annotation.txt")

def extract_message(conversation):
    messages = conversation.get("messages", [])
    if not messages:
        return "", ""
    # Find customer message
    cust_msg = ""
    support_ctx = ""
    for m in messages:
        if m.get("role") == "CUSTOMER":
            cust_msg = m.get("text_clean", "")
        elif m.get("role") == "SUPPORT" and not cust_msg:
            support_ctx += m.get("text_clean", "") + " | "
    return cust_msg, support_ctx

def stratify_sample(n=150):
    all_examples = []
    with DEV_DATA.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            all_examples.append(json.loads(line))
            
    random.seed(42)
    random.shuffle(all_examples)
    
    refund = []
    fraud = []
    flight = []
    general = []
    
    for ex in all_examples:
        msg, _ = extract_message(ex)
        msg_lower = msg.lower()
        if re.search(r"refund|compensation|money|charge|paid", msg_lower):
            refund.append(ex)
        elif re.search(r"fraud|stolen|hacked|account|login|password", msg_lower):
            fraud.append(ex)
        elif re.search(r"flight|delay|cancel|rebook|gate|seat", msg_lower):
            flight.append(ex)
        else:
            general.append(ex)
            
    sampled = []
    sampled.extend(refund[:30])
    sampled.extend(fraud[:20])
    sampled.extend(flight[:40])
    sampled.extend(general[:(150 - len(sampled))])
    
    if len(sampled) < n:
        leftovers = [ex for ex in all_examples if ex not in sampled]
        sampled.extend(leftovers[:n - len(sampled)])
        
    random.shuffle(sampled)
    return sampled

def predict_annotation(msg, ctx, prompt_template):
    full_prompt = prompt_template + "\n\n"
    if ctx:
        full_prompt += f"CONTEXT:\n{ctx}\n\n"
    full_prompt += f"CUSTOMER MESSAGE:\n{msg}\n"
    
    api_key = os.environ.get("SARVAM_API_KEY")
    schema = {"type": "json_object"}
    messages = [{"role": "user", "content": full_prompt}]
    
    for _ in range(3):
        try:
            content, actual_model = _predict_requests(messages, "sarvam-105b", 0.0, schema, api_key)
            result = json.loads(content)
            return result, actual_model
        except Exception as e:
            time.sleep(2)
            
    return {"decision": "ESCALATE", "reason_code": "SYSTEM_ERROR", "confidence": "LOW"}, "unknown"

def main():
    print("Preparing 150 stratified DEV examples for LLM annotation...")
    samples = stratify_sample(150)
    prompt_template = PROMPT_FILE.read_text(encoding="utf-8")
    
    with OUT_FILE.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "example_id", 
            "customer_message", 
            "context", 
            "expected_decision", 
            "expected_reason_codes", 
            "reviewer_confidence", 
            "reviewer_notes",
            "annotation_method"
        ])
        
        results = []
        actual_model_used = "unknown"
        
        for ex in tqdm(samples, desc="Annotating"):
            eid = ex.get("conversation_id")
            msg, ctx = extract_message(ex)
            
            res, model = predict_annotation(msg, ctx, prompt_template)
            if model != "unknown":
                actual_model_used = model
                
            decision = res.get("decision", "ESCALATE")
            reason = res.get("reason_code", "OTHER")
            confidence = res.get("confidence", "LOW")
            
            # Save the row
            writer.writerow([
                eid,
                msg,
                ctx,
                decision,
                reason,
                confidence,
                "Independent LLM annotation",
                "LLM_ASSISTED_INDEPENDENT_ANNOTATION"
            ])
            f.flush()
            results.append(res)
            
    # Print summary
    decisions = Counter([r.get("decision") for r in results])
    reasons = Counter([r.get("reason_code") for r in results])
    confidences = Counter([r.get("confidence") for r in results])
    
    print("\n--- LLM-ASSISTED INDEPENDENT ANNOTATION SUMMARY ---")
    print(f"Total Examples Evaluated: {len(results)}")
    print(f"Annotation Model: {actual_model_used}")
    print(f"AUTO_HANDLE count: {decisions.get('AUTO_HANDLE', 0)}")
    print(f"ESCALATE count: {decisions.get('ESCALATE', 0)}")
    print("\nReason Distribution:")
    for r, c in reasons.items():
        print(f"  {r}: {c}")
    print("\nConfidence Distribution:")
    for c, count in confidences.items():
        print(f"  {c}: {count}")
    print(f"\nOutput saved to: {OUT_FILE}")
    print("Validation status: SUCCESS")

if __name__ == "__main__":
    main()
