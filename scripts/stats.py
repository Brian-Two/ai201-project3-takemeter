"""Check the labeled dataset against the project requirements and print a README-ready table.

    python scripts/stats.py            # report
    python scripts/stats.py --export   # also write data/takemeter_final.csv (text,label,notes; SKIPs removed) for Colab
"""
import argparse
import csv
import os
from collections import Counter

ROOT = os.path.join(os.path.dirname(__file__), "..")
SRC = os.path.join(ROOT, "data", "takemeter_labeled.csv")
FINAL = os.path.join(ROOT, "data", "takemeter_final.csv")

ap = argparse.ArgumentParser()
ap.add_argument("--export", action="store_true")
args = ap.parse_args()

with open(SRC, newline="", encoding="utf-8") as f:
    all_rows = list(csv.DictReader(f))
skipped = sum(r["label"] == "SKIP" for r in all_rows)
rows, seen = [], set()
for r in all_rows:
    if r["label"] != "SKIP" and r["text"] not in seen:
        rows.append(r)
        seen.add(r["text"])
n = len(rows)
if not n:
    raise SystemExit("No labeled examples yet.")
counts = Counter(r["label"] for r in rows)
hard = sum(bool(r["notes"].strip()) for r in rows)

print(f"Usable examples: {n}  (skipped as unusable: {skipped})\n")
print("| Label | Count | % |\n|---|---|---|")
for label, c in counts.most_common():
    print(f"| {label} | {c} | {c / n:.1%} |")
print(f"| **Total** | **{n}** | 100% |\n")

hi, lo = max(counts.values()) / n, min(counts.values()) / n
print("Checks:")
print(f"  [{'x' if n >= 200 else ' '}] at least 200 examples ({n})")
print(f"  [{'x' if hi <= 0.70 else ' '}] no label above 70% (max {hi:.1%})")
print(f"  [{'x' if lo >= 0.20 else ' '}] every label at least 20% — recommended (min {lo:.1%})")
print(f"  [{'x' if hard >= 3 else ' '}] at least 3 hard cases noted ({hard})")

if args.export:
    with open(FINAL, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["text", "label", "notes"], extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"\nWrote {os.path.normpath(FINAL)} — upload this file in Colab Section 1.")
