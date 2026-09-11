# Engineering Decision Log

1. **Decision**: Select Delta Airlines (`@Delta`) as the single target brand.
   - **Alternatives**: @AppleSupport, @Uber_Support.
   - **Why chosen**: High volume of complex support interactions involving refunds, real-time schedule changes, and baggage issues, providing a stringent test environment for safety validation.
   - **Evidence/Trade-off**: High density of sensitive intents, though it required strict deduplication and specific conversation threading.

2. **Decision**: Thread conversations by `in_response_to_tweet_id` to root.
   - **Alternatives**: Treat every tweet as an isolated message.
   - **Why chosen**: Customer support fundamentally requires context. 
   - **Evidence/Trade-off**: Slower processing time, but crucial for accurately retrieving prior context in generative LLM prompts.

3. **Decision**: 70/15/15 Chronological Train/Dev/Test Split.
   - **Alternatives**: Pure random split.
   - **Why chosen**: Chronological splitting prevents information leakage where future knowledge (e.g. flight delays) artificially influences training or evaluation.
   - **Evidence/Trade-off**: Reduced evaluation scores on unseen events, but drastically higher methodological integrity.

4. **Decision**: Enforce a 12-Intent Taxonomy.
   - **Alternatives**: Open-ended LLM intent inference or massive 50+ intent trees.
   - **Why chosen**: A constrained, distinct list allows for manageable deterministic routing and robust unit-testing.
   - **Evidence/Trade-off**: Simplifies policy enforcement but risks shoehorning ambiguous requests into the `COMPLAINT_OR_FEEDBACK` or `AMBIGUOUS_OR_INSUFFICIENT_CONTEXT` bucket.

5. **Decision**: Reserve the 200 Golden Intent labels entirely for evaluation.
   - **Alternatives**: Train heuristics on the golden labels.
   - **Why chosen**: Ensures unbiased benchmarking of baseline models versus the LLM. 
   - **Evidence/Trade-off**: Relegated the heuristic baselines (TF-IDF + LR) to weak supervision (pseudo-labels), depressing baseline scores but maintaining dataset integrity.

6. **Decision**: TF-IDF retrieval for historical evidence.
   - **Alternatives**: Semantic embedding vector DB (e.g., FAISS + MiniLM).
   - **Why chosen**: Rapid prototyping and transparent debuggability without extensive local model hosting.
   - **Evidence/Trade-off**: Fast, but struggles significantly with semantic similarity (e.g., "bag lost" vs "luggage missing").

7. **Decision**: Treat historical evidence purely as DATA, not instructions.
   - **Alternatives**: Feed retrieved responses as few-shot examples or direct rules.
   - **Why chosen**: Protects against LLM hallucination and policy drift. If an old tweet wrongly authorized a $500 refund, the LLM must not blindly copy the action.
   - **Evidence/Trade-off**: Required writing extensive post-generation validation checks.

8. **Decision**: Utilize `sarvam-105b` with strict reasoning-effort schemas for generation.
   - **Alternatives**: Zero-shot vanilla generation.
   - **Why chosen**: Forcing the model to output a structured JSON schema with a specific `reasoning` field drastically improved reliability.
   - **Evidence/Trade-off**: Schema generation achieved 99.5% success, though it introduced 0.5% failure fallback.

9. **Decision**: Deterministic Post-Generation Validator.
   - **Alternatives**: Rely entirely on the LLM's internal system prompt to follow safety rules.
   - **Why chosen**: LLMs are mathematically incapable of 100% adherence to financial policies. The system must hard-block unauthorized substrings.
   - **Evidence/Trade-off**: Intercepted 100% of tested policy violations.

10. **Decision**: Require Verification mapping for `CANCEL_OR_CHANGE_FLIGHT`.
    - **Alternatives**: Allow informational auto-handling for flight change inquiries.
    - **Why chosen**: Flight changes inherently demand secure booking access, which the prototype lacks.
    - **Evidence/Trade-off**: Vastly improved safety (dropping unsafe auto-handles from 78.3% to 56.7%), at the acceptable cost of increased false escalations.

11. **Decision**: Implement a 0.60 heuristic confidence threshold.
    - **Alternatives**: No confidence threshold, trust highest logit/probability.
    - **Why chosen**: Forces routing to human escalation when the LLM is uncertain about the customer's intent.
    - **Evidence/Trade-off**: Acts as a blanket safety net but requires manual calibration against a labeled dataset to optimize perfectly.

12. **Decision**: Independent LLM-vs-LLM Agreement robustness check.
    - **Alternatives**: Fabricate human ratings or blindly trust the single LLM-as-judge.
    - **Why chosen**: Strict adherence to honest methodology. Time constraints prevented manual review of 30 cases, so an explicit limitation was documented alongside a second-LLM check.
    - **Evidence/Trade-off**: Showed 0.00 Spearman correlation, confirming that LLM-as-judge metrics are unreliable without true human alignment validation.
