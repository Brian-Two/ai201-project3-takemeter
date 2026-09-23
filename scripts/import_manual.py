"""Turn hand-copied posts into data/raw_posts.csv so scripts/label.py can use them.

Paste posts into data/manual_posts.txt, one post per block, separated by a line of ---
Optionally put a source URL on the block's first line as "url: https://...".

    url: https://www.reddit.com/r/nba/comments/abc/...
    Jokic is the best passing big ever and it isn't close
    ---
    Another post here...

    python scripts/import_manual.py
Re-run any time. Posts already imported are not added again.
"""
import csv
import hashlib
import os

ROOT = os.path.join(os.path.dirname(__file__), "..")
SRC = os.path.join(ROOT, "data", "manual_posts.txt")
OUT = os.path.join(ROOT, "data", "raw_posts.csv")
FIELDS = ["id", "text", "subreddit", "thread_title", "score", "permalink"]

blocks = [b.strip() for b in open(SRC, encoding="utf-8").read().split("\n---") if b.strip()]
seen = set()
if os.path.exists(OUT):
    with open(OUT, newline="", encoding="utf-8") as f:
        seen = {r["id"] for r in csv.DictReader(f)}

added = 0
with open(OUT, "a", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS)
    if not seen:
        w.writeheader()
    for b in blocks:
        lines = b.splitlines()
        url = ""
        if lines[0].lower().startswith("url:"):
            url = lines.pop(0)[4:].strip()
        text = " ".join(" ".join(lines).split())
        pid = "m_" + hashlib.md5(text.encode()).hexdigest()[:10]
        if not text or pid in seen:
            continue
        w.writerow({"id": pid, "text": text, "subreddit": "", "thread_title": "(manual)",
                    "score": "", "permalink": url})
        seen.add(pid)
        added += 1
print(f"Added {added} posts ({len(seen)} total in raw_posts.csv)")
