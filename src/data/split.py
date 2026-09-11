"""
Phase 2, Step 3 — Conversation-Level Train / Dev / Test Split
=============================================================

CRITICAL INVARIANT:
    The unit of splitting is the CONVERSATION, not the individual tweet or example.
    ALL messages and examples from one conversation belong to exactly one split.
    This is mandatory to prevent leakage between splits.

Split ratios: 70% train / 15% dev / 15% test
Random seed : 42 (deterministic)

After splitting, hard leakage assertions are executed:
    - train ∩ dev   = ∅
    - train ∩ test  = ∅
    - dev   ∩ test  = ∅
    - No message ID appears in more than one split.
    - No example appears in more than one split.
If ANY assertion fails the script exits with a non-zero code.

Run:
    python -m src.data.split

Output:
    data/processed/train.jsonl
    data/processed/dev.jsonl
    data/processed/test.jsonl
    data/processed/dataset_stats.json
"""

from __future__ import annotations

import json
import logging
import random
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────
PROCESSED_DIR  = Path("data/processed")
CONVERSATIONS  = PROCESSED_DIR / "conversations.jsonl"
EXAMPLES       = PROCESSED_DIR / "examples.jsonl"
TRAIN          = PROCESSED_DIR / "train.jsonl"
DEV            = PROCESSED_DIR / "dev.jsonl"
TEST           = PROCESSED_DIR / "test.jsonl"
DATASET_STATS  = PROCESSED_DIR / "dataset_stats.json"

RANDOM_SEED    = 42
TRAIN_RATIO    = 0.70
DEV_RATIO      = 0.15
# TEST_RATIO   = 0.15 (remainder)


# ── I/O helpers ───────────────────────────────────────────────────────────────

