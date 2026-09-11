import argparse
import csv
import json
import logging
import sys
from pathlib import Path
from collections import Counter
import numpy as np

try:
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
except ImportError:
    print("Please install scikit-learn: pip install scikit-learn")
    sys.exit(1)

from src.llm.sarvam_client import predict_intent

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-10s %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)

GOLDEN_FILE = Path("evaluation/golden_set.csv")
CACHE_FILE = Path("evaluation/sarvam_predictions.jsonl")
PROMPT_FILE = Path("src/llm/prompts/sarvam_intent_v1.txt")
PHASE4_RESULTS = Path("evaluation/baseline_results.json")

OUT_DIR = Path("evaluation")
RESULTS_FILE = OUT_DIR / "sarvam_results.json"
PER_INTENT_FILE = OUT_DIR / "sarvam_per_intent.csv"
CONFUSION_FILE = OUT_DIR / "sarvam_confusion_matrix.csv"
COMPARISON_FILE = OUT_DIR / "sarvam_comparison.csv"
REPORT_FILE = OUT_DIR / "phase5_report.md"

VALID_INTENTS = [
    "REFUND_OR_COMPENSATION",
    "PAYMENT_OR_CHARGE_DISPUTE",
    "SPECIAL_ASSISTANCE",
    "CANCEL_OR_CHANGE_FLIGHT",
    "BAGGAGE_ISSUE",
    "CHECKIN_OR_BOARDING",
    "SEAT_OR_UPGRADE",
    "ACCOUNT_ACCESS",
    "SKYMILES_OR_LOYALTY",
    "SCHEDULE_OR_BOOKING_INQUIRY",
    "FLIGHT_STATUS_OR_DELAY",
    "COMPLAINT_OR_FEEDBACK",
    "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT"
]

def load_golden_set():
    rows = []
    with GOLDEN_FILE.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def load_cache():
    cache = {}
    if CACHE_FILE.exists():
        with CACHE_FILE.open("r", encoding="utf-8") as f:
            for line in f:
                if not line.strip(): continue
                rec = json.loads(line)
                key = f"{rec['golden_id']}_{rec['input_mode']}"
                cache[key] = rec
    return cache

def save_to_cache(record):
    with CACHE_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

def get_prediction(row, input_mode, prompt_template, mode, cache):
    key = f"{row['golden_id']}_{input_mode}"
    if key in cache:
        return cache[key]
        
    if mode == "replay":
        log.warning(f"Cache miss for {key} in replay mode. Returning ERROR fallback.")
        return {
            "golden_id": row["golden_id"],
            "customer_message_id": row["customer_message_id"],
            "primary_gold_intent": row["primary_intent"],
            "predicted_primary_intent": "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT",
            "predicted_secondary_intent": None,
            "is_multi_intent": False,
            "confidence": 0.0,
            "reason": "Cache miss in replay mode.",
            "model": "unknown",
            "input_mode": input_mode,
            "raw_response": "",
            "error_status": True
        }
        
    # Construct prompt
    if input_mode == "message":
        text_to_classify = f"CUSTOMER: {row['customer_text']}"
    else:
        ctx = row["context"].strip()
        if ctx:
            text_to_classify = f"{ctx} | CUSTOMER: {row['customer_text']}"
        else:
            text_to_classify = f"CUSTOMER: {row['customer_text']}"
            
    full_prompt = prompt_template + f"\n\nMessage to classify:\n{text_to_classify}\n"
    
    # API Call
    log.info(f"API Call: {key}")
    res = predict_intent(full_prompt)
    
    error_status = False
    if res.get("reason") == "Sarvam classification failed validation.":
        error_status = True
        
    record = {
        "golden_id": row["golden_id"],
        "customer_message_id": row["customer_message_id"],
        "primary_gold_intent": row["primary_intent"],
        "predicted_primary_intent": res["primary_intent"],
        "predicted_secondary_intent": res.get("secondary_intent"),
        "is_multi_intent": res.get("is_multi_intent", False),
        "confidence": res.get("confidence", 0.0),
        "reason": res.get("reason", ""),
        "model": res.get("_actual_model", "sarvam-105b"),
        "input_mode": input_mode,
        "raw_response": res.get("_raw_response", ""),
        "error_status": error_status
    }
    
    save_to_cache(record)
    cache[key] = record
    return record

