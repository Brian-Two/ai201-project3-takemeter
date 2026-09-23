"""Interactive terminal labeler. Reads data/raw_posts.csv, writes data/takemeter_labeled.csv.

    python scripts/label.py

Keys: 1-4 = label, s = skip (unusable post), n = add a note first, u = undo last, q = quit.
Progress saves after every post, so you can quit and resume any time.
Labels come from labels.json.
"""
import csv
import json
import os

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW = os.path.join(ROOT, "data", "raw_posts.csv")
OUT = os.path.join(ROOT, "data", "takemeter_labeled.csv")
FIELDS = ["text", "label", "notes", "id", "permalink"]


def load_labeled():
    if not os.path.exists(OUT):
        return []
    with open(OUT, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save(rows):
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def main():
    cfg = json.load(open(os.path.join(ROOT, "labels.json")))
    labels = list(cfg["labels"])
    with open(RAW, newline="", encoding="utf-8") as f:
        raw = list(csv.DictReader(f))
    rows = load_labeled()
    done = {r["id"] for r in rows}
    queue = [r for r in raw if r["id"] not in done]

    menu = "  ".join(f"[{i + 1}] {l}" for i, l in enumerate(labels))
    i = 0
    while i < len(queue):
        p = queue[i]
        counts = {l: sum(r["label"] == l for r in rows) for l in labels}
        print("\033[2J\033[H", end="")
        print(f"Labeled {sum(counts.values())}  |  " + "  ".join(f"{l}: {c}" for l, c in counts.items()))
        print(f"Thread: {p['thread_title']}\n" + "-" * 70)
        print(p["text"])
        print("-" * 70)
        for l in labels:
            print(f"  {l}: {cfg['labels'][l]}")
        note = ""
        while True:
            k = input(f"\n{menu}  [s]kip [n]ote [u]ndo [q]uit > ").strip().lower()
            if k == "q":
                return
            if k == "n":
                note = input("note (why was this hard?): ").strip()
                continue
            if k == "u" and rows:
                last = rows.pop()
                save(rows)
                if last["label"] != "SKIP":
                    print(f"undid: {last['text'][:60]}")
                i = max(0, i - 1)
                break
            if k == "s" or (k.isdigit() and 1 <= int(k) <= len(labels)):
                label = "SKIP" if k == "s" else labels[int(k) - 1]
                rows.append({"text": p["text"], "label": label, "notes": note,
                             "id": p["id"], "permalink": p["permalink"]})
                save(rows)
                i += 1
                break
    print("Queue empty — collect more with scripts/collect_reddit.py")


if __name__ == "__main__":
    main()
