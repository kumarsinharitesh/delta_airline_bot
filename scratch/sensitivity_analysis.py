import csv
import json
from pathlib import Path
from src.policy.rules import evaluate_policy, PolicyAction, ReasonCode
from src.policy.escalation import decide_escalation
import re

GOLD_FILE = Path("evaluation/escalation_gold.csv")
INTENT_CACHE = Path("evaluation/dev_intent_predictions.jsonl")

def mock_detect_human_request(message: str) -> bool:
    patterns = [
        r"(?i)call me", r"(?i)talk to", r"(?i)speak to",
        r"(?i)dm me", r"(?i)dm please", r"(?i)messaged you", r"(?i)someone",
        r"(?i)customer service", r"(?i)human", r"(?i)agent", r"(?i)representative"
    ]
    return any(re.search(p, message) for p in patterns)

def evaluate_rules(gold_rows, intent_cache, enable_human, enable_flight, enable_loyalty, enable_ambig):
    unsafe = 0
    false_esc = 0
    total_true_esc = sum(1 for r in gold_rows if r["expected_decision"] == "ESCALATE")
    total_true_auto = sum(1 for r in gold_rows if r["expected_decision"] == "AUTO_HANDLE")
    
    for row in gold_rows:
        eid = row["example_id"]
        msg = row["customer_message"]
        ref_dec = row["expected_decision"]
        
        intent_data = intent_cache.get(eid, {})
        intent = intent_data.get("predicted", "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT")
        confidence = intent_data.get("confidence", 0.9)
        
        res = evaluate_policy(msg, intent, confidence)
        
        if enable_human and mock_detect_human_request(msg):
            res.policy_action = PolicyAction.ESCALATE
        
        if enable_flight and intent == "CANCEL_OR_CHANGE_FLIGHT":
            res.policy_action = PolicyAction.REQUIRE_VERIFICATION
            
        if enable_loyalty and intent == "SKYMILES_OR_LOYALTY":
            res.policy_action = PolicyAction.REQUIRE_VERIFICATION
            
        if enable_ambig and intent == "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT":
            res.policy_action = PolicyAction.ESCALATE
            
        esc = decide_escalation(res, confidence, True, [])
        sys_dec = esc.decision.value
        
        if ref_dec == "ESCALATE" and sys_dec == "AUTO_HANDLE":
            unsafe += 1
        elif ref_dec == "AUTO_HANDLE" and sys_dec == "ESCALATE":
            false_esc += 1
            
    unsafe_rate = (unsafe / total_true_esc) * 100
    false_esc_rate = (false_esc / total_true_auto) * 100
    
    return unsafe, false_esc, unsafe_rate, false_esc_rate

def main():
    gold_rows = list(csv.DictReader(GOLD_FILE.open("r", encoding="utf-8")))
    intent_cache = {json.loads(line)["example_id"]: json.loads(line) for line in INTENT_CACHE.open("r", encoding="utf-8") if line.strip()}

    configs = [
        ("BASE", False, False, False, False),
        ("Human", True, False, False, False),
        ("Human + Flight", True, True, False, False),
        ("Human + Flight + Loyalty", True, True, True, False),
        ("Human + Flight + Loyalty + Ambig", True, True, True, True),
        ("Flight Only", False, True, False, False)
    ]
    
    print(f"{'Config':<35} | {'Unsafe (count)':<15} | {'False Esc (count)':<15}")
    print("-" * 75)
    for name, h, f, l, a in configs:
        unsafe, false_esc, u_rate, f_rate = evaluate_rules(gold_rows, intent_cache, h, f, l, a)
        print(f"{name:<35} | {u_rate:>5.1f}% ({unsafe:<2})      | {f_rate:>5.1f}% ({false_esc:<2})")

if __name__ == "__main__":
    main()