def load_jsonl(path: Path) -> List[Dict]:
    records: List[Dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def write_jsonl(path: Path, records: List[Dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


# ── Deterministic conversation-level split ────────────────────────────────────

def conversation_split(
    conversations: List[Dict],
    train_ratio: float = TRAIN_RATIO,
    dev_ratio:   float = DEV_RATIO,
    seed:        int   = RANDOM_SEED,
) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """
    Shuffle conversations deterministically, then cut at (train_ratio, dev_ratio) boundaries.
    Returns (train_convs, dev_convs, test_convs).
    """
    rng = random.Random(seed)
    shuffled = conversations[:]
    rng.shuffle(shuffled)

    n = len(shuffled)
    n_train = int(n * train_ratio)
    n_dev   = int(n * dev_ratio)

    train = shuffled[:n_train]
    dev   = shuffled[n_train : n_train + n_dev]
    test  = shuffled[n_train + n_dev :]

    # Tag each conversation with its split
    for conv in train:
        conv["split"] = "train"
    for conv in dev:
        conv["split"] = "dev"
    for conv in test:
        conv["split"] = "test"

    log.info(
        "Split: train=%d  dev=%d  test=%d  (total=%d)",
        len(train), len(dev), len(test), n,
    )
    return train, dev, test


# ── Hard leakage assertions ───────────────────────────────────────────────────

def assert_no_leakage(
    train: List[Dict],
    dev:   List[Dict],
    test:  List[Dict],
    train_examples: List[Dict],
    dev_examples:   List[Dict],
    test_examples:  List[Dict],
) -> None:
    """
    Explicitly verify zero leakage between all split pairs.
    Checks at conversation, message, and example levels.
    Raises SystemExit on any failure.
    """
    errors: List[str] = []

    train_cids = {c["conversation_id"] for c in train}
    dev_cids   = {c["conversation_id"] for c in dev}
    test_cids  = {c["conversation_id"] for c in test}

    # ── Conversation-level disjointness ───────────────────────────────────────
    if train_cids & dev_cids:
        errors.append(f"LEAKAGE: train ∩ dev conversation IDs: {len(train_cids & dev_cids)} overlap(s)")
    if train_cids & test_cids:
        errors.append(f"LEAKAGE: train ∩ test conversation IDs: {len(train_cids & test_cids)} overlap(s)")
    if dev_cids & test_cids:
        errors.append(f"LEAKAGE: dev ∩ test conversation IDs: {len(dev_cids & test_cids)} overlap(s)")

    # ── Message-level disjointness ────────────────────────────────────────────
    def get_message_ids(convs: List[Dict]) -> Set[str]:
        ids: Set[str] = set()
        for conv in convs:
            for msg in conv.get("messages", []):
                ids.add(msg["message_id"])
        return ids

    train_mids = get_message_ids(train)
    dev_mids   = get_message_ids(dev)
    test_mids  = get_message_ids(test)

    if train_mids & dev_mids:
        errors.append(f"LEAKAGE: train ∩ dev message IDs: {len(train_mids & dev_mids)} overlap(s)")
    if train_mids & test_mids:
        errors.append(f"LEAKAGE: train ∩ test message IDs: {len(train_mids & test_mids)} overlap(s)")
    if dev_mids & test_mids:
        errors.append(f"LEAKAGE: dev ∩ test message IDs: {len(dev_mids & test_mids)} overlap(s)")

    # ── Example-level disjointness ────────────────────────────────────────────
    def get_example_ids(exs: List[Dict]) -> Set[Tuple[str, str]]:
        return {(e["conversation_id"], e["support_response_id"]) for e in exs}

    train_eids = get_example_ids(train_examples)
    dev_eids   = get_example_ids(dev_examples)
    test_eids  = get_example_ids(test_examples)

    if train_eids & dev_eids:
        errors.append(f"LEAKAGE: train ∩ dev example IDs: {len(train_eids & dev_eids)} overlap(s)")
    if train_eids & test_eids:
        errors.append(f"LEAKAGE: train ∩ test example IDs: {len(train_eids & test_eids)} overlap(s)")
    if dev_eids & test_eids:
        errors.append(f"LEAKAGE: dev ∩ test example IDs: {len(dev_eids & test_eids)} overlap(s)")

    # ── No example references a conversation in a different split ─────────────
    for split_name, exs, cids in [
        ("train", train_examples, train_cids),
        ("dev",   dev_examples,   dev_cids),
        ("test",  test_examples,  test_cids),
    ]:
        cross = [e for e in exs if e["conversation_id"] not in cids]
        if cross:
            errors.append(
                f"LEAKAGE: {len(cross)} {split_name} example(s) reference "
                f"conversation_ids not in {split_name} split."
            )

    if errors:
        log.error("=== LEAKAGE ASSERTIONS FAILED ===")
        for err in errors:
            log.error("  %s", err)
        sys.exit(1)
    else:
        log.info("[PASS] All leakage assertions passed -- zero cross-split overlap.")


# ── Temporal distribution analysis ───────────────────────────────────────────

def temporal_distribution(convs: List[Dict], split_name: str) -> Dict:
    """Extract min/max timestamps from all messages in a split's conversations."""
    all_ts = []
    for conv in convs:
        for msg in conv.get("messages", []):
            ts = msg.get("timestamp")
            if ts:
                all_ts.append(ts)
    if not all_ts:
        return {"split": split_name, "min_ts": None, "max_ts": None, "count": 0}
    all_ts.sort()
    return {
        "split":  split_name,
        "min_ts": all_ts[0],
        "max_ts": all_ts[-1],
        "count":  len(all_ts),
    }


# ── Dataset statistics ────────────────────────────────────────────────────────

def compute_dataset_stats(
    conversations:  List[Dict],
    examples:       List[Dict],
    train:          List[Dict],
    dev:            List[Dict],
    test:           List[Dict],
    train_examples: List[Dict],
    dev_examples:   List[Dict],
    test_examples:  List[Dict],
) -> Dict:
    def count_messages(convs: List[Dict]) -> Dict:
        total = cust = supp = unk = 0
        for conv in convs:
            for msg in conv.get("messages", []):
                total += 1
                r = msg.get("role", "UNKNOWN")
                if r == "CUSTOMER": cust += 1
                elif r == "SUPPORT": supp += 1
                else: unk += 1
        return {"total": total, "customer": cust, "support": supp, "unknown": unk}

    all_msgs      = count_messages(conversations)
    train_msgs    = count_messages(train)
    dev_msgs      = count_messages(dev)
    test_msgs     = count_messages(test)

    usable        = [c for c in conversations if c.get("is_usable")]
    single_msg    = [c for c in conversations if c["message_count"] == 1]
    multi_msg     = [c for c in conversations if c["message_count"] > 1]
    cs_convs      = [c for c in conversations if c.get("has_customer_support_interaction")]
    missing_par   = [c for c in conversations if c.get("has_missing_parent")]
    branching     = [c for c in conversations if c.get("has_branching")]

    res_dist: Dict[str, int] = {}
    for c in conversations:
        st = c.get("resolution_status", "UNKNOWN")
        res_dist[st] = res_dist.get(st, 0) + 1

    temporal = [
        temporal_distribution(train, "train"),
        temporal_distribution(dev,   "dev"),
        temporal_distribution(test,  "test"),
    ]

    return {
        # ── Raw counts ─────────────────────────────────────────────────────
        "raw_delta_messages":           all_msgs["total"],
        "reconstructed_conversations":  len(conversations),
        "customer_messages":            all_msgs["customer"],
        "support_messages":             all_msgs["support"],
        "unknown_messages":             all_msgs["unknown"],
        # ── Conversation categories ────────────────────────────────────────
        "single_message_conversations":      len(single_msg),
        "multi_message_conversations":       len(multi_msg),
        "customer_support_conversations":    len(cs_convs),
        "usable_conversations":              len(usable),
        "usable_examples":                   len(examples),
        "missing_parent_conversations":      len(missing_par),
        "branching_conversations":           len(branching),
        # ── Resolution distribution ────────────────────────────────────────
        "resolution_status_distribution": res_dist,
        # ── Splits ────────────────────────────────────────────────────────
        "train_conversations": len(train),
        "dev_conversations":   len(dev),
        "test_conversations":  len(test),
        "train_messages":      train_msgs["total"],
        "dev_messages":        dev_msgs["total"],
        "test_messages":       test_msgs["total"],
        "train_examples":      len(train_examples),
        "dev_examples":        len(dev_examples),
        "test_examples":       len(test_examples),
        # ── Temporal ──────────────────────────────────────────────────────
        "temporal_distribution": temporal,
        "temporal_leakage_note": (
            "Random conversation-level splitting was used. "
            "Conversations from later dates may appear in training while earlier ones are in test. "
            "This is a known limitation of random splitting. "
            "A temporal split can be applied separately as a robustness check."
        ),
        # ── Reproducibility ───────────────────────────────────────────────
        "random_seed": RANDOM_SEED,
        "split_ratios": {"train": TRAIN_RATIO, "dev": DEV_RATIO, "test": round(1 - TRAIN_RATIO - DEV_RATIO, 2)},
        "leakage_assertions": "PASSED",
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    if not CONVERSATIONS.exists():
        log.error("conversations.jsonl not found — run conversations.py first.")
        sys.exit(1)
    if not EXAMPLES.exists():
        log.error("examples.jsonl not found — run preprocess.py first.")
        sys.exit(1)

    log.info("Loading conversations …")
    conversations = load_jsonl(CONVERSATIONS)
    log.info("Loading examples …")
    examples = load_jsonl(EXAMPLES)

    # ── Split conversations ───────────────────────────────────────────────────
    train, dev, test = conversation_split(conversations)

    # ── Route examples to correct split ──────────────────────────────────────
    train_cids = {c["conversation_id"] for c in train}
    dev_cids   = {c["conversation_id"] for c in dev}
    test_cids  = {c["conversation_id"] for c in test}

    train_examples = [e for e in examples if e["conversation_id"] in train_cids]
    dev_examples   = [e for e in examples if e["conversation_id"] in dev_cids]
    test_examples  = [e for e in examples if e["conversation_id"] in test_cids]

    log.info(
        "Examples routed: train=%d  dev=%d  test=%d",
        len(train_examples), len(dev_examples), len(test_examples),
    )

    # ── Hard leakage assertions ───────────────────────────────────────────────
    log.info("Running leakage assertions …")
    assert_no_leakage(train, dev, test, train_examples, dev_examples, test_examples)

    # ── Write split files ─────────────────────────────────────────────────────
    write_jsonl(TRAIN, train)
    write_jsonl(DEV,   dev)
    write_jsonl(TEST,  test)
    log.info("Split files written: %s, %s, %s", TRAIN, DEV, TEST)

    # ── Update conversations.jsonl with split tags ────────────────────────────
    # (Merge split annotation back into conversations.jsonl so it's consistent)
    conv_split_map = {}
    for split_name, convs in [("train", train), ("dev", dev), ("test", test)]:
        for c in convs:
            conv_split_map[c["conversation_id"]] = split_name
    for c in conversations:
        c["split"] = conv_split_map.get(c["conversation_id"])
    write_jsonl(CONVERSATIONS, conversations)
    log.info("conversations.jsonl updated with split tags.")

    # ── Dataset statistics ────────────────────────────────────────────────────
    stats = compute_dataset_stats(
        conversations, examples,
        train, dev, test,
        train_examples, dev_examples, test_examples,
    )

    with DATASET_STATS.open("w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    log.info("Dataset stats written to %s", DATASET_STATS)

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n=== Split Summary ===")
    print(f"  Total conversations : {len(conversations):,}")
    print(f"  Train               : {len(train):,} conversations  {len(train_examples):,} examples")
    print(f"  Dev                 : {len(dev):,} conversations  {len(dev_examples):,} examples")
    print(f"  Test                : {len(test):,} conversations  {len(test_examples):,} examples")
    print(f"\n  Leakage assertions  : PASSED [OK]")

    # Temporal ranges
    for td in stats["temporal_distribution"]:
        print("  {:5} timestamps   : {}  ->  {}".format(td["split"], td["min_ts"], td["max_ts"]))

    print("\n  Note: {}...".format(stats["temporal_leakage_note"][:160]))


if __name__ == "__main__":
    main()
