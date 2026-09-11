# Golden Evaluation Set — Human Label Audit Report

## 1. Executive Summary

- **Total Examples Manually Reviewed**: 200 (100% of golden evaluation set)
- **Unchanged from Rule Suggestion**: 164 (82.0%)
- **Changed by Conscious Human Review**: 36 (18.0%)
- **Authoritative Column**: `human_final_intent` (and `primary_intent` mirrored)
- **Traceability**: `rule_suggested_intent` and `label_changed` retained for full provenance

---

## 2. Intent Distribution Post-Review (12 Support Intents + 1 Fallback Class)

| Intent | Count | % | High Conf | Med Conf | Low Conf | Rule Agree | Rule Disagree |
|---|---|---|---|---|---|---|---|
| `FLIGHT_STATUS_OR_DELAY` | 31 | 15.5% | 29 | 2 | 0 | 28 | 3 |
| `COMPLAINT_OR_FEEDBACK` | 62 | 31.0% | 55 | 5 | 2 | 53 | 9 |
| `SCHEDULE_OR_BOOKING_INQUIRY` | 14 | 7.0% | 13 | 1 | 0 | 6 | 8 |
| `CHECKIN_OR_BOARDING` | 12 | 6.0% | 12 | 0 | 0 | 10 | 2 |
| `SEAT_OR_UPGRADE` | 10 | 5.0% | 10 | 0 | 0 | 9 | 1 |
| `BAGGAGE_ISSUE` | 6 | 3.0% | 6 | 0 | 0 | 6 | 0 |
| `SKYMILES_OR_LOYALTY` | 15 | 7.5% | 15 | 0 | 0 | 15 | 0 |
| `CANCEL_OR_CHANGE_FLIGHT` | 10 | 5.0% | 10 | 0 | 0 | 7 | 3 |
| `REFUND_OR_COMPENSATION` | 8 | 4.0% | 8 | 0 | 0 | 6 | 2 |
| `PAYMENT_OR_CHARGE_DISPUTE` | 3 | 1.5% | 3 | 0 | 0 | 2 | 1 |
| `SPECIAL_ASSISTANCE` | 5 | 2.5% | 3 | 2 | 0 | 4 | 1 |
| `ACCOUNT_ACCESS` *(Not evaluated - 0 held-out examples)* | 0 | 0.0% | 0 | 0 | 0 | 0 | 0 |
| `AMBIGUOUS_OR_INSUFFICIENT_CONTEXT` | 24 | 12.0% | 0 | 0 | 24 | 18 | 6 |

---

## 3. Major Disagreement Patterns (Rule-Based vs. Human)

Rule-based regex matching suffered from predictable failure modes that conscious human annotation resolved:

