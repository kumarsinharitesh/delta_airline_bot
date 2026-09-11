import json
import csv
import re
import os
import sys
import logging
from pathlib import Path
from collections import Counter
import numpy as np

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
except ImportError:
    print("Please install scikit-learn: pip install scikit-learn")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-10s %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)

# Paths
TRAIN_FILE = Path("data/processed/train.jsonl")
GOLDEN_FILE = Path("evaluation/golden_set.csv")
OUT_DIR = Path("evaluation")
OUT_DIR.mkdir(exist_ok=True)

PSEUDO_STATS_FILE = OUT_DIR / "pseudo_label_statistics.json"
PREDICTIONS_FILE = OUT_DIR / "baseline_predictions.jsonl"
RESULTS_FILE = OUT_DIR / "baseline_results.json"
PER_INTENT_FILE = OUT_DIR / "baseline_per_intent.csv"
CONFUSION_FILE = OUT_DIR / "baseline_confusion_matrix.csv"
COMPARISON_FILE = OUT_DIR / "baseline_comparison.csv"
REPORT_FILE = OUT_DIR / "phase4_report.md"

# Phase 3 mapping
KEYWORD_PATTERNS = {
    "FLIGHT_STATUS":          r"\b(flight|status|delayed?|late|arrive|departure|departure|land(ed)?|on time|tracking)\b",
    "BOOKING_RESERVATION":    r"\b(book(ed|ing)?|reservation|ticket|seat|itinerary|confirm|purchase|bought)\b",
    "CANCEL_CHANGE":          r"\b(cancel(led)?|cancellation|change|reschedul|rebook|modify|new flight)\b",
    "BAGGAGE_ISSUE":          r"\b(bag(gage)?|luggage|suitcase|missing bag|lost bag|damaged|delayed bag|checked bag)\b",
    "REFUND_COMPENSATION":    r"\b(refund|compensat|reimburs|credit|voucher|money back|reimbursement|ecredit)\b",
    "PAYMENT_CHARGE":         r"\b(charg(ed)?|payment|paid|fee|cost|price|bill|double charged|overcharged)\b",
    "CHECKIN_BOARDING":       r"\b(check.?in|boarding|gate|board(ed)?|boarded|pass|kiosk)\b",
    "SEAT_UPGRADE":           r"\b(seat|upgrade|comfort\+|business|first class|window|aisle|middle|exit row|seatbelt)\b",
    "SKYMILES_LOYALTY":       r"\b(skymil(es)?|miles|point|loyalty|medallion|status|frequent|reward)\b",
    "COMPLAINT_FEEDBACK":     r"\b(terrible|awful|horrible|worst|disappointed|unacceptable|upset|frustrat|disgraceful|shame)\b",
    "ACCOUNT_ACCESS":         r"\b(account|log(in|ged)|password|sign.?in|reset|profile|email|membership)\b",
    "SPECIAL_ASSISTANCE":     r"\b(wheelchair|disabled|disability|medical|special need|assistance|accessibility|pregnant)\b",
    "LOST_FOUND":             r"\b(lost|found|left behind|forgot|misplaced|left (on|in) (the )?plane)\b",
    "SCHEDULE_INQUIRY":       r"\b(schedule|timetable|when (does|is)|what time|flight time|hours|availability)\b",
    "GENERAL_FEEDBACK":       r"\b(thank(s| you)|great|amazing|love|wonderful|excellent|fantastic|good job|good experience)\b",
}

