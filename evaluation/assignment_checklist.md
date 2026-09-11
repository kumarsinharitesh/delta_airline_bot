# Assignment Requirement Matrix

| Requirement | Implementation File | Evaluation Artifact | Report Section | Verification Command | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A. ONE brand selected** | `data/processed/dev.jsonl` | `phase1_report.md` | Data Selection | `cat data/brand_profile.csv` | **COMPLETE** (Delta Airlines) |
| **B. Intent classification** | `src/llm/sarvam_client.py` | `phase5_report.md` | Classification Metrics | `python -m src.evaluation.sarvam_classifier` | **COMPLETE** |
| **C. Grounded reply drafting** | `src/agent/generate.py` | `phase8_report.md` | Generation Metrics | `pytest tests/test_generation.py` | **COMPLETE** |
| **D. Auto-handle vs Escalation** | `src/policy/escalation.py` | `phase9_report.md` | Escalation Trade-off | `python -m src.evaluation.escalation` | **COMPLETE** |
| **E. Runnable repo** | Root dir | `final_audit.md` | README.md | `pytest -q` | **COMPLETE** |
| **F. 15-min reproducibility** | `README.md` | `final_audit.md` | Reproducibility | (Follow README script) | **COMPLETE** (Subsample commands ready) |
| **G. 150-250 intent golden set** | `src/intents/human_annotation.py` | `golden_set.csv` | Intent Golden Set | `cat evaluation/golden_set.csv \| wc -l` | **COMPLETE** (200 HUMAN-LABELLED intent cases) |
| **H. Automated metrics** | `src/evaluation/baselines.py` | `phase3_report.md` | Baselines | `python -m src.evaluation.baselines` | **COMPLETE** |
| **I. LLM-as-judge reply quality** | `src/evaluation/reply_quality.py` | `phase11_report.md` | Reply Quality | `python src/evaluation/reply_quality.py` | **PASS** |
| **J. Human-vs-judge agreement** | `src/evaluation/reply_quality_agreement.py` | `phase11_report.md` | Reply Quality | `python src/evaluation/reply_quality_agreement.py` | **PARTIAL** (Time constraints prevented human validation; an independent LLM check was substituted but does not satisfy human validation) |
| **K. Two baselines** | `src/evaluation/baselines.py` | `phase3_report.md` | Intent Classification | `pytest tests/` | **PASS** |
| **L. Top 5 failure modes** | N/A | `final_report.md` | Top 5 Failure Modes | N/A | **PASS** |
| **M. Misleading headline number**| N/A | `final_report.md` | Misleading Headline | N/A | **PASS** |
| **N. One-more-week plan** | N/A | `final_report.md` | One More Week | N/A | **PASS** |
| **O. 10–15 decision log entries**| N/A | `decision_log.md` | Decision Log | N/A | **PASS** |

> **Note on Requirement G**: The 200-example Intent Golden Set (`golden_set.csv`) is explicitly HUMAN-LABELLED. The 150-example Escalation Reference Set (`escalation_gold.csv`) is an LLM-ASSISTED reference set and is not counted as the human-labelled ground truth for this requirement.
