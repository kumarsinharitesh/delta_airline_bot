"""
Phase 3, Step 2 — Golden Set Sampling
======================================

Samples ~200 examples from dev + test splits (NEVER from train) for the
hand-labelled golden evaluation set.

Sampling strategy:
  - Stratified across 5 resolution_status groups (RESOLVED, PARTIALLY_RESOLVED,
    REDIRECTED, UNRESOLVED, UNKNOWN) to ensure coverage of diverse conversation
    outcomes (proxy for diverse support scenarios)
  - At most ONE example per conversation (strict) to avoid correlation
  - Preference for root-turn customer messages (conversation openers) to capture
    intent at its clearest
  - Deliberately includes some multi-turn examples (turns 2+) for robustness
  - Random seed 42 for full reproducibility
  - Source: dev + test examples only

Does NOT assign intent labels. Labels are assigned separately by annotation.

Usage:
    python -m src.intents.sample_golden
"""

import json
import csv
import random
import sys
import logging
from pathlib import Path
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-10s %(message)s",
                    datefmt="%H:%M:%S")
log = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────
DEV_FILE   = Path("data/processed/dev.jsonl")
TEST_FILE  = Path("data/processed/test.jsonl")
TRAIN_FILE = Path("data/processed/train.jsonl")
OUT_UNLABELED = Path("data/golden_unlabeled.csv")

RANDOM_SEED    = 42
TARGET_N       = 200
MAX_PER_CONV   = 1      # at most 1 example per conversation

# Resolution status strata and target counts (proportional + oversampling rarer ones)
STRATA_TARGETS = {
    "UNKNOWN":            70,    # largest group (~57%) — proportionally reduced
    "REDIRECTED":         55,    # second largest (~27%)
    "RESOLVED":           25,    # important for quality — 7.8% → slightly over-represented
    "UNRESOLVED":         25,    # important negative case
    "PARTIALLY_RESOLVED": 25,    # small group — over-represented for coverage
}
# Total target = 200


def load_conversations(path: Path) -> List[Dict]:
    convs = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                convs.append(json.loads(line))
    return convs


def get_train_conversation_ids(path: Path) -> set:
    """Return set of all train conversation_ids for leakage check."""
    cids = set()
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                c = json.loads(line)
                cids.add(c["conversation_id"])
    return cids


def get_previous_context(conv: Dict, target_msg_id: str) -> str:
    """
    Build the previous context string for a given customer message.
    Includes all messages that appear BEFORE this message (chronologically).
    Max 2 prior turns shown.
    """
    msgs = sorted(
        conv["messages"],
        key=lambda m: (m.get("timestamp") or "0000", m["message_id"]),
    )
    target_idx = next((i for i, m in enumerate(msgs) if m["message_id"] == target_msg_id), None)
    if target_idx is None or target_idx == 0:
        return ""
    prior = msgs[max(0, target_idx - 2):target_idx]
    parts = []
    for m in prior:
        role = m["role"]
        text = m.get("text_original", "")[:200].replace("\n", " ")
        text_safe = text.encode("ascii", "replace").decode("ascii")
        parts.append("[{}]: {}".format(role, text_safe))
    return " | ".join(parts)


def sample_from_conversations(
    conversations: List[Dict],
    n: int,
    resolution_filter: str,
    rng: random.Random,
    used_conv_ids: set,
) -> List[Dict]:
    """
    Sample up to n examples from conversations with the given resolution_status.
    At most MAX_PER_CONV example per conversation.
    Prefers first customer turn (turn_index=0); falls back to later turns.
    """
    candidates = []

    for conv in conversations:
        cid = conv["conversation_id"]
        if conv["resolution_status"] != resolution_filter:
            continue
        if cid in used_conv_ids:
            continue
        if not conv.get("is_usable", False):
            continue

        msgs = sorted(
            conv["messages"],
            key=lambda m: (m.get("timestamp") or "0000", m["message_id"]),
        )
        customer_msgs = [m for m in msgs if m["role"] == "CUSTOMER"]
        if not customer_msgs:
            continue

        # Prefer the first customer message; also collect non-first for pool
        first = customer_msgs[0]
        text = first.get("text_original", "").strip()
        # Filter out very short or empty texts and pure @mention texts
        import re
        clean = re.sub(r"@\w+", "", text).strip()
        if len(clean) < 10:
            # Try next customer message
            first = None
            for cm in customer_msgs[1:]:
                clean2 = re.sub(r"@\w+", "", cm.get("text_original", "")).strip()
                if len(clean2) >= 10:
                    first = cm
                    break
            if first is None:
                continue
            text = first.get("text_original", "").strip()

        ctx = get_previous_context(conv, first["message_id"])
        candidates.append({
            "conversation_id":     cid,
            "customer_message_id": first["message_id"],
            "customer_text":       text[:500],
            "previous_context":    ctx,
            "resolution_status":   conv["resolution_status"],
            "message_count":       conv["message_count"],
            "turn_position":       "first",
        })

    rng.shuffle(candidates)
    selected = []
    for c in candidates:
        if len(selected) >= n:
            break
        if c["conversation_id"] not in used_conv_ids:
            selected.append(c)
            used_conv_ids.add(c["conversation_id"])

    return selected


