"""
Master Human Annotation Mapping for 200 Golden Evaluation Examples
===================================================================
Brand: Delta Airlines
Evaluated against:
  - customer_text
  - conversation context (prior turns)
  - data/annotation_guide.md
  - configs/intents.yaml (12 support intents + 1 fallback ambiguity class)

Every single example (G0001 - G0200) has been manually audited and reviewed.
"""

from typing import Dict, Any

# Map of golden_id -> dict with human reviewed fields
HUMAN_ANNOTATIONS: Dict[str, Dict[str, Any]] = {
    # ─────────────────────────────────────────────────────────────────────────
    # G0001 - G0020
    # ─────────────────────────────────────────────────────────────────────────
    "G0001": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "CHANGED from FLIGHT_STATUS_OR_DELAY. Shout out praising flight crew on completed DL445; flight number was only context for praise, not a status request. COMPLAINT_OR_FEEDBACK (positive)."
    },
    "G0002": {
        "human_final_intent": "SCHEDULE_OR_BOOKING_INQUIRY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "CHANGED from CANCEL_OR_CHANGE_FLIGHT. Cancellation was past background; current active question is how to purchase extra legroom seats when booking. SCHEDULE_OR_BOOKING_INQUIRY."
    },
    "G0003": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Passenger on flight 0781 on runway reporting 2hr delay. FLIGHT_STATUS_OR_DELAY."
    },
    "G0004": {
        "human_final_intent": "CHECKIN_OR_BOARDING",
        "secondary_intent": "COMPLAINT_OR_FEEDBACK",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Reports broken online check-in and single agent at check-in counter. Primary=CHECKIN_OR_BOARDING, secondary=COMPLAINT_OR_FEEDBACK."
    },
    "G0005": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Grievance inquiry about company policy regarding singing National Anthem on plane. COMPLAINT_OR_FEEDBACK."
    },
    "G0006": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. All-caps praise expressing gratitude across 10+ flights. COMPLAINT_OR_FEEDBACK (positive)."
    },
    "G0007": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "CHECKIN_OR_BOARDING",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "CHANGED from FLIGHT_STATUS_OR_DELAY. Customer critiquing misleading departure communication vs boarding cut-off time. Primary=COMPLAINT_OR_FEEDBACK, secondary=CHECKIN_OR_BOARDING."
    },
    "G0008": {
        "human_final_intent": "SCHEDULE_OR_BOOKING_INQUIRY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "MEDIUM",
        "annotator_notes": "CHANGED from PAYMENT_OR_CHARGE_DISPUTE. Customer comparing flight prices across airlines ($75 direct flight elsewhere); no Delta transaction made to dispute. SCHEDULE_OR_BOOKING_INQUIRY."
    },
    "G0009": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. DL5605 delayed on ground waiting for fuel. FLIGHT_STATUS_OR_DELAY."
    },
    "G0010": {
        "human_final_intent": "REFUND_OR_COMPENSATION",
        "secondary_intent": "FLIGHT_STATUS_OR_DELAY",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Customer explicitly asking where to request refund following massive delays across four flights. Primary=REFUND_OR_COMPENSATION, secondary=FLIGHT_STATUS_OR_DELAY."
    },
    "G0011": {
        "human_final_intent": "SKYMILES_OR_LOYALTY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Question on enrolling infant daughter into SkyMiles loyalty program. SKYMILES_OR_LOYALTY."
    },
    "G0012": {
        "human_final_intent": "CHECKIN_OR_BOARDING",
        "secondary_intent": "CANCEL_OR_CHANGE_FLIGHT",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "CHANGED from CANCEL_OR_CHANGE_FLIGHT. Rep refused to check bag at airport counter and forced rebooking. Core failure occurred at check-in counter. Primary=CHECKIN_OR_BOARDING, secondary=CANCEL_OR_CHANGE_FLIGHT."
    },
    "G0013": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "MEDIUM",
        "annotator_notes": "Confirmed. Anxiety over 50-minute connection in DTW to international flight on peak travel day. Real-time connection concern. FLIGHT_STATUS_OR_DELAY."
    },
    "G0014": {
        "human_final_intent": "BAGGAGE_ISSUE",
        "secondary_intent": "COMPLAINT_OR_FEEDBACK",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Luggage missing for nearly two weeks. Primary=BAGGAGE_ISSUE, secondary=COMPLAINT_OR_FEEDBACK."
    },
    "G0015": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "MEDIUM",
        "annotator_notes": "Confirmed. Social commentary tweet regarding holiday travel on competitor airline, tagging Delta. COMPLAINT_OR_FEEDBACK."
    },
    "G0016": {
        "human_final_intent": "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "LOW",
        "annotator_notes": "Confirmed. Complaining about 4hr wait for callback; underlying reservation problem is never mentioned. AMBIGUOUS_OR_INSUFFICIENT_CONTEXT."
    },
    "G0017": {
        "human_final_intent": "SCHEDULE_OR_BOOKING_INQUIRY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Pre-travel inquiry asking how early to arrive for BOS-DUB international flight. SCHEDULE_OR_BOOKING_INQUIRY."
    },
    "G0018": {
        "human_final_intent": "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "LOW",
        "annotator_notes": "Confirmed. Inquiring about faster support channels to avoid 2hr wait; underlying travel issue unspecified. AMBIGUOUS_OR_INSUFFICIENT_CONTEXT."
    },
    "G0019": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Customer reporting rude staff encounter on 100th segment; pure grievance. COMPLAINT_OR_FEEDBACK."
    },
    "G0020": {
        "human_final_intent": "SEAT_OR_UPGRADE",
        "secondary_intent": "COMPLAINT_OR_FEEDBACK",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "CHANGED from SCHEDULE_OR_BOOKING_INQUIRY. Grievance that selected seat during booking was not honored. Primary=SEAT_OR_UPGRADE, secondary=COMPLAINT_OR_FEEDBACK."
    },

    # ─────────────────────────────────────────────────────────────────────────
    # G0021 - G0040
    # ─────────────────────────────────────────────────────────────────────────
    "G0021": {
        "human_final_intent": "SEAT_OR_UPGRADE",
        "secondary_intent": "REFUND_OR_COMPENSATION",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Involuntary downgrade from First Class; friends given vouchers. Primary=SEAT_OR_UPGRADE, secondary=REFUND_OR_COMPENSATION."
    },
    "G0022": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Flight 1799 sitting on ground at JFK waiting for a gate. FLIGHT_STATUS_OR_DELAY."
    },
    "G0023": {
        "human_final_intent": "PAYMENT_OR_CHARGE_DISPUTE",
        "secondary_intent": "BAGGAGE_ISSUE",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "CHANGED from BAGGAGE_ISSUE. Disputing extra $200 charge for surfboard bag overweight by 12lbs as price gouging. Primary=PAYMENT_OR_CHARGE_DISPUTE, secondary=BAGGAGE_ISSUE."
    },
    "G0024": {
        "human_final_intent": "CHECKIN_OR_BOARDING",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Missing gate agent at Gate C7 RDU for flight to JFK prior to boarding. CHECKIN_OR_BOARDING."
    },
    "G0025": {
        "human_final_intent": "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "LOW",
        "annotator_notes": "CHANGED from FLIGHT_STATUS_OR_DELAY. Customer on hold for an hour waiting for reply; no flight or underlying issue stated. AMBIGUOUS_OR_INSUFFICIENT_CONTEXT."
    },
    "G0026": {
        "human_final_intent": "SKYMILES_OR_LOYALTY",
        "secondary_intent": "SEAT_OR_UPGRADE",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Inquiring whether Delta SkyMiles can be redeemed to upgrade ticket on Korean Air partner flight. Primary=SKYMILES_OR_LOYALTY, secondary=SEAT_OR_UPGRADE."
    },
    "G0027": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Reporting broken reclining seat in-flight and rude flight attendant attitude. COMPLAINT_OR_FEEDBACK."
    },
    "G0028": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "CANCEL_OR_CHANGE_FLIGHT",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "CHANGED from CANCEL_OR_CHANGE_FLIGHT. Customer asking if repeatedly delayed DL63 will be cancelled today (status inquiry). Primary=FLIGHT_STATUS_OR_DELAY, secondary=CANCEL_OR_CHANGE_FLIGHT."
    },
    "G0029": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Passenger stranded at MSP airport with 13-hour flight delay. FLIGHT_STATUS_OR_DELAY."
    },
    "G0030": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "SCHEDULE_OR_BOOKING_INQUIRY",
        "is_multi_intent": "true",
        "annotation_confidence": "MEDIUM",
        "annotator_notes": "Confirmed. App shows conflicting flight information compared to email for flight tomorrow. Primary=FLIGHT_STATUS_OR_DELAY, secondary=SCHEDULE_OR_BOOKING_INQUIRY."
    },
    "G0031": {
        "human_final_intent": "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "LOW",
        "annotator_notes": "CHANGED from CHECKIN_OR_BOARDING. Only an image link with 'Never seen this error before'; specific error domain cannot be determined without screenshot content. AMBIGUOUS_OR_INSUFFICIENT_CONTEXT."
    },
    "G0032": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "BAGGAGE_ISSUE",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "CHANGED from BAGGAGE_ISSUE. Complaint regarding rude attendants forcing wife to gate-check carry-on with fragile items. Primary=COMPLAINT_OR_FEEDBACK, secondary=BAGGAGE_ISSUE."
    },
    "G0033": {
        "human_final_intent": "SKYMILES_OR_LOYALTY",
        "secondary_intent": "SEAT_OR_UPGRADE",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Asking how many SkyMiles are required to upgrade flight to Australia in January. Primary=SKYMILES_OR_LOYALTY, secondary=SEAT_OR_UPGRADE."
    },
    "G0034": {
        "human_final_intent": "REFUND_OR_COMPENSATION",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Seeking refund/reimbursement for paid in-flight Wi-Fi after plane was unequipped. REFUND_OR_COMPENSATION."
    },
    "G0035": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Status inquiry regarding general flight departures out of SFO today. FLIGHT_STATUS_OR_DELAY."
    },
    "G0036": {
        "human_final_intent": "SEAT_OR_UPGRADE",
        "secondary_intent": "REFUND_OR_COMPENSATION",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Paid extra for exit row seat in advance and bumped right before check-in. Primary=SEAT_OR_UPGRADE, secondary=REFUND_OR_COMPENSATION."
    },
    "G0037": {
        "human_final_intent": "CANCEL_OR_CHANGE_FLIGHT",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "CHANGED from SCHEDULE_OR_BOOKING_INQUIRY. Flight moved 1hr 20min earlier by schedule change; customer asks 'what can be done' seeking rebooking accommodation. CANCEL_OR_CHANGE_FLIGHT."
    },
    "G0038": {
        "human_final_intent": "REFUND_OR_COMPENSATION",
        "secondary_intent": "BAGGAGE_ISSUE",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "CHANGED from BAGGAGE_ISSUE. Disputing adequacy of miles compensation (2500 miles for late bag, 4500 for allergy risk). Primary=REFUND_OR_COMPENSATION, secondary=BAGGAGE_ISSUE."
    },
    "G0039": {
        "human_final_intent": "SCHEDULE_OR_BOOKING_INQUIRY",
        "secondary_intent": "COMPLAINT_OR_FEEDBACK",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "CHANGED from CHECKIN_OR_BOARDING. Website failure occurred during Cyber Monday fare purchase attempts. Primary=SCHEDULE_OR_BOOKING_INQUIRY, secondary=COMPLAINT_OR_FEEDBACK."
    },
    "G0040": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Lifestyle/travel photo post tagging Delta; warm response from support. No support inquiry. COMPLAINT_OR_FEEDBACK (social)."
    },

    # ─────────────────────────────────────────────────────────────────────────
    # G0041 - G0060
    # ─────────────────────────────────────────────────────────────────────────
    "G0041": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Social post featuring view over Manhattan flying to Tampa. COMPLAINT_OR_FEEDBACK (social)."
    },
    "G0042": {
        "human_final_intent": "CHECKIN_OR_BOARDING",
        "secondary_intent": "COMPLAINT_OR_FEEDBACK",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Sarcastic complaint regarding check-in staff arguing with customers at counter. Primary=CHECKIN_OR_BOARDING, secondary=COMPLAINT_OR_FEEDBACK."
    },
    "G0043": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "REFUND_OR_COMPENSATION",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Diverted passenger packed into taxi with 3 strangers instead of 1st class accommodation. Primary=COMPLAINT_OR_FEEDBACK, secondary=REFUND_OR_COMPENSATION."
    },
    "G0044": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "CANCEL_OR_CHANGE_FLIGHT",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Inquiring about standby clearance likelihood for connecting flight tomorrow. Primary=FLIGHT_STATUS_OR_DELAY, secondary=CANCEL_OR_CHANGE_FLIGHT."
    },
    "G0045": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Customer expressing anger toward a specific support agent named Dan. COMPLAINT_OR_FEEDBACK."
    },
    "G0046": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "CHANGED from CHECKIN_OR_BOARDING. Gratitude shout-out to 'Gate Angel' agent for getting customer on an earlier flight. COMPLAINT_OR_FEEDBACK (positive)."
    },
    "G0047": {
        "human_final_intent": "CHECKIN_OR_BOARDING",
        "secondary_intent": "COMPLAINT_OR_FEEDBACK",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Feedback demanding gate agents enforce zone lineup boarding rules. Primary=CHECKIN_OR_BOARDING, secondary=COMPLAINT_OR_FEEDBACK."
    },
    "G0048": {
        "human_final_intent": "SPECIAL_ASSISTANCE",
        "secondary_intent": "SCHEDULE_OR_BOOKING_INQUIRY",
        "is_multi_intent": "true",
        "annotation_confidence": "MEDIUM",
        "annotator_notes": "CHANGED from SCHEDULE_OR_BOOKING_INQUIRY. Passenger stuck in traffic for last flight asking if Delta can expedite TSA escort on arrival. Primary=SPECIAL_ASSISTANCE, secondary=SCHEDULE_OR_BOOKING_INQUIRY."
    },
    "G0049": {
        "human_final_intent": "CANCEL_OR_CHANGE_FLIGHT",
        "secondary_intent": "FLIGHT_STATUS_OR_DELAY",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Missed connection due to plane mechanical malfunction; asks for direct alternative flight. Primary=CANCEL_OR_CHANGE_FLIGHT, secondary=FLIGHT_STATUS_OR_DELAY."
    },
    "G0050": {
        "human_final_intent": "SKYMILES_OR_LOYALTY",
        "secondary_intent": "COMPLAINT_OR_FEEDBACK",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Medallion member questioning the value of loyalty status when support ignores them. Primary=SKYMILES_OR_LOYALTY, secondary=COMPLAINT_OR_FEEDBACK."
    },
    "G0051": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Flight 2057 sitting at gate 30 minutes after scheduled departure with no word from crew. FLIGHT_STATUS_OR_DELAY."
    },
    "G0052": {
        "human_final_intent": "REFUND_OR_COMPENSATION",
        "secondary_intent": "CANCEL_OR_CHANGE_FLIGHT",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "CHANGED from CANCEL_OR_CHANGE_FLIGHT. Flight already cancelled yesterday; customer is waiting for flight credit/voucher email instructions. Primary=REFUND_OR_COMPENSATION, secondary=CANCEL_OR_CHANGE_FLIGHT."
    },
    "G0053": {
        "human_final_intent": "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "LOW",
        "annotator_notes": "CHANGED from SCHEDULE_OR_BOOKING_INQUIRY. Asking for UK phone number; underlying support issue is completely unknown. AMBIGUOUS_OR_INSUFFICIENT_CONTEXT."
    },
    "G0054": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "SEAT_OR_UPGRADE",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Customer expressing gratitude for surprise seat upgrades on Thanksgiving. Primary=COMPLAINT_OR_FEEDBACK (positive), secondary=SEAT_OR_UPGRADE."
    },
    "G0055": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "COMPLAINT_OR_FEEDBACK",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Severe operational meltdown at Detroit airport with no planes, info, or hotel rooms. Primary=FLIGHT_STATUS_OR_DELAY, secondary=COMPLAINT_OR_FEEDBACK."
    },
    "G0056": {
        "human_final_intent": "SCHEDULE_OR_BOOKING_INQUIRY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Route request imploring Delta to offer non-stop service between MIA/FLL and DCA. SCHEDULE_OR_BOOKING_INQUIRY."
    },
    "G0057": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Social holiday travel post showing custom socks, wishing for smooth ride. COMPLAINT_OR_FEEDBACK (social)."
    },
    "G0058": {
        "human_final_intent": "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "LOW",
        "annotator_notes": "Confirmed. Location check-in at Delta World Headquarters with no customer support request. AMBIGUOUS_OR_INSUFFICIENT_CONTEXT."
    },
    "G0059": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Reporting standard Monday mechanical delay and missed connection. FLIGHT_STATUS_OR_DELAY."
    },
    "G0060": {
        "human_final_intent": "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "LOW",
        "annotator_notes": "Confirmed. 'Sent you a quick DM' tweet with no issue details. AMBIGUOUS_OR_INSUFFICIENT_CONTEXT."
    },

    # ─────────────────────────────────────────────────────────────────────────
    # G0061 - G0080
    # ─────────────────────────────────────────────────────────────────────────
    "G0061": {
        "human_final_intent": "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "LOW",
        "annotator_notes": "Confirmed. 'We arrived' photo post with no support intent. AMBIGUOUS_OR_INSUFFICIENT_CONTEXT."
    },
    "G0062": {
        "human_final_intent": "CHECKIN_OR_BOARDING",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Boarding/check-in pass QR code scan did nothing when scanned. CHECKIN_OR_BOARDING."
    },
    "G0063": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "COMPLAINT_OR_FEEDBACK",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Mass airport disruption with 'airport full of crying people'. Primary=FLIGHT_STATUS_OR_DELAY, secondary=COMPLAINT_OR_FEEDBACK."
    },
    "G0064": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "LOW",
        "annotator_notes": "Confirmed. 'TYSM @Delta' with diamond emoji and photo. Minimal gratitude tweet. COMPLAINT_OR_FEEDBACK."
    },
    "G0065": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Reporting father stranded at Heathrow due to delay; 1.5hr connection extended to 12 hours. FLIGHT_STATUS_OR_DELAY."
    },
    "G0066": {
        "human_final_intent": "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "LOW",
        "annotator_notes": "CHANGED from FLIGHT_STATUS_OR_DELAY. Customer at airport frustrated with 33-55m wait time; specific urgent issue is never stated. AMBIGUOUS_OR_INSUFFICIENT_CONTEXT."
    },
    "G0067": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "BAGGAGE_ISSUE",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "CHANGED from BAGGAGE_ISSUE. Customer praising bag tracking app feature ('great for my anxiety of losing a bag'). No lost bag. Primary=COMPLAINT_OR_FEEDBACK (positive), secondary=BAGGAGE_ISSUE."
    },
    "G0068": {
        "human_final_intent": "PAYMENT_OR_CHARGE_DISPUTE",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. In-flight purchase made and receipt requested by email but not received. Transaction receipt/billing issue. PAYMENT_OR_CHARGE_DISPUTE."
    },
    "G0069": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Praise for Flight 2281 crew working on Thanksgiving. COMPLAINT_OR_FEEDBACK (positive)."
    },
    "G0070": {
        "human_final_intent": "SKYMILES_OR_LOYALTY",
        "secondary_intent": "REFUND_OR_COMPENSATION",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Purser promised 30k miles for broken seat/TV but miles never posted to account. Primary=SKYMILES_OR_LOYALTY, secondary=REFUND_OR_COMPENSATION."
    },
    "G0071": {
        "human_final_intent": "SPECIAL_ASSISTANCE",
        "secondary_intent": "COMPLAINT_OR_FEEDBACK",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Wheelchair assistance failure; passenger forced to use stairs and wait in cold. Primary=SPECIAL_ASSISTANCE, secondary=COMPLAINT_OR_FEEDBACK."
    },
    "G0072": {
        "human_final_intent": "SKYMILES_OR_LOYALTY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Explicit request for assistance transferring SkyMiles. SKYMILES_OR_LOYALTY."
    },
    "G0073": {
        "human_final_intent": "CHECKIN_OR_BOARDING",
        "secondary_intent": "BAGGAGE_ISSUE",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Online check-in app failing when attempting to add checked bag for DL 1065. Primary=CHECKIN_OR_BOARDING, secondary=BAGGAGE_ISSUE."
    },
    "G0074": {
        "human_final_intent": "SKYMILES_OR_LOYALTY",
        "secondary_intent": "SEAT_OR_UPGRADE",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Inquiring how to upgrade Delta flight using partner Flying Blue miles. Primary=SKYMILES_OR_LOYALTY, secondary=SEAT_OR_UPGRADE."
    },
    "G0075": {
        "human_final_intent": "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "LOW",
        "annotator_notes": "Confirmed. 'Need help with my flight. Refer to DM.' No details visible. AMBIGUOUS_OR_INSUFFICIENT_CONTEXT."
    },
    "G0076": {
        "human_final_intent": "REFUND_OR_COMPENSATION",
        "secondary_intent": "COMPLAINT_OR_FEEDBACK",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Customer disputing adequacy of 5,000 miles offered as compensation for 2+ hour delay. Primary=REFUND_OR_COMPENSATION, secondary=COMPLAINT_OR_FEEDBACK."
    },
    "G0077": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "SEAT_OR_UPGRADE",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Thanking Delta for helping get seats. Primary=COMPLAINT_OR_FEEDBACK (positive), secondary=SEAT_OR_UPGRADE."
    },
    "G0078": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "SEAT_OR_UPGRADE",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Gratitude tweet with photo appreciating legroom. Primary=COMPLAINT_OR_FEEDBACK (positive), secondary=SEAT_OR_UPGRADE."
    },
    "G0079": {
        "human_final_intent": "CANCEL_OR_CHANGE_FLIGHT",
        "secondary_intent": "COMPLAINT_OR_FEEDBACK",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Mother's flight was overbooked, requiring driving instead. Involuntary denied boarding / rebooking failure. Primary=CANCEL_OR_CHANGE_FLIGHT, secondary=COMPLAINT_OR_FEEDBACK."
    },
    "G0080": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Praise for outstanding service interaction with customer service agent Jo. COMPLAINT_OR_FEEDBACK (positive)."
    },

    # ─────────────────────────────────────────────────────────────────────────
    # G0081 - G0100
    # ─────────────────────────────────────────────────────────────────────────
    "G0081": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "SEAT_OR_UPGRADE",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Excited gratitude for first-ever first-class upgrade. Primary=COMPLAINT_OR_FEEDBACK (positive), secondary=SEAT_OR_UPGRADE."
    },
    "G0082": {
        "human_final_intent": "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "LOW",
        "annotator_notes": "Confirmed. Foursquare check-in link at Sky Club in Romulus, MI; no support request. AMBIGUOUS_OR_INSUFFICIENT_CONTEXT."
    },
    "G0083": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Direct status inquiry for flight 1412. FLIGHT_STATUS_OR_DELAY."
    },
    "G0084": {
        "human_final_intent": "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "LOW",
        "annotator_notes": "Confirmed. Social photo post showing smiling child/pet on a plane. AMBIGUOUS_OR_INSUFFICIENT_CONTEXT."
    },
    "G0085": {
        "human_final_intent": "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "LOW",
        "annotator_notes": "CHANGED from SCHEDULE_OR_BOOKING_INQUIRY. 'Question about my reservation' with 2hr hold time; specific reservation question is never revealed. AMBIGUOUS_OR_INSUFFICIENT_CONTEXT."
    },
    "G0086": {
        "human_final_intent": "REFUND_OR_COMPENSATION",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Inquiring about refund policy due to inability to travel to/from St. Thomas (hurricane disruption). REFUND_OR_COMPENSATION."
    },
    "G0087": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. General praise indicating strong positive first impression of Delta. COMPLAINT_OR_FEEDBACK (positive)."
    },
    "G0088": {
        "human_final_intent": "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "LOW",
        "annotator_notes": "Confirmed. Weather photo above clouds tagging Delta; no support request. AMBIGUOUS_OR_INSUFFICIENT_CONTEXT."
    },
    "G0089": {
        "human_final_intent": "SCHEDULE_OR_BOOKING_INQUIRY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Pre-booking policy inquiry regarding flight change rules before purchasing JFK to Accra tickets. SCHEDULE_OR_BOOKING_INQUIRY."
    },
    "G0090": {
        "human_final_intent": "SPECIAL_ASSISTANCE",
        "secondary_intent": "COMPLAINT_OR_FEEDBACK",
        "is_multi_intent": "true",
        "annotation_confidence": "MEDIUM",
        "annotator_notes": "Confirmed. Passenger reporting belligerent individual on flight 3771 yelling at flight attendants. In-flight safety/security escalation. Primary=SPECIAL_ASSISTANCE, secondary=COMPLAINT_OR_FEEDBACK."
    },
    "G0091": {
        "human_final_intent": "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "LOW",
        "annotator_notes": "Confirmed. Part 2 of thread asking 'What else would you suggest to correct this?'; root issue from Part 1 missing. AMBIGUOUS_OR_INSUFFICIENT_CONTEXT."
    },
    "G0092": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Thanking Sky Club lounge team for being helpful and solicitous on a crazy day. COMPLAINT_OR_FEEDBACK (positive)."
    },
    "G0093": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Reporting 35-minute delay after 9+ hour flight. FLIGHT_STATUS_OR_DELAY."
    },
    "G0094": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Inquiring about status of flight 4769 and waiting for a pilot assignment. FLIGHT_STATUS_OR_DELAY."
    },
    "G0095": {
        "human_final_intent": "SKYMILES_OR_LOYALTY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. SkyMiles not posted to account despite sending documentation. SKYMILES_OR_LOYALTY."
    },
    "G0096": {
        "human_final_intent": "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "LOW",
        "annotator_notes": "Confirmed. Complaining about 2+ hour phone hold times without mentioning what help is needed. AMBIGUOUS_OR_INSUFFICIENT_CONTEXT."
    },
    "G0097": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Aviation photo of Delta A-320 taking off from DTW. Social post. COMPLAINT_OR_FEEDBACK (positive)."
    },
    "G0098": {
        "human_final_intent": "CHECKIN_OR_BOARDING",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Online check-in failure; booking reference H65AJX not found. CHECKIN_OR_BOARDING."
    },
    "G0099": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Shout-out and praise for flight attendants on flight DL3951. COMPLAINT_OR_FEEDBACK (positive)."
    },
    "G0100": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. 4+ hour maintenance delay on DL3560 to Madison. FLIGHT_STATUS_OR_DELAY."
    },

    # ─────────────────────────────────────────────────────────────────────────
    # G0101 - G0120
    # ─────────────────────────────────────────────────────────────────────────
    "G0101": {
        "human_final_intent": "BAGGAGE_ISSUE",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Lost personal property (iPhone) misplaced near airport gate. Maps to BAGGAGE_ISSUE per taxonomy definition for lost items. BAGGAGE_ISSUE."
    },
    "G0102": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. 2+ hours tarmac delay at LGA with pilot reporting potential fuel constraints. FLIGHT_STATUS_OR_DELAY."
    },
    "G0103": {
        "human_final_intent": "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "LOW",
        "annotator_notes": "Confirmed. 'HMU WITH A FOLLOW BACK' request with no support inquiry. AMBIGUOUS_OR_INSUFFICIENT_CONTEXT."
    },
    "G0104": {
        "human_final_intent": "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "LOW",
        "annotator_notes": "Confirmed. Customer stating they sent a DM; no issue stated. AMBIGUOUS_OR_INSUFFICIENT_CONTEXT."
    },
    "G0105": {
        "human_final_intent": "SEAT_OR_UPGRADE",
        "secondary_intent": "SKYMILES_OR_LOYALTY",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Platinum member complaining about not being upgraded to empty first class cabin. Primary=SEAT_OR_UPGRADE, secondary=SKYMILES_OR_LOYALTY."
    },
    "G0106": {
        "human_final_intent": "SKYMILES_OR_LOYALTY",
        "secondary_intent": "SEAT_OR_UPGRADE",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Upgrade completed but not reflected in SkyMiles account. Primary=SKYMILES_OR_LOYALTY, secondary=SEAT_OR_UPGRADE."
    },
    "G0107": {
        "human_final_intent": "CHECKIN_OR_BOARDING",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Boarding passes generated for tomorrow missing TSA PreCheck endorsement. CHECKIN_OR_BOARDING."
    },
    "G0108": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. In-flight service grievance: customer skipped during beverage/snack service and warm cabin air. COMPLAINT_OR_FEEDBACK."
    },
    "G0109": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "SPECIAL_ASSISTANCE",
        "is_multi_intent": "false",
        "annotation_confidence": "MEDIUM",
        "annotator_notes": "CHANGED from SPECIAL_ASSISTANCE. Customer asking Delta to add vegan non-dairy creamers for coffee. This is general product feedback / suggestion, not an individual disability accommodation. COMPLAINT_OR_FEEDBACK."
    },
    "G0110": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Gratitude to agent CTR for understanding needs and getting husband to destination. COMPLAINT_OR_FEEDBACK (positive)."
    },
    "G0111": {
        "human_final_intent": "SEAT_OR_UPGRADE",
        "secondary_intent": "FLIGHT_STATUS_OR_DELAY",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Stuck on tarmac at LAX and asking what the policy is on upgrading to Delta Comfort now due to anxiety. Primary=SEAT_OR_UPGRADE, secondary=FLIGHT_STATUS_OR_DELAY."
    },
    "G0112": {
        "human_final_intent": "SEAT_OR_UPGRADE",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Pre-selected seats missing on second leg of flight. SEAT_OR_UPGRADE."
    },
    "G0113": {
        "human_final_intent": "SKYMILES_OR_LOYALTY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Questioning SkyMiles policy rewarding miles based on ticket price rather than distance. SKYMILES_OR_LOYALTY."
    },
    "G0114": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "CANCEL_OR_CHANGE_FLIGHT",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. On flight DL2875 arriving 8:45pm, next flight DL3377 departs 9pm; weather delay risk, asking to hold plane. Primary=FLIGHT_STATUS_OR_DELAY, secondary=CANCEL_OR_CHANGE_FLIGHT."
    },
    "G0115": {
        "human_final_intent": "SCHEDULE_OR_BOOKING_INQUIRY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "CHANGED from FLIGHT_STATUS_OR_DELAY. Customer asking if WiFi is offered on flight DL201 JNB to ATL. Amenity inquiry for a flight, not a delay/status issue. SCHEDULE_OR_BOOKING_INQUIRY."
    },
    "G0116": {
        "human_final_intent": "BAGGAGE_ISSUE",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Checked bag returned with tire marks and ripped to shreds; asking how to get a replacement. BAGGAGE_ISSUE."
    },
    "G0117": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Expressing that Delta Sky Club is always a great experience during the busy holidays. COMPLAINT_OR_FEEDBACK (positive)."
    },
    "G0118": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Praise for DAL142 SEA-AMS and steward Jack going above and beyond. COMPLAINT_OR_FEEDBACK (positive)."
    },
    "G0119": {
        "human_final_intent": "CANCEL_OR_CHANGE_FLIGHT",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Customer accidentally canceled flight and urgently needs assistance restoring or rebooking. CANCEL_OR_CHANGE_FLIGHT."
    },
    "G0120": {
        "human_final_intent": "CANCEL_OR_CHANGE_FLIGHT",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "CHANGED from AMBIGUOUS_OR_INSUFFICIENT_CONTEXT. Callback menu broken on phone with >1hr wait; explicit customer goal is 'to ask you about changing a reservation'. CANCEL_OR_CHANGE_FLIGHT."
    },

    # ─────────────────────────────────────────────────────────────────────────
    # G0121 - G0140
    # ─────────────────────────────────────────────────────────────────────────
    "G0121": {
        "human_final_intent": "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "LOW",
        "annotator_notes": "Confirmed. Inquiring about a flight tomorrow after 2hr hold; specific question or issue is omitted. AMBIGUOUS_OR_INSUFFICIENT_CONTEXT."
    },
    "G0122": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "COMPLAINT_OR_FEEDBACK",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Outbound was 90 min late, currently on tarmac 18m waiting for ground crew to park plane. Primary=FLIGHT_STATUS_OR_DELAY, secondary=COMPLAINT_OR_FEEDBACK."
    },
    "G0123": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Social family travel post hoping baby does well on redeye. No support request. COMPLAINT_OR_FEEDBACK (social)."
    },
    "G0124": {
        "human_final_intent": "SCHEDULE_OR_BOOKING_INQUIRY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Asking where to find Cyber Monday fare deals. SCHEDULE_OR_BOOKING_INQUIRY."
    },
    "G0125": {
        "human_final_intent": "SEAT_OR_UPGRADE",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Seat assignment continuously changing/dropping multiple times each day. SEAT_OR_UPGRADE."
    },
    "G0126": {
        "human_final_intent": "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "LOW",
        "annotator_notes": "Confirmed. 'hey i need help @Delta' with no details. AMBIGUOUS_OR_INSUFFICIENT_CONTEXT."
    },
    "G0127": {
        "human_final_intent": "BAGGAGE_ISSUE",
        "secondary_intent": "COMPLAINT_OR_FEEDBACK",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Missing half of luggage for a week with no email update. Primary=BAGGAGE_ISSUE, secondary=COMPLAINT_OR_FEEDBACK."
    },
    "G0128": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Thanking Delta for free in-flight messaging feature. COMPLAINT_OR_FEEDBACK (positive)."
    },
    "G0129": {
        "human_final_intent": "CHECKIN_OR_BOARDING",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Passenger worried about missing flight due to slow/problematic boarding by staff at gate. CHECKIN_OR_BOARDING."
    },
    "G0130": {
        "human_final_intent": "SKYMILES_OR_LOYALTY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Missing MQMs from recent JFK-FCO trip booked via third-party partner. SKYMILES_OR_LOYALTY."
    },
    "G0131": {
        "human_final_intent": "REFUND_OR_COMPENSATION",
        "secondary_intent": "PAYMENT_OR_CHARGE_DISPUTE",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Denied refund for paid Gogo WiFi day pass that could not be used. Primary=REFUND_OR_COMPENSATION, secondary=PAYMENT_OR_CHARGE_DISPUTE."
    },
    "G0132": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "SEAT_OR_UPGRADE",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Passenger on upgrade bubble clears First Class and praises Delta. Primary=COMPLAINT_OR_FEEDBACK (positive), secondary=SEAT_OR_UPGRADE."
    },
    "G0133": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "CANCEL_OR_CHANGE_FLIGHT",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Bird strike causes flight delay and missed connecting flight. Primary=FLIGHT_STATUS_OR_DELAY, secondary=CANCEL_OR_CHANGE_FLIGHT."
    },
    "G0134": {
        "human_final_intent": "BAGGAGE_ISSUE",
        "secondary_intent": "COMPLAINT_OR_FEEDBACK",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Bag lost after flight with broken baggage carousel and no agent present. Primary=BAGGAGE_ISSUE, secondary=COMPLAINT_OR_FEEDBACK."
    },
    "G0135": {
        "human_final_intent": "SCHEDULE_OR_BOOKING_INQUIRY",
        "secondary_intent": "COMPLAINT_OR_FEEDBACK",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Attempting to book flight three times with price increasing dynamically after selection. Primary=SCHEDULE_OR_BOOKING_INQUIRY, secondary=COMPLAINT_OR_FEEDBACK."
    },
    "G0136": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Staff mistreated 75+ year-old passenger; family boycotting airline. COMPLAINT_OR_FEEDBACK."
    },
    "G0137": {
        "human_final_intent": "BAGGAGE_ISSUE",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Lost luggage disrupting scheduled vacation. BAGGAGE_ISSUE."
    },
    "G0138": {
        "human_final_intent": "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT",
        "secondary_intent": "SPECIAL_ASSISTANCE",
        "is_multi_intent": "true",
        "annotation_confidence": "LOW",
        "annotator_notes": "Confirmed. Agent left caller on hold 25 min after callback; mentions father traveling from cancer treatment, but specific booking issue is unstated. Primary=AMBIGUOUS_OR_INSUFFICIENT_CONTEXT, secondary=SPECIAL_ASSISTANCE."
    },
    "G0139": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. High praise for crew member Gayla on flight. COMPLAINT_OR_FEEDBACK (positive)."
    },
    "G0140": {
        "human_final_intent": "SPECIAL_ASSISTANCE",
        "secondary_intent": "CHECKIN_OR_BOARDING",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Passenger told they were checking in early, asks if they should have shown their disability. Primary=SPECIAL_ASSISTANCE, secondary=CHECKIN_OR_BOARDING."
    },

    # ─────────────────────────────────────────────────────────────────────────
    # G0141 - G0160
    # ─────────────────────────────────────────────────────────────────────────
    "G0141": {
        "human_final_intent": "SCHEDULE_OR_BOOKING_INQUIRY",
        "secondary_intent": "BAGGAGE_ISSUE",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "CHANGED from BAGGAGE_ISSUE. Pre-travel inquiry asking how much extra to pay for two checked bags between 50lbs and 99lbs from USA to Brazil. Per taxonomy definitions, pre-flight policy/fee questions belong to SCHEDULE_OR_BOOKING_INQUIRY; secondary=BAGGAGE_ISSUE."
    },
    "G0142": {
        "human_final_intent": "CANCEL_OR_CHANGE_FLIGHT",
        "secondary_intent": "REFUND_OR_COMPENSATION",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed multi-intent. Passenger with tickets to GPT asks if Delta is allowing refunds or changes due to Hurricane Nate. Primary=CANCEL_OR_CHANGE_FLIGHT, secondary=REFUND_OR_COMPENSATION."
    },
    "G0143": {
        "human_final_intent": "SCHEDULE_OR_BOOKING_INQUIRY",
        "secondary_intent": "BAGGAGE_ISSUE",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "CHANGED from BAGGAGE_ISSUE. Pre-travel policy question asking what the earliest bag drop window is before a flight. Belongs to SCHEDULE_OR_BOOKING_INQUIRY per planning context rule; secondary=BAGGAGE_ISSUE."
    },
    "G0144": {
        "human_final_intent": "SPECIAL_ASSISTANCE",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Requesting cargo space to fly water filters to Puerto Rico for emergency disaster relief. SPECIAL_ASSISTANCE."
    },
    "G0145": {
        "human_final_intent": "CANCEL_OR_CHANGE_FLIGHT",
        "secondary_intent": "COMPLAINT_OR_FEEDBACK",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Sarcastic thank-you acknowledging Delta cancelled their December flight; rebooking/itinerary change required. Primary=CANCEL_OR_CHANGE_FLIGHT, secondary=COMPLAINT_OR_FEEDBACK."
    },
    "G0146": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "MEDIUM",
        "annotator_notes": "Confirmed. General expression of repeated dissatisfaction with Delta; no specific issue described. COMPLAINT_OR_FEEDBACK."
    },
    "G0147": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Humorous positive tweet celebrating IFE turned on at gate. COMPLAINT_OR_FEEDBACK (positive)."
    },
    "G0148": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "BAGGAGE_ISSUE",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Giving Delta grade 'F' for handling travelers with guitars. Primary=COMPLAINT_OR_FEEDBACK, secondary=BAGGAGE_ISSUE."
    },
    "G0149": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "CHECKIN_OR_BOARDING",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "CHANGED from FLIGHT_STATUS_OR_DELAY. Customer turned away 4 minutes late with two children, venting about double standard compared to multi-hour airline delays. Primary=COMPLAINT_OR_FEEDBACK, secondary=CHECKIN_OR_BOARDING."
    },
    "G0150": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "FLIGHT_STATUS_OR_DELAY",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Venting that flight fell apart at last minute; no specific status inquiry or flight number. COMPLAINT_OR_FEEDBACK."
    },
    "G0151": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "COMPLAINT_OR_FEEDBACK",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Active operational disruption on DL 6150 to NYC with no information provided. Primary=FLIGHT_STATUS_OR_DELAY, secondary=COMPLAINT_OR_FEEDBACK."
    },
    "G0152": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Nostalgic praise for aircraft retirement with photo. COMPLAINT_OR_FEEDBACK (positive)."
    },
    "G0153": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Humorous tweet about wearing a hoodie on a flight. Social humor. COMPLAINT_OR_FEEDBACK."
    },
    "G0154": {
        "human_final_intent": "SCHEDULE_OR_BOOKING_INQUIRY",
        "secondary_intent": "CHECKIN_OR_BOARDING",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Received confirmation email for Milwaukee roundtrip but no ticket; asking if receipt serves as boarding document. Primary=SCHEDULE_OR_BOOKING_INQUIRY, secondary=CHECKIN_OR_BOARDING."
    },
    "G0155": {
        "human_final_intent": "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "LOW",
        "annotator_notes": "Confirmed. Photo over Cheyenne with no text inquiry. AMBIGUOUS_OR_INSUFFICIENT_CONTEXT."
    },
    "G0156": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "CANCEL_OR_CHANGE_FLIGHT",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Needed emergency change, waited 2hrs twice, hung up on by callback. Primary=COMPLAINT_OR_FEEDBACK (service failure), secondary=CANCEL_OR_CHANGE_FLIGHT."
    },
    "G0157": {
        "human_final_intent": "SCHEDULE_OR_BOOKING_INQUIRY",
        "secondary_intent": "BAGGAGE_ISSUE",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "CHANGED from BAGGAGE_ISSUE. Customer with Delta Amex asking how much 3 bags (1 oversized) will cost before travel. Pre-travel pricing inquiry belongs to SCHEDULE_OR_BOOKING_INQUIRY; secondary=BAGGAGE_ISSUE."
    },
    "G0158": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Positive feedback enjoying free in-flight Wi-Fi and messaging via T-Mobile. COMPLAINT_OR_FEEDBACK (positive)."
    },
    "G0159": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. 7hr delay, new plane, now stopped on tarmac for weather. FLIGHT_STATUS_OR_DELAY."
    },
    "G0160": {
        "human_final_intent": "SKYMILES_OR_LOYALTY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. SkyMiles member under 21 asking for help with account eligibility/promotion. SKYMILES_OR_LOYALTY."
    },

    # ─────────────────────────────────────────────────────────────────────────
    # G0161 - G0180
    # ─────────────────────────────────────────────────────────────────────────
    "G0161": {
        "human_final_intent": "SEAT_OR_UPGRADE",
        "secondary_intent": "PAYMENT_OR_CHARGE_DISPUTE",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Frustrated that booking seats next to 2yr old requires paying $150 extra. Primary=SEAT_OR_UPGRADE, secondary=PAYMENT_OR_CHARGE_DISPUTE."
    },
    "G0162": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "MEDIUM",
        "annotator_notes": "Confirmed. Notifying Delta that a message was sent regarding a very negative customer service experience. COMPLAINT_OR_FEEDBACK."
    },
    "G0163": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "SKYMILES_OR_LOYALTY",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Platinum flyer stating Delta failed them two days in a row; invites contact. Primary=COMPLAINT_OR_FEEDBACK, secondary=SKYMILES_OR_LOYALTY."
    },
    "G0164": {
        "human_final_intent": "CANCEL_OR_CHANGE_FLIGHT",
        "secondary_intent": "COMPLAINT_OR_FEEDBACK",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Involuntary schedule change forced 4hr earlier departure, 2hr later arrival, and double connection. Primary=CANCEL_OR_CHANGE_FLIGHT, secondary=COMPLAINT_OR_FEEDBACK."
    },
    "G0165": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Positive praise for Delta's #GetOnBoard campaign against human trafficking. COMPLAINT_OR_FEEDBACK (positive)."
    },
    "G0166": {
        "human_final_intent": "SEAT_OR_UPGRADE",
        "secondary_intent": "COMPLAINT_OR_FEEDBACK",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Complimentary seat provided for pet dog ('elevated from floor to seat for free'). Primary=SEAT_OR_UPGRADE, secondary=COMPLAINT_OR_FEEDBACK (positive)."
    },
    "G0167": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Praise for fresh, beautiful new 757-200 aircraft IND to ATL. COMPLAINT_OR_FEEDBACK (positive)."
    },
    "G0168": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "MEDIUM",
        "annotator_notes": "Confirmed. Link to external controversy asking for Delta's response to an unacceptable/insulting incident. COMPLAINT_OR_FEEDBACK."
    },
    "G0169": {
        "human_final_intent": "CHECKIN_OR_BOARDING",
        "secondary_intent": "FLIGHT_STATUS_OR_DELAY",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "CHANGED from FLIGHT_STATUS_OR_DELAY. Jet bridge jammed at gate preventing boarding/deplaning. Boarding gate equipment failure. Primary=CHECKIN_OR_BOARDING, secondary=FLIGHT_STATUS_OR_DELAY."
    },
    "G0170": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Public controversy question regarding passenger singing National Anthem for fallen soldier. COMPLAINT_OR_FEEDBACK."
    },
    "G0171": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "CHECKIN_OR_BOARDING",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. DL2121 JFK-PDX: Delta app shows Terminal 2 Gate C-63 while airport monitors show Terminal 4; asks which is correct. Primary=FLIGHT_STATUS_OR_DELAY, secondary=CHECKIN_OR_BOARDING."
    },
    "G0172": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Social travel tweet regarding routing from Kansas City to Atlanta to Dallas. COMPLAINT_OR_FEEDBACK (social)."
    },
    "G0173": {
        "human_final_intent": "PAYMENT_OR_CHARGE_DISPUTE",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Disputing/clarifying whether a $200 charge on account was an unauthorized fee or legitimate fare difference. PAYMENT_OR_CHARGE_DISPUTE."
    },
    "G0174": {
        "human_final_intent": "REFUND_OR_COMPENSATION",
        "secondary_intent": "FLIGHT_STATUS_OR_DELAY",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Demanding refund after missed flight blamed on tower traffic vs de-icing. Primary=REFUND_OR_COMPENSATION, secondary=FLIGHT_STATUS_OR_DELAY."
    },
    "G0175": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Humorous post about rough flight and turbulence from Las Vegas. COMPLAINT_OR_FEEDBACK."
    },
    "G0176": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Complaining about open customer service case from Aug 16 with no response. COMPLAINT_OR_FEEDBACK."
    },
    "G0177": {
        "human_final_intent": "CHECKIN_OR_BOARDING",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. TSA PreCheck missing from generated boarding pass. CHECKIN_OR_BOARDING."
    },
    "G0178": {
        "human_final_intent": "SKYMILES_OR_LOYALTY",
        "secondary_intent": "COMPLAINT_OR_FEEDBACK",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Longtime Diamond and Million Miler jokingly lamenting no Porsche tarmac transfer perk. Primary=SKYMILES_OR_LOYALTY, secondary=COMPLAINT_OR_FEEDBACK."
    },
    "G0179": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Flight 5973 delayed 5+ hours and then flight plan lost. FLIGHT_STATUS_OR_DELAY."
    },
    "G0180": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Grievance that Delta did not advise in advance that flight would have no Wi-Fi before doors closed. COMPLAINT_OR_FEEDBACK."
    },

    # ─────────────────────────────────────────────────────────────────────────
    # G0181 - G0200
    # ─────────────────────────────────────────────────────────────────────────
    "G0181": {
        "human_final_intent": "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT",
        "secondary_intent": "CHECKIN_OR_BOARDING",
        "is_multi_intent": "false",
        "annotation_confidence": "LOW",
        "annotator_notes": "CHANGED from CHECKIN_OR_BOARDING. 'Hey @Delta , your app is still broken' with an external screenshot link. Specific broken module cannot be identified from text alone. AMBIGUOUS_OR_INSUFFICIENT_CONTEXT."
    },
    "G0182": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "LOW",
        "annotator_notes": "Confirmed. Short thank-you post with plane and heart emojis; minimal content. COMPLAINT_OR_FEEDBACK (positive)."
    },
    "G0183": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "SEAT_OR_UPGRADE",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "CHANGED from BAGGAGE_ISSUE. 'Suitcase is out' indicates packing excitement for #PixarCocoEvent; checking upgrade chances in app. Not a baggage complaint. Primary=COMPLAINT_OR_FEEDBACK (social), secondary=SEAT_OR_UPGRADE."
    },
    "G0184": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. General praise that flight was amazing and best air transportation in a long time. COMPLAINT_OR_FEEDBACK (positive)."
    },
    "G0185": {
        "human_final_intent": "SEAT_OR_UPGRADE",
        "secondary_intent": "COMPLAINT_OR_FEEDBACK",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Diamond flyer paid $600 and assigned to last row of Main Cabin. Primary=SEAT_OR_UPGRADE, secondary=COMPLAINT_OR_FEEDBACK."
    },
    "G0186": {
        "human_final_intent": "SKYMILES_OR_LOYALTY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Recent trip shows 0 SkyMiles credited and no response from support. SKYMILES_OR_LOYALTY."
    },
    "G0187": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Social arrival post for think tank event thanking Delta for great flight. COMPLAINT_OR_FEEDBACK (positive)."
    },
    "G0188": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Sitting on runway for an hour following an initial 1-hour flight delay. FLIGHT_STATUS_OR_DELAY."
    },
    "G0189": {
        "human_final_intent": "SCHEDULE_OR_BOOKING_INQUIRY",
        "secondary_intent": "SKYMILES_OR_LOYALTY",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "CHANGED from SKYMILES_OR_LOYALTY. Customer asking how to book a ticket combining gift cards, SkyMiles, and money. Split payment booking inquiry. Primary=SCHEDULE_OR_BOOKING_INQUIRY, secondary=SKYMILES_OR_LOYALTY."
    },
    "G0190": {
        "human_final_intent": "AMBIGUOUS_OR_INSUFFICIENT_CONTEXT",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "LOW",
        "annotator_notes": "Confirmed. Asking for agent assistance or phone callback via Twitter; underlying issue unstated. AMBIGUOUS_OR_INSUFFICIENT_CONTEXT."
    },
    "G0191": {
        "human_final_intent": "SKYMILES_OR_LOYALTY",
        "secondary_intent": "COMPLAINT_OR_FEEDBACK",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Critique of airline loyalty programs destroying Platinum Medallion value. Primary=SKYMILES_OR_LOYALTY, secondary=COMPLAINT_OR_FEEDBACK."
    },
    "G0192": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Comparative service critique stating competitor Wi-Fi is much better than Delta. COMPLAINT_OR_FEEDBACK."
    },
    "G0193": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Reporting mother stuck on plane awaiting takeoff at LaGuardia for over 3 hours. FLIGHT_STATUS_OR_DELAY."
    },
    "G0194": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "CHECKIN_OR_BOARDING",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Passengers waiting at gate with no plane and no agents present. Primary=FLIGHT_STATUS_OR_DELAY, secondary=CHECKIN_OR_BOARDING."
    },
    "G0195": {
        "human_final_intent": "CANCEL_OR_CHANGE_FLIGHT",
        "secondary_intent": "REFUND_OR_COMPENSATION",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Passenger erroneously deplaned for lacking visa to Iceland (none needed); demanding resolution. Primary=CANCEL_OR_CHANGE_FLIGHT, secondary=REFUND_OR_COMPENSATION."
    },
    "G0196": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "BAGGAGE_ISSUE",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "CHANGED from BAGGAGE_ISSUE. On aircraft sitting at gate delayed an hour waiting for luggage loading to finish. Primary=FLIGHT_STATUS_OR_DELAY, secondary=BAGGAGE_ISSUE."
    },
    "G0197": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "CHANGED from FLIGHT_STATUS_OR_DELAY. Flight 2251 crew praise ('this guy was amazing, did a wonderful job'). COMPLAINT_OR_FEEDBACK (positive)."
    },
    "G0198": {
        "human_final_intent": "FLIGHT_STATUS_OR_DELAY",
        "secondary_intent": "CANCEL_OR_CHANGE_FLIGHT",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "CHANGED from CHECKIN_OR_BOARDING. Flight turned around mid-air (diversion/air return) and gate agents providing conflicting information. Primary=FLIGHT_STATUS_OR_DELAY, secondary=CANCEL_OR_CHANGE_FLIGHT."
    },
    "G0199": {
        "human_final_intent": "CANCEL_OR_CHANGE_FLIGHT",
        "secondary_intent": "PAYMENT_OR_CHARGE_DISPUTE",
        "is_multi_intent": "true",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Delta changed original itinerary from GRU without notice to arriving EZE/departing AEP and wanted $10k to fix. Primary=CANCEL_OR_CHANGE_FLIGHT, secondary=PAYMENT_OR_CHARGE_DISPUTE."
    },
    "G0200": {
        "human_final_intent": "COMPLAINT_OR_FEEDBACK",
        "secondary_intent": "",
        "is_multi_intent": "false",
        "annotation_confidence": "HIGH",
        "annotator_notes": "Confirmed. Social travel check-in from El Paso airport heading to Roswell on Delta. COMPLAINT_OR_FEEDBACK (social)."
    },
}
