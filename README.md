# TakeMeter — r/nba discourse classifier

A fine-tuned DistilBERT model that labels r/nba comments as **`analysis`**, **`hot_take`**, **`reaction`**, or **`banter`**, compared against a zero-shot LLM baseline on the same held-out test set.

- **Demo video:** _TODO: add link (3–5 min)_. Script: [`docs/demo_script.md`](docs/demo_script.md)
- **Labeled dataset:** [`data/takemeter_final.csv`](data/takemeter_final.csv) (389 examples) · full annotation file with skips, notes and provenance: [`data/takemeter_labeled.csv`](data/takemeter_labeled.csv)
- **Planning doc:** [`planning.md`](planning.md) · **Raw metrics:** [`outputs/evaluation_results.json`](outputs/evaluation_results.json)

## Results at a glance

Test set: 59 held-out comments (stratified 15% split, never used for training or model selection).

| Model | Accuracy | Macro F1 | `analysis` F1 | `hot_take` F1 | `reaction` F1 | `banter` F1 |
|---|---|---|---|---|---|---|
| Majority class (always `hot_take`) | 0.475 | 0.161 | 0 | 0.64 | 0 | 0 |
| Zero-shot baseline (Groq `openai/gpt-oss-20b`) | 0.627 | 0.565 | 0.47 | 0.71 | **0.50** | **0.58** |
| **Fine-tuned DistilBERT** | **0.644** | **0.596** | **0.86** | **0.75** | 0.21 | 0.56 |