| Rule-Suggested Intent | Human Final Intent | Frequency | Root Cause / Rationale |
|---|---|---|---|
| `FLIGHT_STATUS_OR_DELAY` | `COMPLAINT_OR_FEEDBACK` | 4 | Customer mentioned flight number or departure time solely to praise crew, critique boarding policy, or vent after travel (no status needed). |
| `BAGGAGE_ISSUE` | `COMPLAINT_OR_FEEDBACK` | 3 | Customer mentioned 'bag' or 'suitcase' in positive social context (packing for event, praising bag-tracker feature). |
| `BAGGAGE_ISSUE` | `SCHEDULE_OR_BOOKING_INQUIRY` | 3 | Pre-flight pricing inquiry asking how much extra bags / overweight bags will cost for future travel. |
| `FLIGHT_STATUS_OR_DELAY` | `AMBIGUOUS_OR_INSUFFICIENT_CONTEXT` | 2 | Customer frustrated by long hold times waiting for assistance; no flight or issue was specified. |
| `CHECKIN_OR_BOARDING` | `AMBIGUOUS_OR_INSUFFICIENT_CONTEXT` | 2 | Tweet contained only an external screenshot link of an error; specific application subsystem is unidentified. |
| `SCHEDULE_OR_BOOKING_INQUIRY` | `AMBIGUOUS_OR_INSUFFICIENT_CONTEXT` | 2 | Customer asked for a UK phone number or stated they have a question about reservation without giving details. |
| `CANCEL_OR_CHANGE_FLIGHT` | `SCHEDULE_OR_BOOKING_INQUIRY` | 1 | Word 'cancel' referred to a past action; customer's active current inquiry is about purchasing extra-legroom seats. |
| `PAYMENT_OR_CHARGE_DISPUTE` | `SCHEDULE_OR_BOOKING_INQUIRY` | 1 | Mentioned price comparison ($75 direct flight elsewhere); no Delta charge made to dispute. |
| `CANCEL_OR_CHANGE_FLIGHT` | `CHECKIN_OR_BOARDING` | 1 | Check-in agent refused bag at desk and told passenger to rebook; core operational failure occurred at check-in counter. |
| `SCHEDULE_OR_BOOKING_INQUIRY` | `SEAT_OR_UPGRADE` | 1 | Selection occurred during booking, but grievance is about pre-selected seat not being honored. |
| `BAGGAGE_ISSUE` | `PAYMENT_OR_CHARGE_DISPUTE` | 1 | Disputing a $200 overweight baggage fee transaction as price gouging, rather than a lost/delayed physical bag. |
| `CANCEL_OR_CHANGE_FLIGHT` | `FLIGHT_STATUS_OR_DELAY` | 1 | Customer asked IF flight will be cancelled (seeking flight status update), not requesting to cancel their booking. |
| `SCHEDULE_OR_BOOKING_INQUIRY` | `CANCEL_OR_CHANGE_FLIGHT` | 1 | Involuntary airline schedule change (moved 1h20m earlier); customer asking what can be done seeking rebooking accommodation. |
| `BAGGAGE_ISSUE` | `REFUND_OR_COMPENSATION` | 1 | Disputing adequacy of miles compensation offered for a delayed bag. |
| `CHECKIN_OR_BOARDING` | `SCHEDULE_OR_BOOKING_INQUIRY` | 1 | Website crash occurred while attempting to purchase Cyber Monday flight fares. |
| `CHECKIN_OR_BOARDING` | `COMPLAINT_OR_FEEDBACK` | 1 | Thank-you shout-out to 'Gate Angel' agent for getting customer on an earlier flight. |
| `SCHEDULE_OR_BOOKING_INQUIRY` | `SPECIAL_ASSISTANCE` | 1 | Customer stuck in traffic asking for special expedited TSA security escort upon arrival. |
| `CANCEL_OR_CHANGE_FLIGHT` | `REFUND_OR_COMPENSATION` | 1 | Cancellation already executed yesterday; customer's active need is receiving the promised flight credit/refund. |
| `SPECIAL_ASSISTANCE` | `COMPLAINT_OR_FEEDBACK` | 1 | General product feedback asking Delta to add vegan coffee creamer, not an individual disability accommodation. |
| `FLIGHT_STATUS_OR_DELAY` | `SCHEDULE_OR_BOOKING_INQUIRY` | 1 | Inquiring about in-flight Wi-Fi availability on flight DL201 JNB-ATL (amenity inquiry, not a delay). |
| `AMBIGUOUS_OR_INSUFFICIENT_CONTEXT` | `CANCEL_OR_CHANGE_FLIGHT` | 1 | Customer noted long phone hold times but explicitly stated their goal: 'to ask you about changing a reservation'. |
| `REFUND_OR_COMPENSATION` | `CANCEL_OR_CHANGE_FLIGHT` | 1 | Human annotator reconciled context and prioritized explicit customer goal over keyword match. |
| `FLIGHT_STATUS_OR_DELAY` | `CHECKIN_OR_BOARDING` | 1 | Jet bridge jammed at the gate preventing boarding; boarding equipment failure. |
| `SKYMILES_OR_LOYALTY` | `SCHEDULE_OR_BOOKING_INQUIRY` | 1 | Booking process inquiry asking how to book combining gift cards, SkyMiles, and cash. |
| `BAGGAGE_ISSUE` | `FLIGHT_STATUS_OR_DELAY` | 1 | Passenger aboard aircraft delayed at gate waiting for luggage loading to complete (flight delay, not lost bag). |
| `CHECKIN_OR_BOARDING` | `FLIGHT_STATUS_OR_DELAY` | 1 | Flight turned around mid-air (diversion/air return) and gate agents providing mixed status info. |

---

## 4. Examples of Difficult Human Annotation Decisions

### Decision 1: G0002 — Cancel Background vs. Booking Goal
- **Text**: *"@Delta Hello. How can I buy seats with extra room when buying a ticket? I had to cancel a reservation..."*
- **Rule-Suggested**: `CANCEL_OR_CHANGE_FLIGHT` (keyword 'cancel')
- **Human-Assigned**: `SCHEDULE_OR_BOOKING_INQUIRY`
- **Rationale**: The cancellation was past context. The customer's active support goal is inquiring how to select and buy extra room seats during a new purchase.

### Decision 2: G0023 — Disputed Baggage Fee vs. Baggage Issue
- **Text**: *"Loyal @Delta customer not happy being charged an extra $200 for a surfboard bag overweight by 12lbs"*
- **Rule-Suggested**: `BAGGAGE_ISSUE` (keyword 'bag')
- **Human-Assigned**: `PAYMENT_OR_CHARGE_DISPUTE` (Secondary: `BAGGAGE_ISSUE`)
- **Rationale**: The bag is neither lost nor damaged. The customer is disputing a $200 fee charge as price gouging. Financial transaction disputes take priority under safety-sensitive rules.

