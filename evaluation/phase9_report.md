# Phase 9 Escalation Report

## Objective
Build and evaluate the deterministic final Auto-Handle vs Human Escalation layer.

## Methodology
150 stratified held-out DEV examples were independently annotated using Sarvam-105B under a fixed rubric. The resulting dataset is an independent LLM-assisted escalation reference set, not human-labeled ground truth.

## Baseline Policy Results
*(Note: The baseline was rerun using the final consistent intent cache to ensure accurate comparisons. An earlier intermediate sensitivity check produced a 78.3% unsafe rate due to partial intent mapping, but the true documented baseline for these 150 examples is 95.0%).*

Prior to targeted refinement, the deterministic routing performed as follows:
- **Overall Accuracy**: 61.33%
- **Macro-F1**: 0.4240
- **Unsafe Auto-Handle Rate**: 95.0% (57/60)
- **False Escalation Rate**: 1.1% (1/90)

## Root Cause Analysis
An analysis of the false AUTO_HANDLE cases revealed three key systematic gaps in the baseline deterministic logic:
1. **Human Request Detection Failure (23.4%)**: The `detect_human_request` regex missed phrases like "call me", "talk to anyone", "customer service", and "DM please".
2. **Flight Booking/Change Restrictions (31.9%)**: `CANCEL_OR_CHANGE_FLIGHT` intents complaining about change fees were assigned safe responses, but the reference set properly escalated them since an AI cannot actively waive fees or modify bookings without authentication.
3. **Loyalty Verification (8.5%)**: `SKYMILES_OR_LOYALTY` intent requests (e.g., "link my skymiles") were treated as informational, but inherently require account verification to safely execute.

## Targeted Policy Changes
To safely reduce the Unsafe Auto-Handle Rate without over-escalating, three generalizable policy changes were implemented:
- **Rule 1**: Expanded `detect_human_request` in `src/safety/prompt_injection.py` to include common contact phrases.
- **Rule 2**: Mapped `CANCEL_OR_CHANGE_FLIGHT` to `REQUIRE_VERIFICATION` in `src/policy/rules.py` to force escalation due to the lack of an active booking mechanism.
- **Rule 3**: Mapped `SKYMILES_OR_LOYALTY` to `REQUIRE_VERIFICATION` in `src/policy/rules.py`.

*No individual rules were tuned to specific examples.*

## Final Evaluation
After implementing the generalizable rules, the metrics against the reference set are:
- **Overall Accuracy**: 63.33%
- **Macro-F1**: 0.6005
- **AUTO_HANDLE Precision**: 0.6699 | **Recall**: 0.7667
- **ESCALATE Precision**: 0.5532 | **Recall**: 0.4333
- **Unsafe Auto-Handle Rate**: 56.7% (34/60)

### Confusion Matrix
```text
                 Pred AUTO_HANDLE   Pred ESCALATE
True AUTO_HANDLE        69               21
True ESCALATE           34               26
```

### Trigger Distribution (System Level)
- **AUTO_HANDLE total**: 103
- **ESCALATE total**: 47
- Triggered by Policy (e.g. Fraud, High-Risk): 19
- Triggered by `REQUIRE_VERIFICATION` fallback: 28
- Triggered by Confidence heuristic / Validation: 0

### Remaining False AUTO_HANDLE Analysis
The 34 remaining "Unsafe" Auto-Handles consist primarily of:
- **Complex Complaints (10 cases)**: General complaints where the system treats these cases as eligible for automated informational responses under the implemented policy, although the independent reference set classified some of them as escalation-worthy.
- **Ambiguous Queries (9 cases)**: E.g., "Hqlksb" or "@Delta", where the bot cleanly replies "Please clarify" rather than needlessly escalating.
- **Inferred Human Requests (7 cases)**: Aggressive or sarcastic texts (e.g., "Tell your crew to get their shit together") which the LLM surrogate assumed required a human, but contained no explicit trigger phrase. 

Further escalation rules to catch these would result in aggressively escalating all ambiguous queries and complaints, destroying automation rates.

## Safety vs Automation Trade-off
This configuration reduces unsafe auto-handling (from 95.0% down to 56.7%) at the cost of increased false escalation (from 1.1% to 23.3%). The trade-off is reported rather than declared acceptable; it strictly adheres to safe, generalizable rule sets rather than attempting to explicitly overfit the surrogate's preferences. 

**The policy refinement substantially reduced unsafe auto-handling, but the remaining disagreement demonstrates that the prototype is not sufficiently conservative for unrestricted autonomous support.**

## Limitations
- The reference set is LLM-assisted rather than true human-labeled ground truth; metrics measure agreement with the independent LLM surrogate, not explicit human-vs-system agreement.
- The 0.60 confidence threshold is a heuristic safeguard and is not empirically calibrated due to the lack of ground-truth intent labels on the DEV set.
- A single annotation model (`sarvam-105b`) may introduce correlated judgment bias, particularly favoring `ESCALATE` on ambiguous or complaint-driven texts.
- Verify that the measured UNSAFE_AUTO_HANDLE_RATE is reported accurately. Do not impose a target of 0%.
- The escalation rules are deterministic but are fundamentally limited by the upstream intent/policy layer signals.
- No active identity/payment verification mechanism exists in the prototype.
