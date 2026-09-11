import pickle
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

INDEX_FILE = Path("evaluation/retrieval_index.pkl")

# Global variables to cache the index in memory
_vectorizer = None
_tfidf_matrix = None
_units = None

def _load_index():
    global _vectorizer, _tfidf_matrix, _units
    if _vectorizer is not None:
        return
    with INDEX_FILE.open("rb") as f:
        data = pickle.load(f)
        _vectorizer = data["vectorizer"]
        _tfidf_matrix = data["tfidf_matrix"]
        _units = data["units"]

def retrieve(query_text: str, intent: str = None, top_k: int = 5):
    """
    Retrieve historical examples based on TF-IDF similarity and intent/resolution bonuses.
    """
    _load_index()
    
    # 1. Transform query
    q_vec = _vectorizer.transform([query_text])
    
    # 2. Compute cosine similarity (base score)
    sims = cosine_similarity(q_vec, _tfidf_matrix)[0]
    
    # 3. Calculate final scores with bonuses
    scored_results = []
    for idx, sim in enumerate(sims):
        unit = _units[idx]
        score = sim
        
        # Intent match bonus
        if intent and intent != "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT" and unit["intent"] == intent:
            score += 0.10
            
        # Resolution quality bonus
        res_status = unit.get("resolution_status", "UNKNOWN")
        if res_status == "RESOLVED":
            score += 0.05
        elif res_status == "PARTIALLY_RESOLVED":
            score += 0.02
        elif res_status == "UNRESOLVED":
            score -= 0.05
        elif res_status == "UNKNOWN":
            score -= 0.05
            
        scored_results.append({
            "unit": unit,
            "sim": sim,
            "score": score
        })
        
    # 4. Sort by score
    scored_results.sort(key=lambda x: x["score"], reverse=True)
    
    # 5. Format Top-K
    results = []
    for rank, sr in enumerate(scored_results[:top_k], start=1):
        unit = sr["unit"]
        results.append({
            "rank": rank,
            "example_id": unit["example_id"],
            "conversation_id": unit["conversation_id"],
            "customer_message_id": unit["customer_message_id"],
            "intent": unit["intent"],
            "customer_text": unit["customer_text"],
            "support_response": f"[HISTORICAL_SUPPORT_RESPONSE] {unit['support_response']}",
            "resolution_status": unit["resolution_status"],
            "semantic_similarity": float(sr["sim"]),
            "final_score": float(sr["score"])
        })
        
    return {
        "query": query_text,
        "results": results
    }
