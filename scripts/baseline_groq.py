"""Zero-shot baseline on Groq, run on the SAME test split as the fine-tuned model.

The assignment specifies meta-llama/llama-4-scout-17b-16e-instruct, but Groq has retired it (it no
longer appears in /v1/models and returns model_not_found), so the default is openai/gpt-oss-20b, the
closest general-purpose open model still served. Override with GROQ_MODEL=... in .env or the env.

Needs GROQ_API_KEY in .env (never committed). Run after scripts/train.py has written data/splits/.

    python scripts/baseline_groq.py
"""
import csv
import json
import os
import ssl
import time
import urllib.error
import urllib.request

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

try:
    import certifi
    CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    CTX = ssl.create_default_context()

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")
LABELS = list(json.load(open(os.path.join(ROOT, "labels.json")))["labels"])

SYSTEM_PROMPT = """You classify comments from r/nba (the NBA subreddit) by what kind of discourse they are.

Labels:
- analysis: The post makes a basketball claim AND supports it with specific, checkable evidence (stats, concrete game events, tactical detail, or a historical comparison) that actually does the reasoning.
- hot_take: The post confidently asserts an evaluative opinion about players, teams, or the league with no real support, or with support that is vague or decorative.
- reaction: The post expresses an in-the-moment feeling (hype, frustration, disbelief, praise) about a specific play, game, or news item without making a broader claim that outlives the moment.
- banter: Humor is the point: jokes, memes, puns, sarcasm, or riffs where any opinion is only implied and the post is written to be funny rather than to persuade.

Decision rules for hard cases:
- analysis vs hot_take: if the evidence would still support the claim with the opinion framing removed, and there is more than one piece of it or the one piece is load-bearing, it is analysis. A single cherry-picked stat or a vague gesture ("look at his numbers") is hot_take.
- reaction vs hot_take: if the post makes a general evaluative claim about a player/team that someone could still argue with next week (washed, overrated, best ever, should be traded), it is hot_take even if emotional. If it only feels about what just happened, it is reaction.
- banter vs anything: if the literal text is a joke or sarcasm and the opinion must be inferred, it is banter. If a sincere claim has a joke tacked on, label the sincere claim.
- Mixed posts: label by the post's dominant purpose.

Respond with exactly one word: analysis, hot_take, reaction, or banter. No punctuation, no explanation."""


def load_key():
    key = os.environ.get("GROQ_API_KEY")
    env = os.path.join(ROOT, ".env")
    if not key and os.path.exists(env):
        for line in open(env):
            if line.startswith("GROQ_API_KEY="):
                key = line.strip().split("=", 1)[1]
    if not key or key == "your_key_here":
        raise SystemExit("Add GROQ_API_KEY=... to .env (see .env.example)")
    return key


def classify(text, key):
    params = {"model": MODEL, "temperature": 0, "max_tokens": 1024}
    if MODEL.startswith("openai/gpt-oss"):
        params["reasoning_effort"] = "low"  # reasoning model: keep thinking short, answer is still one word
    body = json.dumps({**params, "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Comment: {text}\n\nLabel:"}]}).encode()
    for attempt in range(6):
        req = urllib.request.Request("https://api.groq.com/openai/v1/chat/completions", data=body,
                                     headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                                              "User-Agent": "takemeter-ai201/0.1"})
        try:
            with urllib.request.urlopen(req, timeout=60, context=CTX) as r:
                return json.load(r)["choices"][0]["message"]["content"] or ""
        except urllib.error.HTTPError as e:
            if e.code == 429 or e.code >= 500:
                time.sleep(2 ** attempt * 2)
                continue
            raise
    raise RuntimeError("Groq request kept failing")


def parse(raw):
    t = raw.strip().lower().strip(".`'\" \n")
    if t in LABELS:
        return t
    hits = [l for l in LABELS if l in t or l.replace("_", " ") in t]
    return hits[0] if len(hits) == 1 else None


def main():
    key = load_key()
    test = list(csv.DictReader(open(os.path.join(ROOT, "data", "splits", "test.csv"), encoding="utf-8")))
    rows = []
    for i, r in enumerate(test):
        raw = classify(r["text"], key)
        rows.append({"text": r["text"], "true": r["label"], "raw_response": raw, "pred": parse(raw) or "UNPARSEABLE"})
        print(f"{i + 1:>3}/{len(test)}  true={r['label']:<9} pred={rows[-1]['pred']:<9} raw={raw!r}")
        time.sleep(0.5)

    out = os.path.join(ROOT, "outputs")
    with open(os.path.join(out, "baseline_test_predictions.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["text", "true", "pred", "raw_response"])
        w.writeheader()
        w.writerows(rows)

    y = [r["true"] for r in rows]
    p = [r["pred"] for r in rows]  # unparseable counts as wrong
    unparseable = sum(x == "UNPARSEABLE" for x in p)
    report = classification_report(y, p, labels=LABELS, output_dict=True, zero_division=0)
    cm = confusion_matrix(y, p, labels=LABELS)
    print(classification_report(y, p, labels=LABELS, zero_division=0))
    print(f"unparseable: {unparseable}/{len(p)}")
    json.dump({"model": MODEL, "test_size": len(rows), "unparseable": unparseable,
               "accuracy": accuracy_score(y, p), "macro_f1": report["macro avg"]["f1-score"],
               "per_class": {l: report[l] for l in LABELS}, "confusion_matrix": cm.tolist(),
               "labels": LABELS, "system_prompt": SYSTEM_PROMPT},
              open(os.path.join(out, "baseline_metrics.json"), "w"), indent=2)


if __name__ == "__main__":
    main()
