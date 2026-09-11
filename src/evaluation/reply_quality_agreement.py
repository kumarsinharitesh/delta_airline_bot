import json
import csv
import random
import os
import time
from pathlib import Path
from tqdm import tqdm
from scipy.stats import spearmanr
from sklearn.metrics import confusion_matrix
from src.llm.sarvam_client import _predict_requests

OUT_JSON = Path("evaluation/reply_quality_results.json")
SECOND_JUDGE_PROMPT = Path("src/llm/prompts/reply_quality_second_judge.txt")
SECOND_JUDGE_CSV = Path("evaluation/reply_quality_second_judge.csv")
AGREEMENT_JSON = Path("evaluation/reply_quality_llm_agreement.json")

def format_judge_prompt(record, rubric):
    msg = record.get("customer_message", "")
    ctx = record.get("context", "")
    retrieval = record.get("retrieval_context", "")
    reply = record.get("generated_reply", "")
    
    prompt = rubric + "\n\n"
    prompt += "=== EVALUATION TARGET ===\n"
    prompt += f"CUSTOMER MESSAGE:\n{msg}\n\n"
    if ctx:
        prompt += f"PRIOR CONTEXT:\n{ctx}\n\n"
    if retrieval:
        prompt += f"RETRIEVED EVIDENCE:\n{retrieval}\n\n"
    prompt += f"GENERATED REPLY TO EVALUATE:\n{reply}\n"
    return prompt

def select_stratified_sample(records):
    # Try to get a mix of good/bad overall quality, with/without retrieval, and different intents
    random.seed(42) # fixed seed for reproducibility of the 30 subset
    high_q = [r for r in records if r["judge_scores"].get("overall_quality", 3) >= 4]
    low_q = [r for r in records if r["judge_scores"].get("overall_quality", 3) <= 2]
    mid_q = [r for r in records if r["judge_scores"].get("overall_quality", 3) == 3]
    
    sample = []
    sample.extend(random.sample(high_q, min(10, len(high_q))))
    sample.extend(random.sample(low_q, min(10, len(low_q))))
    remaining_needed = 30 - len(sample)
    
    pool = [r for r in records if r not in sample]
    if remaining_needed > 0:
        sample.extend(random.sample(pool, min(remaining_needed, len(pool))))
        
    random.shuffle(sample)
    return sample[:30]

def calculate_agreement(y_true, y_pred):
    if not y_true or not y_pred: return 0, 0, 0
    exact = sum(1 for t, p in zip(y_true, y_pred) if t == p) / len(y_true)
    within_1 = sum(1 for t, p in zip(y_true, y_pred) if abs(t - p) <= 1) / len(y_true)
    mad = sum(abs(t - p) for t, p in zip(y_true, y_pred)) / len(y_true)
    return exact, within_1, mad

def main():
    with OUT_JSON.open("r", encoding="utf-8") as f:
        records = json.load(f)
        
    sample = select_stratified_sample(records)
    rubric = SECOND_JUDGE_PROMPT.read_text(encoding="utf-8")
    api_key = os.environ.get("SARVAM_API_KEY")
    schema = {"type": "json_object"}
    
    second_judge_scores = []
    
    print(f"Evaluating {len(sample)} replies with INDEPENDENT SECOND LLM JUDGE...")
    for rec in tqdm(sample):
        full_prompt = format_judge_prompt(rec, rubric)
        messages = [{"role": "user", "content": full_prompt}]
        
        result_json = {"relevance": 3, "historical_grounding": 3, "unsupported_claims": 3, "helpfulness": 3, "safety_policy": 3, "overall_quality": 3, "brief_reason": ""}
        for _ in range(3):
            try:
                content, _ = _predict_requests(messages, "sarvam-105b", 0.0, schema, api_key)
                parsed = json.loads(content)
                for k in result_json:
                    if k in parsed: result_json[k] = parsed[k]
                break
            except Exception:
                time.sleep(2)
                
        result_json["id"] = rec["example_id"]
        second_judge_scores.append(result_json)
        
    with SECOND_JUDGE_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "relevance", "historical_grounding", "unsupported_claims", "helpfulness", "safety_policy", "overall_quality", "brief_reason", "failure_tags"])
        writer.writeheader()
        for row in second_judge_scores:
            writer.writerow(row)
            
    # Calculate Agreement
    keys = ["relevance", "historical_grounding", "unsupported_claims", "helpfulness", "safety_policy", "overall_quality"]
    agreement_results = {}
    
    first_judge_map = {r["example_id"]: r["judge_scores"] for r in sample}
    second_judge_map = {r["id"]: r for r in second_judge_scores}
    
    for key in keys:
        y1 = [int(first_judge_map[eid][key]) for eid in first_judge_map]
        y2 = [int(second_judge_map[eid][key]) for eid in first_judge_map]
        ex, w1, mad = calculate_agreement(y1, y2)
        agreement_results[key] = {
            "exact_agreement": ex,
            "within_1_point": w1,
            "mean_absolute_diff": mad
        }
        
    y1_over = [int(first_judge_map[eid]["overall_quality"]) for eid in first_judge_map]
    y2_over = [int(second_judge_map[eid]["overall_quality"]) for eid in first_judge_map]
    
    corr, p = spearmanr(y1_over, y2_over)
    cm = confusion_matrix(y1_over, y2_over, labels=[1,2,3,4,5]).tolist()
    
    agreement_results["overall_quality"]["spearman_correlation"] = corr if not str(corr) == 'nan' else 0.0
    agreement_results["overall_quality"]["confusion_matrix"] = cm
    
    with AGREEMENT_JSON.open("w", encoding="utf-8") as f:
        json.dump(agreement_results, f, indent=2)
        
    print("\n--- INDEPENDENT LLM-VS-LLM AGREEMENT METRICS ---")
    print(f"Total Evaluated: {len(sample)}")
    for key in keys:
        res = agreement_results[key]
        print(f"\n{key.upper()}:")
        print(f"  Exact Agreement: {res['exact_agreement']:.2%}")
        print(f"  Within ±1 Point: {res['within_1_point']:.2%}")
        print(f"  Mean Abs Diff:   {res['mean_absolute_diff']:.2f}")
    print(f"\nOverall Quality Spearman Correlation: {agreement_results['overall_quality'].get('spearman_correlation', 0):.2f}")

if __name__ == "__main__":
    main()
