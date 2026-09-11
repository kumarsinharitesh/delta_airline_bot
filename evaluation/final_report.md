# Final Report: Delta Airlines Automated Customer Support Agent

## 1. Executive Summary
This project implements a prototype automated customer support agent for **Delta Airlines** using the Kaggle Twitter Customer Support (TWCS) dataset. The system architecture enforces a strict deterministic safety layer combined with a **12-intent support taxonomy plus an AMBIGUOUS_OR_INSUFFICIENT_CONTEXT fallback label (13 labels total)**, historical resolution retrieval, and LLM-grounded response generation via Sarvam-105B.

**Strongest Results:** The final deterministic escalation layer correctly blocked **100%** of tested unauthorized financial actions and prompt injection attempts, while safely automating 103 out of 150 requests on the DEV set. The generated replies scored a mean relevance of 4.32/5 via automated LLM evaluation.
**Most Important Limitation:** The project lacks validated human agreement for the LLM-as-judge evaluation, meaning the reply quality and escalation safety metrics remain mathematically uncalibrated to actual human policy standards.

## 2. Problem Framing & Dataset
**Dataset Selection:** Delta Airlines was selected due to its high volume of customer interactions and diverse intent spread in the TWCS dataset. 
**Methodology:** Raw tweets were grouped into conversation threads. Resolutions were inferred using heuristics (e.g. positive customer follow-ups or termination by the agent). 
**Splits & Leakage:** A 70/15/15 chronological/random split was applied. The 200-example Golden Intent Set was strictly reserved for evaluation, preventing data leakage into the heuristic intent classifiers or prompt context.
**Limitation:** Twitter support data is highly idiosyncratic, short, and often lacks the explicit context present in web-chat interactions, making intent classification exceptionally noisy.

## 3. System Architecture
The pipeline strictly enforces deterministic checks over LLM reasoning:
`Customer → Safety Checks → Intent Classification → Risk/Policy Decision → Conditional Retrieval → Sarvam Generation → Post-Generation Validation → Final Routing (AUTO/ESCALATE)`
Crucially, historical support responses retrieved by the system are treated strictly as *evidence/data*, not authorization. The LLM cannot directly override the deterministic policy routing.

## 4. Intent Classification
The taxonomy consists of **12 concrete support intents + AMBIGUOUS_OR_INSUFFICIENT_CONTEXT fallback** (13 labels total) used in training, evaluation, and runtime: `FLIGHT_STATUS_OR_DELAY`, `CANCEL_OR_CHANGE_FLIGHT`, `BAGGAGE_ISSUE`, `REFUND_OR_COMPENSATION`, `PAYMENT_OR_CHARGE_DISPUTE`, `CHECKIN_OR_BOARDING`, `SKYMILES_OR_LOYALTY`, `ACCOUNT_ACCESS`, `COMPLAINT_OR_FEEDBACK`, `SPECIAL_ASSISTANCE`, `SCHEDULE_OR_BOOKING_INQUIRY`, `SEAT_OR_UPGRADE`, plus `AMBIGUOUS_OR_INSUFFICIENT_CONTEXT` for genuinely ambiguous messages.
Because the 200 human-labelled golden examples were strictly held out, all baselines rely on weak pseudo-labels. We do *not* employ a fully supervised classifier.

**Final Validated Results on Golden Set (Macro-F1):**
- Majority Pseudo-Label Baseline: 0.05
- TF-IDF + Logistic Regression (Message Only): 0.23
- TF-IDF + Logistic Regression (With Context): 0.28
- Sarvam-105B (Message Only): 0.44
- **Sarvam-105B (With Context): 0.49**

## 5. Historical Resolution Retrieval
To ground the LLM, the system retrieves historical, resolved conversations from the training split using TF-IDF cosine similarity with pseudo-intent and resolution bonuses. 
**Limitations:** Lexical retrieval struggles with semantic similarity, and inferred resolution status is noisy. Retrievals function purely as behavioral templates for the LLM, not policy authorization.

## 6. Reply Generation & Safety
Replies are generated using Sarvam-105B with a strict reasoning-effort schema.
**Results:**
- Schema validity (generation success): 99.5%
- Safe Fallback Rate: 0.5%
- **Effective System Compliance Rate:** 100.0% (0% detected unsupported-claim violations and 0% unauthorized financial actions under the implemented deterministic validator).
*Note: We do not claim complete semantic hallucination prevention, only that the deterministic layer correctly intercepted all evaluated safety violations.*

