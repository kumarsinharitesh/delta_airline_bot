"""
Phase 2, Step 1 — Delta Conversation Reconstruction
====================================================

Two-pass memory-efficient approach:
  Pass 1 : Scan all 2.8M rows, build lightweight reply-graph structures
           (no tweet text stored in this pass).
  Pass 2 : Scan again, extract full column data only for Delta conversation tweets.

Key correctness rules enforced here:
  - response_tweet_id is fully parsed (ALL comma-separated IDs, not just the first).
  - Conversations are reconstructed via explicit parent–child reply links only.
  - Cycles are detected and reported; no cycle-causing edge is used as a root traversal link.
  - Parent-missing messages are retained but flagged.
  - Branching conversations are preserved (a tweet can have multiple children).
  - Roles come exclusively from the `inbound` column; no heuristics.

Outputs:
  data/processed/conversations.jsonl      — one JSON object per line, one conversation per object
  data/processed/relationship_stats.json  — graph validation report
"""

from __future__ import annotations

import json
import logging
import re
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import pandas as pd

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────
CSV_PATH       = Path("dataset_raw/twcs/twcs.csv")
PROCESSED_DIR  = Path("data/processed")
CONVERSATIONS  = PROCESSED_DIR / "conversations.jsonl"
REL_STATS      = PROCESSED_DIR / "relationship_stats.json"
CHUNK_SIZE     = 200_000
BRAND          = "Delta"

# ── Text cleaning (applied here so text_clean is available in conversations.jsonl)
_URL_RE      = re.compile(r"https?://\S+|www\.\S+")
_MULTI_SPACE = re.compile(r"[ \t]+")


def clean_text(raw: str) -> str:
    """
    Light normalisation: replace URLs with [URL], collapse whitespace.
    All meaningful words (including negations, keywords) are preserved.
    text_original is never modified.
    """
    t = _URL_RE.sub("[URL]", raw)
    t = _MULTI_SPACE.sub(" ", t)
    return t.strip()


# ── Resolution evidence patterns ──────────────────────────────────────────────
# Applied to support-message text to populate resolution_evidence.

_REDIRECT_RE = re.compile(
    r"\bDM\b|direct\s+message|private\s+message|\bPM\s+us\b|message\s+us|"
    r"send\s+us\s+a|please\s+contact|call\s+us|our\s+app|delta\.com|"
    r"our\s+website|1[-\s]800|1[-\s]888|submit\s+a.*request|"
    r"via\s+our\s+website|reach\s+us\s+at|contact\s+us\s+at",
    re.IGNORECASE,
)
_SUPPORT_ACTION_RE = re.compile(
    r"has\s+been\s+resolved|has\s+been\s+applied|has\s+been\s+credited|"
    r"refund\s+has\s+been|refund.*(?:process|issu)|credited.*account|"
    r"rebooked|rebooking.*(?:done|complete)|successfully\s+(?:updated|cancelled)|"
    r"confirmed.*cancel|ticket\s+(?:updated|created|opened)",
    re.IGNORECASE,
)
_SUPPORT_INSTRUCTION_RE = re.compile(
    r"\bplease\s+try\b|\byou\s+can\b|please\s+follow|steps?\s*:",
    re.IGNORECASE,
)
_CUSTOMER_CONFIRM_RE = re.compile(
    r"\bthank\s*(?:you|u)\b|\bthanks\b|\bthx\b|"
    r"that\s+(?:worked|fixed|helped|did\s+it|solved)|"
    r"problem\s+(?:solved|fixed)|all\s+set|appreciate|wonderful|"
    r"great.*thanks|thanks.*much",
    re.IGNORECASE,
)


# ── Pass 1 helpers ────────────────────────────────────────────────────────────

def parse_response_ids(raw: Any) -> List[int]:
    """
    Parse response_tweet_id — may contain MULTIPLE comma-separated integers.
    Returns a list with ALL IDs (not just the first).
    """
    s = str(raw).strip() if pd.notna(raw) else ""
    if s in ("", "nan", "NaN", "None"):
        return []
    result: List[int] = []
    for part in s.split(","):
        part = part.strip()
        try:
            result.append(int(float(part)))
        except (ValueError, TypeError):
            pass
    return result


