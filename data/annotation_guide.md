# Delta Customer Support — Annotation Guide
# Phase 3 — Intent Taxonomy v1.0 (12 support intents + 1 fallback ambiguity class)
# For use with: evaluation/golden_set.csv
# Taxonomy definition: configs/intents.yaml

---

## Overview

This guide enables any human annotator to reliably label Delta customer support
messages with the correct **primary intent** across the **12 support intents + 1 fallback ambiguity class** taxonomy.

**Unit of annotation**: A single customer message, read with up to 2 prior turns
of context (previous messages in the conversation).

**Intent = what the customer is trying to get help with right now.**

Intent does NOT depend on:
- Whether support resolved the issue
- The resolution_status field
- How support responded
- The customer's emotional tone (angry, polite, etc.)

---

## 1. Intent Definitions

### FLIGHT_STATUS_OR_DELAY
Customer is asking about the **current or upcoming status** of a specific
flight they are on or about to be on, OR is reporting/complaining about a
**delay, disruption, tarmac hold, missed connection, or cancelled flight**.

**Positive examples (use this intent):**
- "My flight 1251 is delayed 2 hours, any updates?"
- "Is DL 404 on time tonight?"
- "My connecting flight left without me because we arrived late"
- "Still sitting at the gate 30 minutes after scheduled take-off"
- "What is the status of flight 4769? When are you going to find a pilot?"
- "Any news on flights departing SFO today?"
- "Tight 50-minute connection in DTW — fingers crossed"

**Negative examples (do NOT use this intent):**
- "What time do flights leave NYC to LAX tomorrow?" → SCHEDULE_OR_BOOKING_INQUIRY
- "My bag hasn't arrived since my flight landed" → BAGGAGE_ISSUE
- "I want to cancel my delayed flight and get a refund" → CANCEL_OR_CHANGE_FLIGHT (if rebooking is the goal) or REFUND_OR_COMPENSATION

**Tie-breaking rule:**
If the customer both reports a delay AND asks for a rebook/refund, look at
which is the **primary ask**. If they want to rebook → CANCEL_OR_CHANGE_FLIGHT.
If they just want info or acknowledgement of the delay → FLIGHT_STATUS_OR_DELAY.

---

### CANCEL_OR_CHANGE_FLIGHT
Customer wants to **cancel, rebook, reschedule, or change** an existing flight
booking (dates, times, routing, equipment).

**Positive examples:**
- "I need to change my flight from Oct 5 to Oct 8"
- "How do I cancel my Delta ticket?"
- "Can you rebook me on the next available flight to JFK?"
- "Trying to change my flight — website won't let me"
- "Schedule change forced me to leave 4 hours early — not OK"
- "My dad's flight malfunction in RIC is making me miss connection — is there a direct?"

**Negative examples:**
- "My flight was delayed — any updates?" → FLIGHT_STATUS_OR_DELAY
- "I want a refund for a cancelled flight" → REFUND_OR_COMPENSATION (if they've
  already been cancelled and now want money back)

---

### SCHEDULE_OR_BOOKING_INQUIRY
Customer is asking about **future flight availability, schedules, routes, fares,
or a new booking**. Also covers pre-travel policy questions (e.g., bag fee policy,
how early to arrive for international flights, promotional deals).

**Positive examples:**
- "What time is the earliest flight from ATL to LAX tomorrow?"
- "How do I book using my SkyMiles?"
- "Is there a nonstop from JFK to AMS in December?"
- "How much is the checked baggage fee for international?"
- "How early do I need to arrive for a Boston to Dublin flight?"
- "Where's the Cyber Monday deals?"
- "Roundtrip to Milwaukee — got a receipt but no ticket confirmation"

**Negative examples:**
- "My flight 1403 is delayed" → FLIGHT_STATUS_OR_DELAY
- "I need to change my existing reservation" → CANCEL_OR_CHANGE_FLIGHT

**Key distinguisher:**
SCHEDULE = prospective/hypothetical travel planning.
FLIGHT_STATUS = specific existing flight currently happening.

---

### CHECKIN_OR_BOARDING
Customer has a problem or question about the **check-in process, boarding pass,
TSA PreCheck/KTN, gate access, online/app check-in failing**, or the physical
boarding process.

**Positive examples:**
- "My boarding pass doesn't show TSA Pre — how do I fix this?"
- "Cannot check in online for my flight tomorrow"
- "QR scan at gate not working"
- "Online check-in shows trip not found with booking ref H65AJX"
- "Just got boarding passes for tomorrow and no TSA Precheck?"
- "App won't let me add a bag during check-in"
- "Hey @Delta your app is still broken"

