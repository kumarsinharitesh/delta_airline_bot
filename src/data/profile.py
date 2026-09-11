"""
profile.py — Brand profiler for the Kaggle "Customer Support on Twitter" dataset.

Usage:
    python src/data/profile.py \
        --input  dataset_raw/twcs/twcs.csv \
        --output data/brand_profile.csv

The script reads the CSV in chunks (memory-safe), then performs a second
full-pass to reconstruct conversation threads and compute per-brand metrics.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

import pandas as pd

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CSV_PATH_DEFAULT = Path("dataset_raw/twcs/twcs.csv")
OUTPUT_PATH_DEFAULT = Path("data/brand_profile.csv")
CHUNK_SIZE = 200_000

USECOLS = [
    "tweet_id",
    "author_id",
    "inbound",
    "created_at",
    "text",
    "response_tweet_id",
    "in_response_to_tweet_id",
]


# ---------------------------------------------------------------------------
# Pass 1 — Discover brands and load relevant rows
# ---------------------------------------------------------------------------

def discover_brands(csv_path: Path) -> Set[str]:
    """Return the set of author_ids that appear as outbound (support agents)."""
    brands: Set[str] = set()
    log.info("Pass 1a — discovering brand accounts ...")
    for i, chunk in enumerate(
        pd.read_csv(csv_path, usecols=["author_id", "inbound"],
                    chunksize=CHUNK_SIZE, dtype={"author_id": str})
    ):
        outbound = chunk[chunk["inbound"] == False]
        brands.update(outbound["author_id"].dropna().unique())
        if i % 5 == 0:
            log.info("  ... chunk %d processed, brands seen so far: %d", i, len(brands))
    log.info("Discovered %d brand accounts.", len(brands))
    return brands


def load_full_dataset(csv_path: Path) -> pd.DataFrame:
    """Read the full CSV into memory in chunks."""
    log.info("Pass 1b — loading full dataset into memory ...")
    chunks: List[pd.DataFrame] = []
    total_rows = 0
    for i, chunk in enumerate(
        pd.read_csv(
            csv_path,
            usecols=USECOLS,
            chunksize=CHUNK_SIZE,
            dtype={
                "tweet_id": "Int64",
                "author_id": str,
                "inbound": bool,
                "text": str,
                # These columns can contain comma-separated lists; keep as str
                "response_tweet_id": str,
                "in_response_to_tweet_id": str,
            },
        )
    ):
        chunks.append(chunk)
        total_rows += len(chunk)
        if i % 5 == 0:
            log.info("  ... loaded %d rows so far ...", total_rows)

    df = pd.concat(chunks, ignore_index=True)
    # in_response_to_tweet_id may be a string like "5,7"; take the first number only
    df["in_response_to_tweet_id"] = (
        df["in_response_to_tweet_id"]
        .astype(str)
        .str.split(",")
        .str[0]
        .pipe(pd.to_numeric, errors="coerce")
    )
    log.info("Dataset loaded: %d rows, %d columns.", len(df), len(df.columns))
    return df


# ---------------------------------------------------------------------------
# Pass 2 — Conversation reconstruction
# ---------------------------------------------------------------------------

def build_conversation_map(df: pd.DataFrame) -> pd.Series:
    """
    Walk the reply graph to assign a root tweet_id (conversation_id) to every row.
    Uses iterative path compression to avoid recursion limits.
    """
    log.info("Building conversation map ...")

    # Build parent dict
    parent: Dict[int, Optional[int]] = {}
    for row in df[["tweet_id", "in_response_to_tweet_id"]].itertuples(index=False):
        tid = int(row[0]) if pd.notna(row[0]) else None
        pid = int(row[1]) if pd.notna(row[1]) else None
        if tid is not None:
            parent[tid] = pid

    valid_ids: Set[int] = set(parent.keys())
    roots: Dict[int, int] = {}

    def find_root_iterative(start: int) -> int:
        path: List[int] = []
        cur = start
        while True:
            if cur in roots:
                root = roots[cur]
                break
            p = parent.get(cur)
            if p is None or p not in valid_ids:
                root = cur
                break
            path.append(cur)
            cur = p
            if len(path) > 500:
                root = cur
                break
        # path compression
        for node in path:
            roots[node] = root
        roots[start] = root
        return root

    log.info("Resolving roots for %d tweets ...", len(valid_ids))
    for tid in valid_ids:
        if tid not in roots:
            find_root_iterative(tid)

    log.info("Conversation map built.")
    conv_ids = df["tweet_id"].apply(
        lambda tid: roots.get(int(tid), int(tid)) if pd.notna(tid) else None
    )
    return conv_ids


# ---------------------------------------------------------------------------
# Pass 3 — Per-brand metrics
# ---------------------------------------------------------------------------

def profile_brand(brand_df: pd.DataFrame) -> Dict:
    """Compute quality metrics for a single brand's slice of the dataset."""
    total_tweets = len(brand_df)
    customer_tweets = int(brand_df["inbound"].sum())
    support_tweets = total_tweets - customer_tweets

    conv_groups = brand_df.groupby("conversation_id")
    unique_convs = conv_groups.ngroups

    # Conversations with both a customer tweet and a support tweet
    has_both = conv_groups["inbound"].agg(
        lambda x: x.any() and (~x).any()
    )
    usable_convs = int(has_both.sum())

    # Conversation lengths
    conv_lengths = conv_groups["tweet_id"].count()
    avg_turns = float(conv_lengths.mean()) if len(conv_lengths) > 0 else 0.0
    median_turns = float(conv_lengths.median()) if len(conv_lengths) > 0 else 0.0

    pct_with_support = (usable_convs / unique_convs * 100) if unique_convs > 0 else 0.0

    # Heuristic "resolved": last tweet in conversation is outbound (brand closes it)
    last_inbound = conv_groups["inbound"].last()
    resolved_convs = int((last_inbound == False).sum())
    pct_resolved = (resolved_convs / unique_convs * 100) if unique_convs > 0 else 0.0

    # Usable customer messages in usable conversations
    usable_conv_ids = set(has_both[has_both].index)
    usable_customer_msgs = int(
        brand_df[
            brand_df["inbound"] & brand_df["conversation_id"].isin(usable_conv_ids)
        ].shape[0]
    )

    # DQ
    missing_text = int(brand_df["text"].isna().sum())
    missing_in_reply = int(brand_df["in_response_to_tweet_id"].isna().sum())
    dup_ids = int(brand_df["tweet_id"].duplicated().sum())

    return {
        "total_tweets": total_tweets,
        "customer_tweets": customer_tweets,
        "support_tweets": support_tweets,
        "unique_conversations": unique_convs,
        "usable_conversations": usable_convs,
        "resolved_conversations": resolved_convs,
        "avg_turns": round(avg_turns, 2),
        "median_turns": round(median_turns, 2),
        "pct_with_support_response": round(pct_with_support, 1),
        "pct_resolved": round(pct_resolved, 1),
        "usable_customer_msgs": usable_customer_msgs,
        "missing_text": missing_text,
        "missing_in_reply_to": missing_in_reply,
        "duplicate_tweet_ids": dup_ids,
    }


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def run(csv_path: Path, output_path: Path) -> pd.DataFrame:
    brands = discover_brands(csv_path)

    df = load_full_dataset(csv_path)

    log.info("=== Global DQ Check ===")
    log.info("  Total rows      : %d", len(df))
    log.info("  Inbound (cust)  : %d", int(df["inbound"].sum()))
    log.info("  Outbound (brand): %d", int((~df["inbound"]).sum()))
    log.info("  Missing text    : %d", int(df["text"].isna().sum()))
    log.info("  Dup tweet_ids   : %d", int(df["tweet_id"].duplicated().sum()))
    log.info("  Missing in_resp : %d", int(df["in_response_to_tweet_id"].isna().sum()))

    df["conversation_id"] = build_conversation_map(df)

    log.info("Tagging brand affiliation per conversation ...")
    outbound = df[~df["inbound"]]
    # Take the first brand that responded in each conversation
    conv_to_brand = (
        outbound.sort_values("tweet_id")
        .groupby("conversation_id")["author_id"]
        .first()
    )
    df["brand"] = df["conversation_id"].map(conv_to_brand)

    records: List[Dict] = []
    log.info("Profiling %d brands ...", len(brands))
    for brand in sorted(brands):
        brand_df = df[df["brand"] == brand].copy()
        if len(brand_df) == 0:
            log.warning("  Brand %s: no rows found, skipping.", brand)
            continue
        metrics = profile_brand(brand_df)
        metrics["brand"] = brand
        records.append(metrics)
        log.info(
            "  %-25s  tweets=%6d  convs=%5d  usable=%5d  resolved=%5d  avg_turns=%.1f",
            brand,
            metrics["total_tweets"],
            metrics["unique_conversations"],
            metrics["usable_conversations"],
            metrics["resolved_conversations"],
            metrics["avg_turns"],
        )

    col_order = [
        "brand", "total_tweets", "customer_tweets", "support_tweets",
        "unique_conversations", "usable_conversations", "resolved_conversations",
        "avg_turns", "median_turns", "pct_with_support_response", "pct_resolved",
        "usable_customer_msgs", "missing_text", "missing_in_reply_to", "duplicate_tweet_ids",
    ]
    result_df = pd.DataFrame(records)[col_order].sort_values(
        "usable_conversations", ascending=False
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(output_path, index=False)
    log.info("Profiling results saved to: %s", output_path)
    return result_df


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",  type=Path, default=CSV_PATH_DEFAULT)
    p.add_argument("--output", type=Path, default=OUTPUT_PATH_DEFAULT)
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if not args.input.exists():
        log.error(
            "Dataset file not found: %s\n"
            "Please download the Kaggle dataset 'thoughtvector/customer-support-on-twitter' "
            "and place twcs.csv at that path.",
            args.input,
        )
        sys.exit(1)
    result = run(args.input, args.output)
    print("\n=== Top 20 brands by usable conversations ===")
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 180)
    print(result.head(20).to_string(index=False))