def parse_single_id(raw: Any) -> Optional[int]:
    """Parse in_response_to_tweet_id (always a single value; we take the first if multi)."""
    s = str(raw).strip() if pd.notna(raw) else ""
    if s in ("", "nan", "NaN", "None"):
        return None
    try:
        return int(float(s.split(",")[0].strip()))
    except (ValueError, TypeError):
        return None


# ── Pass 1: build global reply graph ─────────────────────────────────────────

def pass1_build_graph(csv_path: Path) -> Tuple[
    Dict[int, Optional[int]],   # parent_map:              tweet_id  → parent_id | None
    Dict[int, Set[int]],        # children_from_parent:    parent_id → {child_ids}  (inverted parent_map)
    Dict[int, List[int]],       # children_from_response:  tweet_id  → [child_ids]  (from response_tweet_id)
    Dict[int, Tuple[str, bool]],# author_inbound_map:      tweet_id  → (author_id, inbound)
    Dict,                       # raw stats for relationship report
]:
    parent_map:             Dict[int, Optional[int]]    = {}
    children_from_parent:   Dict[int, Set[int]]         = defaultdict(set)
    children_from_response: Dict[int, List[int]]        = {}
    author_inbound_map:     Dict[int, Tuple[str, bool]] = {}

    stats = {
        "total_tweets_scanned": 0,
        "total_parent_links": 0,
        "total_response_links": 0,
        "multi_value_response_rows": 0,
        # in_response_to_tweet_id multi-value investigation
        "multi_value_parent_rows": 0,
        "multi_value_parent_extra_links_recovered": 0,
    }

    log.info("Pass 1 — scanning full dataset to build reply graph …")

    for i, chunk in enumerate(pd.read_csv(
        csv_path,
        usecols=["tweet_id", "author_id", "inbound",
                 "in_response_to_tweet_id", "response_tweet_id"],
        chunksize=CHUNK_SIZE,
        dtype={"tweet_id": "Int64", "author_id": str, "inbound": bool,
               "in_response_to_tweet_id": str, "response_tweet_id": str},
    )):
        for row in chunk.itertuples(index=False):
            tid = int(row.tweet_id)

            # Parent relationship
            # Investigate multi-value in_response_to_tweet_id
            raw_parent = str(row.in_response_to_tweet_id) if str(row.in_response_to_tweet_id) not in ("nan", "None", "") else ""
            parent_parts = [p.strip() for p in raw_parent.split(",") if p.strip()] if raw_parent else []
            if len(parent_parts) > 1:
                stats["multi_value_parent_rows"] += 1
                stats["multi_value_parent_extra_links_recovered"] += len(parent_parts) - 1
            pid = parse_single_id(row.in_response_to_tweet_id)
            parent_map[tid] = pid
            if pid is not None:
                children_from_parent[pid].add(tid)
                stats["total_parent_links"] += 1

            # Response children (multi-value — parse ALL)
            resp_ids = parse_response_ids(row.response_tweet_id)
            if resp_ids:
                children_from_response[tid] = resp_ids
                stats["total_response_links"] += len(resp_ids)
                if len(resp_ids) > 1:
                    stats["multi_value_response_rows"] += 1

            # Author / role index
            author_inbound_map[tid] = (str(row.author_id), bool(row.inbound))

        stats["total_tweets_scanned"] += len(chunk)
        if (i + 1) % 5 == 0:
            log.info("  Pass 1 chunk %d — %d tweets indexed", i + 1, len(parent_map))

    log.info(
        "Pass 1 done: %d tweets | %d parent-links | %d response-links | %d multi-value response rows",
        stats["total_tweets_scanned"],
        stats["total_parent_links"],
        stats["total_response_links"],
        stats["multi_value_response_rows"],
    )
    log.info(
        "  in_response_to_tweet_id multi-value rows: %d (extra links recovered: %d)",
        stats["multi_value_parent_rows"],
        stats["multi_value_parent_extra_links_recovered"],
    )
    return (parent_map, dict(children_from_parent),
            children_from_response, author_inbound_map, stats)


