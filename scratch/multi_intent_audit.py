import csv
from pathlib import Path

def main():
    rows = list(csv.DictReader(open("evaluation/golden_set.csv", encoding="utf-8")))
    multi = [r for r in rows if r.get("is_multi_intent", "").strip().lower() == "true"]
    
    invalid = []
    
    for r in multi:
        pid = r.get("primary_intent")
        sid = r.get("secondary_intent")
        if not sid or sid.strip() == "":
            invalid.append(f"Missing secondary_intent for golden_id {r['golden_id']}")
        elif pid == sid:
            invalid.append(f"Primary and secondary intents are the same ({pid}) for golden_id {r['golden_id']}")

    print(f"Total rows: {len(rows)}")
    print(f"Multi-intent count: {len(multi)}")
    print(f"Invalid count: {len(invalid)}")
    for inv in invalid:
        print(f"  - {inv}")

if __name__ == "__main__":
    main()
