import csv
import json
from pathlib import Path
from src.policy.rules import evaluate_policy
from src.policy.escalation import decide_escalation

GOLD_FILE = Path("evaluation/escalation_gold.csv")
INTENT_CACHE = Path("evaluation/dev_intent_predictions.jsonl")

def main():
    gold_rows = []
    with GOLD_FILE.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            gold_rows.append(r)
            
    intent_cache = {}
    with INTENT_CACHE.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            d = json.loads(line)
            intent_cache[d["example_id"]] = d

    false_auto_handles = []
    
    for row in gold_rows:
        eid = row["example_id"]
        msg = row["customer_message"]
        
        intent_data = intent_cache.get(eid, {})
        intent = intent_data.get("predicted", "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT")
        confidence = intent_data.get("confidence", 0.9)
        
        policy_res = evaluate_policy(msg, intent, confidence)
        esc_res = decide_escalation(policy_res, confidence, True, [])
        
        ref_decision = row["expected_decision"]
        sys_decision = esc_res.decision.value
        
        if ref_decision == "ESCALATE" and sys_decision == "AUTO_HANDLE":
            false_auto_handles.append({
                "example_id": eid,
                "msg": msg,
                "intent": intent,
                "confidence": confidence,
                "ref_reason": row["expected_reason_codes"]
            })
            
    print(f"Total False AUTO_HANDLE: {len(false_auto_handles)}\n")
    
    # Analyze by Reference Reason
    reasons = {}
    for case in false_auto_handles:
        r = case["ref_reason"]
        reasons[r] = reasons.get(r, 0) + 1
        
    print("Breakdown by Reference Annotation Reason:")
    for r, count in reasons.items():
        print(f"  {r}: {count}")
        
    # Let's see the intents for POLICY_RESTRICTION
    print("\nIntents for POLICY_RESTRICTION:")
    for case in false_auto_handles:
        if case["ref_reason"] == "POLICY_RESTRICTION":
            print(f"  [{case['intent']}] {case['msg']}")
            
    # Intents for LOW_CONTEXT
    print("\nIntents for LOW_CONTEXT:")
    for case in false_auto_handles:
        if case["ref_reason"] == "LOW_CONTEXT":
            print(f"  [{case['intent']}] {case['msg']}")
            
    # Intents for HUMAN_REQUEST
    print("\nIntents for HUMAN_REQUEST:")
    for case in false_auto_handles:
        if case["ref_reason"] == "HUMAN_REQUEST":
            print(f"  [{case['intent']}] {case['msg']}")

if __name__ == "__main__":
    main()