# ── Root-finding: walk UP the parent chain ────────────────────────────────────

def find_root_iterative(
    start: int,
    parent_map: Dict[int, Optional[int]],
    valid_ids: Set[int],
    root_cache: Dict[int, int],
    cycles_detected: List[int],
    missing_parent_set: Set[int],
) -> int:
    """
    Walk UP the parent chain to find the root tweet.
    Uses iterative traversal with cycle detection and path-compression caching.
    If a cycle is detected the traversal stops at the cycle point; that node
    becomes the root of that sub-graph and is recorded in cycles_detected.
    If a parent is referenced but not in the dataset the node is a "missing-parent root".
    """
    if start in root_cache:
        return root_cache[start]

    path: List[int]  = []
    visited: Set[int] = set()
    cur = start

    while True:
        if cur in root_cache:
            root = root_cache[cur]
            break
        if cur in visited:
            # Cycle detected — use this node as the root for this subgraph
            root = cur
            cycles_detected.append(cur)
            log.debug("Cycle detected at tweet_id %d", cur)
            break
        visited.add(cur)
        path.append(cur)

        parent = parent_map.get(cur)
        if parent is None or parent not in valid_ids:
            root = cur
            if parent is not None:
                # Parent is referenced but absent from the dataset
                missing_parent_set.add(cur)
            break
        cur = parent

    # Path compression: cache root for every node on the path
    for node in path:
        root_cache[node] = root

    return root


# ── BFS DOWN from roots ───────────────────────────────────────────────────────

def collect_bfs_down(
    root: int,
    children_from_parent: Dict[int, Set[int]],
) -> Set[int]:
    """
    BFS downward from a root using the inverted parent map.
    Collects ALL tweet IDs reachable (the complete conversation subtree).
    """
    collected: Set[int] = set()
    queue = deque([root])
    while queue:
        cur = queue.popleft()
        if cur in collected:
            continue
        collected.add(cur)
        for child in children_from_parent.get(cur, set()):
            if child not in collected:
                queue.append(child)
    return collected


# ── Pass 2: extract full column data ─────────────────────────────────────────

def pass2_extract_delta_data(
    csv_path: Path,
    target_ids: Set[int],
) -> Dict[int, Dict]:
    """Scan full CSV a second time, returning complete row data for Delta tweets only."""
    data: Dict[int, Dict] = {}
    log.info("Pass 2 — extracting full data for %d Delta tweets …", len(target_ids))

    for i, chunk in enumerate(pd.read_csv(
        csv_path,
        chunksize=CHUNK_SIZE,
        dtype={"tweet_id": "Int64", "author_id": str, "inbound": bool,
               "in_response_to_tweet_id": str, "response_tweet_id": str,
               "text": str, "created_at": str},
    )):
        mask = chunk["tweet_id"].apply(
            lambda x: pd.notna(x) and int(x) in target_ids
        )
        for row in chunk[mask].itertuples(index=False):
            tid = int(row.tweet_id)
            data[tid] = {
                "author_id":                   str(row.author_id),
                "inbound":                     bool(row.inbound),
                "created_at":                  str(row.created_at) if pd.notna(row.created_at) else None,
                "text":                        str(row.text) if pd.notna(row.text) else "",
                "response_tweet_id_raw":       str(row.response_tweet_id) if pd.notna(row.response_tweet_id) else "",
                "in_response_to_tweet_id_raw": str(row.in_response_to_tweet_id) if pd.notna(row.in_response_to_tweet_id) else "",
            }
        if (i + 1) % 5 == 0:
            log.info("  Pass 2 chunk %d — %d Delta rows collected", i + 1, len(data))

    log.info("Pass 2 done: %d Delta tweet records extracted", len(data))
    return data


# ── Resolution classification ─────────────────────────────────────────────────

