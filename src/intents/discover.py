"""
Phase 3, Step 1 — Intent Discovery (Train Split Only)
=====================================================

Performs frequency analysis, keyword analysis, and TF-IDF n-gram exploration
on customer messages from the TRAIN split to inform the intent taxonomy.

Uses NO held-out dev/test data.
Does NOT produce intent labels.
Output is used by a human to define the taxonomy.

Usage:
    python -m src.intents.discover
"""

import json
import re
import sys
import logging
import csv
from pathlib import Path
from collections import Counter
from typing import List, Dict, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-10s %(message)s",
                    datefmt="%H:%M:%S")
log = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────
TRAIN_FILE  = Path("data/processed/train.jsonl")
OUT_DIR     = Path("data")
OUT_ANALYSIS = OUT_DIR / "intent_discovery.txt"

# Stopwords for TF-IDF cleaning
STOPWORDS = {
    "the","a","an","in","on","at","to","for","of","and","or","but","is","was",
    "are","be","been","it","i","my","me","we","us","you","your","he","she","they",
    "them","their","this","that","with","from","as","by","have","has","had","do",
    "did","not","no","so","if","its","our","will","can","just","would","could",
    "should","there","about","which","than","then","when","what","how","who",
    "all","also","more","some","very","please","hi","hello","hey","dear","amp",
    "delta","dlts","dlt","http","https","co","rt","t","s","re","ve","m","ll",
    "@delta","@dlts","0","1","2","3","4","5","6","7","8","9",
}

def load_train_customer_texts(path: Path) -> List[Dict]:
    """Load all customer messages from train.jsonl."""
    records = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            conv = json.loads(line)
            for msg in conv["messages"]:
                if msg["role"] == "CUSTOMER":
                    records.append({
                        "conversation_id":   conv["conversation_id"],
                        "message_id":        msg["message_id"],
                        "text":              msg.get("text_clean") or msg.get("text_original", ""),
                        "text_original":     msg.get("text_original", ""),
                        "resolution_status": conv["resolution_status"],
                    })
    return records


def clean_text(text: str) -> str:
    """Minimal cleaning: lowercase, remove @mentions, URLs, punctuation."""
    text = text.lower()
    text = re.sub(r"@\w+", " ", text)           # remove @mentions
    text = re.sub(r"https?://\S+", " ", text)   # remove URLs
    text = re.sub(r"[^a-z0-9\s]", " ", text)    # remove punctuation
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> List[str]:
    """Tokenize and remove stopwords."""
    return [w for w in text.split() if w not in STOPWORDS and len(w) > 2]


def ngrams(tokens: List[str], n: int) -> List[str]:
    return [" ".join(tokens[i:i+n]) for i in range(len(tokens)-n+1)]


def compute_tfidf_top(docs: List[List[str]], top_n: int = 50) -> List[Tuple[str, float]]:
    """Simple TF-IDF over the token lists."""
    import math
    N = len(docs)
    # DF
    df: Counter = Counter()
    for doc in docs:
        for term in set(doc):
            df[term] += 1
    # TF-IDF scores: sum over all docs
    tfidf: Counter = Counter()
    for doc in docs:
        tf: Counter = Counter(doc)
        for term, count in tf.items():
            idf = math.log((N + 1) / (df[term] + 1)) + 1
            tfidf[term] += (count / len(doc) if doc else 0) * idf
    return tfidf.most_common(top_n)


# ── Keyword patterns for known domains ────────────────────────────────────────
# Used to give the human analyst a head start — NOT definitive intent labels

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


def keyword_match_counts(records: List[Dict]) -> Dict[str, int]:
    counts = {k: 0 for k in KEYWORD_PATTERNS}
    for rec in records:
        text = rec["text"].lower()
        for label, pattern in KEYWORD_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                counts[label] += 1
    return counts


def sample_by_pattern(records: List[Dict], pattern: str, n: int = 5) -> List[str]:
    matched = [r["text_original"] for r in records
               if re.search(pattern, r["text"].lower(), re.IGNORECASE)]
    import random
    rng = random.Random(42)
    return rng.sample(matched, min(n, len(matched)))


