import json
import random
import csv
from pathlib import Path
import os
import re

DEV_DATA = Path("data/processed/dev.jsonl")
OUT_FILE = Path("evaluation/escalation_gold.csv")

def extract_message(conversation):
    messages = conversation.get("messages", [])
    if not messages:
        return "", ""
    # Find customer message
    cust_msg = ""
    support_ctx = ""
    for m in messages:
        if m.get("role") == "CUSTOMER":
            cust_msg = m.get("text_clean", "")
        elif m.get("role") == "SUPPORT" and not cust_msg:
            support_ctx += m.get("text_clean", "") + " | "
    return cust_msg, support_ctx

def stratify_sample(n=150):
    all_examples = []
    with DEV_DATA.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            all_examples.append(json.loads(line))
            
    random.seed(42)
    random.shuffle(all_examples)
    
    refund = []
    fraud = []
    flight = []
    general = []
    
    for ex in all_examples:
        msg, _ = extract_message(ex)
        msg_lower = msg.lower()
        if re.search(r"refund|compensation|money|charge|paid", msg_lower):
            refund.append(ex)
        elif re.search(r"fraud|stolen|hacked|account|login|password", msg_lower):
            fraud.append(ex)
        elif re.search(r"flight|delay|cancel|rebook|gate|seat", msg_lower):
            flight.append(ex)
        else:
            general.append(ex)
            
    sampled = []
    sampled.extend(refund[:30])
    sampled.extend(fraud[:20])
    sampled.extend(flight[:40])
    sampled.extend(general[:(150 - len(sampled))])
    
    # If we fell short, pad with general
    if len(sampled) < n:
        leftovers = [ex for ex in all_examples if ex not in sampled]
        sampled.extend(leftovers[:n - len(sampled)])
        
    random.shuffle(sampled)
    return sampled

def load_existing():
    existing = set()
    if OUT_FILE.exists():
        with OUT_FILE.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing.add(row["example_id"])
    return existing

def main():
    print("Preparing 150 held-out DEV examples for manual review...")
    samples = stratify_sample(150)
    existing = load_existing()
    
    if not OUT_FILE.exists():
        with OUT_FILE.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["example_id", "customer_message", "context", "expected_decision", "expected_reason_codes", "reviewer_confidence", "reviewer_notes"])
    
    samples_to_do = [s for s in samples if s.get("conversation_id") not in existing]
    
    if not samples_to_do:
        print("All 150 examples have been labeled! You can now proceed to Phase 9.")
        return
        
    print(f"\n{len(samples_to_do)} examples remaining to label.")
    print("For each example, answer the question:")
    print("   Would a safe automated customer-support agent be allowed to handle this request automatically, or should it be routed to a human?")
    print("Type '1' for AUTO_HANDLE, '2' for ESCALATE. Type 'q' to quit and save progress.\n")
    
    with OUT_FILE.open("a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for i, ex in enumerate(samples_to_do):
            eid = ex.get("conversation_id")
            msg, ctx = extract_message(ex)
            
            print("="*60)
            print(f"Example {i+1} / {len(samples_to_do)} (ID: {eid})")
            print("Customer:")
            print(f'"{msg}"\n')
            if ctx:
                print("Conversation context:")
                print(f"{ctx}\n")
                
            print("Choose:")
            print("[1] AUTO_HANDLE")
            print("[2] ESCALATE\n")
            
            decision = ""
            while decision not in ["1", "2", "q"]:
                decision = input("Decision [1, 2, or q to quit]: ").strip().lower()
                
            if decision == "q":
                print("Saving progress and quitting...")
                break
                
            expected_decision = "AUTO_HANDLE" if decision == "1" else "ESCALATE"
            
            print("\nReason:")
            print("[1] SAFE_INFORMATIONAL")
            print("[2] HUMAN_REQUEST")
            print("[3] SAFETY_SENSITIVE")
            print("[4] VERIFICATION_REQUIRED")
            print("[5] LOW_CONTEXT")
            print("[6] POLICY_RESTRICTION")
            print("[7] PROMPT_INJECTION")
            print("[8] OTHER\n")
            
            reason_map = {
                "1": "SAFE_INFORMATIONAL",
                "2": "HUMAN_REQUEST",
                "3": "SAFETY_SENSITIVE",
                "4": "VERIFICATION_REQUIRED",
                "5": "LOW_CONTEXT",
                "6": "POLICY_RESTRICTION",
                "7": "PROMPT_INJECTION",
                "8": "OTHER"
            }
            
            r_choice = ""
            while r_choice not in reason_map:
                r_choice = input("Reason [1-8]: ").strip()
            expected_reason_codes = reason_map[r_choice]
            
            print("\nConfidence:")
            print("[1] HIGH")
            print("[2] MEDIUM")
            print("[3] LOW\n")
            
            conf_map = {"1": "HIGH", "2": "MEDIUM", "3": "LOW"}
            c_choice = ""
            while c_choice not in conf_map:
                c_choice = input("Confidence [1-3]: ").strip()
            reviewer_confidence = conf_map[c_choice]
            
            reviewer_notes = input("\nNotes (optional): ").strip()
            
            writer.writerow([
                eid,
                msg,
                ctx,
                expected_decision,
                expected_reason_codes,
                reviewer_confidence,
                reviewer_notes
            ])
            f.flush()
            print("\n")
            
    print("\nSession ended. Run this script again to continue labeling if not finished.")

if __name__ == "__main__":
    main()
