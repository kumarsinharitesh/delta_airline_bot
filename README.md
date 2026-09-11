# Delta Airlines Customer Support Agent (Prototype)

> 📘 **Beginner-Friendly Full Project Report**: Read [PROJECT_REPORT.md](PROJECT_REPORT.md) for a complete, step-by-step breakdown of the entire system architecture, pipeline, tech stack, libraries, and codebase written in plain English for non-technical readers.

This repository contains the prototype implementation for an automated customer support agent designed specifically for Delta Airlines, using the Kaggle Twitter Customer Support (TWCS) dataset. The framework incorporates intent classification, historical resolution retrieval, and LLM-grounded response generation governed by a strict deterministic safety routing layer.

## Architecture
1. **Preprocessing**: Raw tweets are grouped into conversational threads.
2. **Deterministic Safety Guard**: Hardcoded rules detect explicit human requests, fraud, and prompt injection attempts.
3. **Intent Classification**: The project uses a 12-intent support taxonomy plus an AMBIGUOUS_OR_INSUFFICIENT_CONTEXT fallback label (13 labels total) to predict the primary user request.

| Intent | What it covers |
|:--|:--|
| `FLIGHT_STATUS_OR_DELAY` | Asking about flight delays, on-time status |
| `CANCEL_OR_CHANGE_FLIGHT` | Cancellation, rebooking, schedule changes |
| `BAGGAGE_ISSUE` | Lost, delayed, damaged baggage |
| `REFUND_OR_COMPENSATION` | Refund requests, compensation claims |
| `PAYMENT_OR_CHARGE_DISPUTE` | Disputed charges, billing issues |
| `CHECKIN_OR_BOARDING` | Check-in problems, boarding pass issues |
| `SKYMILES_OR_LOYALTY` | SkyMiles points, frequent flyer account |
| `ACCOUNT_ACCESS` | Login issues, account changes |
| `COMPLAINT_OR_FEEDBACK` | General complaints, compliments |
| `SPECIAL_ASSISTANCE` | Wheelchair, medical, service animal, unaccompanied minor |
| `SCHEDULE_OR_BOOKING_INQUIRY` | New booking questions, policy in planning context |
| `SEAT_OR_UPGRADE` | Seat selection, upgrades, exit row |
| `AMBIGUOUS_OR_INSUFFICIENT_CONTEXT` | Too vague to classify |

4. **Historical Retrieval**: Resolved historical support responses are retrieved via TF-IDF to ground the generated response.
5. **Generation**: Sarvam-105B drafts responses using a constrained reasoning-effort schema.
6. **Escalation Routing**: A deterministic policy validates the generated text and intent-confidence to decide whether to AUTO_HANDLE or ESCALATE to a human agent.

## Quickstart & Setup (Subsample Reproducibility)
You can reproduce the core pipeline on a small 1000-row subset of the data in under 15 minutes.

### 1. Prerequisites & Installation
Ensure you have Python 3.9+ installed.
```bash
pip install -r requirements.txt
```
*(Dependencies primarily include `scikit-learn`, `requests`, `pydantic`, `pytest`, `tqdm`)*

### 2. Environment Setup
Create a `.env` file in the root directory and add your Sarvam API key:
```env
SARVAM_API_KEY=your_key_here
```
*(Do not commit this file to version control. It is protected by `.gitignore`).*

### 3. Data Setup
Extract the Kaggle TWCS dataset `twcs.csv` into `dataset_raw/twcs/twcs.csv`.

### 4. Run the Pipeline (Minimal Reproducible Path)
Execute the following commands sequentially from the project root:

```bash
# 1. Preprocess and split the data
python -m src.data.preprocess
python -m src.data.profile
python -m src.data.split

# 2. Run Intent Classification Evaluation
python -m src.evaluation.sarvam_classifier --mode replay

# 3. Run Safety & Deterministic Policy Layer Evaluation
python -m src.evaluation.phase7

# 4. Run Grounded Generation & Validation Tests
python -m pytest tests/test_generation.py

# 5. Run Final Escalation Routing Evaluation
python -m src.evaluation.escalation
```

## Running the Test Suite
The repository includes a comprehensive unit-test suite for the deterministic policies and format validations. Run it using:
```bash
python -m pytest -q
```

## Where the Results Live
Detailed methodology, automated metrics, and qualitative traces are stored in the `evaluation/` directory:
- **`PROJECT_REPORT.md`**: The complete beginner-friendly report explaining the pipeline, tech stack, and codebase.
- **`evaluation/final_report.md`**: The final 6-page summary report containing all metrics, failure modes, and limitations.
- **`evaluation/decision_log.md`**: A log of the 12 most critical engineering decisions made during development.
- **`evaluation/assignment_checklist.md`**: The exact matrix tracking all system requirements.
- **`evaluation/phase*_report.md`**: Granular reports for each individual phase (Intent, Retrieval, Generation, Escalation, etc).
- **`evaluation/reply_quality_llm_agreement.json`**: The independent LLM-vs-LLM agreement robustness check.
