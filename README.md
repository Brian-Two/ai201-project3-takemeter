# TakeMeter: r/nba discourse classifier

A fine-tuned DistilBERT model that labels r/nba comments as **`analysis`**, **`hot_take`**, **`reaction`**, or **`banter`**, compared against a zero-shot LLM baseline on the same held-out test set.

- **Demo video:** _TODO: add link (3–5 min)_. Script: [`docs/demo_script.md`](docs/demo_script.md)
- **Labeled dataset:** [`data/takemeter_final.csv`](data/takemeter_final.csv) (375 examples) · full annotation file with skips, notes, reviewer status and provenance: [`data/takemeter_labeled.csv`](data/takemeter_labeled.csv)
- **Planning doc:** [`planning.md`](planning.md) · **Raw metrics:** [`outputs/evaluation_results.json`](outputs/evaluation_results.json)

## Results at a glance

Test set: 57 held-out comments (stratified 15% split, never used for training or model selection).

| Model | Accuracy | Macro F1 | `analysis` F1 | `hot_take` F1 | `reaction` F1 | `banter` F1 |
|---|---|---|---|---|---|---|
| Majority class (always `hot_take`) | 0.456 | 0.157 | 0 | 0.63 | 0 | 0 |
| **Zero-shot baseline** (Groq `openai/gpt-oss-20b`) | **0.684** | **0.605** | 0.17 | **0.75** | **0.83** | **0.67** |
| Fine-tuned DistilBERT | 0.561 | 0.557 | **0.70** | 0.60 | 0.50 | 0.44 |