def main() -> None:
    if not TRAIN_FILE.exists():
        log.error("Train file not found: %s", TRAIN_FILE)
        sys.exit(1)

    log.info("Loading train customer messages ...")
    records = load_train_customer_texts(TRAIN_FILE)
    log.info("Total customer messages in train: %d", len(records))

    # Clean and tokenize
    log.info("Cleaning and tokenizing ...")
    for r in records:
        r["clean"] = clean_text(r["text"])
        r["tokens"] = tokenize(r["clean"])

    docs = [r["tokens"] for r in records if r["tokens"]]

    # ── Unigram frequency ────────────────────────────────────────────────
    unigram_counts: Counter = Counter()
    bigram_counts:  Counter = Counter()
    trigram_counts: Counter = Counter()
    for r in records:
        toks = r["tokens"]
        unigram_counts.update(toks)
        bigram_counts.update(ngrams(toks, 2))
        trigram_counts.update(ngrams(toks, 3))

    # ── TF-IDF ───────────────────────────────────────────────────────────
    log.info("Computing TF-IDF ...")
    tfidf_top = compute_tfidf_top(docs, top_n=80)

    # ── Keyword pattern counts ────────────────────────────────────────────
    log.info("Running keyword pattern matching ...")
    kw_counts = keyword_match_counts(records)
    total = len(records)

    # ── Write report ─────────────────────────────────────────────────────
    lines = []
    lines.append("=" * 72)
    lines.append("PHASE 3 -- INTENT DISCOVERY REPORT (Train split only)")
    lines.append("=" * 72)
    lines.append("Total customer messages in train split: {:,}".format(total))
    lines.append("")

    lines.append("--- TOP 60 UNIGRAMS (excluding stopwords) ---")
    for w, c in unigram_counts.most_common(60):
        lines.append("  {:30s} {:,}  ({:.1f}%)".format(w, c, c/total*100))
    lines.append("")

    lines.append("--- TOP 60 BIGRAMS ---")
    for bg, c in bigram_counts.most_common(60):
        lines.append("  {:40s} {:,}  ({:.1f}%)".format(bg, c, c/total*100))
    lines.append("")

    lines.append("--- TOP 40 TRIGRAMS ---")
    for tg, c in trigram_counts.most_common(40):
        lines.append("  {:50s} {:,}  ({:.1f}%)".format(tg, c, c/total*100))
    lines.append("")

    lines.append("--- TF-IDF TOP 80 TERMS ---")
    for term, score in tfidf_top:
        lines.append("  {:30s} {:.4f}".format(term, score))
    lines.append("")

    lines.append("--- KEYWORD PATTERN MATCH COUNTS ---")
    lines.append("(Pattern can match same message multiple times; totals > 100% normal)")
    lines.append("{:<30s} {:>8s} {:>8s}".format("Pattern", "Count", "%"))
    for label, cnt in sorted(kw_counts.items(), key=lambda x: -x[1]):
        lines.append("{:<30s} {:>8,} {:>7.1f}%".format(label, cnt, cnt/total*100))
    lines.append("")

    lines.append("--- SAMPLE MESSAGES PER DOMAIN PATTERN ---")
    for label, pattern in KEYWORD_PATTERNS.items():
        samples = sample_by_pattern(records, pattern, n=5)
        lines.append("\n[{}]".format(label))
        for s in samples:
            safe = s[:120].replace("\n", " ").encode("ascii", "replace").decode("ascii")
            lines.append("  >> {}".format(safe))

    report = "\n".join(lines)
    OUT_ANALYSIS.write_text(report, encoding="utf-8")
    log.info("Discovery report written to %s", OUT_ANALYSIS)

    # Print keyword summary to console
    print("\n" + "=" * 60)
    print("KEYWORD PATTERN MATCH SUMMARY (train customer messages)")
    print("=" * 60)
    print("{:<30s} {:>8s} {:>8s}".format("Domain Pattern", "Count", "%"))
    print("-" * 50)
    for label, cnt in sorted(kw_counts.items(), key=lambda x: -x[1]):
        print("{:<30s} {:>8,} {:>7.1f}%".format(label, cnt, cnt/total*100))
    print()
    print("Top 30 bigrams:")
    for bg, c in bigram_counts.most_common(30):
        print("  {:40s} {:,}".format(bg, c))
    print()
    print("Full report: {}".format(OUT_ANALYSIS))


if __name__ == "__main__":
    main()
