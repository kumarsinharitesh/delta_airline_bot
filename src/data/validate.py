"""
Phase 2, Step 4 — Dataset Validation
======================================

Runs 10 categories of lightweight validation tests over all Phase 2 outputs.
Reports PASS/FAIL per category and exits with code 1 if any test fails.

Tests:
    1. Multi-value response_tweet_id parsing
    2. Parent-child link consistency
    3. Conversation reconstruction integrity
    4. Missing-parent handling
    5. Branch preservation
    6. Role assignment
    7. Resolution status assignment
    8. Conversation-level split correctness
    9. Zero cross-split leakage
    10. Example references valid conversation / message IDs

Run:
    python -m src.data.validate
"""

from __future__ import annotations

import json
import logging
import sys
from collections import defaultdict
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
PROCESSED_DIR   = Path("data/processed")
CONVERSATIONS   = PROCESSED_DIR / "conversations.jsonl"
EXAMPLES        = PROCESSED_DIR / "examples.jsonl"
TRAIN           = PROCESSED_DIR / "train.jsonl"
DEV             = PROCESSED_DIR / "dev.jsonl"
TEST            = PROCESSED_DIR / "test.jsonl"
REL_STATS       = PROCESSED_DIR / "relationship_stats.json"
RESOLUTION_STATS= PROCESSED_DIR / "resolution_stats.json"
DATASET_STATS   = PROCESSED_DIR / "dataset_stats.json"

