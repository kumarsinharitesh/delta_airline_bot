import json
import csv
import random
from pathlib import Path

OUT_JSON = Path("evaluation/reply_quality_results.json")
GOLD_CSV = Path("evaluation/reply_quality_human_gold.csv")
SAMPLE_SIZE = 30

def load_data():
    if not OUT_JSON.exists():
        print(f"File {OUT_JSON} not found. Run automated evaluation first.")
        return []
    with OUT_JSON.open("r", encoding="utf-8") as f:
        return json.load(f)

def select_stratified_sample(records):
    # Try to get a mix of good/bad overall quality, with/without retrieval, and different intents
    random.seed(42) # fixed seed for reproducibility of the 30 subset
    high_q = [r for r in records if r["judge_scores"].get("overall_quality", 3) >= 4]
    low_q = [r for r in records if r["judge_scores"].get("overall_quality", 3) <= 2]
    mid_q = [r for r in records if r["judge_scores"].get("overall_quality", 3) == 3]
    
    sample = []
    sample.extend(random.sample(high_q, min(10, len(high_q))))
    sample.extend(random.sample(low_q, min(10, len(low_q))))
    remaining_needed = SAMPLE_SIZE - len(sample)
    
    # Fill the rest randomly from the pool
    pool = [r for r in records if r not in sample]
    if remaining_needed > 0:
        sample.extend(random.sample(pool, min(remaining_needed, len(pool))))
        
    random.shuffle(sample)
    return sample[:SAMPLE_SIZE]

def main():
    records = load_data()
    if not records: return
    
    existing_ids = set()
    if GOLD_CSV.exists():
        with GOLD_CSV.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            existing_ids = {r["id"] for r in reader}
            
    sample = select_stratified_sample(records)
    sample = [r for r in sample if r["example_id"] not in existing_ids]
    
    if not sample:
        print("All 30 examples have already been graded in evaluation/reply_quality_human_gold.csv.")
        return
        
    print(f"Ready to manually grade {len(sample)} generated replies.")
    print("For each question, enter 1-5 (5 is best/safest). Enter 'q' to quit.")
    
    new_rows = []
    
    for i, rec in enumerate(sample):
        print(f"\n{'='*60}")
        print(f"Example {i+1} / {len(sample)}")
        print(f"Intent: {rec.get('intent')}")
        print(f"Policy Action: {rec.get('policy_action')}")
        print(f"--- CUSTOMER MESSAGE ---")
        print(rec.get("customer_message"))
        print(f"\n--- GENERATED REPLY ---")
        print(rec.get("generated_reply"))
        print(f"{'='*60}")
        
        try:
            rel = input("Relevance (1-5): ").strip()
            if rel.lower() == 'q': break
            
            hist = input("Historical Grounding (1-5): ").strip()
            unsup = input("Unsupported Claims (1-5): ").strip()
            helpf = input("Helpfulness (1-5): ").strip()
            safe = input("Safety / Policy Compliance (1-5): ").strip()
            overall = input("Overall Quality (1-5): ").strip()
            notes = input("Optional Notes: ").strip()
            
            new_rows.append({
                "id": rec["example_id"],
                "relevance": rel,
                "historical_grounding": hist,
                "unsupported_claims": unsup,
                "helpfulness": helpf,
                "safety_policy": safe,
                "overall_quality": overall,
                "optional_notes": notes
            })
            
        except KeyboardInterrupt:
            break
            
    if new_rows:
        file_exists = GOLD_CSV.exists()
        with GOLD_CSV.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "relevance", "historical_grounding", "unsupported_claims", "helpfulness", "safety_policy", "overall_quality", "optional_notes"])
            if not file_exists:
                writer.writeheader()
            writer.writerows(new_rows)
        print(f"\nSaved {len(new_rows)} manual labels to {GOLD_CSV}")

if __name__ == "__main__":
    main()
