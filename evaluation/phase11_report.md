# Phase 11: Reply Quality Evaluation

## 1. Objective
Evaluate the semantic quality, relevance, helpfulness, and safety of the generated support replies using an independent LLM-as-judge, and prepare for human agreement validation.

## 2. LLM-as-Judge Automated Metrics
204 generated replies from the DEV subset were evaluated using `sarvam-105b` against a rigorous 1-5 rubric.

- **Judge Model**: `sarvam-105b`
- **Total Evaluated Replies**: 204
- **Mean Relevance**: 4.32
- **Mean Historical Grounding**: 4.85
- **Mean Unsupported Claims** *(5 is safest)*: 4.95
- **Mean Helpfulness**: 4.09
- **Mean Safety / Policy** *(5 is safest)*: 4.97
- **Mean Overall Quality**: 4.30

### Thresholds
- **Overall Quality >= 4**: 81.4%
- **Safety Score <= 2**: 0.0%
- **Unsupported Claims <= 2**: 0.5%

*(Note: Grounding/Retrieval breakdown omitted as this subset did not trigger historical retrieval in Phase 8).*

## 3. Independent Second-LLM Agreement Study (Methodological Robustness Check)

**PARTIALLY SATISFIED / LIMITATION:**
Due to time constraints, the planned 30-example human agreement study was not completed. Instead, an independent second-LLM agreement study was performed as a methodological robustness check. This does not substitute for human-vs-judge validation.

**Methodology:**
To assess robustness of the LLM-as-judge methodology, a stratified sample of 30 generated replies was evaluated by an independent second LLM (`sarvam-105b` with a fresh prompt). The second judge had zero access to the first judge's scores, reasons, or phase 9 routing labels.

**Independent LLM-vs-LLM Agreement Metrics (n=30):**
- **Relevance**: 50.00% Exact | 50.00% Within ±1 | MAD: 1.50
- **Historical Grounding**: 50.00% Exact | 50.00% Within ±1 | MAD: 1.00
- **Unsupported Claims**: 50.00% Exact | 50.00% Within ±1 | MAD: 1.50
- **Helpfulness**: 0.00% Exact | 50.00% Within ±1 | MAD: 2.00
- **Safety / Policy**: 50.00% Exact | 50.00% Within ±1 | MAD: 1.50
- **Overall Quality**: 50.00% Exact | 50.00% Within ±1 | MAD: 1.50
- **Spearman Correlation (Overall)**: 0.00 (Undefined due to constant array output in the second judge, indicating potential mode collapse on this prompt).

## 4. Limitations
- **Human agreement — NOT COMPLETED.** The independent second-LLM agreement does not constitute human validation.
- Automated LLM metrics cannot replace manual human evaluation for empathetic or subtle policy nuances.
- The 204 evaluated replies include safe fallbacks (which inherently score high on safety but potentially lower on helpfulness).
- The agreement metrics indicate very poor alignment (or mode collapse) between the two prompt formulations, further emphasizing the need for true human validation.

**Status:** COMPLETE WITH LIMITATION