**Negative examples:**
- "I want to select a different seat" → SEAT_OR_UPGRADE
- "My flight was delayed 2 hours" → FLIGHT_STATUS_OR_DELAY

**Tie-breaking:**
If the problem is the boarding pass itself or the check-in system → CHECKIN_OR_BOARDING.
If the problem is which seat is assigned → SEAT_OR_UPGRADE.

---

### SEAT_OR_UPGRADE
Customer wants to **select, change, or upgrade a seat**; is asking about
Comfort+, First Class, exit rows; or is complaining that their assigned seat
was changed without consent.

**Positive examples:**
- "Can I pay to upgrade to Comfort+ for my flight tomorrow?"
- "You changed my seat without notifying me — I had a window seat"
- "Best to leave first class 85% empty instead of upgrading platinum members?"
- "On second leg of the flight, seats I picked aren't there either"
- "Dear Delta, packing me in a taxi after diversion is not 1st class experience I paid for"
- "Booking Xmas flight — have to pay $150 extra to sit with my 2yr old"

**Negative examples:**
- "Boarding pass doesn't show my seat" → CHECKIN_OR_BOARDING
- "How do flights work?" → SCHEDULE_OR_BOOKING_INQUIRY

---

### BAGGAGE_ISSUE
Customer has a problem with **checked baggage that is delayed, lost, damaged,
or misrouted**. Also includes items left on the plane (LOST_AND_FOUND maps here).

**Positive examples:**
- "My bag hasn't arrived — was on DL 1251 three hours ago"
- "My suitcase was damaged, who do I contact?"
- "Lost my iPhone SE at Orlando gate 72/73 — can anyone help?"
- "Bag was sent to wrong city"
- "Bag delivery promised 12am–3am, now 10am and still no bag"

**Negative examples:**
- "How much is the checked bag fee?" → SCHEDULE_OR_BOOKING_INQUIRY
- "I need a refund for my damaged bag claim" → REFUND_OR_COMPENSATION (if claim settled)

**Taxonomy decision:**
LOST_AND_FOUND and BAGGAGE_ISSUE use the **same support team and process** at
Delta, so both map to BAGGAGE_ISSUE.

---

### SKYMILES_OR_LOYALTY
Customer has a question or problem with **SkyMiles earning, redemption,
account balance, elite status, award bookings, or partner miles**.

**Positive examples:**
- "My flight miles aren't showing in my SkyMiles account"
- "How do I book a flight using SkyMiles?"
- "I should have qualified for Platinum but status isn't updated"
- "Miles from JFK-FCO not posted, missing MQMs"
- "How many miles to upgrade to Australia in January?"
- "Since when do you reward miles based on ticket price?"
- "Transferring SkyMiles — can someone help?"

**Negative examples:**
- "I can't log in to my SkyMiles account" → ACCOUNT_ACCESS
- "I want the miles back from my cancelled flight" → REFUND_OR_COMPENSATION

---

### ACCOUNT_ACCESS
Customer **cannot log in**, needs a password reset, or has issues accessing
their account profile.

**Positive examples:**
- "Can't log in to my SkyMiles account — forgot password"
- "Delta.com won't let me sign in on the app"
- "My BF couldn't sign in when trying to check in — please help"

**Negative examples:**
- "My miles balance is wrong" → SKYMILES_OR_LOYALTY
- "App crashes during check-in" → CHECKIN_OR_BOARDING

---

### REFUND_OR_COMPENSATION ⚠️ SAFETY-SENSITIVE
Customer is **explicitly requesting money, credit, voucher, or miles** back,
OR is disputing whether compensation promised to them was delivered.

**Positive examples:**
- "My flight was cancelled, I want a full refund"
- "I paid for Comfort+ but was downgraded — requesting refund"
- "I spent $300 on a hotel due to your delay, I want reimbursement"
- "Where is the $50 travel voucher I was promised?"
- "Delta offering 5000 SkyMiles for delaying me 2 hours doesn't seem fair"
- "What is your policy for refunding due to inability to travel to STT?"
- "On 2-hour hold to refund first class award booking"

**Negative examples:**
- "I need to cancel my flight" → CANCEL_OR_CHANGE_FLIGHT
- "I was double charged for baggage" → PAYMENT_OR_CHARGE_DISPUTE

**Safety rule:**
AI must NOT promise refund amounts. Acknowledge and route to correct process.
Escalate denied-boarding and legal/regulatory compensation to human.