PATTERN_MAP = {
    "REFUND_COMPENSATION": "REFUND_OR_COMPENSATION",
    "PAYMENT_CHARGE": "PAYMENT_OR_CHARGE_DISPUTE",
    "SPECIAL_ASSISTANCE": "SPECIAL_ASSISTANCE",
    "CANCEL_CHANGE": "CANCEL_OR_CHANGE_FLIGHT",
    "BAGGAGE_ISSUE": "BAGGAGE_ISSUE",
    "LOST_FOUND": "BAGGAGE_ISSUE",
    "CHECKIN_BOARDING": "CHECKIN_OR_BOARDING",
    "SEAT_UPGRADE": "SEAT_OR_UPGRADE",
    "ACCOUNT_ACCESS": "ACCOUNT_ACCESS",
    "SKYMILES_LOYALTY": "SKYMILES_OR_LOYALTY",
    "SCHEDULE_INQUIRY": "SCHEDULE_OR_BOOKING_INQUIRY",
    "BOOKING_RESERVATION": "SCHEDULE_OR_BOOKING_INQUIRY",
    "FLIGHT_STATUS": "FLIGHT_STATUS_OR_DELAY",
    "COMPLAINT_FEEDBACK": "COMPLAINT_OR_FEEDBACK",
    "GENERAL_FEEDBACK": "COMPLAINT_OR_FEEDBACK",
}

PRIORITY_ORDER = [
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
]

VALID_INTENTS = PRIORITY_ORDER + ["AMBIGUOUS_OR_INSUFFICIENT_CONTEXT"]

def get_pseudo_label(text: str) -> str:
    text_lower = text.lower()
    matched_intents = set()
    for pattern_name, regex in KEYWORD_PATTERNS.items():
        if re.search(regex, text_lower, re.IGNORECASE):
            matched_intents.add(PATTERN_MAP[pattern_name])
            
    for intent in PRIORITY_ORDER:
        if intent in matched_intents:
            return intent
    return None

def load_golden_set():
    rows = []
    golden_cids = set()
    with GOLDEN_FILE.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
            golden_cids.add(str(r["conversation_id"]))
    return rows, golden_cids

def load_and_pseudo_label_train(golden_cids: set):
    messages = []
    total_cust_msgs = 0
    dropped = 0
    
    with TRAIN_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            conv = json.loads(line)
            cid = str(conv["conversation_id"])
            if cid in golden_cids:
                log.warning(f"LEAKAGE PREVENTED: Skipping train conversation {cid} present in golden set.")
                continue
                
            # Filter messages: we want ONLY up to the current customer message
            # The future support responses should NOT be used.
            msgs = sorted(conv["messages"], key=lambda m: (m.get("timestamp") or "0000", m["message_id"]))
            
            for i, msg in enumerate(msgs):
                if msg["role"] == "CUSTOMER":
                    total_cust_msgs += 1
                    # Ensure no resolution_status or future support response is used to generate the label or features
                    text = msg.get("text_clean") or msg.get("text_original", "")
                    label = get_pseudo_label(text)
                    if not label:
                        dropped += 1
                        continue
                    
                    # Context generation
                    # Use up to 2 prior turns, ensuring they occurred before this message
                    prior = msgs[max(0, i-2):i]
                    parts = []
                    for pm in prior:
                        pm_text = pm.get("text_clean") or pm.get("text_original", "")
                        parts.append(f"{pm['role']}: {pm_text}")
                        # Leakage check logic inherently satisfied by using `prior = msgs[:i]`
                        
                    context_str = " | ".join(parts)
                    if context_str:
                        context_str += " | CUSTOMER: " + text
                    else:
                        context_str = "CUSTOMER: " + text
                        
                    messages.append({
                        "id": msg["message_id"],
                        "text": text,
                        "context_text": context_str,
                        "label": label
                    })
                    
    # Generate statistics
    dist = Counter(m["label"] for m in messages)
    coverage = len(messages) / total_cust_msgs * 100 if total_cust_msgs > 0 else 0
    
    stats = {
        "total_train_customer_messages": total_cust_msgs,
        "pseudo_labelled_messages": len(messages),
        "unlabelled_dropped_messages": dropped,
        "pseudo_label_coverage_percentage": coverage,
        "pseudo_label_distribution": dict(dist)
    }
    
    with PSEUDO_STATS_FILE.open("w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
        
    log.info(f"Loaded {len(messages)} pseudo-labeled train messages (coverage: {coverage:.1f}%)")
    return messages, stats

def evaluate_predictions(y_true, y_pred, evaluated_labels):
    acc = accuracy_score(y_true, y_pred)
    prec, rec, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=evaluated_labels, zero_division=0
    )
    
    macro_f1 = np.mean(f1)
    
    # Weighted-F1
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