### Decision 3: G0038 — Delayed Bag Compensation Adequacy
- **Text**: *"@Delta offers 2500 miles for a late bag and 4500 after serving nuts (bf is allergic). I guess someone's life isn't even worth two late bags."*
- **Rule-Suggested**: `BAGGAGE_ISSUE` (keyword 'late bag')
- **Human-Assigned**: `REFUND_OR_COMPENSATION` (Secondary: `BAGGAGE_ISSUE`)
- **Rationale**: The customer is actively contesting the quantitative adequacy of miles compensation awarded by Delta, not reporting a missing bag. High financial/safety sensitivity.

### Decision 4: G0120 — Long Phone Hold vs. Explicit Change Request
- **Text**: *"@Delta — the menu to select 'call back' when on hold isn't working. And your current hold times are over an hour. So here I am, turning to Twitter to ask you about changing a reservation. :/"*
- **Rule-Suggested**: `AMBIGUOUS_OR_INSUFFICIENT_CONTEXT` (keywords 'hold' / 'call back')
- **Human-Assigned**: `CANCEL_OR_CHANGE_FLIGHT`
- **Rationale**: Although phone hold friction is described, the message contains an unambiguous primary goal: 'ask you about changing a reservation'.

### Decision 5: G0141 & G0157 — Future Baggage Fee Inquiries
- **Text (G0141)**: *"@delta flying from USA to Brazil, how much extra do I pay to check two luggages heavier than 50lbs but lighter than 99lbs? Thanks"*
- **Rule-Suggested**: `BAGGAGE_ISSUE`
- **Human-Assigned**: `SCHEDULE_OR_BOOKING_INQUIRY` (Secondary: `BAGGAGE_ISSUE`)
- **Rationale**: Under taxonomy guidelines, questions about baggage policies or fee schedules for prospective/future travel belong to `SCHEDULE_OR_BOOKING_INQUIRY` rather than an operational `BAGGAGE_ISSUE`.

### Decision 6: G0183 — Metaphorical 'Suitcase' in Social Post
- **Text**: *"The suitcase is out and I've been looking at my upgrade chances in the @Delta app regularly. That means #PixarCocoEvent is almost here!"*
- **Rule-Suggested**: `BAGGAGE_ISSUE` (keyword 'suitcase')
- **Human-Assigned**: `COMPLAINT_OR_FEEDBACK` (social praise; Secondary: `SEAT_OR_UPGRADE`)
- **Rationale**: The word 'suitcase' denotes packing excitement for an event, not a baggage mishap. Pure positive social tweet.

### Decision 7: G0196 — On-Plane Luggage Loading Delay
- **Text**: *"In the plane sitting at the gate for an hour waiting for luggage to load in a few minutes @Delta"*
- **Rule-Suggested**: `BAGGAGE_ISSUE` (keyword 'luggage')
- **Human-Assigned**: `FLIGHT_STATUS_OR_DELAY` (Secondary: `BAGGAGE_ISSUE`)
- **Rationale**: The passenger is seated inside the aircraft enduring a departure delay while ground crew loads luggage. The actionable issue is the flight delay.

---

## 5. Account Access Analysis (Dev & Test Splits)

- **Golden Set Count**: 0
- **Status**: Explicitly marked **'Not evaluated due to insufficient held-out examples.'**
- **Dev/Test Candidate Analysis**: Exactly 11 candidates were identified across dev and test splits matching login/password patterns (e.g., `801114`, `1792850`, `2556180`, `1645696`, `922188`).
- **Exclusion Rationale**: Golden set sampling was stratified on `resolution_status` (proportional to conversation outcomes) without pre-label knowledge of intent. Because `ACCOUNT_ACCESS` accounts for only ~2.1% of customer volume in general and is even rarer in held-out splits, zero examples were selected into the 200-sample set under random strata sampling.
- **Strict Split Integrity**: Candidates were NOT pulled from `train.jsonl` to ensure zero evaluation split leakage.

---

## 6. Verification and Compliance

- All 200 examples have `human_final_intent` set.
- All 200 examples have `annotation_confidence` assigned (`HIGH`: 164, `MEDIUM`: 10, `LOW`: 26).
- Zero examples originate from `train.jsonl`.
- Zero duplicate customer message IDs exist.
- Multi-intent examples identified: 78.
- Safety-sensitive examples identified: 16 (`REFUND_OR_COMPENSATION`: 8, `SPECIAL_ASSISTANCE`: 5, `PAYMENT_OR_CHARGE_DISPUTE`: 3).