def classify_resolution(messages: List[Dict]) -> Tuple[str, List[str]]:
    """
    Evidence-based multi-state resolution classification.

    CRITICAL CORRECTNESS RULE (corrected in Phase 2 audit):
        CUSTOMER_CONFIRMED is valid ONLY when a customer message containing
        confirmation language appears AFTER the first support intervention.
        A customer saying "Thanks" in their initial tweet is NOT a post-support
        confirmation. The confirming message_id is stored for auditability.

    resolution_status values:
        RESOLVED           — customer explicitly confirmed post-support (strong signal)
        PARTIALLY_RESOLVED — support took concrete action but customer did not confirm,
                             OR gave concrete instructions that ended the conversation
        REDIRECTED         — support redirected to DM / phone / website with no
                             subsequent evidence of actual resolution in this thread
        UNRESOLVED         — conversation ends with an unanswered customer message
        UNKNOWN            — cannot determine from available evidence

    Conservative rules (per spec):
        - "Conversation ended after support reply" alone → UNKNOWN (not RESOLVED)
        - "Please DM us" alone → REDIRECTED (not RESOLVED)
        - "Call this number" alone → REDIRECTED (not RESOLVED)
        - Redirect dominates: if support redirected AND customer then said thanks,
          the resolution happened off-channel → REDIRECTED (not RESOLVED)
    """
    if not messages:
        return "UNKNOWN", ["NO_CLEAR_RESOLUTION"]

    # Sort chronologically for correct before/after detection
    sorted_msgs = sorted(
        messages,
        key=lambda m: (m.get("timestamp") or "0000", m["message_id"]),
    )

    support_msgs  = [m for m in sorted_msgs if m["role"] == "SUPPORT"]
    customer_msgs = [m for m in sorted_msgs if m["role"] == "CUSTOMER"]

    if not support_msgs:
        return "UNRESOLVED", ["NO_CLEAR_RESOLUTION"]

    # Index of first support message in the sorted list
    first_support_idx = next(
        i for i, m in enumerate(sorted_msgs) if m["role"] == "SUPPORT"
    )

    # ── CUSTOMER_CONFIRMED: ONLY valid AFTER the first support message ─────────
    # Messages that appear before first_support_idx are the customer's initial
    # messages; any "thanks" there is politeness, not a resolution confirmation.
    customer_confirmed = False
    confirming_mid: Optional[str] = None
    for m in sorted_msgs[first_support_idx + 1:]:
        if m["role"] == "CUSTOMER" and _CUSTOMER_CONFIRM_RE.search(m["text_clean"]):
            customer_confirmed = True
            confirming_mid = m["message_id"]
            break

    # ── Analyse support messages ───────────────────────────────────────────────
    redirect_found    = False
    action_found      = False
    instruction_found = False

    for msg in support_msgs:
        txt = msg["text_clean"]
        if _REDIRECT_RE.search(txt):
            redirect_found = True
        if _SUPPORT_ACTION_RE.search(txt):
            action_found = True
        if _SUPPORT_INSTRUCTION_RE.search(txt):
            instruction_found = True

    last_msg = sorted_msgs[-1]

    # ── Build evidence list ────────────────────────────────────────────────────
    evidence: List[str] = []

    if last_msg["role"] == "SUPPORT":
        evidence.append("CONVERSATION_ENDED_AFTER_SUPPORT_REPLY")

    if customer_confirmed:
        evidence.append("CUSTOMER_CONFIRMED")
        # Record the exact message that triggered this — auditable
        if confirming_mid:
            evidence.append("CONFIRMED_BY_MSG:" + confirming_mid)

    if action_found:
        evidence.append("SUPPORT_CONFIRMED_ACTION")
    if instruction_found:
        evidence.append("SUPPORT_GAVE_CONCRETE_INSTRUCTION")

    if redirect_found:
        all_support_text = " ".join(m["text_clean"] for m in support_msgs).upper()
        if re.search(r"\bDM\b|DIRECT\s+MESSAGE|PRIVATE\s+MESSAGE|\bPM\s+US\b", all_support_text):
            evidence.append("SUPPORT_REQUESTED_DM")
        else:
            evidence.append("SUPPORT_REDIRECTED_TO_EXTERNAL_CHANNEL")
        evidence.append("SUPPORT_PROVIDED_CONTACT_PATH")

    # ── Classification (conservative) ─────────────────────────────────────────
    # Rule priority:
    #   1. If support redirected → REDIRECTED (redirect dominates even if customer
    #      said "thanks" — the resolution happened off-channel, not here)
    #   2. If customer explicitly confirmed post-support AND no redirect → RESOLVED
    #   3. If support confirmed concrete action (no redirect, no cust confirmation) → PARTIALLY_RESOLVED
    #   4. If support gave concrete instruction (no redirect) and convo ends with support → PARTIALLY_RESOLVED
    #   5. If conversation ends with unanswered customer message → UNRESOLVED
    #   6. Otherwise → UNKNOWN
    if redirect_found:
        # Redirect dominates: any "thanks" from customer after a redirect means
        # they acknowledged the redirect, not that the issue was resolved here.
        status = "REDIRECTED"
    elif customer_confirmed:
        # Post-intervention confirmation with no redirect → genuine resolution
        status = "RESOLVED"
    elif action_found:
        # Support confirmed an action, customer did not confirm
        status = "PARTIALLY_RESOLVED"
    elif instruction_found and last_msg["role"] == "SUPPORT":
        # Support gave concrete instructions, conversation closed by support
        status = "PARTIALLY_RESOLVED"
    elif last_msg["role"] == "CUSTOMER":
        # Conversation ends with unanswered customer message
        status = "UNRESOLVED"
        evidence.append("NO_CLEAR_RESOLUTION")
    else:
        # Support replied but nothing confirmatory or actionable
        status = "UNKNOWN"
        evidence.append("NO_CLEAR_RESOLUTION")

    return status, evidence


