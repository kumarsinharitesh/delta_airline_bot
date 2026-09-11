import json
import random
from pathlib import Path
from tqdm import tqdm
from src.llm.sarvam_client import predict_intent

def main():
    dev_path = Path("data/processed/dev.jsonl")
    examples = []
    with dev_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            examples.append(json.loads(line))
            
    random.seed(42)
    random.shuffle(examples)
    test_cases = examples[:150]
    
    prompt_template = Path("src/llm/prompts/sarvam_intent_v1.txt").read_text(encoding="utf-8")
    
    results = []
    
    # We will use the cache if it exists, otherwise generate
    cache_path = Path("evaluation/dev_intent_predictions.jsonl")
    cache = {}
    if cache_path.exists():
        with cache_path.open("r") as f:
            for line in f:
                d = json.loads(line)
                cache[d["example_id"]] = d
                
    with cache_path.open("a", encoding="utf-8") as f:
        for ex in tqdm(test_cases):
            eid = ex.get("example_id", ex.get("conversation_id"))
            
            if eid in cache:
                res = cache[eid]
            else:
                text_to_classify = f"CUSTOMER: {ex.get('messages', [{}])[0].get('text_clean', '')}"
                full_prompt = prompt_template + f"\n\nMessage to classify:\n{text_to_classify}\n"
                
                try:
                    pred = predict_intent(full_prompt)
                    res = {
                        "example_id": eid,
                        "predicted": pred.get("primary_intent"),
                        "confidence": pred.get("confidence", 0.0)
                    }
                    f.write(json.dumps(res) + "\n")
                    f.flush()
                except Exception as e:
                    print(f"Error on {eid}: {e}")
                    continue
                    
            results.append(res)
            
    low_conf = [r for r in results if r["confidence"] < 0.6]
    high_conf = [r for r in results if r["confidence"] >= 0.6]
    
    print("\n--- CONFIDENCE THRESHOLD ANALYSIS ---")
    print(f"Total Evaluated: {len(results)}")
    print(f"Count < 0.60: {len(low_conf)}")
    print(f"Count >= 0.60: {len(high_conf)}")
    print("Error rate cannot be calculated on DEV because DEV lacks golden intent labels. 0.60 remains a heuristic.")

if __name__ == "__main__":
    main()