def evaluate_predictions(y_true, y_pred, evaluated_labels):
    acc = accuracy_score(y_true, y_pred)
    prec, rec, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=evaluated_labels, zero_division=0
    )
    macro_f1 = np.mean(f1)
    weighted_f1 = np.average(f1, weights=support)
    
    per_intent = {}
    for i, label in enumerate(evaluated_labels):
        per_intent[label] = {
            "Precision": float(prec[i]),
            "Recall": float(rec[i]),
            "F1": float(f1[i]),
            "Support": int(support[i])
        }
    conf_mat = confusion_matrix(y_true, y_pred, labels=evaluated_labels)
    return {
        "Accuracy": float(acc),
        "Macro-F1": float(macro_f1),
        "Weighted-F1": float(weighted_f1),
        "per_intent": per_intent,
        "confusion_matrix": conf_mat.tolist()
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["live", "replay", "smoke"], required=True)
    args = parser.parse_args()
    
    rows = load_golden_set()
    cache = load_cache()
    prompt_template = PROMPT_FILE.read_text(encoding="utf-8")
    
    if args.mode == "smoke":
        log.info("Running SMOKE TEST on first 2 golden examples...")
        rows = rows[:2]
        
    predictions = []
    success_count = 0
    error_count = 0
    actual_model_seen = "unknown"
    
    for row in rows:
        for imode in ["message", "context"]:
            rec = get_prediction(row, imode, prompt_template, args.mode, cache)
            predictions.append(rec)
            if rec.get("error_status"):
                error_count += 1
            else:
                success_count += 1
            if rec.get("model") != "unknown":
                actual_model_seen = rec.get("model")
                
    log.info(f"Finished {args.mode} evaluation. Success: {success_count}, Error: {error_count}")
    
    if args.mode == "smoke":
        print("\n=== SMOKE TEST RESULTS ===")
        print(f"Total API/Cache Calls: {len(predictions)}")
        print(f"Successful Parse: {success_count}")
        print(f"Errors: {error_count}")
        print(f"Model Recorded: {actual_model_seen}")
        for p in predictions:
            print(f"- {p['golden_id']} [{p['input_mode']}] -> {p['predicted_primary_intent']} (multi={p['is_multi_intent']}, conf={p['confidence']})")
        sys.exit(0)
        
    # --- Metrics Computation ---
    evaluated_labels = [i for i in VALID_INTENTS if i != "ACCOUNT_ACCESS"]
    
    y_true = [r["primary_intent"] for r in rows]
    y_pred_msg = [p["predicted_primary_intent"] for p in predictions if p["input_mode"] == "message"]
    y_pred_ctx = [p["predicted_primary_intent"] for p in predictions if p["input_mode"] == "context"]
    
    res_msg = evaluate_predictions(y_true, y_pred_msg, evaluated_labels)
    res_ctx = evaluate_predictions(y_true, y_pred_ctx, evaluated_labels)
    
    all_results = {
        "Sarvam_Message": res_msg,
        "Sarvam_Context": res_ctx
    }
    with RESULTS_FILE.open("w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)
        
    # Per intent
    with PER_INTENT_FILE.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Intent", "Golden Support", "Precision", "Recall", "F1", "Status"])
        for intent in VALID_INTENTS:
            if intent == "ACCOUNT_ACCESS":
                writer.writerow([intent, 0, "—", "—", "—", "Not evaluated"])
            else:
                m = res_msg["per_intent"][intent]
                writer.writerow([intent, m["Support"], f"{m['Precision']:.4f}", f"{m['Recall']:.4f}", f"{m['F1']:.4f}", "Evaluated"])

    # Confusion Matrix
    with CONFUSION_FILE.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["True \\ Pred"] + evaluated_labels)
        for i, row_vals in enumerate(res_msg["confusion_matrix"]):
            writer.writerow([evaluated_labels[i]] + row_vals)
            
    # Load Phase 4 results
    phase4 = {}
    if PHASE4_RESULTS.exists():
        phase4 = json.loads(PHASE4_RESULTS.read_text(encoding="utf-8"))
        
    # Comparison table
    with COMPARISON_FILE.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Model", "Input", "Accuracy", "Macro-F1", "Weighted-F1"])
        if phase4:
            writer.writerow(["Majority pseudo-label", "—", f"{phase4['Majority']['Accuracy']:.4f}", f"{phase4['Majority']['Macro-F1']:.4f}", f"{phase4['Majority']['Weighted-F1']:.4f}"])
            writer.writerow(["TF-IDF + LR", "Current message", f"{phase4['TFIDF_LR_Message']['Accuracy']:.4f}", f"{phase4['TFIDF_LR_Message']['Macro-F1']:.4f}", f"{phase4['TFIDF_LR_Message']['Weighted-F1']:.4f}"])
            writer.writerow(["TF-IDF + LR", "+ Context", f"{phase4['TFIDF_LR_Context']['Accuracy']:.4f}", f"{phase4['TFIDF_LR_Context']['Macro-F1']:.4f}", f"{phase4['TFIDF_LR_Context']['Weighted-F1']:.4f}"])
        writer.writerow(["Sarvam", "Current message", f"{res_msg['Accuracy']:.4f}", f"{res_msg['Macro-F1']:.4f}", f"{res_msg['Weighted-F1']:.4f}"])
        writer.writerow(["Sarvam", "+ Context", f"{res_ctx['Accuracy']:.4f}", f"{res_ctx['Macro-F1']:.4f}", f"{res_ctx['Weighted-F1']:.4f}"])

    print(f"Evaluation complete. Extracted metrics. Actual Model: {actual_model_seen}")

if __name__ == "__main__":
    main()
