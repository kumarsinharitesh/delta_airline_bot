# Golden Set Sampling Plan
# Phase 3 — Delta Customer Support Intent Classification

---

## Objective

Sample ~200 examples from the **dev and test splits only** for manual intent
annotation, forming the golden evaluation set.

This set is used in Phase 4 to evaluate intent classifiers.

---

## Sampling Unit

Each example = **one customer message** from one conversation.

At most **1 example per conversation** (strict).

This avoids high correlation between examples from the same conversation.

---

## Source Split

| Split | Purpose |
|---|---|
| **train** | EXCLUDED — used for model training, must not contaminate evaluation |
| **dev** | Included |
| **test** | Included |

Leakage guard: `get_train_conversation_ids()` in `sample_golden.py` loads all
train conversation IDs and filters them out before any sampling.

---

## Sampling Strategy

**Stratified by `resolution_status`** (proxy for conversation type diversity):

| Stratum | Available in dev+test | Target | Rationale |
|---|---|---|---|
| UNKNOWN | 4,477 | 70 | Largest group; covers social + ambiguous + general complaints |
| REDIRECTED | 2,123 | 55 | Represents "support redirected to DM/phone"; diverse issues |
| RESOLVED | 623 | 25 | High-quality conversations; CUSTOMER_CONFIRMED post-support |
| UNRESOLVED | 492 | 25 | Escalation-prone conversations |
| PARTIALLY_RESOLVED | 136 | 25 | Support gave instruction but unconfirmed; policy queries |
| **TOTAL** | **7,851** | **200** | |

---

## Message Selection Within Each Stratum

1. For each conversation, prefer the **first customer message** (chronological order)
   — it captures the customer's initial intent most cleanly.
2. If the first message is too short (<10 characters after removing @mentions),
   fall back to the second customer message.
3. If no usable customer message exists, skip the conversation.

---

## Random Seed

**Seed = 42** (set on `random.Random` instance; fully deterministic).

---

## Inclusion Criteria

- Conversation must be `is_usable = True`
- Source must be dev or test (not train)
- Customer message must have >10 characters of content (excluding @mentions)
- At most 1 example per `conversation_id`

## Exclusion Criteria

- Any conversation whose `conversation_id` appears in train split
- Non-usable conversations
- Customer messages with <10 content characters

---

## Target Count

**200 examples exactly** (as produced by `python -m src.intents.sample_golden`).

---

## Comparison: Sampling Distribution vs Train Distribution

| resolution_status | Train % | Golden sample % |
|---|---|---|
| UNKNOWN | 56.7% | 35.0% |
| REDIRECTED | 27.4% | 27.5% |
| RESOLVED | 7.8% | 12.5% |
| UNRESOLVED | 6.3% | 12.5% |
| PARTIALLY_RESOLVED | 1.9% | 12.5% |

The golden set deliberately **over-represents** RESOLVED, UNRESOLVED,
and PARTIALLY_RESOLVED to ensure coverage of edge cases and safety-sensitive
conversations in evaluation.

---

## Script

```bash
python -m src.intents.sample_golden
```

Output: `data/golden_unlabeled.csv`

Manual annotation then follows using `data/annotation_guide.md`.

Final labeled output: `evaluation/golden_set.csv`