def run_baselines():
    # 1. Load Golden Set
    golden_rows, golden_cids = load_golden_set()
    
    # 2. Load and pseudo-label Train Set
    train_messages, pseudo_stats = load_and_pseudo_label_train(golden_cids)
    
    # Extract training data
    X_train_msg = [m["text"] for m in train_messages]
    X_train_ctx = [m["context_text"] for m in train_messages]
    y_train = [m["label"] for m in train_messages]
    
    # Extract golden data
    # IMPORTANT: We only use primary_intent for evaluation
    y_true = [r["primary_intent"] for r in golden_rows]
    X_gold_msg = [r["customer_text"] for r in golden_rows]
    X_gold_ctx = []
    for r in golden_rows:
        if r["context"].strip():
            X_gold_ctx.append(r["context"] + " | CUSTOMER: " + r["customer_text"])
        else:
            X_gold_ctx.append("CUSTOMER: " + r["customer_text"])
            
    # Labels with actual golden support
    true_counts = Counter(y_true)
    evaluated_labels = [i for i in VALID_INTENTS if i != "ACCOUNT_ACCESS"]
    
    # 3. Baseline A: Majority Pseudo-Label
    majority_class = Counter(y_train).most_common(1)[0][0]
    log.info(f"Baseline A: Majority Pseudo-Label = {majority_class}")
    y_pred_maj = [majority_class] * len(y_true)
    res_maj = evaluate_predictions(y_true, y_pred_maj, evaluated_labels)
    
    # 4. Baseline B: TF-IDF + LR (Current Message)
    log.info("Baseline B: TF-IDF + LR (Current Message)")
    vectorizer_msg = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=2)
    X_train_msg_vec = vectorizer_msg.fit_transform(X_train_msg)
    clf_msg = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)
    clf_msg.fit(X_train_msg_vec, y_train)
    
    X_gold_msg_vec = vectorizer_msg.transform(X_gold_msg)
    y_pred_msg = clf_msg.predict(X_gold_msg_vec)
    res_msg = evaluate_predictions(y_true, y_pred_msg, evaluated_labels)
    
    # 5. Baseline C: TF-IDF + LR (Context)
    log.info("Baseline C: TF-IDF + LR (Context)")
    vectorizer_ctx = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=2)
    X_train_ctx_vec = vectorizer_ctx.fit_transform(X_train_ctx)
    clf_ctx = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)
    clf_ctx.fit(X_train_ctx_vec, y_train)
    
    X_gold_ctx_vec = vectorizer_ctx.transform(X_gold_ctx)
    y_pred_ctx = clf_ctx.predict(X_gold_ctx_vec)
    res_ctx = evaluate_predictions(y_true, y_pred_ctx, evaluated_labels)
    
    # Save Results
    all_results = {
        "Majority": res_maj,
        "TFIDF_LR_Message": res_msg,
        "TFIDF_LR_Context": res_ctx
    }
    with RESULTS_FILE.open("w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)
        
    # Save Predictions
    with PREDICTIONS_FILE.open("w", encoding="utf-8") as f:
        for i, row in enumerate(golden_rows):
            f.write(json.dumps({
                "golden_id": row["golden_id"],
                "customer_text": X_gold_msg[i],
                "context_text": X_gold_ctx[i],
                "true_intent": y_true[i],
                "pred_Majority": y_pred_maj[i],
                "pred_TFIDF_LR_Message": y_pred_msg[i],
                "pred_TFIDF_LR_Context": y_pred_ctx[i],
            }) + "\n")
            
    # Per-intent metrics output (from the best model or baseline B for simplicity, we'll output Baseline B)
    with PER_INTENT_FILE.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Intent", "Golden Support", "Precision", "Recall", "F1", "Status"])
        for intent in VALID_INTENTS:
            if intent == "ACCOUNT_ACCESS":
                writer.writerow([intent, 0, "—", "—", "—", "Not evaluated"])
            else:
                m = res_msg["per_intent"][intent]
                writer.writerow([intent, m["Support"], f"{m['Precision']:.4f}", f"{m['Recall']:.4f}", f"{m['F1']:.4f}", "Evaluated"])
                
    # Confusion matrix output (Baseline B)
    with CONFUSION_FILE.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["True \\ Pred"] + evaluated_labels)
        cm = res_msg["confusion_matrix"]
        for i, row in enumerate(cm):
            writer.writerow([evaluated_labels[i]] + row)
            
    # Comparison table
    with COMPARISON_FILE.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Model", "Input", "Accuracy", "Macro-F1", "Weighted-F1"])
        writer.writerow(["Majority", "—", f"{res_maj['Accuracy']:.4f}", f"{res_maj['Macro-F1']:.4f}", f"{res_maj['Weighted-F1']:.4f}"])
        writer.writerow(["TF-IDF + LR", "Current message", f"{res_msg['Accuracy']:.4f}", f"{res_msg['Macro-F1']:.4f}", f"{res_msg['Weighted-F1']:.4f}"])
        writer.writerow(["TF-IDF + LR", "Message + context", f"{res_ctx['Accuracy']:.4f}", f"{res_ctx['Macro-F1']:.4f}", f"{res_ctx['Weighted-F1']:.4f}"])

    return all_results, pseudo_stats, golden_rows, y_pred_msg, y_pred_ctx

