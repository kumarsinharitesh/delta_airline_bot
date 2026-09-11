import json
import os
import time
from pathlib import Path
from tqdm import tqdm
from src.llm.sarvam_client import _predict_requests

RESULTS_FILE = Path("evaluation/phase8_results_full.jsonl")
PROMPT_FILE = Path("src/llm/prompts/reply_quality_judge.txt")
OUT_JSON = Path("evaluation/reply_quality_results.json")

def format_judge_prompt(record, rubric):
    msg = record.get("customer_message", "")
    ctx = record.get("context", "")
    intent = record.get("intent", "UNKNOWN")
    policy = record.get("policy_action", "UNKNOWN")
    retrieval = record.get("retrieval_context", "")
    reply = record.get("generated_reply", "")
    
    prompt = rubric + "\n\n"
    prompt += "=== EVALUATION TARGET ===\n"
    prompt += f"CUSTOMER MESSAGE:\n{msg}\n\n"
    if ctx:
        prompt += f"PRIOR CONTEXT:\n{ctx}\n\n"
    prompt += f"SYSTEM INTENT: {intent}\n"
    prompt += f"POLICY ACTION: {policy}\n\n"
    if retrieval:
        prompt += f"RETRIEVED EVIDENCE:\n{retrieval}\n\n"
    prompt += f"GENERATED REPLY TO EVALUATE:\n{reply}\n"
    return prompt

def main():
    if not RESULTS_FILE.exists():
        print(f"File {RESULTS_FILE} not found.")
        return
        
    records = []
    with RESULTS_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
                
    rubric = PROMPT_FILE.read_text(encoding="utf-8")
    api_key = os.environ.get("SARVAM_API_KEY")
    schema = {"type": "json_object"}
    
    judged_results = []
    
    # Check if we already have some cached
    cache = {}
    if OUT_JSON.exists():
        try:
            with OUT_JSON.open("r", encoding="utf-8") as f:
                existing = json.load(f)
                for item in existing:
                    cache[item["example_id"]] = item
        except:
            pass
            
    print(f"Evaluating {len(records)} generated replies with Sarvam-105b as judge...")
    
    for rec in tqdm(records):
        eid = rec["example_id"]
        if eid in cache:
            judged_results.append(cache[eid])
            continue
            
        full_prompt = format_judge_prompt(rec, rubric)
        messages = [{"role": "user", "content": full_prompt}]
        
        result_json = {
            "relevance": 3, "historical_grounding": 3, "unsupported_claims": 3,
            "helpfulness": 3, "safety_policy": 3, "overall_quality": 3,
            "failure_tags": ["EVAL_ERROR"], "brief_reason": "Evaluation failed."
        }
        
        for _ in range(3):
            try:
                content, _ = _predict_requests(messages, "sarvam-105b", 0.0, schema, api_key)
                parsed = json.loads(content)
                # Ensure all keys exist
                for k in ["relevance", "historical_grounding", "unsupported_claims", "helpfulness", "safety_policy", "overall_quality"]:
                    if k in parsed: result_json[k] = parsed[k]
                result_json["failure_tags"] = parsed.get("failure_tags", [])
                result_json["brief_reason"] = parsed.get("brief_reason", "")
                break
            except Exception as e:
                time.sleep(2)
                
        rec_copy = rec.copy()
        rec_copy["judge_scores"] = result_json
        judged_results.append(rec_copy)
        
        # Incremental save
        with OUT_JSON.open("w", encoding="utf-8") as f:
            json.dump(judged_results, f, indent=2)

    # --- METRICS CALCULATION ---
    def avg(key):
        vals = [r["judge_scores"].get(key, 1) for r in judged_results]
        return sum(vals) / len(vals) if vals else 0
        
    def pct(condition):
        count = sum(1 for r in judged_results if condition(r["judge_scores"]))
        return (count / len(judged_results)) * 100 if judged_results else 0
        
    print("\n--- LLM-AS-JUDGE AUTOMATED METRICS ---")
    print(f"Total Evaluated: {len(judged_results)}")
    print(f"Judge Model: sarvam-105b")
    print(f"Mean Relevance: {avg('relevance'):.2f}")
    print(f"Mean Historical Grounding: {avg('historical_grounding'):.2f}")
    print(f"Mean Unsupported Claims (5 is best): {avg('unsupported_claims'):.2f}")
    print(f"Mean Helpfulness: {avg('helpfulness'):.2f}")
    print(f"Mean Safety/Policy (5 is best): {avg('safety_policy'):.2f}")
    print(f"Mean Overall Quality: {avg('overall_quality'):.2f}")
    print(f"Overall Quality >= 4: {pct(lambda x: x.get('overall_quality', 0) >= 4):.1f}%")
    print(f"Safety Score <= 2: {pct(lambda x: x.get('safety_policy', 5) <= 2):.1f}%")
    print(f"Unsupported Claims <= 2: {pct(lambda x: x.get('unsupported_claims', 5) <= 2):.1f}%")
    
    # Split by retrieval
    with_ret = [r for r in judged_results if r.get("retrieval_context")]
    no_ret = [r for r in judged_results if not r.get("retrieval_context")]
    
    if with_ret:
        print(f"\n[With Retrieval] Mean Overall: {sum(r['judge_scores'].get('overall_quality', 0) for r in with_ret)/len(with_ret):.2f}")
    if no_ret:
        print(f"[No Retrieval] Mean Overall: {sum(r['judge_scores'].get('overall_quality', 0) for r in no_ret)/len(no_ret):.2f}")
        
    print("\nNext step: Run the manual human grading script to generate the 30-case gold set.")
    print("Execute: $env:PYTHONPATH=\".\"; python scratch/label_reply_quality.py")

if __name__ == "__main__":
    main()
