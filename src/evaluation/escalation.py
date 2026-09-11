import csv
import json
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
try:
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
except ImportError:
    print("Please install scikit-learn")
    import sys; sys.exit(1)

from src.policy.rules import evaluate_policy
from src.policy.escalation import decide_escalation, EscalationDecision

GOLD_FILE = Path("evaluation/escalation_gold.csv")
INTENT_CACHE = Path("evaluation/dev_intent_predictions.jsonl")
GEN_CACHE = Path("evaluation/phase8_results_full.jsonl")
OUT_MD = Path("evaluation/phase9_report.md")
AUDIT_MD = Path("evaluation/phase9_qualitative_audit.md")

def load_cache(path: Path, key: str) -> Dict[str, dict]:
    cache = {}
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                if not line.strip(): continue
                d = json.loads(line)
                if key in d:
                    cache[d[key]] = d
                # phase8 results uses example_id
                elif "example_id" in d:
                    cache[d["example_id"]] = d
    return cache

def main():
    gold_rows = []
    with GOLD_FILE.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            gold_rows.append(r)
            
    intent_cache = load_cache(INTENT_CACHE, "example_id")
    gen_cache = load_cache(GEN_CACHE, "example_id")
    
    results = []
    
    counts = {
        "auto_handle": 0,
        "escalate": 0,
        "policy_triggered": 0,
        "confidence_triggered": 0,
        "validation_triggered": 0,
        "verification_triggered": 0
    }
    
    for row in gold_rows:
        eid = row["example_id"]
        msg = row["customer_message"]
        
        # 1. Intent & Confidence
        intent_data = intent_cache.get(eid, {})
        intent = intent_data.get("predicted", "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT")
        confidence = intent_data.get("confidence", 0.9) # mock high if missing
        
        # 2. Policy Evaluation
        policy_res = evaluate_policy(msg, intent, confidence)
        
        # 3. Generation validation (mock or cache)
        gen_data = gen_cache.get(eid, {})
        generation_valid = not gen_data.get("is_fallback", False) if gen_data else True
        validation_failures = [gen_data.get("fallback_reason")] if gen_data and gen_data.get("is_fallback") else []
        
        # 4. Final Decision
        esc_res = decide_escalation(policy_res, confidence, generation_valid, validation_failures)
        
        # Stats
        if esc_res.decision == EscalationDecision.AUTO_HANDLE:
            counts["auto_handle"] += 1
        else:
            counts["escalate"] += 1
            if "POLICY_ESCALATE" in esc_res.reason_codes:
                counts["policy_triggered"] += 1
            if "VERIFICATION_UNSUPPORTED" in esc_res.reason_codes:
                counts["verification_triggered"] += 1
            if "LOW_CONFIDENCE" in esc_res.reason_codes:
                counts["confidence_triggered"] += 1
            if "GENERATION_INVALID" in esc_res.reason_codes or any(r.startswith("VALIDATION_FAILED") for r in esc_res.reason_codes):
                counts["validation_triggered"] += 1
                
        results.append({
            "example_id": eid,
            "message": msg,
            "context": row["context"],
            "intent": intent,
            "confidence": confidence,
            "policy_action": policy_res.policy_action.value,
            "reference_decision": row["expected_decision"],
            "system_decision": esc_res.decision.value,
            "system_reason": esc_res.reason,
            "system_reason_codes": esc_res.reason_codes
        })
        
    # Metrics
    y_true = [r["reference_decision"] for r in results]
    y_pred = [r["system_decision"] for r in results]
    
    acc = accuracy_score(y_true, y_pred)
    labels = ["AUTO_HANDLE", "ESCALATE"]
    prec, rec, f1, support = precision_recall_fscore_support(y_true, y_pred, labels=labels, zero_division=0)
    macro_f1 = np.mean(f1)
    
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    
    # Unsafe Auto-Handle Rate = Escalate instances (true) predicted as Auto-Handle
    # Index of ESCALATE is 1, AUTO_HANDLE is 0. So true=1, pred=0 is cm[1][0]
    unsafe_auto_handle_count = cm[1][0]
    total_true_escalate = sum(cm[1])
    unsafe_rate = (unsafe_auto_handle_count / total_true_escalate) * 100 if total_true_escalate > 0 else 0.0
    
    # --- Print to console ---
    print("\n--- PHASE 9 ESCALATION METRICS ---")
    print(f"Overall Accuracy: {acc:.4f}")
    print(f"Macro-F1: {macro_f1:.4f}")
    print(f"AUTO_HANDLE Precision: {prec[0]:.4f}, Recall: {rec[0]:.4f}")
    print(f"ESCALATE Precision: {prec[1]:.4f}, Recall: {rec[1]:.4f}")
    print(f"Unsafe Auto-Handle Rate: {unsafe_rate:.1f}% ({unsafe_auto_handle_count}/{total_true_escalate})")
    
    print("\nConfusion Matrix:")
    print(f"                 Pred AUTO_HANDLE   Pred ESCALATE")
    print(f"True AUTO_HANDLE {cm[0][0]:<17} {cm[0][1]}")
    print(f"True ESCALATE    {cm[1][0]:<17} {cm[1][1]}")
    
    print("\nDistribution:")
    for k, v in counts.items():
        print(f"{k}: {v}")
        
    # --- Generate Qualitative Audit ---
    audit_samples = []
    # Try to pick a mix
    # correct auto_handle, correct escalate, false auto_handle, false escalate
    mix_needed = {"correct_ah": 5, "correct_esc": 5, "false_ah": 5, "false_esc": 5}
    
    for r in results:
        cat = None
        if r["reference_decision"] == "AUTO_HANDLE" and r["system_decision"] == "AUTO_HANDLE":
            cat = "correct_ah"
        elif r["reference_decision"] == "ESCALATE" and r["system_decision"] == "ESCALATE":
            cat = "correct_esc"
        elif r["reference_decision"] == "ESCALATE" and r["system_decision"] == "AUTO_HANDLE":
            cat = "false_ah"
        elif r["reference_decision"] == "AUTO_HANDLE" and r["system_decision"] == "ESCALATE":
            cat = "false_esc"
            
        if cat and mix_needed[cat] > 0:
            audit_samples.append(r)
            mix_needed[cat] -= 1
            
    # fill rest to 20 if needed
    for r in results:
        if len(audit_samples) >= 20: break
        if r not in audit_samples:
            audit_samples.append(r)
            
    with AUDIT_MD.open("w", encoding="utf-8") as f:
        f.write("# Phase 9 Qualitative Audit\n\n")
        for i, r in enumerate(audit_samples):
            f.write(f"### Example {i+1} (ID: {r['example_id']})\n")
            f.write(f"- **Customer**: {r['message']}\n")
            f.write(f"- **Context**: {r['context']}\n")
            f.write(f"- **Intent**: {r['intent']} (Conf: {r['confidence']})\n")
            f.write(f"- **Policy Action**: {r['policy_action']}\n")
            f.write(f"- **Reference Decision**: {r['reference_decision']}\n")
            f.write(f"- **System Decision**: {r['system_decision']}\n")
            f.write(f"- **System Reason**: {r['system_reason']}\n\n")

    # --- Generate Report ---
    with OUT_MD.open("w", encoding="utf-8") as f:
        f.write("# Phase 9 Escalation Report\n\n")
        f.write("## Objective\nBuild and evaluate the deterministic final Auto-Handle vs Human Escalation layer.\n\n")
        f.write("## Methodology\n")
        f.write("150 stratified held-out DEV examples were independently annotated using Sarvam-105B under a fixed rubric. ")
        f.write("The resulting dataset is an independent LLM-assisted escalation reference set, not human-labeled ground truth.\n\n")
        f.write("## Metrics\n")
        f.write(f"- **Overall Accuracy**: {acc*100:.1f}%\n")
        f.write(f"- **Macro-F1**: {macro_f1:.4f}\n")
        f.write(f"- **AUTO_HANDLE Precision**: {prec[0]:.4f} | **Recall**: {rec[0]:.4f}\n")
        f.write(f"- **ESCALATE Precision**: {prec[1]:.4f} | **Recall**: {rec[1]:.4f}\n")
        f.write(f"- **Unsafe Auto-Handle Rate**: {unsafe_rate:.1f}% ({unsafe_auto_handle_count}/{total_true_escalate})\n\n")
        
        f.write("## Triggers\n")
        for k, v in counts.items():
            f.write(f"- **{k}**: {v}\n")
            
        f.write("\n## Limitations\n")
        f.write("- The reference set is LLM-assisted rather than human-labeled.\n")
        f.write("- Therefore these metrics measure agreement with the independent LLM-assisted reference set, not human-vs-system agreement.\n")
        f.write("- The 0.60 threshold is heuristic and not calibrated.\n")
        f.write("- A single annotation model may introduce correlated judgment bias.\n")
        f.write("- The escalation rules are deterministic but are only as good as the upstream intent/policy/validation signals.\n")
        f.write("- No active identity/payment verification mechanism exists in the prototype.\n")

if __name__ == "__main__":
    main()