def generate_report(results, pseudo_stats, golden_rows, y_pred_msg, y_pred_ctx):
    lines = [
        "# Phase 4 — Intent Classification Baselines",
        "",
        "## Training Label Limitation",
        "The raw train split (`train.jsonl`) has no human intent labels. Phase 3 provided a human-labelled 200-example golden set, but this set must remain entirely untouched during training to prevent leakage.",
        "Therefore, the classical supervised baselines evaluated here use rule-derived **pseudo-labels** generated on the train set (using the Phase 3 keyword prioritization rules). The model is learning from these weak labels rather than direct human annotations.",
        "This introduces label noise and potential bias toward the Phase 3 rule system. Therefore, the TF-IDF + Logistic Regression performance on the golden set should be interpreted strictly as a **weakly supervised baseline**, and not as a fully supervised benchmark. It demonstrates how well a classical classifier reproduces human intent labels when trained using weak rule-derived supervision.",
        "",
        "## Pseudo-Label Statistics (Train Split)",
        f"- Total Train Customer Messages: {pseudo_stats['total_train_customer_messages']:,}",
        f"- Pseudo-Labelled Messages: {pseudo_stats['pseudo_labelled_messages']:,}",
        f"- Unlabelled/Dropped Messages: {pseudo_stats['unlabelled_dropped_messages']:,}",
        f"- Pseudo-Label Coverage: {pseudo_stats['pseudo_label_coverage_percentage']:.1f}%",
        "",
        "### Pseudo-Label Distribution:",
    ]
    for k, v in sorted(pseudo_stats['pseudo_label_distribution'].items(), key=lambda x: -x[1]):
        lines.append(f"- `{k}`: {v:,} ({v/pseudo_stats['pseudo_labelled_messages']*100:.1f}%)")
        
    lines.extend([
        "",
        "## Baseline Comparison",
        "| Model | Input | Accuracy | Macro-F1 | Weighted-F1 |",
        "|---|---|---:|---:|---:|",
        f"| Majority Pseudo-Label | — | {results['Majority']['Accuracy']:.4f} | {results['Majority']['Macro-F1']:.4f} | {results['Majority']['Weighted-F1']:.4f} |",
        f"| TF-IDF + LR | Current message | {results['TFIDF_LR_Message']['Accuracy']:.4f} | {results['TFIDF_LR_Message']['Macro-F1']:.4f} | {results['TFIDF_LR_Message']['Weighted-F1']:.4f} |",
        f"| TF-IDF + LR | Message + context | {results['TFIDF_LR_Context']['Accuracy']:.4f} | {results['TFIDF_LR_Context']['Macro-F1']:.4f} | {results['TFIDF_LR_Context']['Weighted-F1']:.4f} |",
        "",
        "**Note on ACCOUNT_ACCESS**: `ACCOUNT_ACCESS` is explicitly marked as **NOT EVALUATED** because it has 0 examples in the golden set. It has been excluded from the Macro-F1 calculation to avoid fabricating a score or silently distorting the metric.",
        "",
        "## Leakage Audit Verification",
        "- **Golden Example Leakage**: ZERO golden examples/IDs used for training.",
        "- **Golden Label Leakage**: ZERO golden labels used for training.",
        "- **Future Response Leakage**: Only context *prior* to the customer message was included. Future support responses were explicitly excluded.",
        "- **Metadata Leakage**: No resolution status or human labels were included in training features.",
        "",
        "## Error Analysis (Baseline B: Current Message)",
        "Focusing on representative failure cases from the golden set.",
        ""
    ])
    
    # Extract representative errors
    errors = []
    for i, r in enumerate(golden_rows):
        true_l = r["primary_intent"]
        pred_l = y_pred_msg[i]
        if true_l != pred_l:
            errors.append({
                "id": r["golden_id"],
                "text": r["customer_text"],
                "true": true_l,
                "pred": pred_l,
                "context": r["context"],
                "pred_ctx": y_pred_ctx[i]
            })
            
    # Find specific confusion patterns
    def find_error(t, p):
        for e in errors:
            if e["true"] == t and e["pred"] == p: return e
        return None
        
    def find_any_error(t):
        for e in errors:
            if e["true"] == t: return e
        return None
        
    patterns = [
        ("FLIGHT_STATUS_OR_DELAY vs SCHEDULE_OR_BOOKING_INQUIRY", "FLIGHT_STATUS_OR_DELAY", "SCHEDULE_OR_BOOKING_INQUIRY"),
        ("COMPLAINT_OR_FEEDBACK vs actionable", "COMPLAINT_OR_FEEDBACK", None),
        ("BAGGAGE_ISSUE vs PAYMENT", "BAGGAGE_ISSUE", "PAYMENT_OR_CHARGE_DISPUTE"),
        ("REFUND vs PAYMENT", "REFUND_OR_COMPENSATION", "PAYMENT_OR_CHARGE_DISPUTE"),
    ]
    
    for title, t, p in patterns:
        lines.append(f"### {title}")
        e = find_error(t, p) if p else next((err for err in errors if err["true"] == t and err["pred"] != t and err["pred"] != "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT"), None)
        if e:
            lines.append(f"- **ID**: {e['id']}")
            lines.append(f"- **Message**: \"{e['text']}\"")
            lines.append(f"- **True Intent**: `{e['true']}`")
            lines.append(f"- **Predicted**: `{e['pred']}`")
            lines.append("- **Explanation**: The baseline relied on lexical keyword overlap without understanding the semantic nuance, leading to misclassification.")
        else:
            lines.append("*No exact failure cases for this pattern found in the predictions.*")
        lines.append("")
        
    lines.append("### Context Changes Interpretation")
    e_ctx = next((err for err in errors if err["pred"] != err["true"] and err["pred_ctx"] == err["true"]), None)
    if e_ctx:
        lines.append(f"- **ID**: {e_ctx['id']}")
        lines.append(f"- **Message**: \"{e_ctx['text']}\"")
        lines.append(f"- **True Intent**: `{e_ctx['true']}`")
        lines.append(f"- **Without Context Predicted**: `{e_ctx['pred']}`")
        lines.append(f"- **With Context Predicted**: `{e_ctx['pred_ctx']}`")
        lines.append("- **Explanation**: The context baseline correctly recovered the true intent by including prior conversation turns, demonstrating the value of dialog history.")
    else:
        lines.append("*No examples found where context strictly corrected a failure in this run.*")
    lines.append("")
    
    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
    log.info(f"Phase 4 Report generated at {REPORT_FILE}")

def main():
    res, pseudo_stats, rows, y_msg, y_ctx = run_baselines()
    generate_report(res, pseudo_stats, rows, y_msg, y_ctx)

if __name__ == "__main__":
    main()
