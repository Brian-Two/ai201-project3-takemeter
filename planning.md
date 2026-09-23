# TakeMeter — Planning

> Written before data collection (Milestone 2). Updated before each stretch feature.
> Graded on its own (4 pts). Every `TODO` needs a real, specific answer.

## 1. Community

**Community:** TODO (e.g. r/___)

**Why it fits a classification task:** TODO — what makes the discourse varied? What would a regular recognize as a good vs. bad take here?

**Summary (2–3 sentences):** TODO — the community, the labels, and why those distinctions matter to people who participate.

## 2. Labels

Written after reading 30–40 real posts. Notes from that read-through: TODO

| Label | Definition (one complete sentence) |
|---|---|
| `label_1` | TODO |
| `label_2` | TODO |
| `label_3` | TODO |

### `label_1`
- Example 1: "TODO"
- Example 2: "TODO"
- Unsure case: "TODO" — could also be ___ because ___

### `label_2`
- Example 1: "TODO"
- Example 2: "TODO"
- Unsure case: "TODO"

### `label_3`
- Example 1: "TODO"
- Example 2: "TODO"
- Unsure case: "TODO"

**Mutual exclusivity check:** TODO — could you assign a random post to exactly one label? Which pair overlaps most?

## 3. Hard Edge Cases

**Hardest anticipated edge case:** TODO — the type of post that sits between `___` and `___`.

**Example post:** "TODO"

**Decision rule:** TODO — "If the post ___, label it ___; otherwise ___."

Other boundary rules:
- Sarcasm / jokes: TODO
- Very short posts (e.g. "lol", "this"): TODO — label or skip?
- Mixed posts (part argument, part emotion): TODO

## 4. Data Collection Plan

- **Source:** TODO (subreddit(s), which threads — game threads vs. discussion posts give different label mixes)
- **Method:** `scripts/collect_reddit.py` pulls public comments; `scripts/label.py` for annotation.
- **Target:** TODO total, roughly TODO per label (aim ≥20% each).
- **If a label is underrepresented after 200:** TODO (e.g. pull from thread types where it's common, like ___)
- **What gets skipped:** TODO (non-English, bot posts, pure links, ...)

## 5. Evaluation Metrics

TODO — which metrics and why they fit *this* task. Consider:
- Why accuracy alone is misleading if labels are imbalanced
- Which per-class metric matters most (is a false `___` worse than a missed `___` for a community tool?)
- Macro-F1 vs. accuracy
- What the confusion matrix will tell you that numbers won't

## 6. Definition of Success

TODO — concrete thresholds, e.g.:
- Fine-tuned accuracy ≥ ___ on the test set
- Macro-F1 ≥ ___, and no class F1 below ___
- Beats the Groq zero-shot baseline by at least ___ points

**Good enough for a real community tool means:** TODO

## 7. AI Tool Plan

- **Label stress-testing:** TODO — which tool; prompt it with definitions + edge case, ask for 5–10 boundary posts; what you'll change if you can't classify them.
- **Annotation assistance:** TODO — will you pre-label? If yes: which tool, and track pre-labeled rows with a note in the `notes` column (e.g. `prelabeled:llm`) for disclosure.
- **Failure analysis:** TODO — paste wrong predictions into ___, ask for patterns (length, sarcasm, label pair); how you'll verify each pattern by re-reading.

## 8. Stretch Feature Plans

_(Fill in before starting each one.)_

- [ ] Inter-annotator reliability — TODO
- [ ] Confidence calibration — TODO
- [ ] Error pattern analysis — TODO
- [ ] Deployed interface — TODO (`app/app.py`, Gradio)