---

### PAYMENT_OR_CHARGE_DISPUTE ⚠️ SAFETY-SENSITIVE
Customer is **disputing a transaction**: double charge, incorrect fee, unexpected
charge, or billing discrepancy.

**Positive examples:**
- "I was charged twice for my baggage fee"
- "Unexpected $200 charge on my credit card from Delta"
- "In-flight purchase receipt not received"
- "Bought a direct flight and $75 seems wrong"
- "Asking if I was charged a fee or if it was a fare difference of $200"

**Negative examples:**
- "I want a refund for my cancelled flight" → REFUND_OR_COMPENSATION
- "What is the baggage fee?" → SCHEDULE_OR_BOOKING_INQUIRY

---

### SPECIAL_ASSISTANCE ⚠️ SAFETY-SENSITIVE
Customer needs an **accommodation due to disability, medical condition, dietary
restriction, pet travel, unaccompanied minor, or emergency humanitarian need**.

**Positive examples:**
- "I need wheelchair assistance at ATL for my elderly mother"
- "Do you have vegan meals? I need a nondairy creamer option"
- "My mom was forced to use stairs despite wheelchair note on ticket"
- "Help with cargo space for water filters for Puerto Rico hurricane relief"
- "Good day — I provided medical assistance for a passenger on Flight 1841"
- "Reporting a belligerent passenger on flight 3771"

**Negative examples:**
- "I need extra legroom" → SEAT_OR_UPGRADE
- "I lost my medication on the plane" → BAGGAGE_ISSUE

**Safety rule:**
Medical emergencies and safety-impacting requests must be immediately escalated.
AI must NOT make binding accessibility commitments.

---

### COMPLAINT_OR_FEEDBACK
Customer is **expressing general dissatisfaction, praise, or feedback** without
a specific actionable request. This is the **residual intent** — use it when
no other intent applies.

**Positive examples:**
- "Your customer service is terrible, never flying again"
- "Big shout-out to the Delta crew on DL 148 — outstanding service!"
- "Thank you for helping get my seats to my family" (if just saying thank-you)
- "100th segment, that employee was really rude"
- "The crew on our flight were absolutely incredible! Big shout-out to Gayla!"
- "In-flight WiFi not working — why weren't passengers warned in advance?"
- "Wish I had a better option than Delta today — Southwest WiFi much better"

**Negative examples:**
- "That delay is unacceptable — when will we leave?" → FLIGHT_STATUS_OR_DELAY
- "Terrible service and I want my money back" → REFUND_OR_COMPENSATION

**Rule:** If the tweet contains an explicit ask (refund, rebook, compensation),
use the more specific intent. COMPLAINT is only for pure venting or pure praise.

---

### AMBIGUOUS_OR_INSUFFICIENT_CONTEXT
No clear intent can be determined even with conversation context. Used
**only as a last resort**.

**Positive examples (truly ambiguous):**
- "@Delta can you help me?" (with no further context)
- "@Delta the hold times are CRAZY! 2+ hours!" (no underlying issue stated)
- "@Delta Hey folks, just sent you a quick DM!" (no content)
- Location check-in posts ("I'm at Delta Sky Club in Romulus, MI")
- Pure social photo posts with no content

**Rule:** Try all other intents first. Only use AMBIGUOUS if you have genuinely
exhausted all context clues. Mark annotation_confidence as LOW.

---

## 2. Multi-Intent Policy

Some messages contain **two distinct customer goals**:

> "My flight was cancelled AND I also need a refund."

**Policy:**
- Identify the PRIMARY intent: the most urgent, actionable goal right now.
- Set `is_multi_intent = true`.
- Set `secondary_intent` to the second goal.
- If more than 2 intents, record only the top 2.

**Common multi-intent pairs:**
| Primary | Secondary |
|---|---|
| CANCEL_OR_CHANGE_FLIGHT | REFUND_OR_COMPENSATION |
| SEAT_OR_UPGRADE | REFUND_OR_COMPENSATION |
| SKYMILES_OR_LOYALTY | SEAT_OR_UPGRADE |
| FLIGHT_STATUS_OR_DELAY | CANCEL_OR_CHANGE_FLIGHT |
| BAGGAGE_ISSUE | REFUND_OR_COMPENSATION |

For the Phase 4 classifier, only `primary_intent` will be evaluated.
`secondary_intent` is retained for error analysis.

---

## 3. Ambiguity Policy

If a message is ambiguous:
1. First consult the `previous_context` field (prior messages).
2. If context resolves the ambiguity, label with the resolved intent at
   MEDIUM confidence.