# ── Build conversation objects ────────────────────────────────────────────────

def build_message_obj(
    tid: int,
    d: Dict,
    parent_id: Optional[int],
    parent_in_delta: bool,
    child_ids_in_delta: List[int],
) -> Dict:
    """Construct the message-level schema object."""
    text_orig = d.get("text", "")
    inbound   = d["inbound"]
    # Role: always from `inbound`; UNKNOWN only if value is missing/invalid
    if inbound is None:
        role = "UNKNOWN"
    else:
        role = "CUSTOMER" if inbound else "SUPPORT"

    return {
        "message_id":        str(tid),
        "author_id":         d["author_id"],
        "role":              role,
        "inbound":           inbound,
        "timestamp":         d.get("created_at"),
        "text_original":     text_orig,
        "text_clean":        clean_text(text_orig),
        "parent_message_id": str(parent_id) if parent_id is not None else None,
        "child_message_ids": [str(c) for c in sorted(child_ids_in_delta)],
        # parent_missing = we know the parent but it's outside the dataset
        "parent_missing":    (parent_id is not None and not parent_in_delta),
    }


def build_conversations_from_roots(
    delta_roots: Set[int],
    root_to_members: Dict[int, Set[int]],
    delta_data: Dict[int, Dict],
    parent_map: Dict[int, Optional[int]],
    children_from_parent: Dict[int, Set[int]],
    valid_delta_ids: Set[int],
) -> List[Dict]:
    """Assemble one conversation dict per root tweet."""
    conversations: List[Dict] = []

    for root_id in sorted(delta_roots):
        members = root_to_members.get(root_id, {root_id})
        # Keep only members for which we have full data
        present = {tid for tid in members if tid in delta_data}
        if not present:
            continue

        messages: List[Dict] = []
        for tid in present:
            d         = delta_data[tid]
            parent_id = parent_map.get(tid)
            parent_in = parent_id in valid_delta_ids if parent_id is not None else True
            # Children = tweets in this Delta conversation that reference tid as parent
            children  = sorted(children_from_parent.get(tid, set()) & valid_delta_ids)
            messages.append(build_message_obj(tid, d, parent_id, parent_in, children))

        # Sort chronologically; fall back to message_id for stability
        messages.sort(key=lambda m: (m.get("timestamp") or "", m["message_id"]))

        has_cust   = any(m["role"] == "CUSTOMER" for m in messages)
        has_supp   = any(m["role"] == "SUPPORT"  for m in messages)
        has_multi  = len(messages) > 1
        has_both   = has_cust and has_supp
        has_miss   = any(m["parent_missing"] for m in messages)
        # Branching: a tweet has >1 child within this conversation
        has_branch = any(len(m["child_message_ids"]) > 1 for m in messages)
        # Final message is a support reply
        has_final_supp = len(messages) > 0 and messages[-1]["role"] == "SUPPORT"
        is_usable  = has_both and has_multi

        res_status, res_evidence = classify_resolution(messages)

        conv = {
            "conversation_id":           str(root_id),
            "messages":                  messages,
            "message_count":             len(messages),
            "customer_message_count":    sum(1 for m in messages if m["role"] == "CUSTOMER"),
            "support_message_count":     sum(1 for m in messages if m["role"] == "SUPPORT"),
            "unknown_message_count":     sum(1 for m in messages if m["role"] == "UNKNOWN"),
            # Quality flags
            "has_customer_message":           has_cust,
            "has_support_message":            has_supp,
            "has_multiple_messages":          has_multi,
            "has_customer_support_interaction": has_both,
            "has_support_response":           has_supp,
            "has_final_support_message":      has_final_supp,
            "has_missing_parent":             has_miss,
            "has_branching":                  has_branch,
            "is_usable":                      is_usable,
            # Resolution
            "resolution_status":   res_status,
            "resolution_evidence": res_evidence,
            # Split placeholder (filled by split.py)
            "split": None,
        }
        conversations.append(conv)

    return conversations


