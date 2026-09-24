"""Second, independent annotator: the zero-shot Groq model labels every usable post, using the same
definitions and rules as the baseline prompt. Used to (1) measure agreement with the primary labels and
(2) triage human review: `python scripts/label.py --review --disagreements` shows only the posts where
the two annotators disagree.

    python scripts/second_annotator.py      # resumable; writes data/second_annotator.csv
"""
import csv
import os
import time
from collections import Counter

from baseline_groq import MODEL, classify, load_key, parse

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "data", "takemeter_labeled.csv")
OUT = os.path.join(ROOT, "data", "second_annotator.csv")


def kappa(a, b):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(a) | set(b)) / n ** 2
    return po, (po - pe) / (1 - pe)


def main():
    key = load_key()
    rows = [r for r in csv.DictReader(open(SRC, encoding="utf-8")) if r["label"] != "SKIP"]
    done = {}
    if os.path.exists(OUT):
        done = {r["id"]: r for r in csv.DictReader(open(OUT, encoding="utf-8"))}
    new = not done
    with open(OUT, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "llm_label", "raw_response", "model"])
        if new:
            w.writeheader()
        for i, r in enumerate(rows):
            if r["id"] in done:
                continue
            raw = classify(r["text"], key)
            rec = {"id": r["id"], "llm_label": parse(raw) or "UNPARSEABLE", "raw_response": raw, "model": MODEL}
            w.writerow(rec)
            f.flush()
            done[r["id"]] = rec
            print(f"{len(done):>3}/{len(rows)}  primary={r['label']:<9} llm={rec['llm_label']}")
            time.sleep(0.5)

    primary = [r["label"] for r in rows]
    second = [done[r["id"]]["llm_label"] for r in rows]
    po, k = kappa(primary, second)
    print(f"\nagreement {po:.3f}   Cohen's kappa {k:.3f}   disagreements {sum(a != b for a, b in zip(primary, second))}/{len(rows)}")
    print("disagreement pairs (primary -> llm):", Counter((a, b) for a, b in zip(primary, second) if a != b).most_common())


if __name__ == "__main__":
    main()
