import json
import random
import logging
from pathlib import Path
import numpy as np
from collections import Counter

from src.retrieval.retrieve import retrieve
from src.retrieval.utils import get_pseudo_intent, get_golden_ids

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-10s %(message)s")
log = logging.getLogger(__name__)

DEV_FILE = Path("data/processed/dev.jsonl")
OUT_RESULTS = Path("evaluation/retrieval_results.json")
OUT_EXAMPLES = Path("evaluation/retrieval_examples.jsonl")
OUT_AUDIT = Path("evaluation/retrieval_qualitative_audit.md")

def evaluate_retrieval():
    golden_cids, golden_mids = get_golden_ids()
    
    queries = []
    excluded = 0
    
    # 1. Parse DEV queries
    with DEV_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            conv = json.loads(line)
            cid = str(conv["conversation_id"])
            if cid in golden_cids:
                continue
                
            msgs = sorted(conv["messages"], key=lambda m: (m.get("timestamp") or "0000", m["message_id"]))
            
            for i, msg in enumerate(msgs):
                if msg["role"] == "CUSTOMER":
                    mid = str(msg["message_id"])
                    if mid in golden_mids:
                        continue
                        
                    cust_text = msg.get("text_clean") or msg.get("text_original", "")
                    pseudo_intent = get_pseudo_intent(cust_text)
                    
                    if pseudo_intent == "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT":
                        excluded += 1
                        continue
                        
                    queries.append({
                        "conversation_id": cid,
                        "customer_message_id": mid,
                        "customer_text": cust_text,
                        "intent": pseudo_intent
                    })
                    
    log.info(f"Total valid DEV queries extracted: {len(queries)}")
    log.info(f"Excluded due to no intent: {excluded}")
    log.info(f"Pseudo-intent coverage: {len(queries)/(len(queries)+excluded)*100:.1f}%")
    
    # 2. Execute Retrieval
    same_intent_1 = 0
    same_intent_3 = 0
    same_intent_5 = 0
    
    top5_has_response = []
    top5_res_status = []
    top5_sims = []
    top1_sims = []
    top5_intent_match_rates = []
    
    all_outputs = []
    
    for idx, q in enumerate(queries):
        if idx % 100 == 0:
            log.info(f"Processed {idx}/{len(queries)}")
            
        ret = retrieve(q["customer_text"], intent=q["intent"], top_k=5)
        results = ret["results"]
        
        q_intent = q["intent"]
        result_intents = [r["intent"] for r in results]
        
        if len(result_intents) >= 1 and result_intents[0] == q_intent:
            same_intent_1 += 1
        if q_intent in result_intents[:3]:
            same_intent_3 += 1
        if q_intent in result_intents[:5]:
            same_intent_5 += 1
            
        has_resp = sum(1 for r in results if r["support_response"].strip() != "[HISTORICAL_SUPPORT_RESPONSE]")
        top5_has_response.append(has_resp / len(results) if results else 0)
        
        res_statuses = [r["resolution_status"] for r in results]
        top5_res_status.extend(res_statuses)
        
        sims = [r["semantic_similarity"] for r in results]
        if sims:
            top1_sims.append(sims[0])
            top5_sims.extend(sims)
            
        matches = sum(1 for ri in result_intents if ri == q_intent)
        top5_intent_match_rates.append(matches / len(results) if results else 0)
        
        all_outputs.append({
            "query": q,
            "retrieval": results
        })
        
    # 3. Compute Metrics
    n = len(queries)
    metrics = {
        "Same-Intent@1": same_intent_1 / n,
        "Same-Intent@3": same_intent_3 / n,
        "Same-Intent@5": same_intent_5 / n,
        "Support-Response-Availability": float(np.mean(top5_has_response)),
        "Top1-Mean-Similarity": float(np.mean(top1_sims)),
        "Top5-Mean-Similarity": float(np.mean(top5_sims)),
        "Intent-Match-Rate-Top5": float(np.mean(top5_intent_match_rates)),
        "Resolution-Status-Dist": dict(Counter(top5_res_status)),
        "Total-DEV-Examples": n,
        "Excluded-No-Intent": excluded,
        "Pseudo-Intent-Coverage": n / (n + excluded)
    }
    
    with OUT_RESULTS.open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
        
    with OUT_EXAMPLES.open("w", encoding="utf-8") as f:
        for out in all_outputs:
            f.write(json.dumps(out) + "\n")
            
    # 4. Generate Qualitative Audit
    generate_audit(all_outputs)
    
    log.info(f"Saved evaluation metrics to {OUT_RESULTS}")

def generate_audit(all_outputs):
    # Try to pick 1 from each intent
    by_intent = {}
    for out in all_outputs:
        by_intent.setdefault(out["query"]["intent"], []).append(out)
        
    audit_samples = []
    # Try getting 10 diverse ones
    intents_to_sample = list(by_intent.keys())
    random.seed(42)
    random.shuffle(intents_to_sample)
    
    for intent in intents_to_sample:
        if len(audit_samples) >= 10:
            break
        samp = random.choice(by_intent[intent])
        audit_samples.append(samp)
        
    with OUT_AUDIT.open("w", encoding="utf-8") as f:
        f.write("# Retrieval Qualitative Audit\n\n")
        f.write("10 diverse DEV examples and their top retrieved historical cases.\n\n")
        for i, samp in enumerate(audit_samples, 1):
            q = samp["query"]
            res = samp["retrieval"][0] if samp["retrieval"] else None
            
            f.write(f"## Example {i}: {q['intent']}\n\n")
            f.write(f"**Query**: {q['customer_text']}\n\n")
            if not res:
                f.write("**No retrieval results**\n\n")
                continue
                
            f.write(f"**Top Retrieved Intent**: {res['intent']} (Sim: {res['semantic_similarity']:.2f})\n\n")
            f.write(f"**Retrieved Customer Text**: {res['customer_text']}\n\n")
            f.write(f"**Retrieved Support Response**: {res['support_response']}\n\n")
            f.write(f"**Resolution**: {res['resolution_status']}\n\n")
            f.write(f"**Why it is relevant / Potential risk**: \n\n")
            f.write("*Requires manual review*\n\n")
            f.write("---\n\n")

if __name__ == "__main__":
    evaluate_retrieval()