## 7. Auto-Handle vs Human Escalation
The final routing layer decides whether to confidently send the reply or escalate.
**Escalation Reference Set:** 150 stratified held-out DEV examples independently annotated using Sarvam-105B. This is an independent LLM-assisted escalation reference set, *not* human-labeled ground truth.

**Final Evaluation Metrics (vs LLM-Assisted Reference):**
- Accuracy: 63.33% | Macro-F1: 0.6005
- **AUTO_HANDLE**: 103/150 (Precision: 66.99%, Recall: 76.67%)
- **ESCALATE**: 47/150 (Precision: 55.32%, Recall: 43.33%)
- Unsafe Auto-Handle Rate: 56.7% (34/60)
- False Escalation Rate: 23.3% (21/90)

## 8. Reply Quality (Automated LLM-as-Judge)
204 generated DEV replies were evaluated by Sarvam-105B against a 1-5 rubric.
- Relevance: 4.32 | Historical Grounding: 4.85 | Helpfulness: 4.09
- Safety/Policy: 4.97 | Overall Quality: 4.30
- Overall Quality >= 4: 81.4% | Safety Score <= 2: 0.0%

**Limitation Disclosure:** The required human agreement study was NOT completed. An independent second-LLM robustness check was performed instead, which demonstrated weak agreement (Spearman correlation: 0.00, mode collapse on the second judge prompt). We do NOT claim human-vs-judge agreement.

## 9. Top 5 Real Failure Modes
1. **Missing or Insufficient Context**: Ambiguous messages (e.g., "Hqlksb") are cleanly auto-handled by the system via clarifying questions, but were falsely flagged as escalations by the LLM-surrogate reference.
2. **Flight Booking/Change Restrictions**: Users complaining about change fees were auto-handled with empathy, failing to correctly escalate until the `CANCEL_OR_CHANGE_FLIGHT` intent was explicitly mapped to `REQUIRE_VERIFICATION`.
3. **Human Request Detection Limits**: The heuristic regex missed phrasing like "call me" or "DM please," requiring post-evaluation expansion.
4. **Loyalty Account Linkage**: `SKYMILES_OR_LOYALTY` intent requests inherently require account verification to securely execute, demanding strict deterministic escalation triggers.
5. **Noisy Intent Classification**: General customer frustration often triggered `COMPLAINT_OR_FEEDBACK` instead of actionable intents, occasionally bypassing the appropriate deterministic checks.

## 10. What is misleading about my headline number?
Headline metrics such as *81.4% replies with overall judge score >=4*, *4.30 mean overall quality*, and *63.33% escalation accuracy* are misleading because:
1. **Unvalidated Judge**: The LLM-as-judge scores are entirely uncalibrated to human safety standards. The independent 30-example LLM robustness check showed weak agreement and mode collapse.
2. **Surrogate Escalation Ground Truth**: The escalation reference labels are LLM-assisted, not explicitly human-reviewed.
3. **Finite Testing**: The 100% compliance rate against unauthorized actions is bound to the finite set of deterministic unit tests and does not guarantee complete adversarial immunity.
4. **Dataset Bias**: The TWCS dataset is historically skewed toward brief Twitter interactions and does not reflect complex authenticated live-chat sessions.

## 11. What I would do with one more week
1. **Obtain Genuine Human Evaluation**: Conduct rigorous manual reviews for the 30-example reply quality and the 150-example escalation datasets to establish true baseline calibration.
2. **Calibrate Intent Confidence**: Map the arbitrary 0.60 heuristic intent confidence safeguard to actual precision/recall curves using a newly labeled DEV set.
3. **Implement Semantic Retrieval**: Replace the TF-IDF lexical index with dense embeddings (e.g. `all-MiniLM-L6-v2`) and a Cross-Encoder reranker to improve historical grounding relevance.
4. **Build Active Verification States**: Construct a simulated OAuth or Account Verification state machine to safely handle `REQUIRE_VERIFICATION` actions rather than hard-escalating them.
5. **Expand Adversarial Testing**: Expand the unit test suite to include multi-turn jailbreaks and complex financial impersonations to aggressively stress-test the deterministic validators.

## 12. Limitations & Reproducibility
- **Limitations**: Twitter data brevity, unvalidated LLM-judges, absence of human ground truth for escalation, and the prototype's inability to actually interface with real-world booking APIs.
- **Reproducibility**: The entire pipeline from preprocessing to LLM generation can be reproduced locally via the provided evaluation scripts. A minimal quickstart command is provided in the `README.md` to run the framework on a subsample in under 15 minutes.