# ── Relationship validation report ────────────────────────────────────────────

def compute_relationship_stats(
    parent_map:             Dict[int, Optional[int]],
    children_from_parent:   Dict[int, Set[int]],
    children_from_response: Dict[int, List[int]],
    author_inbound_map:     Dict[int, Tuple[str, bool]],
    valid_delta_ids:        Set[int],
    delta_roots:            Set[int],
    cycles_detected:        List[int],
    missing_parent_set:     Set[int],
    pass1_stats:            Dict,
    conversations:          List[Dict],
) -> Dict:
    """Build the relationship_stats.json content."""
    global_ids = set(parent_map.keys())

    # Missing parent links (for Delta tweets only)
    delta_missing_parents = sum(
        1 for tid in valid_delta_ids
        if parent_map.get(tid) is not None and parent_map[tid] not in global_ids
    )

    # Orphan child links: IDs in response_tweet_id that don't exist in global graph
    orphan_response = 0
    for tid, children in children_from_response.items():
        if tid in valid_delta_ids:
            for cid in children:
                if cid not in global_ids:
                    orphan_response += 1

    # Conflicting links: response_tweet_id says "tweet X is a child of me" but
    # X.in_response_to_tweet_id points to a DIFFERENT parent.
    conflicting = 0
    for tid, resp_children in children_from_response.items():
        if tid in valid_delta_ids:
            for cid in resp_children:
                actual_parent = parent_map.get(cid)
                if actual_parent is not None and actual_parent != tid:
                    conflicting += 1

    # Multi-value response rows inside Delta conversations only
    delta_multi_value = sum(
        1 for tid, children in children_from_response.items()
        if tid in valid_delta_ids and len(children) > 1
    )

    branching_convs = sum(1 for c in conversations if c["has_branching"])

    return {
        "brand": BRAND,
        # Global graph metrics
        "global_total_tweets":       len(global_ids),
        "total_parent_links":        pass1_stats["total_parent_links"],
        "total_response_links":      pass1_stats["total_response_links"],
        "global_multi_value_response_rows": pass1_stats["multi_value_response_rows"],
        # in_response_to_tweet_id multi-value audit
        "multi_value_parent_rows_global": pass1_stats["multi_value_parent_rows"],
        "multi_value_parent_extra_links": pass1_stats["multi_value_parent_extra_links_recovered"],
        "multi_value_parent_note": (
            "Confirmed 0 multi-value in_response_to_tweet_id rows in the full dataset. "
            "This field is always a single integer. Only response_tweet_id is multi-valued."
            if pass1_stats["multi_value_parent_rows"] == 0
            else f"WARNING: {pass1_stats['multi_value_parent_rows']} rows with multi-value in_response_to_tweet_id found. "
                 f"Currently only first ID is used as parent. {pass1_stats['multi_value_parent_extra_links_recovered']} extra links may be lost."
        ),
        # Delta-specific
        "delta_tweet_ids":           len(valid_delta_ids),
        "delta_conversation_roots":  len(delta_roots),
        "delta_multi_value_response_rows": delta_multi_value,
        "missing_parent_links":      delta_missing_parents,
        "orphan_child_links":        orphan_response,
        "conflicting_links":         conflicting,
        "cycles_detected":           len(cycles_detected),
        "cycle_tweet_ids":           sorted(cycles_detected)[:20],  # sample
        "branching_conversations":   branching_convs,
        # Phase 1 vs Phase 2 reconciliation
        "phase1_vs_phase2_reconciliation": {
            "phase1_unique_convs": 26052,
            "phase1_usable_convs": 26050,
            "phase2_roots":        len(delta_roots),
            "phase2_usable":       sum(1 for c in conversations if c["is_usable"]),
            "extra_roots_in_phase2": len(delta_roots) - 26052,
            "explanation": (
                "Phase 1 attributed each conversation to the brand with the LOWEST "
                "outbound tweet_id in that conversation ('first responder' heuristic). "
                "Phase 2 includes ANY conversation where Delta has ANY outbound tweet. "
                "The difference (116 conversations) are threads where another brand "
                "(AmericanAir, SouthwestAir, etc.) replied first, but Delta also replied. "
                "These 116 conversations are legitimately Delta conversations that Phase 1 "
                "silently excluded."
            ),
        },
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    if not CSV_PATH.exists():
        log.error("Raw CSV not found at %s — aborting.", CSV_PATH)
        sys.exit(1)

    # ── Phase validation ──────────────────────────────────────────────────────
    log.info("=== Phase 2 — Delta Conversation Reconstruction ===")
    log.info("Brand selected: %s", BRAND)

    # ── Pass 1 ────────────────────────────────────────────────────────────────
    (
        parent_map,
        children_from_parent,
        children_from_response,
        author_inbound_map,
        pass1_stats,
    ) = pass1_build_graph(CSV_PATH)

    valid_ids: Set[int] = set(parent_map.keys())

    # ── Identify Delta outbound tweets ────────────────────────────────────────
    delta_outbound_ids = {
        tid for tid, (author, inbound) in author_inbound_map.items()
        if author == BRAND and not inbound
    }
    log.info("Delta outbound tweet_ids found: %d", len(delta_outbound_ids))

    if not delta_outbound_ids:
        log.error("No outbound tweets for brand '%s' — check brand name.", BRAND)
        sys.exit(1)

    # ── Find conversation roots ───────────────────────────────────────────────
    log.info("Finding conversation roots for %d Delta outbound tweets …", len(delta_outbound_ids))
    root_cache:         Dict[int, int] = {}
    cycles_detected:    List[int]      = []
    missing_parent_set: Set[int]       = set()

    for tid in delta_outbound_ids:
        find_root_iterative(
            tid, parent_map, valid_ids,
            root_cache, cycles_detected, missing_parent_set,
        )

    delta_roots: Set[int] = {root_cache[tid] for tid in delta_outbound_ids if tid in root_cache}
    log.info("Delta conversation roots: %d", len(delta_roots))

    # Resolve roots for root tweets themselves (they may not have been traversed)
    for root_id in list(delta_roots):
        if root_id not in root_cache:
            root_cache[root_id] = root_id

    # ── Collect ALL tweets in Delta conversations (BFS down from each root) ──
    log.info("BFS-collecting all tweets in %d Delta conversations …", len(delta_roots))
    root_to_members: Dict[int, Set[int]] = {}
    all_delta_tweet_ids: Set[int] = set()

    for root_id in delta_roots:
        members = collect_bfs_down(root_id, children_from_parent)
        root_to_members[root_id] = members
        all_delta_tweet_ids |= members

    log.info(
        "Total tweet IDs in Delta conversations: %d (across %d conversations)",
        len(all_delta_tweet_ids),
        len(delta_roots),
    )

    # ── Pass 2: extract full data ─────────────────────────────────────────────
    delta_data = pass2_extract_delta_data(CSV_PATH, all_delta_tweet_ids)

    # ── Confirm raw Delta counts ──────────────────────────────────────────────
    raw_delta_outbound = sum(
        1 for tid in delta_data if not delta_data[tid]["inbound"]
        and delta_data[tid]["author_id"] == BRAND
    )
    raw_customer = sum(1 for d in delta_data.values() if d["inbound"])
    raw_support  = sum(1 for d in delta_data.values() if not d["inbound"])
    log.info(
        "=== Raw Delta message counts (direct from CSV) ===\n"
        "  Total Delta-conversation tweets : %d\n"
        "  Customer (inbound=True)         : %d\n"
        "  Support  (inbound=False)        : %d\n"
        "  Delta-authored support tweets   : %d",
        len(delta_data), raw_customer, raw_support, raw_delta_outbound,
    )

    # ── Build conversation objects ────────────────────────────────────────────
    log.info("Building conversation objects …")
    conversations = build_conversations_from_roots(
        delta_roots, root_to_members, delta_data,
        parent_map, children_from_parent, all_delta_tweet_ids,
    )
    log.info("Conversations built: %d", len(conversations))

    # ── Relationship validation ───────────────────────────────────────────────
    rel_stats = compute_relationship_stats(
        parent_map, children_from_parent, children_from_response,
        author_inbound_map, all_delta_tweet_ids,
        delta_roots, cycles_detected, missing_parent_set,
        pass1_stats, conversations,
    )

    # ── Write outputs ─────────────────────────────────────────────────────────
    log.info("Writing conversations.jsonl …")
    with CONVERSATIONS.open("w", encoding="utf-8") as f:
        for conv in conversations:
            f.write(json.dumps(conv, ensure_ascii=False) + "\n")
    log.info("Wrote %d conversations to %s", len(conversations), CONVERSATIONS)

    with REL_STATS.open("w", encoding="utf-8") as f:
        json.dump(rel_stats, f, indent=2)
    log.info("Wrote relationship stats to %s", REL_STATS)

    # ── Summary print ─────────────────────────────────────────────────────────
    usable = sum(1 for c in conversations if c["is_usable"])
    branching = sum(1 for c in conversations if c["has_branching"])
    has_miss  = sum(1 for c in conversations if c["has_missing_parent"])
    print("\n=== Conversation Reconstruction Summary ===")
    print("  Brand                       : {}".format(BRAND))
    print("  Raw Delta tweet IDs         : {:,}".format(len(delta_data)))
    print("  Customer messages           : {:,}".format(raw_customer))
    print("  Support messages            : {:,}".format(raw_support))
    print("  Conversation roots          : {:,}".format(len(conversations)))
    print("  Usable conversations        : {:,}".format(usable))
    print("  Branching conversations     : {:,}".format(branching))
    print("  Missing-parent conversations: {:,}".format(has_miss))
    print("  Cycles detected             : {:,}".format(len(cycles_detected)))
    print("  Multi-value in_response_to  : {:,} rows (extra links: {:,})".format(
        pass1_stats["multi_value_parent_rows"],
        pass1_stats["multi_value_parent_extra_links_recovered"],
    ))
    res_dist: Dict[str, int] = {}
    for c in conversations:
        res_dist[c["resolution_status"]] = res_dist.get(c["resolution_status"], 0) + 1
    print("  Resolution distribution:")
    for status, cnt in sorted(res_dist.items(), key=lambda x: -x[1]):
        print("    {:<22}: {:,} ({:.1f}%)".format(status, cnt, cnt / len(conversations) * 100))
    print()
    print("=== Phase 1 vs Phase 2 Reconciliation ===")
    print("  Phase 1 unique convs (first-responder attribution) : 26,052")
    print("  Phase 1 usable convs                               : 26,050")
    print("  Phase 2 roots (Delta has ANY outbound tweet)        : {:,}".format(len(delta_roots)))
    print("  Phase 2 usable                                     : {:,}".format(usable))
    print("  Extra roots in Phase 2                             : {:,}".format(len(delta_roots) - 26052))
    print("  Reason: {} conversations where another brand (AmericanAir,".format(len(delta_roots) - 26052))
    print("          SouthwestAir, etc.) replied FIRST, but Delta also replied later.")
    print("          Phase 1 excluded them; Phase 2 correctly includes them.")


if __name__ == "__main__":
    main()
