import json
import csv
import pickle
import logging
from pathlib import Path
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer

from src.retrieval.utils import get_pseudo_intent, get_golden_ids

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-10s %(message)s")
log = logging.getLogger(__name__)

TRAIN_FILE = Path("data/processed/train.jsonl")
OUT_INDEX_FILE = Path("evaluation/retrieval_index.pkl")

def index_corpus():
    golden_cids, golden_mids = get_golden_ids()
    
    corpus_cids = set()
    corpus_mids = set()
    
    units = []
    
    with TRAIN_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            conv = json.loads(line)
            cid = str(conv["conversation_id"])
            corpus_cids.add(cid)
            
            resolution_status = conv.get("resolution_status", "UNKNOWN")
            
            msgs = sorted(conv["messages"], key=lambda m: (m.get("timestamp") or "0000", m["message_id"]))
            
            # Find customer -> support pairs
            for i, msg in enumerate(msgs):
                if msg["role"] == "CUSTOMER":
                    mid = str(msg["message_id"])
                    corpus_mids.add(mid)
                    
                    # Look for subsequent support response
                    support_resp = None
                    for j in range(i+1, len(msgs)):
                        if msgs[j]["role"] == "SUPPORT":
                            text = msgs[j].get("text_clean") or msgs[j].get("text_original", "")
                            if text.strip():
                                support_resp = text
                                break
                                
                    if support_resp:
                        # We have a valid pair!
                        cust_text = msg.get("text_clean") or msg.get("text_original", "")
                        pseudo_intent = get_pseudo_intent(cust_text)
                        
                        # Generate context
                        prior = msgs[max(0, i-2):i]
                        parts = []
                        for pm in prior:
                            pm_text = pm.get("text_clean") or pm.get("text_original", "")
                            parts.append(f"{pm['role']}: {pm_text}")
                        context_str = " | ".join(parts)
                        
                        full_search_text = context_str + " | CUSTOMER: " + cust_text if context_str else "CUSTOMER: " + cust_text
                        
                        units.append({
                            "example_id": f"{cid}_{mid}",
                            "conversation_id": cid,
                            "customer_message_id": mid,
                            "customer_text": cust_text,
                            "context": context_str,
                            "search_text": full_search_text,
                            "support_response": support_resp,
                            "intent": pseudo_intent,
                            "resolution_status": resolution_status,
                            "timestamp": msg.get("timestamp", "")
                        })

    # Explicit Golden Leakage Check
    overlap_cids = golden_cids.intersection(corpus_cids)
    overlap_mids = golden_mids.intersection(corpus_mids)
    
    log.info(f"Total Train Conversations: {len(corpus_cids)}")
    log.info(f"Total Train Customer Messages: {len(corpus_mids)}")
    log.info(f"Golden Conversation Overlap: {len(overlap_cids)}")
    log.info(f"Golden Message Overlap: {len(overlap_mids)}")
    
    if overlap_cids or overlap_mids:
        log.warning("Found overlap with Golden Set! Filtering out overlapped examples...")
        units = [u for u in units if u["conversation_id"] not in golden_cids and u["customer_message_id"] not in golden_mids]
    
    log.info(f"Valid retrieval units extracted: {len(units)}")
    
    # Check resolutions
    res_dist = Counter(u["resolution_status"] for u in units)
    log.info(f"Resolution distribution: {dict(res_dist)}")
    
    # Build TF-IDF
    log.info("Building TF-IDF Index...")
    texts = [u["search_text"] for u in units]
    vectorizer = TfidfVectorizer(max_features=10000, stop_words="english", ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform(texts)
    
    index_data = {
        "vectorizer": vectorizer,
        "tfidf_matrix": tfidf_matrix,
        "units": units
    }
    
    with OUT_INDEX_FILE.open("wb") as f:
        pickle.dump(index_data, f)
        
    log.info(f"Saved retrieval index to {OUT_INDEX_FILE}")

if __name__ == "__main__":
    index_corpus()