**Headline:** the zero-shot LLM beats the fine-tuned model overall, by 7 test examples in accuracy and 4.8 points of macro-F1. The fine-tuned model wins decisively on exactly one class, and it's the one the tool exists for:
- On **`analysis`**, the fine-tuned model scores F1 0.70 versus 0.17. The LLM almost never says `analysis`: it caught 1 of 11 and called the other 10 `hot_take`.
- The LLM is better at everything that depends on reading tone.
- The fine-tuned model learned mostly **length and specificity**, and confuses short `hot_take`s with `banter`. See the [reflection](#reflection-what-the-model-learned-vs-what-i-intended).

**Against the success criteria set in `planning.md` before any data was collected:**

| Criterion (planning.md §6) | Result | Met? |
|---|---|---|
| Macro-F1 ≥ 0.60 | 0.557 | ✗ |
| No class F1 below 0.45 | `banter` = 0.44 | ✗ (just missed) |
| Beat baseline by ≥ 5 pts macro-F1 | −4.8 pts | ✗ |
| `analysis` precision ≥ 0.70 | 0.67 | ✗ (just missed) |

None of the four thresholds is met.

**How stable is that verdict? Not very, and that's a finding too.** Before the human label review, the same pipeline on a different random 59-post test split gave the *opposite* overall result: fine-tuned 0.644 accuracy / 0.596 macro-F1 versus baseline 0.627 / 0.565. That earlier version is in the commit history.

With about 57 test posts, each post is worth about 1.8 points of accuracy, so "which model wins overall" flips depending on which posts land in the test set. What held up in **both** runs is the per-class pattern:
- fine-tuned `analysis` F1 was 0.86 and 0.70, against the baseline's 0.47 and 0.17;
- the LLM was better at `reaction` and `banter` both times.

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

**Labeling process (three passes):**
1. **AI pre-labels.** Claude read all 472 comments against the definitions and rules A–C, assigned a label or marked a post out of scope, and wrote a note on the 40 cases that needed a rule to resolve. This is disclosed in [AI usage](#ai-usage).
2. **Independent second annotator.** A different model, zero-shot `openai/gpt-oss-20b` with the same definitions ([`scripts/second_annotator.py`](scripts/second_annotator.py)), labeled all 389 in-scope posts. It disagreed with the pre-label on **142** of them.
3. **Human review of every disputed label.** I reviewed all 142 disagreements with `python scripts/label.py --review --disagreements`, which shows the post, the current label and the second annotator's label, and judged each against the written definitions:
   - **kept** the pre-label on 104;
   - **changed** 38: 14 to the second annotator's label, 10 to a third label, and 14 to out of scope.

The `annotator` column records each row's status. **128 of the 375 final labels are human-reviewed** (`human-reviewed` or `human-corrected`). The other **247 are AI labels on which both models independently agreed**, and weren't individually reviewed.

In total 97 of 472 comments (20.6%) are out of scope. That's higher than the ~10% estimated in `planning.md`, mainly because of user-vs-user insult chains in discussion threads.

**Label distribution (375 usable examples):**

| Label | Count | % |
|---|---|---|
| hot_take | 174 | 46.4% |
| banter | 88 | 23.5% |
| analysis | 71 | 18.9% |
| reaction | 42 | 11.2% |
| **Total** | **375** | 100% |

No label is above 70%. `analysis` and `reaction` are below the recommended 20%; this is handled in training with class weights (below).

**Split** ([`data/splits/`](data/splits)): stratified 70/15/15 with seed 42, giving 262 train, 56 validation and 57 test. The baseline and the fine-tuned model are scored on the identical `test.csv`.

### Difficult-to-label examples

1. **"[r-slur] rule. Average all star player play sth like 60 games. So if you are going to set a rule, make it meaningful stats wise. If average of your top 24 player is around 62 games then minimum threshold should be somewhere like 50-55 games…"**
   - *Three annotators, three different labels:*
     - the AI pre-label said **`analysis`**: strip the anger and a real argument backed by a number remains, which is rule A;
     - the second annotator said **`hot_take`**, anchoring on the outraged voice;
     - on review I labeled it **`reaction`**. The case for that label: the post opens with a slur and is mostly venting at the 65-game rule, and its numbers are rough guesses ("sth like 60games") rather than checkable evidence.
   - *Final:* **`reaction`**. The example shows that rule A breaks down when a rant contains approximate numbers.
2. **"Embiid is a fucking warrior."** (on news that Embiid would play through injury)
   - *Could be:* `hot_take` (a general claim about his character) or `reaction`.
   - *Decided:* **`reaction`**; confirmed on review. By rule B, it praises *this* decision in *this* moment, not a claim anyone would still be debating next week. The same words in a "who's the toughest player in the league" thread would be a `hot_take`. The fine-tuned model got it wrong (error table, #17).
3. **"if ant went for 40 in both games shooting a combined 64% while devin booker shot a tour date in one game and missed the other, surely the wolves won those games right?"**
   - *Could be:* `analysis` (real stats making a real point) or `banter`.
   - *Decided:* **`banter`**; confirmed on review. By rule C, the literal text is sarcasm, and the point (individual stats don't decide games) has to be inferred. This is the case the taxonomy handles worst: the post is funny *and* makes an argument.
4. **"Fox went nuclear and the blazers couldn't stop turning the ball over."**
   - *Could be:* `reaction` (short, excited) or `analysis`.
   - *Decided:* **`analysis`**; confirmed on review. It explains a result with two concrete game events, which is the minimum rule A allows. It's also one of the shortest `analysis` posts in the data, which is exactly the kind the fine-tuned model struggles with.

## Fine-tuning

- **Base model:** `distilbert-base-uncased` (66M parameters) with a 4-way classification head.
- **Platform:** trained locally on an Apple-silicon MacBook GPU (PyTorch MPS) using Hugging Face `transformers` `Trainer`: [`scripts/train.py`](scripts/train.py). It mirrors the CodePath starter notebook: same model, same 70/15/15 split and the same default hyperparameters, run as a script. Each run takes about 2 minutes.
- **Setup:** max 256 tokens, AdamW with weight decay 0.01, 10% warmup, evaluation on the validation set after every epoch. The checkpoint with the best **validation** macro-F1 is kept.
- **Final config:** 8 epochs, learning rate 3e-5, batch size 16, **inverse-frequency class weights** in the loss (`analysis` 1.31, `hot_take` 0.54, `reaction` 2.26, `banter` 1.07). The best checkpoint was at epoch 4.

### Key hyperparameter decisions

All configs were compared on the 56-example **validation** set only; the test set was scored once at the end. Full per-epoch log: [`outputs/hparam_runs.json`](outputs/hparam_runs.json).

| Config | Class weights | Best val macro-F1 | Best epoch | Val loss: best epoch → last epoch |
|---|---|---|---|---|
| 3 epochs, lr 2e-5, bs 16 (notebook default) | no | 0.159 | — | Predicted `hot_take` for every post |
| 8 epochs, lr 3e-5, bs 16 | no | 0.486 | 4 | 0.97 → 1.02 |
| **8 epochs, lr 3e-5, bs 16** | **yes** | **0.581** | **4** | **1.02 → 1.09 (chosen)** |
| 10 epochs, lr 5e-5, bs 16 | yes | 0.561 | 3 | 1.03 → 2.03 |
| 8 epochs, lr 3e-5, bs 8 | yes | 0.557 | 2 | 1.08 → 1.62 |
| 12 epochs, lr 2e-5, bs 8 | yes | 0.542 | 3 | 1.07 → 1.92 |

1. **More epochs than the default.** With 262 training examples at batch size 16, 3 epochs is only about 50 gradient updates. At that point the model had only learned the class prior: validation accuracy was 0.464, exactly the `hot_take` share, and macro-F1 was 0.16. Accuracy alone would have hidden this, which is why `planning.md` made macro-F1 the primary metric.
2. **Class weights.** At identical settings, weighting the loss by inverse class frequency raised validation macro-F1 from 0.49 to 0.58. `reaction` is only 11% of the training data; without weights it was rarely predicted.
3. **A moderate learning rate and batch size 16, with the best checkpoint where validation loss is lowest.** Every higher-learning-rate or smaller-batch run peaked by epoch 2–3 and then its validation loss exploded (to 1.6–2.0): it was memorizing 262 examples and becoming confidently wrong. The chosen run's best macro-F1 comes at its lowest-validation-loss epoch, and it stays stable afterwards.

The same config also won on the pre-review dataset, where I chose it over a run with a 0.016 higher score because of the same overfitting signal. On the corrected data it wins outright.

## Baseline

**Approach:** zero-shot classification with an LLM on Groq, no examples or training. Temperature 0, one API call per test comment, same 57-comment `test.csv`. Script: [`scripts/baseline_groq.py`](scripts/baseline_groq.py). Raw responses: [`outputs/baseline_test_predictions.csv`](outputs/baseline_test_predictions.csv).

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

**Parsing:** a response counts only if it is exactly one label name, or contains exactly one label name. Anything else would count as wrong. All 57 responses parsed cleanly (0 unparseable).

**A caveat on fairness.** The same model was also the second annotator, and 14 of the 38 human corrections moved a label *to* its answer. Corrections were made against the written definitions, and 104 of 142 disputes were resolved *against* it. Still, only 19 of the 57 test posts were human-reviewed; the rest carry labels both models agreed on. Both facts slightly favor the baseline on this test set.

## Evaluation report

### Per-class metrics (test set, n = 57)

| Label | Support | Baseline P | Baseline R | Baseline F1 | Fine-tuned P | Fine-tuned R | Fine-tuned F1 |
|---|---|---|---|---|---|---|---|
| analysis | 11 | **1.00** | 0.09 | 0.17 | 0.67 | **0.73** | **0.70** |
| hot_take | 26 | 0.60 | **1.00** | **0.75** | **0.67** | 0.54 | 0.60 |
| reaction | 6 | **0.83** | **0.83** | **0.83** | 0.50 | 0.50 | 0.50 |
| banter | 14 | **1.00** | 0.50 | **0.67** | 0.39 | 0.50 | 0.44 |
| **macro avg** | 57 | 0.86 | 0.61 | **0.61** | 0.56 | 0.57 | 0.56 |

### Confusion matrix: fine-tuned DistilBERT (rows = true label, columns = predicted)

| true \ pred | analysis | hot_take | reaction | banter | total |
|---|---|---|---|---|---|
| **analysis** | **8** | 3 | 0 | 0 | 11 |
| **hot_take** | 2 | **14** | 2 | 8 | 26 |
| **reaction** | 0 | 0 | **3** | 3 | 6 |
| **banter** | 2 | 4 | 1 | **7** | 14 |

Image copy: [`outputs/confusion_matrix.png`](outputs/confusion_matrix.png)

### Confusion matrix: zero-shot baseline

| true \ pred | analysis | hot_take | reaction | banter | total |
|---|---|---|---|---|---|
| **analysis** | **1** | 10 | 0 | 0 | 11 |
| **hot_take** | 0 | **26** | 0 | 0 | 26 |
| **reaction** | 0 | 1 | **5** | 0 | 6 |
| **banter** | 0 | 6 | 1 | **7** | 14 |

**How to read the two matrices:**
- **The baseline has one failure mode: everything uncertain becomes `hot_take`.** It predicted `hot_take` 43 times for 26 real ones. That's why its `hot_take` recall is a perfect 1.00 while `analysis` recall is 0.09. When it does say `analysis` or `banter` it's always right (precision 1.00), but it almost never commits.
- **The fine-tuned model's errors are spread out, with one dominant cell: true `hot_take` predicted as `banter` (8).** Together with `banter` → `hot_take` (4), the `hot_take`↔`banter` boundary accounts for **12 of its 25 errors**.

### Wrong predictions, analyzed

**1. True `hot_take` → predicted `banter` (confidence 0.64), the most common error direction (8 of 25)**
> "cade is a tier above brunson at this point sorry buddy"

- **What went wrong:** this is a sincere, confident ranking claim with no evidence, a textbook `hot_take`. But it's 54 characters long, in lowercase, and ends with a teasing "sorry buddy." In the training data, `banter` has a median length of 52 characters and short casual posts are overwhelmingly `banter` or `reaction`. The model reads the *register* (short, slangy, needling), not the *speech act* (a sincere claim).
- **Is it a labeling problem?** No. Rule C covers this directly: a sincere claim with a jab attached is labeled by the claim. The labels are consistent; the model just can't separate "sincere but casual" from "joking" with 262 examples.
- **Fix:** more short, casual `hot_take`s in training, which r/nba has plenty of, so shortness stops signaling humor.

**2. True `analysis` → predicted `hot_take` (confidence 0.62)**
> "If you're a second apron team out a bunch of FRPs you are essentially all-in on winning a championship immediately. So no I would not call getting swept or 4-1'd in the CFs a success at all."

- **What went wrong:** the evidence here is *domain knowledge*, not numbers. "Second apron" is the NBA salary-cap tier that restricts trades, and "FRPs" means first-round picks, so the post argues that the cap situation makes anything short of a title a failure. To DistilBERT, "second apron" and "FRPs" are rare tokens it has no basketball meaning for. With no stats and a 190-character body that ends in an opinion ("I would not call … a success"), it looks like a take.
- **Is it a labeling problem?** No; it's a model-knowledge problem. The same weakness shows up in error #25 ("teams just haven't been guarding him for 3 months").
- **Fix:** a basketball-aware base model, or many more jargon-based `analysis` examples. The LLM baseline *does* know what a second apron is, but its bias sends nearly all `analysis` to `hot_take` anyway.

**3. True `hot_take` → predicted `analysis` (confidence 0.69, the model's most confident error)**
> "I've heard this theory and don't buy it. Let's say an average person shoots on a nerf hoop, same issue, you're too big, ball is too light, you're still making more baskets from 2 feet away than 3 feet, if you took hundreds of shots."

- **What went wrong:** this *looks* like reasoning: long, structured ("Let's say…"), step by step. But the support is a hypothetical thought experiment, not checkable evidence, so under rule A it's a `hot_take`. The model has learned "long and argumentative" as a proxy for `analysis`, and a proxy can't tell a real argument from a hypothetical one.
- **Is it a labeling problem?** Borderline. Reasonable annotators could call a well-built thought experiment "tactical detail." It's consistent with the written rule, though, which requires *checkable* evidence.
- **Fix:** add "argument-shaped" `hot_take`s (hypotheticals, analogies, "imagine if…") to training, and make "checkable" explicit in the definition, for example "a number, a named game or play, or a verifiable fact."

### Sample classifications (fine-tuned model)

| Post | Predicted | Confidence | True / note |
|---|---|---|---|
| "I don't hate it for the Bucks because on draft night they have access to 3 picks and a swap, but they won't have any contracts to make trades with. So, if they can't make a trade for a wing…" | `analysis` | 0.80 | `analysis` ✓ (test set) |
| "Are we pretending that KD is some ball hog? He's always been a team player and is a great playmaker." | `hot_take` | 0.57 | `hot_take` ✓ (test set) |
| "Caught everyone off guard with that shit. What a fucking dime Good catch and finish from Evan" | `reaction` | 0.54 | `reaction` ✓ (test set) |
| "Kawhi and a Fistful of dollars" | `banter` | 0.56 | `banter` ✓ (test set) |
| "Wemby is already the best defender in the league and it isn't close." | `hot_take` | 0.59 | new post, not in the dataset; `hot_take` ✓ |
| "Grudge avenged!! CHAMPS BABY!" | `banter` | 0.50 | new post; should be `reaction` ✗ (reaction 0.36) |

**Why the first prediction is reasonable:** the Bucks post argues that a Ja Morant trade is low-risk for Milwaukee, and every step rests on checkable facts: the Bucks' 3 picks and a swap, their lack of tradeable contracts, and the salaries it lists later (Turner 25m, Kuzma 20m…). Remove the "I don't hate it" framing and the cap logic still holds, which is exactly rule A. It's also long and full of numbers, so the model's surface pattern and the intended definition agree here, which is why this is its most confident correct prediction.

**Why the last one is instructive:** pure celebration is a textbook `reaction`, but it's short, all-caps and exclamatory, which the model associates with `banter`. It split 0.50 / 0.36 between the two, and its low confidence shows it knows it's guessing.

### Confidence calibration (stretch)

| Confidence | Predictions | Accuracy | Mean confidence |
|---|---|---|---|
| < 0.50 | 30 | 0.47 | 0.41 |
| 0.50–0.70 | 24 | 0.62 | 0.59 |
| 0.70–0.90 | 3 | 1.00 | 0.76 |
| ≥ 0.90 | 0 | — | — |

Expected calibration error (4 bins): **0.056**.

**The confidence scores are meaningful.** Accuracy rises steadily with confidence (0.47 → 0.62 → 1.00), and within each bin the stated confidence is close to the actual accuracy (0.41 vs 0.47, 0.59 vs 0.62).

The model is never *very* confident: nothing is above 0.90, and 30 of 57 predictions are below 0.50. That's expected from an early checkpoint (epoch 4) trained with class weights, and honest given the task. The three predictions above 0.70 were all correct, and all three are `analysis` posts.

**In practice:** a community tool should surface only high-confidence `analysis` predictions and leave the rest unlabeled.

### Error pattern analysis (stretch)

| Length | n | Accuracy |
|---|---|---|
| short (< 80 chars) | 24 | 0.46 |
| medium (80–200) | 22 | 0.55 |
| long (> 200) | 11 | **0.82** |

| true → predicted | count |
|---|---|
| hot_take → banter | 8 |
| banter → hot_take | 4 |
| analysis → hot_take | 3 |
| reaction → banter | 3 |
| hot_take → analysis | 2 |
| hot_take → reaction | 2 |
| banter → analysis | 2 |
| banter → reaction | 1 |

Two patterns explain most errors:
1. **Length.** Accuracy is 82% on long posts and 46% on short ones.
2. **The short-casual boundary.** 18 of the 25 errors are confusions among `hot_take`, `banter` and `reaction`; the other 7 involve `analysis`. The model has no reliable way to tell a sincere short opinion from a joke or an outburst: 12 of 25 errors are `hot_take`↔`banter`.

Hypotheses that were tested and **discarded**:
- **"Profanity pushes posts toward `hot_take`."** Profane test posts have exactly the same accuracy as the rest (0.56), and their predictions are spread across all four labels.
- **"'lol/lmao' makes the model say `banter`."** Of the three "lol" posts, the model predicted `hot_take` for two.

### Annotator agreement (stretch, model-vs-model plus human adjudication)

This is **not** a full human inter-annotator study, since no second person labeled the data independently. It combines two AI annotators with human adjudication of their disagreements. Scripts and data: [`scripts/second_annotator.py`](scripts/second_annotator.py), [`data/second_annotator.csv`](data/second_annotator.csv).

| Comparison | n | % agreement | Cohen's κ |
|---|---|---|---|
| AI pre-labels vs second annotator (`gpt-oss-20b`), before review | 389 | 63.5% | 0.42 |
| Final labels (after human review) vs second annotator | 375 | 69.6% | 0.52 |

**On the 142 disputed posts, human review sided with:**

| Outcome | Posts | Share |
|---|---|---|
| The AI pre-label | 104 | 73% |
| The second annotator | 14 | 10% |
| Neither: a third label | 10 | 7% |
| Neither: out of scope | 14 | 10% |

| Before review, pre-label → second annotator | count |
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
- **94 of the 142 disagreements (66%) are the second annotator saying `hot_take`.** That's the same bias it shows as the baseline: 10 of 11 test-set `analysis` posts became `hot_take`.
- **Disagreement was higher on the 40 posts the pre-labeler flagged as borderline** (47% vs 35%). The boundaries the rules were written for are the ones that are actually contested.
- **The `analysis`/`hot_take` boundary is the least reliable part of the taxonomy.** Before review, the second annotator agreed with only 36% of `analysis` labels.

## Reflection: what the model learned vs. what I intended

**I intended** the labels to capture a post's *purpose*: is it arguing with evidence, asserting without it, emoting, or joking? **What the fine-tuned model actually learned** is closer to a *length and specificity detector*, plus a weak sense of register.

The training data makes the shortcut available:

| Label | Median length | % over 200 chars | % containing a digit |
|---|---|---|---|
| analysis | 239 | 63% | 61% |
| hot_take | 124 | 30% | 35% |
| reaction | 50 | 7% | 17% |
| banter | 52 | 1% | 27% |

The model's decision boundary follows that table:
- **Long, specific and argument-shaped → `analysis`.** This is why it wins `analysis` by a mile (F1 0.70 vs 0.17). It's also why its most confident error is a long hypothetical argument that is really a `hot_take` (error 3), and why jargon-based analysis without numbers gets missed (error 2).
- **Short and casual → `banter` or `reaction`,** decided almost at random. `reaction` and `banter` have nearly the same length profile (medians 50 and 52 characters), and short sincere `hot_take`s look just like them (error 1). This is where the model loses to the LLM, whose general language understanding reads tone and sarcasm far better (`reaction` F1 0.83, `banter` precision 1.00).

Part of the length correlation is real: evidence takes words. **But I amplified it with my own sampling decision.** The top-up batch meant to find `analysis` kept only comments of 220+ characters, and the one meant to find `reaction` kept only comments of 160 or fewer. That wrote "`analysis` is long, `reaction` is short" into the data more strongly than it exists in r/nba.

**The zero-shot LLM shows the mirror-image failure.** It understands jokes and feelings but treats nearly every opinion-shaped post as a take: 43 `hot_take` predictions for 26 true ones, and 10 of 11 `analysis` posts included. It seems to anchor on the confident *voice* of a post and rarely credits the evidence as load-bearing. **Neither model does what rule A actually asks, which is to weigh whether the evidence carries the claim.** The fine-tuned model counts words and numbers; the LLM listens to tone.

**What would close the gap:**
1. **Break the length shortcut in the data.** Add long `hot_take`s (hypotheticals, rants), short `analysis` posts, and short sincere `hot_take`s. Sample top-ups by thread type, not character count.
2. **Tighten rule A** so "evidence" means *checkable*: a number, a named game or play, or a cap or contract fact. Hypotheticals and analogies don't count. This is the boundary where all three annotators disagreed most.
3. **Build a hybrid.** The fine-tuned model is the only one that finds `analysis`, and the LLM is better at tone. A "surface the analysis" tool could use DistilBERT's `analysis` score with a confidence cutoff and let the LLM handle everything else.
4. **Evaluate more robustly.** With ~57 test posts, the overall winner flipped between two splits. Cross-validation, or a larger test set, is needed before any overall claim.

## Spec reflection

**How the spec helped.**
- **Rules A–C made nearly 500 labeling and review decisions tractable.** Writing them *before* collecting data gave every hard case a pre-committed answer. The rules also gave the human review a standard to judge disputes against, instead of picking whichever model sounded right, which is why 104 of 142 disputes went against the second annotator.
- **Choosing macro-F1 as the primary metric in advance caught a real problem.** The default training run's 46% validation accuracy would have looked plausible on its own; macro-F1 of 0.16 showed it was predicting one class.
- **The pre-set thresholds kept the write-up honest.** The first run, before review, beat the baseline, and it would have been easy to stop there. With the thresholds and the re-run, it's clear the model meets none of the four criteria overall, and that its real value is narrower: finding `analysis`.

**Where the implementation diverged, and why:**
1. **Data source.** The plan assumed Reddit's public JSON endpoints, which now block requests without a login, so collection moved to the Arctic Shift archive of the same public comments.
2. **Out-of-scope rate.** The plan estimated about 10% of posts would be out of scope; it was 20.6%.
3. **Top-up sampling.** I filtered by character count rather than by thread type, which introduced the length shortcut described above.
4. **Annotation workflow.** The plan was AI pre-labeling plus a full human review. In practice the human review covered all 142 posts where two independent models disagreed, not all 375.
5. **Baseline model.** Groq retired Llama 4 Scout, so the baseline is `openai/gpt-oss-20b`.
6. **Training platform.** The model was trained locally with a script that mirrors the Colab notebook, rather than in Colab.

## AI usage

This project was built with **Claude Code (Claude Opus 5.5)** as an agent working in this repository, at my direction. Specific instances:

1. **Label pre-annotation (disclosed).**
   - *What I directed:* have Claude read and pre-label all 472 collected comments using the definitions and rules A–C from `planning.md`.
   - *What it produced:* a label per comment, plus written rationales for 40 borderline cases.
   - *What I changed:* I reviewed every label that a second model disputed (142 posts). I kept 104 and **overrode 38**: 14 to the second model's answer, 10 to a label neither model chose, and 14 to out of scope. For example, I relabeled the "65-game rule" rant from `analysis` to `reaction` (difficult example 1). Rows nobody reviewed keep `annotator=claude-prelabel` (247 of 375), and I don't count agreement between two AIs as human verification.
2. **Review triage with a second annotator.**
   - *What I directed:* instead of skimming all 472 posts, have a second model independently label everything and send only the disagreements to me.
   - *What it produced:* the 142-post review queue and the agreement statistics above.
   - *Caveat:* that second model is also the baseline, so I judged disputes against the written definitions, not against its answer. See the fairness caveat in [Baseline](#baseline).
3. **Planning draft, and a correction to it.** Claude drafted `planning.md` after reading about 40 real comments. Its first draft included a `reaction` example that wasn't a real post ("How are the Cavs down 20 again…"). That was replaced with a real comment from a Post Game Thread before the file was committed.
4. **Hyperparameter selection.** On the pre-review data, the sweep's top validation score came from the 10-epoch, lr 5e-5 run. That was overridden in favor of the 8-epoch, lr 3e-5 class-weighted run, because the "winner's" validation loss nearly doubled (overfitting). On the corrected data the chosen config also wins outright.
5. **Failure analysis: patterns verified or discarded.** Claude proposed error patterns from the list of misclassified posts: length, confusion between the short casual labels, profanity, and "lol" markers. Each was checked by counting:
   - length and the `hot_take`↔`banter` confusion were **confirmed**;
   - profanity and "lol" were **discarded** (see Error pattern analysis).

   The length finding also led to checking the *collection* process, which showed that the length-filtered top-ups amplified the shortcut.
6. **Baseline substitution.** When the specified Groq model returned `model_not_found`, Claude listed the account's available models and switched to `openai/gpt-oss-20b` with reasoning-model settings. The change is documented rather than hidden.

## Reproduce / run it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                                   # add GROQ_API_KEY (never committed)

python scripts/collect_arctic.py --target 400          # collect (optional, data is committed)
python scripts/second_annotator.py                     # second annotator + agreement stats
python scripts/label.py --review --disagreements       # human review of disputed labels
python scripts/stats.py --export                       # distribution checks → data/takemeter_final.csv
python scripts/train.py --epochs 8 --lr 3e-5 --class-weights --tag e8_lr3e-5_w --final   # train + test eval → model/, outputs/
python scripts/baseline_groq.py                        # zero-shot baseline on the same test split
python scripts/analyze.py > outputs/analysis.md        # comparison, calibration, error patterns → evaluation_results.json
python app/app.py                                      # demo UI at http://127.0.0.1:7860
```

To regenerate the split after label changes, delete `data/splits/` before running `train.py`.

**Deployed interface (stretch):** [`app/app.py`](app/app.py) is a Gradio app. Paste any comment and it shows the predicted label and the confidence for all four classes, with four built-in examples. The trained weights (`model/`, about 255 MB) are too large for git, so the `train.py` command above rebuilds them in about 2 minutes.

```
data/raw_posts.csv            collected comments with provenance (permalink, thread type, batch)
data/takemeter_labeled.csv    all labels incl. SKIPs, notes, annotator status (claude-prelabel / human-reviewed / human-corrected)
data/second_annotator.csv     independent labels from gpt-oss-20b
data/takemeter_final.csv      final 375-example dataset (text, label, notes)
data/splits/                  train / val / test used by both models
outputs/                      metrics JSON, predictions, confusion_matrix.png, hparam_runs.json, analysis.md
scripts/                      collect_arctic, import_manual, second_annotator, label, stats, train, baseline_groq, analyze
app/app.py                    Gradio demo
labels.json                   label names + definitions shared by every script
```