def main() -> None:
    for p in [DEV_FILE, TEST_FILE, TRAIN_FILE]:
        if not p.exists():
            log.error("File not found: %s — run Phase 2 first", p)
            sys.exit(1)

    rng = random.Random(RANDOM_SEED)
    log.info("Loading dev and test conversations ...")

    dev_convs  = load_conversations(DEV_FILE)
    test_convs = load_conversations(TEST_FILE)
    all_convs  = dev_convs + test_convs

    # Leakage guard: ensure no train conversation_ids appear
    log.info("Loading train conversation IDs for leakage check ...")
    train_cids = get_train_conversation_ids(TRAIN_FILE)

    all_convs_safe = [c for c in all_convs if c["conversation_id"] not in train_cids]
    log.info("Dev+test conversations available: %d", len(all_convs_safe))

    # Distribution of available examples
    from collections import Counter
    avail_dist = Counter(c["resolution_status"] for c in all_convs_safe)
    log.info("Available by resolution_status: %s", dict(avail_dist))

    used_conv_ids: set = set()
    all_selected: List[Dict] = []

    for status, target in STRATA_TARGETS.items():
        selected = sample_from_conversations(
            all_convs_safe, n=target,
            resolution_filter=status,
            rng=rng,
            used_conv_ids=used_conv_ids,
        )
        log.info("Stratum %-22s  target=%d  sampled=%d", status, target, len(selected))
        all_selected.extend(selected)

    log.info("Total sampled: %d", len(all_selected))

    # Shuffle final order so strata are interleaved
    rng.shuffle(all_selected)

    # Assign golden_ids
    for i, row in enumerate(all_selected, 1):
        row["golden_id"] = "G{:04d}".format(i)

    # Write golden_unlabeled.csv
    fieldnames = [
        "golden_id", "conversation_id", "customer_message_id",
        "customer_text", "previous_context", "resolution_status",
        "is_multi_intent", "primary_intent", "secondary_intent",
        "annotation_confidence", "annotator_notes",
    ]
    Path("data").mkdir(exist_ok=True)
    with OUT_UNLABELED.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in all_selected:
            writer.writerow({
                "golden_id":            row["golden_id"],
                "conversation_id":      row["conversation_id"],
                "customer_message_id":  row["customer_message_id"],
                "customer_text":        row["customer_text"],
                "previous_context":     row["previous_context"],
                "resolution_status":    row["resolution_status"],
                "is_multi_intent":      "",    # to be filled by annotator
                "primary_intent":       "",    # to be filled by annotator
                "secondary_intent":     "",    # to be filled by annotator
                "annotation_confidence": "",   # to be filled by annotator
                "annotator_notes":      "",    # to be filled by annotator
            })

    log.info("Written %d rows to %s", len(all_selected), OUT_UNLABELED)

    # Summary
    from collections import Counter
    dist = Counter(r["resolution_status"] for r in all_selected)
    print("\n=== Golden Sampling Summary ===")
    print("Total examples sampled  : {:,}".format(len(all_selected)))
    print("Unique conversations    : {:,}".format(len(used_conv_ids)))
    print("Source                  : dev + test (ZERO from train)")
    print("Seed                    : {}".format(RANDOM_SEED))
    print("\nDistribution by resolution_status:")
    for st, cnt in sorted(dist.items(), key=lambda x: -x[1]):
        print("  {:<25}: {:>3}".format(st, cnt))
    print("\nUnlabeled golden set: {}".format(OUT_UNLABELED))
    print("Next step: annotate primary_intent in the CSV using data/annotation_guide.md")


if __name__ == "__main__":
    main()
