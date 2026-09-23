# TakeMeter

A fine-tuned DistilBERT classifier that rates discourse quality in TODO (community).

**Demo video:** TODO (3–5 min link)
**Dataset:** [`data/takemeter_final.csv`](data/takemeter_final.csv)
**Planning doc:** [`planning.md`](planning.md)

## Results Summary

| Model | Accuracy | Macro F1 |
|---|---|---|
| Groq zero-shot (llama-4-scout-17b) | TODO | TODO |
| Fine-tuned DistilBERT | TODO | TODO |

TODO: one or two sentences on the headline finding.

## Community

TODO — which community and why it fits this task.

## Label Taxonomy

| Label | Definition | Example 1 | Example 2 |
|---|---|---|---|
| `label_1` | TODO | "TODO" | "TODO" |
| `label_2` | TODO | "TODO" | "TODO" |
| `label_3` | TODO | "TODO" | "TODO" |

## Dataset

- **Source:** TODO (subreddits, thread types, date range)
- **Collection:** TODO
- **Labeling process:** TODO (read each post, decision rules, any LLM pre-labeling disclosed)

**Label distribution** (paste output of `python scripts/stats.py`):

| Label | Count | % |
|---|---|---|
| TODO | | |

### Difficult-to-label examples

1. "TODO" — could be `___` or `___`. Decided `___` because ___.
2. "TODO" — ...
3. "TODO" — ...

## Fine-Tuning

- **Base model:** `distilbert-base-uncased`
- **Platform:** Google Colab, T4 GPU (CodePath starter notebook)
- **Split:** 70 / 15 / 15 train / val / test
- **Hyperparameters:** epochs TODO, learning rate TODO, batch size TODO
- **Key decision:** TODO — what you changed or kept, and the observation that justified it (e.g. validation loss per epoch)

## Baseline

Zero-shot `meta-llama/llama-4-scout-17b-16e-instruct` via Groq, run on the same test set.

Prompt used:

```
TODO paste exact prompt
```

How results were collected: TODO (unparseable responses count, etc.)

## Evaluation Report

### Per-class metrics

| Label | Baseline P | Baseline R | Baseline F1 | Fine-tuned P | Fine-tuned R | Fine-tuned F1 |
|---|---|---|---|---|---|---|
| TODO | | | | | | |

### Confusion matrix (fine-tuned, rows = true, columns = predicted)

| true \ pred | label_1 | label_2 | label_3 |
|---|---|---|---|
| **label_1** | | | |
| **label_2** | | | |
| **label_3** | | | |

Image copy: [`outputs/confusion_matrix.png`](outputs/confusion_matrix.png) · Raw numbers: [`outputs/evaluation_results.json`](outputs/evaluation_results.json)

### Wrong predictions

1. **"TODO"** — true `___`, predicted `___` (conf ___). Why: TODO (label boundary? sarcasm? length? annotation inconsistency?) What would fix it: TODO
2. ...
3. ...

### Sample classifications

| Post | Predicted | Confidence | Correct? |
|---|---|---|---|
| "TODO" | | | |

Why the correct prediction in row ___ is reasonable: TODO

## Reflection: What the Model Learned vs. What I Intended

TODO — a specific pattern (label pair, post type, distribution issue), not "needs more data".

## Spec Reflection

- **How the spec helped:** TODO
- **Where implementation diverged and why:** TODO

## AI Usage

1. **TODO:** what I directed the AI to do → what it produced → what I changed or overrode.
2. **TODO:** ...

Annotation assistance disclosure: TODO

## Repo Layout & How to Run

```
data/raw_posts.csv            unlabeled comments from collect_reddit.py
data/takemeter_labeled.csv    working labels (incl. SKIPs, notes)
data/takemeter_final.csv      final dataset uploaded to Colab
outputs/                      evaluation_results.json, confusion_matrix.png from Colab
scripts/collect_reddit.py     collect public comments via the official Reddit API
scripts/import_manual.py      or: import hand-copied posts from data/manual_posts.txt
scripts/label.py              terminal labeling tool
scripts/stats.py              distribution + requirement checks, exports final CSV
app/app.py                    (stretch) Gradio interface
labels.json                   label names + definitions shared by all scripts
```

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add Reddit API keys if using collect_reddit.py (never committed)

# collect: either the API...
python scripts/collect_reddit.py --subreddit nba --target 300
# ...or paste posts into data/manual_posts.txt (separated by ---) and run
python scripts/import_manual.py

python scripts/label.py
python scripts/stats.py --export
```
