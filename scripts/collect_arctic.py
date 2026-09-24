"""Collect public r/nba comments into data/raw_posts.csv (unlabeled) from the Arctic Shift
Reddit archive (https://arctic-shift.photon-reddit.com — free, read-only, public content only).
Reddit's own .json endpoints block unauthenticated requests, so this is the no-login route.

    python scripts/collect_arctic.py --target 400

Samples threads across the 2025-26 season, keeps at most --per-thread comments from each so no
single thread dominates, and records thread type (post game / news / discussion) for traceability.
"""
import argparse
import csv
import json
import os
import random
import ssl
import time
import urllib.parse
import urllib.request

try:  # python.org macOS builds ship without CA certs
    import certifi
    CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    CTX = ssl.create_default_context()

UA = "takemeter-ai201-class-project/0.1"
API = "https://arctic-shift.photon-reddit.com/api"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "raw_posts.csv")
FIELDS = ["id", "text", "subreddit", "thread_title", "thread_type", "score", "created_utc", "permalink", "batch"]
# (after, before) windows across the regular season and playoffs
WINDOWS = [("2026-01-05", "2026-01-12"), ("2026-02-02", "2026-02-09"), ("2026-03-02", "2026-03-09"),
           ("2026-04-06", "2026-04-13"), ("2026-04-20", "2026-04-27"), ("2026-05-04", "2026-05-11"),
           ("2026-05-18", "2026-05-25"), ("2026-06-08", "2026-06-15")]


def get(path, **params):
    url = f"{API}/{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40, context=CTX) as r:
        return json.load(r)["data"]


def thread_type(title):
    t = title.lower()
    if "post game thread" in t:
        return "post_game"
    if t.startswith("[highlight]"):
        return "highlight"
    if any(k in t for k in ("[wojnarowski]", "[charania]", "[shams]", "[stein]", "[fischer]", "[haynes]", "source:")):
        return "news"
    return "discussion"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subreddit", default="nba")
    ap.add_argument("--threads-per-window", type=int, default=7)
    ap.add_argument("--per-thread", type=int, default=8)
    ap.add_argument("--target", type=int, default=400)
    ap.add_argument("--min-chars", type=int, default=25)
    ap.add_argument("--max-chars", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=201)
    ap.add_argument("--types", default="discussion,post_game,news,highlight",
                    help="thread types to sample, e.g. 'discussion' for a targeted top-up batch")
    ap.add_argument("--batch", default="random", help="tag stored with each row, e.g. 'topup_analysis'")
    args = ap.parse_args()
    rng = random.Random(args.seed)

    seen = set()
    if os.path.exists(OUT):
        with open(OUT, newline="", encoding="utf-8") as f:
            seen = {r["id"] for r in csv.DictReader(f)}
    new_file = not seen

    kept = 0
    with open(OUT, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            w.writeheader()
        for after, before in WINDOWS:
            posts = get("posts/search", subreddit=args.subreddit, after=after, before=before, limit=100)
            posts = [p for p in posts if p.get("num_comments", 0) >= 80 and not p.get("stickied")]
            # mix thread types: post game threads, news, and discussion
            by_type = {}
            for p in posts:
                by_type.setdefault(thread_type(p["title"]), []).append(p)
            picks = []
            types = args.types.split(",")
            for ttype in types:
                pool = by_type.get(ttype, [])
                rng.shuffle(pool)
                picks += pool[:max(2, args.threads_per_window // len(types))]
            for p in picks[:args.threads_per_window]:
                if kept >= args.target:
                    break
                time.sleep(1)
                try:
                    comments = get("comments/search", link_id=p["id"], limit=100)
                except Exception as e:
                    print(f"skip ({e}): {p['title'][:60]}")
                    continue
                rng.shuffle(comments)
                n = 0
                for c in comments:
                    body = (c.get("body") or "").strip()
                    if (c["id"] in seen or body in ("[deleted]", "[removed]")
                            or c.get("author") in ("AutoModerator", "[deleted]")
                            or not args.min_chars <= len(body) <= args.max_chars):
                        continue
                    w.writerow({
                        "id": c["id"], "text": " ".join(body.split()), "subreddit": args.subreddit,
                        "thread_title": p["title"], "thread_type": thread_type(p["title"]),
                        "score": c.get("score", ""), "created_utc": c.get("created_utc", ""),
                        "permalink": "https://www.reddit.com" + c.get("permalink", ""),
                        "batch": args.batch,
                    })
                    seen.add(c["id"])
                    n += 1
                    kept += 1
                    if n >= args.per_thread or kept >= args.target:
                        break
                print(f"{after}  +{n:>2}  [{thread_type(p['title'])}] {p['title'][:70]}")
    print(f"\nAdded {kept} comments -> {os.path.normpath(OUT)} ({len(seen)} total)")


if __name__ == "__main__":
    main()
