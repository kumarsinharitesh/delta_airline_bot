"""
Phase 2, Step 2 — Modeling Examples & Resolution Statistics
============================================================

Reads the conversations.jsonl produced by conversations.py and:
  1. Builds customer→support modeling examples using the actual reply graph
     (never creates pairs from chronological adjacency alone).
  2. Computes resolution_stats.json — distribution and illustrative examples.
  3. Writes examples.jsonl — one example per support response.

Run:
    python -m src.data.preprocess

Output:
    data/processed/examples.jsonl       — one example per line
    data/processed/resolution_stats.json
"""

from __future__ import annotations

import json
import logging
import random
from pathlib import Path
from typing import Any, Dict, List, Optional

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────
PROCESSED_DIR     = Path("data/processed")
CONVERSATIONS     = PROCESSED_DIR / "conversations.jsonl"
EXAMPLES          = PROCESSED_DIR / "examples.jsonl"
RESOLUTION_STATS  = PROCESSED_DIR / "resolution_stats.json"

RANDOM_SEED = 42


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_conversations(path: Path) -> List[Dict]:
    convs: List[Dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                convs.append(json.loads(line))
    return convs


def build_message_index(messages: List[Dict]) -> Dict[str, Dict]:
    """Return mid → message dict for fast lookup."""
    return {m["message_id"]: m for m in messages}


def get_previous_context(
    target_mid: str,
    msg_index: Dict[str, Dict],
    messages_sorted: List[Dict],
    max_context: int = 10,
) -> List[Dict]:
    """
    Return messages that came BEFORE the target message in chronological order.
    Limit to max_context to keep examples manageable.
    """
    context: List[Dict] = []
    for m in messages_sorted:
        if m["message_id"] == target_mid:
            break
        context.append({
            "message_id": m["message_id"],
            "role":       m["role"],
            "text":       m["text_clean"],
            "timestamp":  m.get("timestamp"),
        })
    return context[-max_context:]


def find_direct_customer_parent(
    support_msg: Dict,
    msg_index: Dict[str, Dict],
) -> Optional[Dict]:
    """
    Walk up the parent chain from a support message until we find a CUSTOMER message.
    Returns that customer message, or None if no customer ancestor is found.
    Uses explicit reply-graph links only — never adjacency.
    """
    parent_mid = support_msg.get("parent_message_id")
    visited: set = set()

    while parent_mid is not None and parent_mid not in visited:
        visited.add(parent_mid)
        parent_msg = msg_index.get(parent_mid)
        if parent_msg is None:
            # Parent outside dataset
            return None
        if parent_msg["role"] == "CUSTOMER":
            return parent_msg
        # Keep walking up
        parent_mid = parent_msg.get("parent_message_id")

    return None


# ── Example building ──────────────────────────────────────────────────────────

def build_examples(conversations: List[Dict]) -> List[Dict]:
    """
    For each support response, find the direct customer ancestor via the reply graph
    and create a modeling example.

    We do NOT create pairs from adjacent messages — only from explicit reply chains.
    If no customer ancestor exists in the dataset, the example is skipped.
    """
    examples: List[Dict] = []

    for conv in conversations:
        if not conv.get("is_usable", False):
            continue

        messages    = conv["messages"]
        msg_index   = build_message_index(messages)
        # Sort chronologically for context building
        msgs_sorted = sorted(
            messages,
            key=lambda m: (m.get("timestamp") or "", m["message_id"]),
        )

        cid           = conv["conversation_id"]
        res_status    = conv["resolution_status"]
        res_evidence  = conv["resolution_evidence"]

        for msg in messages:
            if msg["role"] != "SUPPORT":
                continue

            # Find the customer message this support reply is responding to
            customer_msg = find_direct_customer_parent(msg, msg_index)
            if customer_msg is None:
                continue  # No customer ancestor — skip this pair

            context = get_previous_context(msg["message_id"], msg_index, msgs_sorted)

            example = {
                "conversation_id":    cid,
                "customer_message_id": customer_msg["message_id"],
                "customer_text":       customer_msg["text_clean"],
                "support_response_id": msg["message_id"],
                "support_response":    msg["text_clean"],
                "previous_context":    context,
                "branch_parent_id":    msg.get("parent_message_id"),
                "resolution_status":   res_status,
                "resolution_evidence": res_evidence,
            }
            examples.append(example)

    return examples


# ── Resolution statistics ─────────────────────────────────────────────────────

def compute_resolution_stats(conversations: List[Dict]) -> Dict:
    """
    Compute counts and percentages for each resolution_status.
    Also includes up to 3 illustrative conversation_ids per status.
    """
    counts: Dict[str, int] = {}
    examples_per_status: Dict[str, List[str]] = {}
    evidence_by_status: Dict[str, List[List[str]]] = {}

    total = len(conversations)

    for conv in conversations:
        st = conv["resolution_status"]
        counts[st] = counts.get(st, 0) + 1

        if st not in examples_per_status:
            examples_per_status[st] = []
        if len(examples_per_status[st]) < 3:
            examples_per_status[st].append(conv["conversation_id"])

        if st not in evidence_by_status:
            evidence_by_status[st] = []
        if len(evidence_by_status[st]) < 3:
            evidence_by_status[st].append(conv["resolution_evidence"])

    distribution = {}
    for st, cnt in sorted(counts.items(), key=lambda x: -x[1]):
        distribution[st] = {
            "count":               cnt,
            "percentage":          round(cnt / total * 100, 2) if total > 0 else 0,
            "example_conv_ids":    examples_per_status.get(st, []),
            "example_evidence":    evidence_by_status.get(st, []),
        }

    # Comparison with Phase 1
    phase1_resolved_candidate = 3454
    new_resolved = counts.get("RESOLVED", 0)

    return {
        "total_conversations":          total,
        "resolution_distribution":      distribution,
        "phase1_resolution_candidates": phase1_resolved_candidate,
        "phase2_RESOLVED_count":        new_resolved,
        "phase1_vs_phase2_note": (
            "Phase 1 used 'last message is a support reply' as the resolution proxy, "
            "yielding {} candidates. ".format(phase1_resolved_candidate) +
            "Phase 2 (corrected) requires CUSTOMER_CONFIRMED to appear AFTER the first support "
            "message, and redirect-only conversations are classified as REDIRECTED not RESOLVED. "
            "Phase 2 RESOLVED count = {}. ".format(new_resolved) +
            "The audit correction removed false positives where the initial customer message "
            "contained 'thanks' before any support reply (politeness, not resolution confirmation). "
            "Redirect-dominated conversations that were previously RESOLVED are now REDIRECTED."
        ),
    }


# ── Sample conversations for manual inspection ────────────────────────────────

def print_sample_conversations(conversations: List[Dict], n: int = 20) -> None:
    """
    Deterministically print n conversations for manual validation.
    Uses seed 42 for reproducibility.
    """
    rng = random.Random(RANDOM_SEED)
    sample = rng.sample(conversations, min(n, len(conversations)))

    print(f"\n{'=' * 70}")
    print(f"SAMPLE CONVERSATIONS FOR MANUAL INSPECTION (n={len(sample)})")
    print("=" * 70)

    for i, conv in enumerate(sample, 1):
        print(f"\n--- Conversation {i}/{len(sample)} " + "-" * 40)
        print(f"  conversation_id  : {conv['conversation_id']}")
        print(f"  message_count    : {conv['message_count']}")
        print(f"  resolution_status: {conv['resolution_status']}")
        print(f"  resolution_evidence: {conv['resolution_evidence']}")
        print(f"  has_branching    : {conv['has_branching']}")
        print(f"  is_usable        : {conv['is_usable']}")
        for j, msg in enumerate(conv["messages"], 1):
            role   = msg["role"]
            ts     = (msg.get("timestamp") or "")[:24]
            parent = msg.get("parent_message_id") or "—"
            kids   = msg.get("child_message_ids") or []
            text_safe = msg["text_original"][:120].replace("\n", " ")
            text_safe = text_safe.encode("ascii", errors="replace").decode("ascii")
            print(f"    [{j}] {role:<10} ts={ts}  mid={msg['message_id']}  parent={parent}  children={kids}")
            print(f"          {text_safe!r}")
        print()


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    if not CONVERSATIONS.exists():
        log.error("conversations.jsonl not found — run conversations.py first.")
        return

    log.info("Loading conversations from %s …", CONVERSATIONS)
    conversations = load_conversations(CONVERSATIONS)
    log.info("Loaded %d conversations.", len(conversations))

    # ── Build modeling examples ───────────────────────────────────────────────
    log.info("Building modeling examples (reply-graph pairs only) …")
    examples = build_examples(conversations)
    log.info("Examples built: %d", len(examples))

    # ── Write examples.jsonl ──────────────────────────────────────────────────
    with EXAMPLES.open("w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    log.info("Wrote %d examples to %s", len(examples), EXAMPLES)

    # ── Resolution statistics ─────────────────────────────────────────────────
    res_stats = compute_resolution_stats(conversations)

    with RESOLUTION_STATS.open("w", encoding="utf-8") as f:
        json.dump(res_stats, f, indent=2, ensure_ascii=False)
    log.info("Wrote resolution stats to %s", RESOLUTION_STATS)

    # ── Sample inspection ─────────────────────────────────────────────────────
    print_sample_conversations(conversations, n=20)

    # ── Summary ───────────────────────────────────────────────────────────────
    usable = sum(1 for c in conversations if c["is_usable"])
    print("\n=== Preprocessing Summary ===")
    print("  Total conversations : {:,}".format(len(conversations)))
    print("  Usable conversations: {:,}".format(usable))
    print("  Modeling examples   : {:,}".format(len(examples)))
    print("  Resolution distribution:")
    for st, d in res_stats["resolution_distribution"].items():
        print("    {:<22}: {:,} ({:.1f}%)".format(st, d["count"], d["percentage"]))
    print()
    print("  Phase 1 resolution candidates : {:,}".format(res_stats["phase1_resolution_candidates"]))
    print("  Phase 2 RESOLVED (evidence)   : {:,}".format(res_stats["phase2_RESOLVED_count"]))

    # ── 5x5 Manual Audit ─────────────────────────────────────────────────────
    print_status_audit(conversations, n=5)


def print_status_audit(conversations: List[Dict], n: int = 5) -> None:
    """
    Print n examples per resolution status for manual audit.
    For each conversation show:
      - All messages with role, timestamp, message_id, parent
      - Which message triggered each evidence signal (via CONFIRMED_BY_MSG:<id>)
    """
    by_status: Dict[str, List[Dict]] = {}
    for conv in conversations:
        st = conv["resolution_status"]
        if st not in by_status:
            by_status[st] = []
        by_status[st].append(conv)

    TARGET_STATUSES = ["RESOLVED", "REDIRECTED", "UNKNOWN", "UNRESOLVED", "PARTIALLY_RESOLVED"]
    rng = random.Random(RANDOM_SEED)

    print("\n" + "=" * 72)
    print("5 x 5 MANUAL AUDIT -- {} EXAMPLES PER RESOLUTION STATUS".format(n))
    print("=" * 72)

    for status in TARGET_STATUSES:
        pool = by_status.get(status, [])
        sample = rng.sample(pool, min(n, len(pool)))
        print("\n" + "-" * 72)
        print("STATUS: {}  ({} total, showing {})".format(status, len(pool), len(sample)))
        print("-" * 72)

        for i, conv in enumerate(sample, 1):
            cid = conv["conversation_id"]
            ev  = conv["resolution_evidence"]
            # Extract confirming message_id if present
            confirmed_mid = next((e.split(":", 1)[1] for e in ev if e.startswith("CONFIRMED_BY_MSG:")), None)

            print("\n  [{}/{}] conv_id={} | msgs={} | branching={} | usable={}".format(
                i, len(sample), cid, conv["message_count"],
                conv["has_branching"], conv["is_usable"],
            ))
            print("  evidence: {}".format([e for e in ev if not e.startswith("CONFIRMED_BY_MSG:")]))
            if confirmed_mid:
                print("  confirming_message_id: {}".format(confirmed_mid))

            msgs = sorted(
                conv["messages"],
                key=lambda m: (m.get("timestamp") or "0000", m["message_id"]),
            )
            for msg in msgs:
                mid      = msg["message_id"]
                role     = msg["role"]
                ts       = (msg.get("timestamp") or "")[:24]
                parent   = msg.get("parent_message_id") or "--"
                text_raw = msg.get("text_original", "")[:100].replace("\n", " ")
                text_safe = text_raw.encode("ascii", errors="replace").decode("ascii")
                marker = " <-- CONFIRMING MSG" if mid == confirmed_mid else ""
                print("    [{role:<10}] mid={mid}  parent={parent}  ts={ts}{marker}".format(
                    role=role, mid=mid, parent=parent, ts=ts, marker=marker,
                ))
                print("      {!r}".format(text_safe))
        print()




if __name__ == "__main__":
    main()