**Headline:** fine-tuning roughly matches the zero-shot LLM overall. It's one more correct test example, which is within noise at n=59. But the two models are good at different things. The fine-tuned model is far better at spotting **`analysis`** (F1 0.86 vs 0.47, precision 0.82). It's much worse at telling **`reaction`** from **`banter`**, because it mostly learned post *length and specificity*, not *purpose*. See the [reflection](#reflection-what-the-model-learned-vs-what-i-intended).

**Against the success criteria set in `planning.md` before any data was collected:**

| Criterion (planning.md §6) | Result | Met? |
|---|---|---|
| Macro-F1 ≥ 0.60 | 0.596 | ✗ (just missed) |
| No class F1 below 0.45 | `reaction` = 0.21 | ✗ |
| Beat baseline by ≥ 5 pts macro-F1 | +3.1 pts | ✗ |
| `analysis` precision ≥ 0.70 | 0.82 | ✓ |

So the "show me the analysis comments" use case described in `planning.md` works. A general-purpose four-way classifier does not.

---

## Community

**r/nba**, the main NBA subreddit (~17M members). Comments were taken from Post Game Threads, highlight clips, news/insider threads, and discussion posts across the 2025–26 season and playoffs (Jan–June 2026).

It's a good fit because a single r/nba thread mixes four genuinely different kinds of writing:
- people breaking down *why* something happened, using stats or film;
- people declaring someone washed or overrated with nothing behind it;
- people yelling about the play that just happened;
- people making jokes.

Regulars care about the difference. "Source?", "hot take", and "nephew behavior" are standard replies, and r/nbadiscussion exists as a spin-off precisely because r/nba is seen as too hot-take-heavy. A tool that surfaced the `analysis` comments out of a 3,000-comment Post Game Thread would be useful to people who want substance.

## Label taxonomy

Each label answers a different question about the comment's **purpose**:

| Label | Definition | Example 1 | Example 2 |
|---|---|---|---|
| `analysis` | The post makes a basketball claim **and** supports it with specific, checkable evidence (stats, concrete game events, tactical detail, or a historical comparison) that actually does the reasoning. | "Yeah it really wasn't close but Boston won 64 games for a reason. They beat up the East as they should and Luka was already hobbled coming into the Finals…" | "Celtics have the toughest remaining strength of schedule for any of the east teams. Cleveland, New York, and Detroit are all in the bottom 10…" |
| `hot_take` | The post confidently asserts an evaluative opinion about players, teams, or the league with no real support, or with support that is vague or decorative. | "He is literally a byproduct of LeBron. He will be irrelevant once LeBron retires" | "Knicks might be in trouble. When you can't beat the team that can't beat anyone above .500, you're in trouble." |
| `reaction` | The post expresses an in-the-moment feeling (hype, frustration, disbelief, praise) about a specific play, game, or news item without making a broader claim that outlives the moment. | "Chuck is a gem Ima miss him when he retires man" | "I was so pissed when he hit this shot." |
| `banter` | Humor is the point: jokes, memes, puns, sarcasm, or riffs where any opinion is only implied and the post is written to be funny rather than to persuade. | "They got that DAWG in them — and by dawg I mean so much spyware" | "We just call any shot in the 4th quarter a dagger now huh" |

**Decision rules for boundary cases** (full versions in [`planning.md` §3](planning.md)):
- **A (`analysis` vs `hot_take`):** it's `analysis` only if the evidence would still support the claim with the opinion framing removed, *and* there's more than one piece of evidence or the one piece is load-bearing. A single cherry-picked stat is `hot_take`.
- **B (`reaction` vs `hot_take`):** "Would this still be a claim someone could argue with next week?" If yes, it's `hot_take` even when emotional ("Luka is washed"). If it only feels about what just happened, it's `reaction`.
- **C (`banter` vs anything):** if the literal text is a joke or sarcasm and the opinion must be inferred, it's `banter`. A sincere claim with a joke tacked on is labeled by the claim.
- **Out of scope (skipped, not labeled):** pure questions, logistics ("how do I watch this?"), off-topic arguments (politics, personal insults between users), non-basketball content, and link-only posts.

## Dataset

**Source:** public r/nba comments from the [Arctic Shift](https://arctic-shift.photon-reddit.com) Reddit archive, a free, read-only research API. Reddit's own `.json` endpoints now return `403 Blocked` for requests without a login. Collection script: [`scripts/collect_arctic.py`](scripts/collect_arctic.py). Every row keeps its permalink, thread type and collection batch.

**Collection (472 comments from ~60 threads):**
1. **Random batch (352):** up to 8 comments from each of 44 threads across 8 one-week windows from January to June 2026. Threads were mixed by type: discussion, post game, news, highlight.
2. **Targeted top-ups (120).** After the first 352 were labeled, `analysis` (15%) and `reaction` (13%) were under the 20% target. Following the plan in `planning.md` §4, I pulled:
   - 60 long comments (≥ 220 characters) from discussion threads, for `analysis`;
   - 60 short comments (≤ 160 characters) from post game and highlight threads, for `reaction`.

   _This length filtering turned out to matter; see [Reflection](#reflection-what-the-model-learned-vs-what-i-intended)._

**Labeling process:**
- Labels were first assigned by Claude (AI pre-labeling, disclosed in [AI usage](#ai-usage)). Every comment was read in full against the definitions and rules A–C.
- The annotator wrote a note on any case that needed a rule to resolve; there are 40 notes in the `notes` column.
- Each row's `annotator` column records whether it's an AI pre-label, a human-confirmed label, or a human correction. `python scripts/label.py --review` steps through the pre-labels for human review.
- **Review triage.** A second, independent annotator (the zero-shot Groq model, same definitions) labeled all 389 posts; see [Annotator agreement](#annotator-agreement-stretch-model-vs-model). The 142 posts where the two disagree are the review queue: `python scripts/label.py --review --disagreements`. Posts where both annotators agree (247) are more likely correct, but they are still AI labels, not human-verified.
- 83 of 472 comments (17.6%) were skipped as out of scope. That's higher than the ~10% estimated in `planning.md`, mainly because of user-vs-user insult chains in discussion threads.

**Label distribution (389 usable examples):**

| Label | Count | % |
|---|---|---|
| hot_take | 182 | 46.8% |
| banter | 90 | 23.1% |
| analysis | 66 | 17.0% |
| reaction | 51 | 13.1% |
| **Total** | **389** | 100% |

No label is above 70%. `analysis` and `reaction` stayed below the recommended 20% even after the top-ups, because the `reaction` top-up mostly surfaced more `hot_take` and `banter`. This imbalance is handled in training with class weights (below).

**Split** ([`data/splits/`](data/splits)): stratified 70/15/15 with seed 42, giving 272 train, 58 validation and 59 test. The baseline and the fine-tuned model are scored on the identical `test.csv`.

### Difficult-to-label examples

1. **"[r-slur] rule. Average all star player play sth like 60 games. So if you are going to set a rule, make it meaningful stats wise. If average of your top 24 player is around 62 games then minimum threshold should be somewhere like 50-55 games…"**
   - *Could be:* `hot_take`, since the tone is pure outrage and it opens with a slur, or `analysis`.
   - *Decided:* **`analysis`**. By rule A, strip the anger and a real argument is left: the threshold should sit just below the typical games played by top players, backed by a specific number. The lesson is that tone doesn't decide the label; the structure of the argument does.
2. **"Embiid is a fucking warrior."** (on news that Embiid would play through injury)
   - *Could be:* `hot_take` (a general claim about his character) or `reaction`.
   - *Decided:* **`reaction`**. By rule B, this is praise for *this* decision in *this* moment, not a claim anyone would still be debating next week. The same words in a "who's the toughest player in the league" thread would be a `hot_take`.
3. **"if ant went for 40 in both games shooting a combined 64% while devin booker shot a tour date in one game and missed the other, surely the wolves won those games right?"**
   - *Could be:* `analysis` (real stats making a real point) or `banter`.
   - *Decided:* **`banter`**. By rule C, the literal text is sarcasm, and the point (individual stats don't decide games) has to be inferred. This is the case the taxonomy handles worst: the post is funny *and* makes an argument.
4. **A long nostalgic memory:** "I remember a late-night game at Sacramento in March of '19 where he went nuclear in the 4th quarter and led them back from 25 down, with Atkinson going with DLo, Kurucs, Treveon Graham, Dudley and RHJ the whole quarter…"
   - *Could be:* `analysis`, because it's packed with specifics.
   - *Decided:* **`reaction`**. The specifics don't support any claim; the purpose is fond memory. The fine-tuned model got this one wrong in exactly the way the decision predicts (error 1 below).

## Fine-tuning

- **Base model:** `distilbert-base-uncased` (66M parameters) with a 4-way classification head.
- **Platform:** trained locally on an Apple-silicon MacBook GPU (PyTorch MPS) using Hugging Face `transformers` `Trainer`: [`scripts/train.py`](scripts/train.py). It mirrors the CodePath starter notebook: same model, same 70/15/15 split and the same default hyperparameters, run as a script. Each run takes about 2 minutes.
- **Setup:** max 256 tokens, AdamW with weight decay 0.01, 10% warmup, evaluation on the validation set after every epoch. The checkpoint with the best **validation** macro-F1 is kept.
- **Final config:** 8 epochs, learning rate 3e-5, batch size 16, **inverse-frequency class weights** in the loss. The best checkpoint was at epoch 4.

### Key hyperparameter decisions

All configs were compared on the 58-example **validation** set only; the test set was scored once at the end. Full log: [`outputs/hparam_runs.json`](outputs/hparam_runs.json).

| Config | Class weights | Best val macro-F1 | Best epoch | What happened |
|---|---|---|---|---|
| 3 epochs, lr 2e-5, bs 16 (notebook default) | no | 0.159 | — | Predicted `hot_take` for every post |
| 8 epochs, lr 3e-5, bs 16 | no | 0.444 | 8 | Learns, but minority classes lag |
| **8 epochs, lr 3e-5, bs 16** | **yes** | **0.529** | **4** | **Chosen**: best epoch = lowest val loss (1.03) |
| 10 epochs, lr 5e-5, bs 16 | yes | 0.545 | 9 | Val loss rose 1.02 → 1.87; overconfident |
| 8 epochs, lr 3e-5, bs 8 | yes | 0.509 | 2 | Peaked early, then degraded |
| 12 epochs, lr 2e-5, bs 8 | yes | 0.531 | 5 | Similar, slower |

1. **More epochs than the default.** With 272 training examples at batch size 16, 3 epochs is only 51 gradient updates. At that point the model had only learned the class prior: validation accuracy was 0.466, exactly the `hot_take` share, and macro-F1 was 0.16. Accuracy alone would have hidden this, which is why `planning.md` made macro-F1 the primary metric.
2. **Class weights.** At identical settings, weighting the loss by inverse class frequency raised validation macro-F1 from 0.44 to 0.53. Without the weights, the 47% `hot_take` class pulled predictions toward itself.
3. **Picking the second-best config on purpose.** The 10-epoch, lr 5e-5 run had the highest validation macro-F1 (0.545), but its validation loss climbed from 1.02 to 1.87 while macro-F1 bounced around. It was memorizing the training set and becoming confidently wrong. The chosen run's best checkpoint sits at its lowest validation loss. The 0.016 macro-F1 gap is less than one validation example, so I preferred the better-calibrated model.

## Baseline

**Approach:** zero-shot classification with an LLM on Groq, no examples or training. Temperature 0, one API call per test comment, same 59-comment `test.csv`. Script: [`scripts/baseline_groq.py`](scripts/baseline_groq.py). Raw responses: [`outputs/baseline_test_predictions.csv`](outputs/baseline_test_predictions.csv).

**Model substitution.** The assignment specifies `meta-llama/llama-4-scout-17b-16e-instruct`, but Groq has retired it. It no longer appears in `/v1/models`, and requests return `model_not_found`. I used **`openai/gpt-oss-20b`**, the closest general-purpose open-weights model still offered, with `reasoning_effort: low` because it's a reasoning model.

**Prompt** (system message; the user message is `Comment: <text>\n\nLabel:`):

```
You classify comments from r/nba (the NBA subreddit) by what kind of discourse they are.

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

Respond with exactly one word: analysis, hot_take, reaction, or banter. No punctuation, no explanation.
```

**Parsing:** a response counts only if it is exactly one label name, or contains exactly one label name. Anything else would count as wrong. All 59 responses parsed cleanly (0 unparseable).

## Evaluation report

### Per-class metrics (test set, n = 59)

| Label | Support | Baseline P | Baseline R | Baseline F1 | Fine-tuned P | Fine-tuned R | Fine-tuned F1 |
|---|---|---|---|---|---|---|---|
| analysis | 10 | 0.57 | 0.40 | 0.47 | **0.82** | **0.90** | **0.86** |
| hot_take | 28 | 0.62 | **0.82** | 0.71 | **0.80** | 0.71 | **0.75** |
| reaction | 7 | **0.60** | **0.43** | **0.50** | 0.17 | 0.29 | 0.21 |
| banter | 14 | **0.70** | 0.50 | **0.58** | 0.64 | 0.50 | 0.56 |
| **macro avg** | 59 | 0.62 | 0.54 | 0.57 | 0.61 | 0.60 | **0.60** |

### Confusion matrix: fine-tuned DistilBERT (rows = true label, columns = predicted)

| true \ pred | analysis | hot_take | reaction | banter | total |
|---|---|---|---|---|---|
| **analysis** | **9** | 1 | 0 | 0 | 10 |
| **hot_take** | 1 | **20** | 4 | 3 | 28 |
| **reaction** | 1 | 3 | **2** | 1 | 7 |
| **banter** | 0 | 1 | 6 | **7** | 14 |

Image copy: [`outputs/confusion_matrix.png`](outputs/confusion_matrix.png)

### Confusion matrix: zero-shot baseline

| true \ pred | analysis | hot_take | reaction | banter | total |
|---|---|---|---|---|---|
| **analysis** | **4** | 6 | 0 | 0 | 10 |
| **hot_take** | 3 | **23** | 1 | 1 | 28 |
| **reaction** | 0 | 2 | **3** | 2 | 7 |
| **banter** | 0 | 6 | 1 | **7** | 14 |

**How to read the two matrices:**
- The **baseline's** errors mostly flow *into* `hot_take`. It called 6 of 10 `analysis` posts and 6 of 14 `banter` posts `hot_take`. It treats anything opinionated as a take and underrates evidence.
- The **fine-tuned model's** errors are concentrated in the short, casual corner: `banter` → `reaction` (6) and `hot_take` → `reaction` (4). It over-predicts `reaction` (12 predictions for 7 true examples), and only 2 of those 12 are right.

### Wrong predictions, analyzed

**1. True `reaction` → predicted `analysis` (confidence 0.76, the model's most confident error)**
> "I remember a late-night game at Sacramento in March of '19 where he went nuclear in the 4th quarter and led them back from 25 down, with Atkinson going with DLo, Kurucs, Treveon Graham, Dudley and RHJ the whole quarter. RHJ had the most awkward looking game-winning layup…"

- **What went wrong:** the post has everything the model associates with `analysis`: over 300 characters, a date, a score margin, a coach and five player names. But it argues nothing; it's nostalgia. This is difficult example #4 above, and the label is correct under rule A: specifics that don't support a claim aren't analysis.
- **Is it a labeling problem?** No. It's a data problem. In training, 68% of `analysis` posts are over 200 characters, against 4% of `reaction` posts. The model learned "long + proper nouns + numbers = analysis."
- **Fix:** add long `reaction`/`hot_take` posts full of names and numbers, so length and specificity stop predicting the label.

**2. True `banter` → predicted `reaction` (confidence 0.42), one of 6 identical-direction errors**
> "That man is married with 3 kids. He gone gone."

- **What went wrong:** it's a joke about a player "leaving" after a trade rumor, and getting it requires knowing the context and reading the deadpan tone. On the surface it's a short, casual, feeling-ish sentence with no argument.
- **Is it a labeling problem?** Not mainly. In the training data `banter` and `reaction` have almost the same length profile (medians of 54 and 48 characters), and both come mostly from post game and highlight threads. Length and thread vocabulary can't separate them, and 272 examples aren't enough for DistilBERT to learn humor cues. The model's low confidence (0.42) shows it is basically guessing between the two; the second choice was `banter` at 0.36.
- **Fix:** far more `banter` and `reaction` examples. Alternatively merge them into one `non-argument` label if the tool's purpose is "surface the argued comments."

**3. True `analysis` → predicted `hot_take` (confidence 0.39)**
> "Fox went nuclear and the blazers couldn't stop turning the ball over."

- **What went wrong:** at 69 characters, this is one of the shortest `analysis` posts in the dataset. It explains a result with two concrete game events, so I labeled it `analysis` and noted it as borderline. It's a short explanation, and the model's length prior says short posts aren't analysis.
- **Is it a labeling problem? Partly yes.** Re-reading similar posts, I labeled a comparable one-line game explanation ("he played like he was crawling through molasses and was given a bunch of open mid range shots…") as `hot_take`. The line between "concrete game event" and "vague impression" wasn't applied consistently for one-sentence posts.
- **Fix:** tighten rule A for short posts, for example require at least one *checkable* fact such as a number, a named play or a lineup, and relabel the one-sentence cases consistently.

### Sample classifications (fine-tuned model)

| Post | Predicted | Confidence | True / note |
|---|---|---|---|
| "I'm just stating how they can be skewed. Also yes, just 2 years ago the nuggets literally ran Jokic for 80% of his minutes with AT LEAST 3 other starters on the court…" | `analysis` | 0.86 | `analysis` ✓ (test set) |
| "Just mature. Don't have dumb turnovers, don't think you've won the game before you actually did…" | `hot_take` | 0.65 | `hot_take` ✓ (test set) |
| "I was so pissed when he hit this shot." | `reaction` | 0.59 | `reaction` ✓ (test set) |
| "We just call any shot in the 4th quarter a dagger now huh" | `banter` | 0.51 | `banter` ✓ (test set) |
| "Wemby is already the best defender in the league and it isn't close." | `hot_take` | 0.64 | new post, not in the dataset; `hot_take` ✓ |
| "If it's the Spurs maybe. Not for OKC though. SGA is the only player on their who's played more than 30 mpg in the last 2 games. They're stupid deep" | `hot_take` | 0.63 | new post, not in the dataset; should be `analysis` ✗ |

**Why the first prediction is reasonable:** the Jokic post makes a methodological claim (on/off stats can be skewed by lineup context) and backs it with a specific, checkable fact: Jokic playing about 80% of his minutes alongside three or more starters. With the attitude stripped out ("I'm just stating…"), the argument still stands, which is exactly rule A. It's also long and full of numbers, so it matches the model's surface pattern *and* the intended definition. Confidence is correspondingly high.

**Why the last one is instructive:** it's a real `analysis` post (a claim supported by a specific minutes stat), but it's only 150 characters and opens with a hedge ("If it's the Spurs maybe"). The model reads it as a take. That's the length shortcut from error 1 in reverse.

### Confidence calibration (stretch)

| Confidence | Predictions | Accuracy | Mean confidence |
|---|---|---|---|
| < 0.50 | 29 | 0.41 | 0.44 |
| 0.50–0.70 | 21 | 0.86 | 0.58 |
| 0.70–0.90 | 9 | 0.89 | 0.79 |
| ≥ 0.90 | 0 | — | — |

Expected calibration error (4 bins): 0.125.

**The confidence scores are meaningful in *ranking*, but underconfident in absolute terms.**
- Accuracy doubles from the lowest bin to the middle one (0.41 → 0.86), so a higher score really does mean "more likely right."
- But predictions in the 0.50–0.70 band are right 86% of the time, which is about 28 points better than their stated confidence.
- The model never goes above 0.90. That's expected: we picked an early, lowest-validation-loss checkpoint (epoch 4) and trained with class weights, and both make the output probabilities flatter.
- Nearly half the test set (29 of 59) sits below 0.50. Those are almost all the short `banter`/`reaction`/`hot_take` posts.
- **In practice:** a community tool could show only predictions above 0.50. That keeps 30 of 59 posts at 87% accuracy.

### Error pattern analysis (stretch)

| Length | n | Accuracy |
|---|---|---|
| short (< 80 chars) | 20 | 0.45 |
| medium (80–200) | 24 | 0.62 |
| long (> 200) | 15 | **0.93** |

The dominant pattern is **length**. Accuracy on long posts is 93%, against 45% on short ones. **20 of the 21 errors are on posts of 200 characters or fewer.** The second pattern is **`reaction`**: 15 of the 21 errors have `reaction` as either the true or the predicted label (`banter`→`reaction` 6, `hot_take`→`reaction` 4, `reaction`→`hot_take` 3, `reaction`→`analysis` 1, `reaction`→`banter` 1), and 14 of those 15 are short or medium posts. The model hasn't learned what a reaction *is*; it uses `reaction` as the default for "short, no argument, not obviously a joke."

Hypotheses that were tested and **discarded**:
- **"Profanity pushes posts toward `hot_take`."** Profane test posts were classified *more* accurately (75% vs 63%), and their predictions were spread across labels.
- **"'lol/lmao' makes the model say `banter`."** Four of the six "lol" posts are truly `hot_take`, and the model mostly predicted `hot_take` for them.

### Annotator agreement (stretch, model-vs-model)

This is **not** the human inter-annotator study the stretch feature describes, since no second person labeled the data. Instead, a second *independent model* labeled all 389 posts with the same definitions and rules ([`scripts/second_annotator.py`](scripts/second_annotator.py), output in [`data/second_annotator.csv`](data/second_annotator.csv)):
- **primary annotator:** Claude pre-labels;
- **second annotator:** zero-shot `openai/gpt-oss-20b`.

**Percent agreement 63.5%, Cohen's kappa 0.42** ("moderate" agreement). The two annotators disagree on 142 of 389 posts.

| Primary label | n | Second annotator agrees |
|---|---|---|
| hot_take | 182 | 86% |
| reaction | 51 | 49% |
| banter | 90 | 47% |
| analysis | 66 | **36%** |

| Primary → second annotator | count |
|---|---|
| analysis → hot_take | 41 |
| banter → hot_take | 34 |
| reaction → hot_take | 19 |
| banter → reaction | 12 |
| hot_take → reaction | 11 |
| hot_take → banter | 10 |
| reaction → banter | 7 |
| other | 8 |

**Where the annotators disagree:**
- **94 of the 142 disagreements (66%) are the second annotator saying `hot_take`.** It applies rule A much more strictly: 41 of the 66 `analysis` posts become takes for it. It also reads a lot of sarcasm as sincere opinion: 34 `banter` posts become `hot_take`. That's the same bias it showed as the baseline on the test set.
- **Disagreement is higher on the 40 posts the primary annotator flagged as borderline** (47%, versus 35% on the rest). The boundaries the rules were written for are the ones that are really contested.
- **The `analysis`↔`hot_take` boundary is the least reliable part of the taxonomy.** Two annotators working from the *same written rule* agree only about a third of the time on what counts as load-bearing evidence. That should be tightened before collecting more data, for example by requiring a checkable fact.

Caveat when reviewing: the second annotator is the same model as the baseline. Changing test-set labels *toward* its answers would inflate the baseline's score, so the review is done against the written definitions, not by deferring to either model.

## Reflection: what the model learned vs. what I intended

**I intended** the labels to capture a post's *purpose*: is it arguing with evidence, asserting without it, emoting, or joking? **What the model actually learned** is closer to a *specificity and length detector*.

The data shows the shortcut plainly:

| Label | Median length | % over 200 chars | % containing a digit |
|---|---|---|---|
| analysis | 270 | 68% | 67% |
| hot_take | 124 | 31% | 34% |
| banter | 54 | 2% | 26% |
| reaction | 48 | 4% | 18% |

The model's decision boundary follows that table:
- **Long and specific → `analysis`.** This is why `analysis` recall is 0.90 and why the long nostalgic memory (error 1) was confidently called `analysis`.
- **Medium, confident, no numbers → `hot_take`.** This works well: F1 0.75, beating the baseline.
- **Short and casual → a coin flip between `reaction` and `banter`,** with `reaction` winning. This is where it falls apart (F1 0.21 and 0.56).

Part of this correlation is real: evidence takes words. **But I made it worse with my own sampling decision.** The top-up batch meant to find more `analysis` kept only comments of 220+ characters, and the one meant to find `reaction` kept only comments of 160 or fewer. That wrote "`analysis` is long, `reaction` is short" into the training data more strongly than it exists in r/nba. It helped the headline `analysis` number and hurt everything that depends on reading tone.

The **zero-shot LLM shows the mirror-image failure.** It understands jokes and feelings better (`reaction` F1 0.50, `banter` precision 0.70). But it treats nearly any opinion as a take: 6 of 10 `analysis` posts became `hot_take`, which suggests it anchors on the confident *voice* of a post rather than checking whether the evidence is load-bearing. Neither model does what rule A actually asks, which is to weigh the evidence.

**What would close the gap:**
1. **Remove the length shortcut from the data.** Add long `hot_take`/`reaction` posts and short `analysis` posts, and sample top-ups by thread type rather than character count.
2. **Decide whether `reaction` vs `banter` matters for the use case.** For "surface the substantive comments," merging them into one `non-argument` label would likely raise macro-F1 a lot with no loss of usefulness.
3. **Consider a hybrid.** Use the fine-tuned model for the `analysis` decision, where it's precise and cheap, and the LLM for tone-based labels.

## Spec reflection

**How the spec helped.**
- **Rules A–C made 472 labeling decisions tractable.** Writing them before collecting data meant the hard cases had a pre-committed answer instead of whatever felt right that day. That includes the profane-but-argued rule rant, "Embiid is a warrior," and the sarcastic stat post.
- **Choosing macro-F1 as the primary metric in advance caught a real problem.** The default training run's 46.6% validation accuracy would have looked plausible on its own; macro-F1 of 0.16 showed immediately that it was predicting a single class.
- **The pre-set success thresholds kept the write-up honest.** Without them it would have been tempting to call "beats the LLM" a win. With them, it's clear the model met one of four criteria.

**Where the implementation diverged, and why:**
1. **Data source.** The plan assumed Reddit's public JSON endpoints, which now block requests without a login, so collection moved to the Arctic Shift archive of the same public comments.
2. **Out-of-scope rate.** The plan estimated about 10% of posts would be out of scope; it was 17.6%, driven by user-vs-user insult threads.
3. **Top-up sampling.** The plan said to pull `analysis` from "discussion/stat-heavy threads and longer comments." In practice I filtered by character count for both top-ups. The reflection above shows this introduced a shortcut, so thread-based targeting would have been the better way to follow the plan.
4. **Baseline model.** Groq retired Llama 4 Scout, so the baseline is `openai/gpt-oss-20b`.
5. **Training platform.** The model was trained locally with a script that mirrors the Colab notebook, rather than in Colab.

## AI usage

This project was built with **Claude Code (Claude Opus 5.5)** as an agent working in this repository, at my direction. Specific instances:

1. **Label pre-annotation (disclosed).**
   - *What I directed:* have Claude read and pre-label every one of the 472 collected comments, using the definitions and rules A–C from `planning.md`.
   - *What it produced:* a label per comment, plus a written rationale for the 40 borderline cases (the `notes` column).
   - *Review and correction:* every row carries `annotator=claude-prelabel` until a human reviews it with `python scripts/label.py --review`. Confirmed rows become `human-reviewed`; changed rows become `human-corrected`, with the original pre-label recorded in `notes`. _Current review status: see the `annotator` column counts in `data/takemeter_labeled.csv`._
2. **Planning draft, and a correction to it.** Claude drafted `planning.md` after reading about 40 real comments. Its first draft included a `reaction` example that wasn't a real post ("How are the Cavs down 20 again…"). That was replaced with a real comment from a Post Game Thread before the file was committed, because the assignment asks for examples from the community itself.
3. **Hyperparameter selection: overriding the top score.** The sweep's highest validation macro-F1 was the 10-epoch, lr 5e-5 run. That was overridden in favor of the 8-epoch, lr 3e-5 class-weighted run, because the "winner's" validation loss nearly doubled (overfitting) and the gap was smaller than one validation example.
4. **Failure analysis: patterns verified or discarded.** Claude proposed four error patterns from the list of misclassified posts: length, `banter`↔`reaction` confusion, profanity, and "lol" markers. Each was checked by counting:
   - length and `banter`↔`reaction` were **confirmed** (93% vs 45% accuracy by length; 6 of 21 errors in one cell);
   - profanity and "lol" were **discarded** (see Error pattern analysis).

   The length finding also led to checking the *collection* process, which showed that the length-filtered top-ups had amplified the shortcut.
5. **Review triage with a second annotator.**
   - *What I directed:* since a full manual pass over 472 posts wasn't feasible, have a second model independently label everything and send only the disagreements to human review.
   - *What it produced:* 142 disagreement posts plus the agreement statistics above.
   - *Honesty caveat:* rows that nobody reviewed keep `annotator=claude-prelabel`. Agreement between two AIs is not treated as human verification.
6. **Baseline substitution.** When the specified Groq model returned `model_not_found`, Claude listed the models available on the account and switched to `openai/gpt-oss-20b`, adding the reasoning-model settings. The change is documented rather than hidden.

## Reproduce / run it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                                   # add GROQ_API_KEY (never committed)

python scripts/collect_arctic.py --target 400          # collect (optional, data is committed)
python scripts/second_annotator.py                     # second annotator + agreement stats
python scripts/label.py --review --disagreements       # review / correct only the disputed labels
python scripts/stats.py --export                       # distribution checks → data/takemeter_final.csv
python scripts/train.py --epochs 8 --lr 3e-5 --class-weights --tag e8_lr3e-5_w --final   # train + test eval → model/, outputs/
python scripts/baseline_groq.py                        # zero-shot baseline on the same test split
python scripts/analyze.py > outputs/analysis.md        # comparison, calibration, error patterns → evaluation_results.json
python app/app.py                                      # demo UI at http://127.0.0.1:7860
```

**Deployed interface (stretch):** [`app/app.py`](app/app.py) is a Gradio app. Paste any comment and it shows the predicted label and the confidence for all four classes, with four built-in examples. The trained weights (`model/`, about 255 MB) are too large for git, so the command above rebuilds them in about 2 minutes.

```
data/raw_posts.csv            collected comments with provenance (permalink, thread type, batch)
data/takemeter_labeled.csv    all labels incl. SKIPs, annotator notes, annotator column
data/takemeter_final.csv      final 389-example dataset (text, label, notes)
data/splits/                  train / val / test used by both models
outputs/                      metrics JSON, predictions, confusion_matrix.png, hparam_runs.json, analysis.md
scripts/                      collect_arctic, import_manual, label, stats, train, baseline_groq, analyze
app/app.py                    Gradio demo
labels.json                   label names + definitions shared by every script
```
