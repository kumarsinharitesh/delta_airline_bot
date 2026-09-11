import json
from pathlib import Path
import random

def format_audit(mode="full"):
    results_path = Path(f"evaluation/phase8_results_{mode}.jsonl")
    if not results_path.exists():
        print(f"Results file {results_path} not found.")
        return
        
    records = []
    with results_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
                
    # Prioritize edge cases and a mix of intents
    selected = []
    
    # 1. Grab all explicit adversarial cases
    adv_records = [r for r in records if r["example_id"].startswith("adv_")]
    selected.extend(adv_records)
    
    # 2. Grab at least one of each major intent from the remaining
    remaining = [r for r in records if not r["example_id"].startswith("adv_")]
    random.shuffle(remaining)
    
    intent_seen = set()
    for r in remaining:
        if r["intent"] not in intent_seen:
            intent_seen.add(r["intent"])
            selected.append(r)
            if len(selected) >= 15:
                break
                
    # Fill remaining if needed
    for r in remaining:
        if len(selected) >= 15:
            break
        if r not in selected:
            selected.append(r)
            
    out_path = Path("evaluation/phase8_qualitative_audit.md")
    with out_path.open("w", encoding="utf-8") as out_f:
        out_f.write("# Phase 8: Qualitative Generation Audit\n\n")
        out_f.write("This audit demonstrates Sarvam-105b's generation grounded in Phase 6 retrieval and constrained by Phase 7 deterministic policy.\n\n")
        
        for i, r in enumerate(selected[:15], 1):
            out_f.write(f"## Scenario {i}: {r['intent']}\n\n")
            out_f.write(f"**Customer Message:** `{r['customer_message']}`\n\n")
            out_f.write(f"**Phase 7 Policy Decision:** `{r['policy_action']}`\n\n")
            if r['is_fallback']:
                out_f.write(f"**Generation Status:** ❌ REJECTED BY VALIDATOR -> Fallback\n\n")
                out_f.write(f"**Fallback Reason:** {r['fallback_reason']}\n\n")
            else:
                out_f.write(f"**Generation Status:** ✅ APPROVED BY VALIDATOR\n\n")
                
            out_f.write(f"**Final Output sent to customer:**\n> {r['generated_reply']}\n\n")
            out_f.write("---\n")
            
    print(f"Generated {out_path} with {len(selected[:15])} scenarios.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="full")
    args = parser.parse_args()
    format_audit(args.mode)
