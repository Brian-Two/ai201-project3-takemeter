"""Combine fine-tuned + baseline results into outputs/evaluation_results.json and print README-ready
markdown: comparison, per-class metrics, confusion matrices, calibration, and error patterns.

    python scripts/analyze.py > outputs/analysis.md
"""
import json
import os
from collections import Counter

import pandas as pd

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "outputs")
ft = json.load(open(os.path.join(OUT, "finetuned_metrics.json")))
bl_path = os.path.join(OUT, "baseline_metrics.json")
bl = json.load(open(bl_path)) if os.path.exists(bl_path) else None
LABELS = ft["labels"]
preds = pd.read_csv(os.path.join(OUT, "finetuned_test_predictions.csv"), keep_default_na=False)


def cm_table(cm):
    lines = ["| true \\ pred | " + " | ".join(LABELS) + " | total |", "|---" * (len(LABELS) + 2) + "|"]
    for l, row in zip(LABELS, cm):
        lines.append(f"| **{l}** | " + " | ".join(str(v) for v in row) + f" | {sum(row)} |")
    return "\n".join(lines)


print("## Overall\n")
print("| Model | Accuracy | Macro F1 |\n|---|---|---|")
if bl:
    print(f"| Groq zero-shot ({bl['model'].split('/')[-1]}) | {bl['accuracy']:.3f} | {bl['macro_f1']:.3f} |")
print(f"| Fine-tuned DistilBERT | {ft['accuracy']:.3f} | {ft['macro_f1']:.3f} |")
maj = Counter(preds.true).most_common(1)[0]
print(f"| Majority class (always `{maj[0]}`) | {maj[1] / len(preds):.3f} | — |")

print("\n## Per-class (test set, n=%d)\n" % len(preds))
head = "| Label | Support |" + (" Baseline P | Baseline R | Baseline F1 |" if bl else "") + " Fine-tuned P | Fine-tuned R | Fine-tuned F1 |"
print(head)
print("|---" * (head.count("|") - 1) + "|")
for l in LABELS:
    f = ft["per_class"][l]
    row = f"| {l} | {int(f['support'])} |"
    if bl:
        b = bl["per_class"][l]
        row += f" {b['precision']:.2f} | {b['recall']:.2f} | {b['f1-score']:.2f} |"
    row += f" {f['precision']:.2f} | {f['recall']:.2f} | {f['f1-score']:.2f} |"
    print(row)

print("\n## Confusion matrix — fine-tuned (rows = true, columns = predicted)\n")
print(cm_table(ft["confusion_matrix"]))
if bl:
    print("\n## Confusion matrix — baseline\n")
    print(cm_table(bl["confusion_matrix"]))
    if bl["unparseable"]:
        print(f"\n(baseline had {bl['unparseable']} unparseable responses, counted as wrong)")

# ---- calibration ----
preds["correct"] = preds.true == preds.pred
bins = [0, 0.5, 0.7, 0.9, 1.01]
names = ["< 0.50", "0.50–0.70", "0.70–0.90", "≥ 0.90"]
preds["bin"] = pd.cut(preds.confidence, bins=bins, labels=names, right=False)
print("\n## Calibration (fine-tuned)\n")
print("| Confidence | Predictions | Accuracy | Mean confidence |\n|---|---|---|---|")
calib = []
for n in names:
    g = preds[preds.bin == n]
    if len(g):
        print(f"| {n} | {len(g)} | {g.correct.mean():.2f} | {g.confidence.mean():.2f} |")
        calib.append({"bin": n, "n": len(g), "accuracy": round(g.correct.mean(), 3),
                      "mean_confidence": round(g.confidence.mean(), 3)})
ece = sum(c["n"] / len(preds) * abs(c["accuracy"] - c["mean_confidence"]) for c in calib)
print(f"\nExpected calibration error (4 bins): {ece:.3f}")

# ---- error patterns ----
err = preds[~preds.correct]
print(f"\n## Error patterns ({len(err)} errors / {len(preds)})\n")
print("| true → predicted | count |\n|---|---|")
pairs = Counter(zip(err.true, err.pred)).most_common()
for (t, p), c in pairs:
    print(f"| {t} → {p} | {c} |")
preds["length"] = pd.cut(preds.text.str.len(), [0, 80, 200, 10000], labels=["short (<80)", "medium (80–200)", "long (>200)"])
print("\n| Length | n | Accuracy |\n|---|---|---|")
length = []
for n in ["short (<80)", "medium (80–200)", "long (>200)"]:
    g = preds[preds.length == n]
    print(f"| {n} | {len(g)} | {g.correct.mean():.2f} |")
    length.append({"bucket": n, "n": len(g), "accuracy": round(g.correct.mean(), 3)})
print("\n| Predicted label | times predicted | true count |\n|---|---|---|")
for l in LABELS:
    print(f"| {l} | {(preds.pred == l).sum()} | {(preds.true == l).sum()} |")

print("\n## All fine-tuned errors\n")
print("| # | true | pred | conf | text |\n|---|---|---|---|---|")
for i, r in enumerate(err.itertuples(), 1):
    t = r.text.replace("|", "\\|")
    print(f"| {i} | {r.true} | {r.pred} | {r.confidence:.2f} | {t[:220]}{'…' if len(t) > 220 else ''} |")

json.dump({"test_size": len(preds), "labels": LABELS, "finetuned": ft, "baseline": bl,
           "majority_class_accuracy": maj[1] / len(preds), "calibration": calib, "ece": round(ece, 4),
           "error_pairs": [{"true": t, "pred": p, "count": c} for (t, p), c in pairs],
           "accuracy_by_length": length},
          open(os.path.join(OUT, "evaluation_results.json"), "w"), indent=2)