3. If context does not resolve it, use AMBIGUOUS_OR_INSUFFICIENT_CONTEXT
   with LOW confidence.
4. Never force a specific intent where you are not reasonably confident.

---

## 4. How to Use Conversation Context

The `context` field shows up to 2 prior messages. Context helps when:

- The customer's message is a follow-up ("Yes, exactly" / "Part 2")
- The customer is replying to a support suggestion
- The customer's message alone is too short to interpret

**Example where context changes the label:**

```
customer_text: "Yes, exactly"
context:      [SUPPORT]: "Are you saying your bag hasn't been delivered?"
→ Label: BAGGAGE_ISSUE (context reveals the topic)
```

**Important:** Do NOT use future support responses (after this message) to
determine intent. Classify based only on what the customer has said up to
and including this message.

---

## 5. Safety-Sensitive Intent Rules

Three intents require special handling:

| Intent | Rule |
|---|---|
| REFUND_OR_COMPENSATION | AI must acknowledge but not promise amounts |
| PAYMENT_OR_CHARGE_DISPUTE | AI must acknowledge; escalate potential fraud |
| SPECIAL_ASSISTANCE | AI must not make binding accessibility commitments |

These are still valid intents — do not avoid labeling them. The risk rules
come in Phase 4 (escalation modeling).

---

## 6. Annotation Confidence

| Level | Meaning |
|---|---|
| HIGH | Clear single intent; annotator would label the same way every time |
| MEDIUM | Reasonable interpretation but some ambiguity remains |
| LOW | Genuinely ambiguous even after using context |

Low-confidence examples are **valuable** — they test classifier robustness.
Do NOT remove them.

---

## 7. Decision Tree Summary

```
1. Does the message explicitly request special accommodation
   (medical, disability, dietary, humanitarian)?  → SPECIAL_ASSISTANCE

2. Is the customer unable to log in / reset password? → ACCOUNT_ACCESS

3. Is there a disputed transaction / incorrect charge? → PAYMENT_OR_CHARGE_DISPUTE

4. Is the customer asking for money, credit, miles back? → REFUND_OR_COMPENSATION

5. Does the customer want to cancel/rebook/change a flight? → CANCEL_OR_CHANGE_FLIGHT

6. Is there a baggage problem or lost item at airport/on plane? → BAGGAGE_ISSUE

7. Is the problem specifically about check-in, boarding pass, gate? → CHECKIN_OR_BOARDING

8. Is the problem specifically about seat assignment or upgrade? → SEAT_OR_UPGRADE

9. Is the problem about SkyMiles, status, award booking? → SKYMILES_OR_LOYALTY

10. Is the customer asking about a specific flight's status or reporting a delay? → FLIGHT_STATUS_OR_DELAY

11. Is the customer asking about future flights, availability, booking, policies? → SCHEDULE_OR_BOOKING_INQUIRY

12. Is the message expressing feedback/praise/venting with no specific ask? → COMPLAINT_OR_FEEDBACK

13. None of the above / truly insufficient context → AMBIGUOUS_OR_INSUFFICIENT_CONTEXT
```

---

## 8. Commonly Confusable Pairs

| Pair | Decision Rule |
|---|---|
| FLIGHT_STATUS_OR_DELAY vs CANCEL_OR_CHANGE_FLIGHT | Delay info only → FLIGHT_STATUS; wants to rebook → CANCEL |
| FLIGHT_STATUS_OR_DELAY vs SCHEDULE_OR_BOOKING_INQUIRY | Existing disrupted flight → FLIGHT_STATUS; future/hypothetical → SCHEDULE |
| SKYMILES_OR_LOYALTY vs ACCOUNT_ACCESS | Miles data wrong → SKYMILES; can't log in → ACCOUNT |
| SKYMILES_OR_LOYALTY vs REFUND_OR_COMPENSATION | Miles earned inquiry → SKYMILES; miles back from cancellation → REFUND |
| BAGGAGE_ISSUE vs LOST_AND_FOUND | Both map to BAGGAGE_ISSUE |
| SEAT_OR_UPGRADE vs CHECKIN_OR_BOARDING | Seat content → SEAT; boarding process/pass → CHECKIN |
| COMPLAINT_OR_FEEDBACK vs any specific intent | If there's a specific ask, use the specific intent |
| REFUND_OR_COMPENSATION vs PAYMENT_OR_CHARGE_DISPUTE | Overcharged → PAYMENT; want refund → REFUND |
