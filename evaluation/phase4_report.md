# Phase 4 — Intent Classification Baselines

## Training Label Limitation
The raw train split (`train.jsonl`) has no human intent labels. Phase 3 provided a human-labelled 200-example golden set, but this set must remain entirely untouched during training to prevent leakage.
Therefore, the classical supervised baselines evaluated here use rule-derived **pseudo-labels** generated on the train set (using the Phase 3 keyword prioritization rules). The model is learning from these weak labels rather than direct human annotations.
This introduces label noise and potential bias toward the Phase 3 rule system. Therefore, the TF-IDF + Logistic Regression performance on the golden set should be interpreted strictly as a **weakly supervised baseline**, and not as a fully supervised benchmark. It demonstrates how well a classical classifier reproduces human intent labels when trained using weak rule-derived supervision.

## Pseudo-Label Statistics (Train Split)
- Total Train Customer Messages: 31,791
- Pseudo-Labelled Messages: 20,676
- Unlabelled/Dropped Messages: 11,115
- Pseudo-Label Coverage: 65.0%

### Pseudo-Label Distribution:
- `FLIGHT_STATUS_OR_DELAY`: 4,114 (19.9%)
- `COMPLAINT_OR_FEEDBACK`: 3,843 (18.6%)
- `CHECKIN_OR_BOARDING`: 2,435 (11.8%)
- `SCHEDULE_OR_BOOKING_INQUIRY`: 1,904 (9.2%)
- `SEAT_OR_UPGRADE`: 1,896 (9.2%)
- `BAGGAGE_ISSUE`: 1,866 (9.0%)
- `CANCEL_OR_CHANGE_FLIGHT`: 1,206 (5.8%)
- `SKYMILES_OR_LOYALTY`: 1,140 (5.5%)
- `PAYMENT_OR_CHARGE_DISPUTE`: 797 (3.9%)
- `REFUND_OR_COMPENSATION`: 723 (3.5%)
- `ACCOUNT_ACCESS`: 486 (2.4%)
- `SPECIAL_ASSISTANCE`: 266 (1.3%)

## Baseline Comparison
| Model | Input | Accuracy | Macro-F1 | Weighted-F1 |
|---|---|---:|---:|---:|
| Majority Pseudo-Label | — | 0.1550 | 0.0224 | 0.0416 |
| TF-IDF + LR | Current message | 0.3450 | 0.3527 | 0.3387 |
| TF-IDF + LR | Message + context | 0.3450 | 0.3543 | 0.3373 |

**Note on ACCOUNT_ACCESS**: `ACCOUNT_ACCESS` is explicitly marked as **NOT EVALUATED** because it has 0 examples in the golden set. It has been excluded from the Macro-F1 calculation to avoid fabricating a score or silently distorting the metric.

## Leakage Audit Verification
- **Golden Example Leakage**: ZERO golden examples/IDs used for training.
- **Golden Label Leakage**: ZERO golden labels used for training.
- **Future Response Leakage**: Only context *prior* to the customer message was included. Future support responses were explicitly excluded.
- **Metadata Leakage**: No resolution status or human labels were included in training features.

## Error Analysis (Baseline B: Current Message)
Focusing on representative failure cases from the golden set.

### FLIGHT_STATUS_OR_DELAY vs SCHEDULE_OR_BOOKING_INQUIRY
- **ID**: G0029
- **Message**: "Still in #MSP airport . My @delta flight is now 13 HOURS DELAYED 🤬 I really feel sorry for the families here with small children"
- **True Intent**: `FLIGHT_STATUS_OR_DELAY`
- **Predicted**: `SCHEDULE_OR_BOOKING_INQUIRY`
- **Explanation**: The baseline relied on lexical keyword overlap without understanding the semantic nuance, leading to misclassification.

### COMPLAINT_OR_FEEDBACK vs actionable
- **ID**: G0001
- **Message**: "Shout out to @Delta for Flight DL445 from Fiumicino. Best. Crew. Ever!! Thanks Pam, Susan, Cheryl &amp; Gil for a great ending to our trip!"
- **True Intent**: `COMPLAINT_OR_FEEDBACK`
- **Predicted**: `FLIGHT_STATUS_OR_DELAY`
- **Explanation**: The baseline relied on lexical keyword overlap without understanding the semantic nuance, leading to misclassification.

### BAGGAGE_ISSUE vs PAYMENT
*No exact failure cases for this pattern found in the predictions.*

### REFUND vs PAYMENT
- **ID**: G0086
- **Message**: "@delta, what is your policy for refunding due to inability to travel to and from STT?  Please advise."
- **True Intent**: `REFUND_OR_COMPENSATION`
- **Predicted**: `PAYMENT_OR_CHARGE_DISPUTE`
- **Explanation**: The baseline relied on lexical keyword overlap without understanding the semantic nuance, leading to misclassification.

### Context Changes Interpretation
- **ID**: G0054
- **Message**: "@Delta, y’all continue to spoil me with your surprise seats upgrades 🤗. Happy Thanksgiving to you and especially those staff working to get others to their destination today. ✈️"
- **True Intent**: `COMPLAINT_OR_FEEDBACK`
- **Without Context Predicted**: `SEAT_OR_UPGRADE`
- **With Context Predicted**: `COMPLAINT_OR_FEEDBACK`
- **Explanation**: The context baseline correctly recovered the true intent by including prior conversation turns, demonstrating the value of dialog history.
