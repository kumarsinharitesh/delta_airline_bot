import csv
import json
from pathlib import Path
from tqdm import tqdm
from src.llm.sarvam_client import predict_intent
import time

def main():
    GOLD_FILE = Path("evaluation/escalation_gold.csv")
    CACHE_FILE = Path("evaluation/dev_intent_predictions.jsonl")
    
    # load cache
    cache = {}
    if CACHE_FILE.exists():
        with CACHE_FILE.open("r", encoding="utf-8") as f:
            for line in f:
                d = json.loads(line)
                cache[d["example_id"]] = d
                
    prompt_template = Path("src/llm/prompts/sarvam_intent_v1.txt").read_text(encoding="utf-8")
    
    with GOLD_FILE.open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
        
    with CACHE_FILE.open("a", encoding="utf-8") as f:
        for row in tqdm(rows):
            eid = row["example_id"]
            if eid in cache: continue
            
            msg = row["customer_message"]
            full_prompt = prompt_template + f"\n\nMessage to classify:\nCUSTOMER: {msg}\n"
            
            for _ in range(3):
                try:
                    res = predict_intent(full_prompt)
                    d = {
                        "example_id": eid,
                        "predicted": res.get("primary_intent"),
                        "confidence": res.get("confidence", 0.0)
                    }
                    f.write(json.dumps(d) + "\n")
                    f.flush()
                    break
                except Exception as e:
                    time.sleep(2)

if __name__ == "__main__":
    main()
