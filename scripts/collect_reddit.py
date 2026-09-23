"""Collect public comments from a subreddit into data/raw_posts.csv (unlabeled).

Reddit blocks anonymous .json requests, so this uses the official API (app-only,
read-only, public content). One-time setup:
  1. Go to https://www.reddit.com/prefs/apps -> "create another app" -> type "script"
  2. Put the id (under the app name) and secret in .env:
       REDDIT_CLIENT_ID=...
       REDDIT_CLIENT_SECRET=...
If you'd rather collect by hand, use scripts/import_manual.py instead.

    python scripts/collect_reddit.py --subreddit nba --posts 25 --target 300

Collect more than 200 so you have room to drop unusable ones and rebalance labels.
"""
import argparse
import base64
import csv
import json
import os
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
ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "data", "raw_posts.csv")
API = "https://oauth.reddit.com"
TOKEN = None


def load_env():
    path = os.path.join(ROOT, ".env")
    if os.path.exists(path):
        for line in open(path):
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ.setdefault(k, v)


def auth():
    global TOKEN
    cid, secret = os.environ.get("REDDIT_CLIENT_ID"), os.environ.get("REDDIT_CLIENT_SECRET")
    if not cid or not secret:
        raise SystemExit("Missing REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET in .env — see the setup steps at the top of this file.")
    req = urllib.request.Request(
        "https://www.reddit.com/api/v1/access_token",
        data=urllib.parse.urlencode({"grant_type": "client_credentials"}).encode(),
        headers={"User-Agent": UA, "Authorization": "Basic " + base64.b64encode(f"{cid}:{secret}".encode()).decode()},
    )
    with urllib.request.urlopen(req, timeout=20, context=CTX) as r:
        TOKEN = json.load(r)["access_token"]


def get_json(path):
    req = urllib.request.Request(API + path, headers={"User-Agent": UA, "Authorization": f"bearer {TOKEN}"})
    with urllib.request.urlopen(req, timeout=20, context=CTX) as r:
        return json.load(r)


def walk(children, out):
    for c in children:
        if c.get("kind") != "t1":
            continue
        d = c["data"]
        out.append(d)
        replies = d.get("replies")
        if isinstance(replies, dict):
            walk(replies["data"]["children"], out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subreddit", default="nba")
    ap.add_argument("--sort", default="hot", choices=["hot", "top", "new"])
    ap.add_argument("--time", default="week", help="for --sort top: day/week/month/year")
    ap.add_argument("--posts", type=int, default=25, help="threads to pull comments from")
    ap.add_argument("--per-thread", type=int, default=15, help="max comments kept per thread (keeps data diverse)")
    ap.add_argument("--target", type=int, default=300)
    ap.add_argument("--min-chars", type=int, default=30)
    ap.add_argument("--max-chars", type=int, default=1200)
    args = ap.parse_args()

    load_env()
    auth()
    listing = get_json(f"/r/{args.subreddit}/{args.sort}?limit={args.posts}&t={args.time}")
    threads = [c["data"] for c in listing["data"]["children"] if not c["data"].get("stickied")]

    seen = set()
    if os.path.exists(OUT):
        with open(OUT, newline="", encoding="utf-8") as f:
            seen = {r["id"] for r in csv.DictReader(f)}
    new_file = not os.path.exists(OUT)
    fields = ["id", "text", "subreddit", "thread_title", "score", "permalink"]

    kept = 0
    with open(OUT, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if new_file:
            w.writeheader()
        for t in threads:
            if kept >= args.target:
                break
            time.sleep(2)  # be polite to Reddit's rate limits
            try:
                data = get_json(f"{t['permalink']}?limit=200")
            except Exception as e:
                print(f"skip thread ({e}): {t['title'][:60]}")
                continue
            comments = []
            walk(data[1]["data"]["children"], comments)
            n = 0
            for d in comments:
                body = (d.get("body") or "").strip()
                if (d["id"] in seen or body in ("[deleted]", "[removed]")
                        or d.get("author") == "AutoModerator"
                        or not args.min_chars <= len(body) <= args.max_chars):
                    continue
                w.writerow({
                    "id": d["id"],
                    "text": " ".join(body.split()),
                    "subreddit": args.subreddit,
                    "thread_title": t["title"],
                    "score": d.get("score", 0),
                    "permalink": "https://www.reddit.com" + d.get("permalink", ""),
                })
                seen.add(d["id"])
                n += 1
                kept += 1
                if n >= args.per_thread or kept >= args.target:
                    break
            print(f"+{n:>3}  {t['title'][:70]}")
    print(f"\nAdded {kept} comments -> {os.path.normpath(OUT)} ({len(seen)} total)")


if __name__ == "__main__":
    main()