VALID_ROLES      = {"CUSTOMER", "SUPPORT", "UNKNOWN"}
VALID_RES_STATUS = {"RESOLVED", "PARTIALLY_RESOLVED", "REDIRECTED", "UNRESOLVED", "UNKNOWN"}


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_jsonl(path: Path) -> List[Dict]:
    records: List[Dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def report(name: str, passed: bool, details: str = "") -> bool:
    if passed:
        log.info("  ✓ PASS  — %s", name)
    else:
        log.error("  ✗ FAIL  — %s%s", name, f": {details}" if details else "")
    return passed


# ── Test 1: Multi-value response_tweet_id parsing ─────────────────────────────

def test_multi_value_response_parsing(rel_stats: Dict) -> bool:
    """
    Verify that the relationship stats were computed with multi-value awareness.
    Also checks that the parsing function itself is correct via inline unit test.
    """
    from src.data.conversations import parse_response_ids

    cases = [
        ("123",          [123]),
        ("123,456",      [123, 456]),
        ("123,456,789",  [123, 456, 789]),
        ("",             []),
        ("nan",          []),
        (None,           []),
        ("1.0,2.0",      [1, 2]),
    ]
    errors = []
    for raw, expected in cases:
        got = parse_response_ids(raw)
        if got != expected:
            errors.append(f"parse_response_ids({raw!r}) = {got} ≠ {expected}")

    if errors:
        return report("Multi-value response_tweet_id parsing", False, "; ".join(errors))

    # Check that the pipeline actually encountered multi-value rows
    mv = rel_stats.get("delta_multi_value_response_rows", 0)
    if mv == 0:
        log.warning("  ⚠  No multi-value response_tweet_id rows found for Delta — expected some.")
    else:
        log.info("  ✓  delta_multi_value_response_rows = %d (multi-value rows processed)", mv)

    return report("Multi-value response_tweet_id parsing", len(errors) == 0)


# ── Test 2: Parent-child link consistency ─────────────────────────────────────

def test_parent_child_consistency(conversations: List[Dict]) -> bool:
    """
    For every message with a parent_message_id:
      - The parent should exist in the same conversation (or be flagged parent_missing).
    For every child_message_id in a message:
      - That child should exist in the same conversation.
      - The child's parent_message_id should point back to the current message.
    """
    errors = 0
    for conv in conversations:
        msg_index = {m["message_id"]: m for m in conv["messages"]}
        for msg in conv["messages"]:
            pid = msg.get("parent_message_id")
            if pid is not None and not msg.get("parent_missing", False):
                if pid not in msg_index:
                    errors += 1
                    if errors <= 3:
                        log.debug("  Parent %s of msg %s not in conversation %s",
                                  pid, msg["message_id"], conv["conversation_id"])
            for cid in msg.get("child_message_ids", []):
                if cid not in msg_index:
                    errors += 1
                    if errors <= 3:
                        log.debug("  Child %s of msg %s not in conversation %s",
                                  cid, msg["message_id"], conv["conversation_id"])
                else:
                    # Bidirectional check: child.parent_message_id should == current msg
                    child = msg_index[cid]
                    if child.get("parent_message_id") != msg["message_id"]:
                        errors += 1
                        if errors <= 3:
                            log.debug("  Child %s parent pointer mismatch in conv %s",
                                      cid, conv["conversation_id"])
    return report("Parent-child link consistency", errors == 0,
                  f"{errors} inconsistency(ies) found")


# ── Test 3: Conversation reconstruction integrity ─────────────────────────────

def test_conversation_reconstruction(conversations: List[Dict]) -> bool:
    """
    Each conversation must:
      - Have at least one message.
      - Have a unique conversation_id.
      - message_count == len(messages).
      - customer_message_count + support_message_count + unknown_message_count == message_count.
    """
    cids_seen: Set[str] = set()
    errors = 0

    for conv in conversations:
        cid = conv["conversation_id"]
        msgs = conv.get("messages", [])

        if cid in cids_seen:
            errors += 1
            log.debug("Duplicate conversation_id: %s", cid)
        cids_seen.add(cid)

        if len(msgs) == 0:
            errors += 1
            log.debug("Empty conversation: %s", cid)

        if conv.get("message_count") != len(msgs):
            errors += 1
            log.debug("message_count mismatch in conv %s: stored=%d actual=%d",
                      cid, conv.get("message_count"), len(msgs))

        stored_total = (
            conv.get("customer_message_count", 0)
            + conv.get("support_message_count", 0)
            + conv.get("unknown_message_count", 0)
        )
        if stored_total != len(msgs):
            errors += 1
            log.debug("Role count mismatch in conv %s: %d+%d+%d=%d ≠ %d",
                      cid,
                      conv.get("customer_message_count", 0),
                      conv.get("support_message_count", 0),
                      conv.get("unknown_message_count", 0),
                      stored_total, len(msgs))

    return report("Conversation reconstruction integrity", errors == 0,
                  f"{errors} error(s)")


# ── Test 4: Missing-parent handling ──────────────────────────────────────────

def test_missing_parent_handling(conversations: List[Dict]) -> bool:
    """
    Messages with parent_missing=True should:
      - Still exist in the conversation (not dropped).
      - Have parent_message_id set to some value (the referenced but absent parent).
    """
    missing_correctly_handled = 0
    errors = 0

    for conv in conversations:
        for msg in conv["messages"]:
            if msg.get("parent_missing", False):
                missing_correctly_handled += 1
                # parent_message_id should be set (it points to the absent parent)
                if msg.get("parent_message_id") is None:
                    errors += 1
                    log.debug("parent_missing=True but parent_message_id is None in conv %s msg %s",
                              conv["conversation_id"], msg["message_id"])

    log.info("  Messages with parent_missing=True: %d", missing_correctly_handled)
    return report("Missing-parent handling", errors == 0,
                  f"{errors} error(s) in parent_missing messages")


# ── Test 5: Branch preservation ───────────────────────────────────────────────

def test_branch_preservation(conversations: List[Dict]) -> bool:
    """
    For branching conversations (has_branching=True):
      - At least one message should have >1 child_message_id.
    For non-branching conversations:
      - No message should have >1 child_message_id.
    """
    errors = 0
    branching_count = 0

    for conv in conversations:
        has_branch_flag = conv.get("has_branching", False)
        actual_branches = any(len(m.get("child_message_ids", [])) > 1 for m in conv["messages"])

        if has_branch_flag and not actual_branches:
            errors += 1
            log.debug("has_branching=True but no message has >1 child in conv %s",
                      conv["conversation_id"])
        if not has_branch_flag and actual_branches:
            errors += 1
            log.debug("has_branching=False but a message has >1 child in conv %s",
                      conv["conversation_id"])
        if has_branch_flag:
            branching_count += 1

    log.info("  Branching conversations found: %d", branching_count)
    return report("Branch preservation", errors == 0, f"{errors} flag mismatch(es)")


# ── Test 6: Role assignment ───────────────────────────────────────────────────

def test_role_assignment(conversations: List[Dict]) -> bool:
    """
    Every message role must be in {CUSTOMER, SUPPORT, UNKNOWN}.
    Role must match inbound:
        inbound=True  → CUSTOMER
        inbound=False → SUPPORT
        inbound=None  → UNKNOWN
    """
    errors = 0
    for conv in conversations:
        for msg in conv["messages"]:
            role    = msg.get("role")
            inbound = msg.get("inbound")

            if role not in VALID_ROLES:
                errors += 1
                log.debug("Invalid role %r in conv %s msg %s", role, conv["conversation_id"], msg["message_id"])
                continue

            if inbound is True  and role != "CUSTOMER":
                errors += 1
            elif inbound is False and role != "SUPPORT":
                errors += 1
            elif inbound is None  and role != "UNKNOWN":
                errors += 1

    return report("Role assignment", errors == 0,
                  f"{errors} role/inbound mismatch(es)")


# ── Test 7: Resolution status assignment ──────────────────────────────────────

def test_resolution_status(conversations: List[Dict]) -> bool:
    """
    Every conversation must have:
      - resolution_status in VALID_RES_STATUS
      - resolution_evidence as a list
      - No RESOLVED conversation should have only CONVERSATION_ENDED_AFTER_SUPPORT_REPLY as evidence
        (that alone should not produce RESOLVED per the spec).
    """
    errors = 0
    for conv in conversations:
        st  = conv.get("resolution_status", "")
        ev  = conv.get("resolution_evidence", [])

        if st not in VALID_RES_STATUS:
            errors += 1
            log.debug("Invalid resolution_status %r in conv %s", st, conv["conversation_id"])

        if not isinstance(ev, list):
            errors += 1
            log.debug("resolution_evidence is not a list in conv %s", conv["conversation_id"])

        # Spec: "CONVERSATION_ENDED_AFTER_SUPPORT_REPLY alone does NOT prove resolution"
        if st == "RESOLVED" and ev == ["CONVERSATION_ENDED_AFTER_SUPPORT_REPLY"]:
            errors += 1
            log.debug(
                "RESOLVED with only CONVERSATION_ENDED_AFTER_SUPPORT_REPLY evidence in conv %s — "
                "violates spec conservative rule",
                conv["conversation_id"],
            )

    return report("Resolution status assignment", errors == 0,
                  f"{errors} error(s)")


# ── Test 8: Conversation-level split correctness ──────────────────────────────

def test_conversation_level_split(
    train: List[Dict],
    dev:   List[Dict],
    test:  List[Dict],
) -> bool:
    """
    Verify split ratios are approximately correct and split tags are present.
    """
    total = len(train) + len(dev) + len(test)
    if total == 0:
        return report("Conversation-level split", False, "No conversations in any split")

    train_pct = len(train) / total
    dev_pct   = len(dev)   / total
    test_pct  = len(test)  / total

    TOLERANCE = 0.03  # allow ±3% due to integer rounding
    errors = []
    if abs(train_pct - 0.70) > TOLERANCE:
        errors.append(f"train ratio={train_pct:.2f} (expected ~0.70)")
    if abs(dev_pct - 0.15) > TOLERANCE:
        errors.append(f"dev ratio={dev_pct:.2f} (expected ~0.15)")
    if abs(test_pct - 0.15) > TOLERANCE:
        errors.append(f"test ratio={test_pct:.2f} (expected ~0.15)")

    # Every conversation must have split tag set
    for split_name, convs, expected_tag in [("train", train, "train"), ("dev", dev, "dev"), ("test", test, "test")]:
        wrong_tags = [c for c in convs if c.get("split") != expected_tag]
        if wrong_tags:
            errors.append(f"{len(wrong_tags)} conversations in {split_name} have wrong split tag")

    log.info(
        "  Split ratios: train=%.3f  dev=%.3f  test=%.3f",
        train_pct, dev_pct, test_pct,
    )
    return report("Conversation-level split correctness", len(errors) == 0, "; ".join(errors))


# ── Test 9: Zero cross-split leakage ──────────────────────────────────────────

def test_no_cross_split_leakage(
    train: List[Dict],
    dev:   List[Dict],
    test:  List[Dict],
    train_examples: List[Dict],
    dev_examples:   List[Dict],
    test_examples:  List[Dict],
) -> bool:
    """
    Explicitly verify all three split pairs are disjoint at conversation, message,
    and example levels.
    """
    train_cids = {c["conversation_id"] for c in train}
    dev_cids   = {c["conversation_id"] for c in dev}
    test_cids  = {c["conversation_id"] for c in test}

    errors = []
    if overlap := train_cids & dev_cids:
        errors.append(f"train∩dev conversations: {len(overlap)}")
    if overlap := train_cids & test_cids:
        errors.append(f"train∩test conversations: {len(overlap)}")
    if overlap := dev_cids & test_cids:
        errors.append(f"dev∩test conversations: {len(overlap)}")

    def mids(convs: List[Dict]) -> Set[str]:
        s: Set[str] = set()
        for c in convs:
            for m in c.get("messages", []):
                s.add(m["message_id"])
        return s

    tm, dm, xm = mids(train), mids(dev), mids(test)
    if overlap := tm & dm:
        errors.append(f"train∩dev messages: {len(overlap)}")
    if overlap := tm & xm:
        errors.append(f"train∩test messages: {len(overlap)}")
    if overlap := dm & xm:
        errors.append(f"dev∩test messages: {len(overlap)}")

    def ex_ids(exs: List[Dict]) -> Set[Tuple]:
        return {(e["conversation_id"], e["support_response_id"]) for e in exs}

    te, de, xe = ex_ids(train_examples), ex_ids(dev_examples), ex_ids(test_examples)
    if overlap := te & de:
        errors.append(f"train∩dev examples: {len(overlap)}")
    if overlap := te & xe:
        errors.append(f"train∩test examples: {len(overlap)}")
    if overlap := de & xe:
        errors.append(f"dev∩test examples: {len(overlap)}")

    return report("Zero cross-split leakage", len(errors) == 0, "; ".join(errors))


# ── Test 10: Example references valid IDs ─────────────────────────────────────

def test_example_references(
    conversations: List[Dict],
    examples: List[Dict],
) -> bool:
    """
    Every example must:
      - Reference a conversation_id that exists in conversations.jsonl.
      - Reference a customer_message_id that exists in that conversation.
      - Reference a support_response_id that exists in that conversation.
    """
    conv_msg_map: Dict[str, Set[str]] = {}
    for conv in conversations:
        cid  = conv["conversation_id"]
        mids = {m["message_id"] for m in conv["messages"]}
        conv_msg_map[cid] = mids

    errors = 0
    for ex in examples:
        cid  = ex.get("conversation_id", "")
        cmid = ex.get("customer_message_id", "")
        smid = ex.get("support_response_id", "")

        if cid not in conv_msg_map:
            errors += 1
            continue
        if cmid not in conv_msg_map[cid]:
            errors += 1
            log.debug("customer_message_id %s not in conv %s", cmid, cid)
        if smid not in conv_msg_map[cid]:
            errors += 1
            log.debug("support_response_id %s not in conv %s", smid, cid)

    return report("Example references valid conversation/message IDs", errors == 0,
                  f"{errors} invalid reference(s)")


# ── Main ──────────────────────────────────────────────────────────────────────

# ── Test 11: CUSTOMER_CONFIRMED only fires after first support message ─────────

def test_customer_confirmed_post_support(conversations: List[Dict]) -> bool:
    """
    For every conversation where CUSTOMER_CONFIRMED appears in resolution_evidence:
      - There must be at least one customer message that appears AFTER the
        first support message in chronological order.
      - The confirming message_id (CONFIRMED_BY_MSG:xxx) should point to a
        customer message that comes after the first support message.
    
    If CUSTOMER_CONFIRMED is found on a conversation where the only customer
    messages appear BEFORE any support message, that is a false positive.
    """
    errors = 0
    confirmed_convs = [c for c in conversations if "CUSTOMER_CONFIRMED" in c.get("resolution_evidence", [])]
    log.info("  CUSTOMER_CONFIRMED conversations: %d", len(confirmed_convs))

    for conv in confirmed_convs:
        msgs = sorted(
            conv["messages"],
            key=lambda m: (m.get("timestamp") or "0000", m["message_id"]),
        )
        # Find index of first support message
        first_sup_idx = next((i for i, m in enumerate(msgs) if m["role"] == "SUPPORT"), None)
        if first_sup_idx is None:
            # No support message but CUSTOMER_CONFIRMED set — error
            errors += 1
            log.debug("CUSTOMER_CONFIRMED but no support message in conv %s", conv["conversation_id"])
            continue

        # Check if any customer message after the first support message exists
        post_support_customers = [
            m for i, m in enumerate(msgs) if i > first_sup_idx and m["role"] == "CUSTOMER"
        ]
        if not post_support_customers:
            # CUSTOMER_CONFIRMED triggered but no customer message after support — false positive
            errors += 1
            log.debug(
                "CUSTOMER_CONFIRMED false positive in conv %s: no customer msg after first support msg",
                conv["conversation_id"],
            )
            continue

        # If CONFIRMED_BY_MSG:<id> is present, verify that message is after first support
        ev = conv.get("resolution_evidence", [])
        confirmed_mids = [e.split(":", 1)[1] for e in ev if e.startswith("CONFIRMED_BY_MSG:")]
        msg_index = {m["message_id"]: i for i, m in enumerate(msgs)}
        for cmid in confirmed_mids:
            if cmid not in msg_index:
                errors += 1
                log.debug("CONFIRMED_BY_MSG %s not found in conv %s messages", cmid, conv["conversation_id"])
            elif msg_index[cmid] <= first_sup_idx:
                # Confirming message is BEFORE or AT the first support message — false positive
                errors += 1
                log.debug(
                    "CONFIRMED_BY_MSG %s is BEFORE first support message in conv %s (false positive)",
                    cmid, conv["conversation_id"],
                )

    return report("CUSTOMER_CONFIRMED only fires after first support message", errors == 0,
                  "{} false positive(s) detected".format(errors))



def main() -> None:
    missing = [p for p in [CONVERSATIONS, EXAMPLES, TRAIN, DEV, TEST, REL_STATS] if not p.exists()]
    if missing:
        log.error("Missing output files — run the pipeline first:\n  %s",
                  "\n  ".join(str(p) for p in missing))
        sys.exit(1)

    log.info("Loading all Phase 2 outputs …")
    conversations = load_jsonl(CONVERSATIONS)
    examples      = load_jsonl(EXAMPLES)
    train         = load_jsonl(TRAIN)
    dev           = load_jsonl(DEV)
    test          = load_jsonl(TEST)

    with REL_STATS.open() as f:
        rel_stats = json.load(f)

    train_cids = {c["conversation_id"] for c in train}
    dev_cids   = {c["conversation_id"] for c in dev}
    test_cids  = {c["conversation_id"] for c in test}
    train_examples = [e for e in examples if e["conversation_id"] in train_cids]
    dev_examples   = [e for e in examples if e["conversation_id"] in dev_cids]
    test_examples  = [e for e in examples if e["conversation_id"] in test_cids]

    print("\n" + "=" * 60)
    print("Phase 2 -- Validation Report")
    print("=" * 60)

    results = [
        test_multi_value_response_parsing(rel_stats),
        test_parent_child_consistency(conversations),
        test_conversation_reconstruction(conversations),
        test_missing_parent_handling(conversations),
        test_branch_preservation(conversations),
        test_role_assignment(conversations),
        test_resolution_status(conversations),
        test_conversation_level_split(train, dev, test),
        test_no_cross_split_leakage(train, dev, test, train_examples, dev_examples, test_examples),
        test_example_references(conversations, examples),
        test_customer_confirmed_post_support(conversations),
    ]

    passed = sum(results)
    total  = len(results)
    print("\n" + "=" * 60)
    print("Result: {}/{} tests passed".format(passed, total))
    print("=" * 60 + "\n")

    if passed < total:
        sys.exit(1)


if __name__ == "__main__":
    main()
