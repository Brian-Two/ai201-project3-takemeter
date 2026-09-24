"""Interactive terminal labeler. Labels come from labels.json.

    python scripts/label.py            # label new posts from data/raw_posts.csv
    python scripts/label.py --review   # step through existing labels and correct them
    python scripts/label.py --review --disagreements   # only posts where the second annotator
                                                       # (scripts/second_annotator.py) disagrees

Label mode keys: 1-4 = label, s = skip (out of scope), n = add a note first, u = undo last, q = quit.
Review mode keys: Enter = keep, 1-4 = change label, s = mark SKIP, n = edit note, b = back, q = quit.
Rows you confirm or change in review are marked human-reviewed / human-corrected in the annotator column.
Progress saves after every post, so you can quit and resume any time.
"""
import argparse
import csv
import json
import os

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW = os.path.join(ROOT, "data", "raw_posts.csv")
OUT = os.path.join(ROOT, "data", "takemeter_labeled.csv")
FIELDS = ["text", "label", "notes", "annotator", "id", "permalink", "thread_type", "batch"]


def load_labeled():
    if not os.path.exists(OUT):
        return []
    with open(OUT, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save(rows):
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def show(cfg, labels, rows, text, header):
    counts = {l: sum(r["label"] == l for r in rows) for l in labels}
    print("\033[2J\033[H", end="")
    print(f"Labeled {sum(counts.values())}  |  " + "  ".join(f"{l}: {c}" for l, c in counts.items()))
    print(header + "\n" + "-" * 70)
    print(text)
    print("-" * 70)
    for l in labels:
        print(f"  {l}: {cfg['labels'][l]}")


def label_mode(cfg, labels):
    with open(RAW, newline="", encoding="utf-8") as f:
        raw = list(csv.DictReader(f))
    rows = load_labeled()
    done = {r["id"] for r in rows}
    queue = [r for r in raw if r["id"] not in done]
    menu = "  ".join(f"[{i + 1}] {l}" for i, l in enumerate(labels))
    i = 0
    while i < len(queue):
        p = queue[i]
        show(cfg, labels, rows, p["text"], f"Thread: {p['thread_title']}")
        note = ""
        while True:
            k = input(f"\n{menu}  [s]kip [n]ote [u]ndo [q]uit > ").strip().lower()
            if k == "q":
                return
            if k == "n":
                note = input("note (why was this hard?): ").strip()
                continue
            if k == "u" and rows:
                rows.pop()
                save(rows)
                i = max(0, i - 1)
                break
            if k == "s" or (k.isdigit() and 1 <= int(k) <= len(labels)):
                rows.append({"text": p["text"], "label": "SKIP" if k == "s" else labels[int(k) - 1],
                             "notes": note, "annotator": "human", "id": p["id"],
                             "permalink": p["permalink"], "thread_type": p.get("thread_type", ""),
                             "batch": p.get("batch", "")})
                save(rows)
                i += 1
                break
    print("Queue empty — collect more with scripts/collect_arctic.py or scripts/import_manual.py")


def review_mode(cfg, labels, disagreements=False):
    rows = load_labeled()
    menu = "  ".join(f"[{i + 1}] {l}" for i, l in enumerate(labels))
    second = {}
    if disagreements:
        path = os.path.join(ROOT, "data", "second_annotator.csv")
        if not os.path.exists(path):
            raise SystemExit("Run scripts/second_annotator.py first.")
        second = {r["id"]: r["llm_label"] for r in csv.DictReader(open(path, encoding="utf-8"))}
        order = [i for i, r in enumerate(rows) if r["id"] in second and second[r["id"]] != r["label"]]
    else:
        order = list(range(len(rows)))
    pos = next((k for k, i in enumerate(order) if not rows[i]["annotator"].startswith("human")), len(order))
    while pos < len(order):
        i = order[pos]
        r = rows[i]
        reviewed = sum(rows[j]["annotator"].startswith("human") for j in order)
        other = f"   SECOND ANNOTATOR SAYS: {second[r['id']].upper()}" if disagreements else ""
        show(cfg, labels, rows, r["text"],
             f"Review {pos + 1}/{len(order)} (reviewed {reviewed})   CURRENT LABEL: {r['label'].upper()}{other}"
             + (f"\nNote: {r['notes']}" if r["notes"] else ""))
        k = input(f"\n[Enter] keep  {menu}  [s]kip [n]ote [b]ack [q]uit > ").strip().lower()
        if k == "q":
            return
        if k == "b":
            pos = max(0, pos - 1)
            continue
        if k == "n":
            r["notes"] = input("note: ").strip()
            save(rows)
            continue
        new = r["label"]
        if k == "s":
            new = "SKIP"
        elif k.isdigit() and 1 <= int(k) <= len(labels):
            new = labels[int(k) - 1]
        elif k:
            continue
        if new != r["label"]:
            r["notes"] = (r["notes"] + f" | was {r['label']} (pre-label), corrected on review").strip(" |")
            r["label"], r["annotator"] = new, "human-corrected"
        elif not r["annotator"].startswith("human"):
            r["annotator"] = "human-reviewed"
        save(rows)
        pos += 1
    print("Review complete. Re-run: python scripts/stats.py --export")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", action="store_true")
    ap.add_argument("--disagreements", action="store_true", help="with --review: only posts the second annotator labels differently")
    args = ap.parse_args()
    cfg = json.load(open(os.path.join(ROOT, "labels.json")))
    labels = list(cfg["labels"])
    if args.review:
        review_mode(cfg, labels, args.disagreements)
    else:
        label_mode(cfg, labels)
