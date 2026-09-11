import json
import csv
import re
import os
from pathlib import Path
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
import numpy as np

# Mapping keywords from Phase 3 discover.py
KEYWORD_PATTERNS = {
    "FLIGHT_STATUS":          r"\b(flight|status|delayed?|late|arrive|departure|departure|land(ed)?|on time|tracking)\b",
    "BOOKING_RESERVATION":    r"\b(book(ed|ing)?|reservation|ticket|seat|itinerary|confirm|purchase|bought)\b",
    "CANCEL_CHANGE":          r"\b(cancel(led)?|cancellation|change|reschedul|rebook|modify|new flight)\b",
    "BAGGAGE_ISSUE":          r"\b(bag(gage)?|luggage|suitcase|missing bag|lost bag|damaged|delayed bag|checked bag)\b",
    "REFUND_COMPENSATION":    r"\b(refund|compensat|reimburs|credit|voucher|money back|reimbursement|ecredit)\b",
    "PAYMENT_CHARGE":         r"\b(charg(ed)?|payment|paid|fee|cost|price|bill|double charged|overcharged)\b",
    "CHECKIN_BOARDING":       r"\b(check.?in|boarding|gate|board(ed)?|boarded|pass|kiosk)\b",
    "SEAT_UPGRADE":           r"\b(seat|upgrade|comfort\+|business|first class|window|aisle|middle|exit row|seatbelt)\b",
    "SKYMILES_LOYALTY":       r"\b(skymil(es)?|miles|point|loyalty|medallion|status|frequent|reward)\b",
    "COMPLAINT_FEEDBACK":     r"\b(terrible|awful|horrible|worst|disappointed|unacceptable|upset|frustrat|disgraceful|shame)\b",
    "ACCOUNT_ACCESS":         r"\b(account|log(in|ged)|password|sign.?in|reset|profile|email|membership)\b",
    "SPECIAL_ASSISTANCE":     r"\b(wheelchair|disabled|disability|medical|special need|assistance|accessibility|pregnant)\b",
    "LOST_FOUND":             r"\b(lost|found|left behind|forgot|misplaced|left (on|in) (the )?plane)\b",
    "SCHEDULE_INQUIRY":       r"\b(schedule|timetable|when (does|is)|what time|flight time|hours|availability)\b",
    "GENERAL_FEEDBACK":       r"\b(thank(s| you)|great|amazing|love|wonderful|excellent|fantastic|good job|good experience)\b",
}

PATTERN_MAP = {
    "REFUND_COMPENSATION": "REFUND_OR_COMPENSATION",
    "PAYMENT_CHARGE": "PAYMENT_OR_CHARGE_DISPUTE",
    "SPECIAL_ASSISTANCE": "SPECIAL_ASSISTANCE",
    "CANCEL_CHANGE": "CANCEL_OR_CHANGE_FLIGHT",
    "BAGGAGE_ISSUE": "BAGGAGE_ISSUE",
    "LOST_FOUND": "BAGGAGE_ISSUE",
    "CHECKIN_BOARDING": "CHECKIN_OR_BOARDING",
    "SEAT_UPGRADE": "SEAT_OR_UPGRADE",
    "ACCOUNT_ACCESS": "ACCOUNT_ACCESS",
    "SKYMILES_LOYALTY": "SKYMILES_OR_LOYALTY",
    "SCHEDULE_INQUIRY": "SCHEDULE_OR_BOOKING_INQUIRY",
    "BOOKING_RESERVATION": "SCHEDULE_OR_BOOKING_INQUIRY",
    "FLIGHT_STATUS": "FLIGHT_STATUS_OR_DELAY",
    "COMPLAINT_FEEDBACK": "COMPLAINT_OR_FEEDBACK",
    "GENERAL_FEEDBACK": "COMPLAINT_OR_FEEDBACK",
}

PRIORITY_ORDER = [
    "REFUND_OR_COMPENSATION",
    "PAYMENT_OR_CHARGE_DISPUTE",
    "SPECIAL_ASSISTANCE",
    "CANCEL_OR_CHANGE_FLIGHT",
    "BAGGAGE_ISSUE",
    "CHECKIN_OR_BOARDING",
    "SEAT_OR_UPGRADE",
    "ACCOUNT_ACCESS",
    "SKYMILES_OR_LOYALTY",
    "SCHEDULE_OR_BOOKING_INQUIRY",
    "FLIGHT_STATUS_OR_DELAY",
    "COMPLAINT_OR_FEEDBACK",
]

VALID_INTENTS = PRIORITY_ORDER + ["AMBIGUOUS_OR_INSUFFICIENT_CONTEXT"]

def get_pseudo_label(text):
    text_lower = text.lower()
    matched_intents = set()
    for pattern_name, regex in KEYWORD_PATTERNS.items():
        if re.search(regex, text_lower, re.IGNORECASE):
            matched_intents.add(PATTERN_MAP[pattern_name])
            
    for intent in PRIORITY_ORDER:
        if intent in matched_intents:
            return intent
    return None

def load_train_data(path, golden_cids):
    messages = []
    dropped = 0
    total = 0
    
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            conv = json.loads(line)
            cid = str(conv["conversation_id"])
            if cid in golden_cids:
                # Leakage check: skip completely
                continue
                
            msgs = sorted(conv["messages"], key=lambda m: (m.get("timestamp") or "0000", m["message_id"]))
            
            for i, msg in enumerate(msgs):
                if msg["role"] == "CUSTOMER":
                    total += 1
                    text = msg.get("text_clean") or msg.get("text_original", "")
                    label = get_pseudo_label(text)
                    if not label:
                        dropped += 1
                        continue
                    
                    # Context: up to 2 prior turns
                    prior = msgs[max(0, i-2):i]
                    parts = []
                    for pm in prior:
                        parts.append(f"{pm['role']}: {pm.get('text_clean') or pm.get('text_original', '')}")
                    context_str = " | ".join(parts)
                    if context_str:
                        context_str += " | CUSTOMER: " + text
                    else:
                        context_str = "CUSTOMER: " + text
                        
                    messages.append({
                        "id": msg["message_id"],
                        "text": text,
                        "context_text": context_str,
                        "label": label
                    })
    
    return messages, total, dropped

print("Functions defined.")
