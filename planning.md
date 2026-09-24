# TakeMeter — Planning

> Written before data collection (Milestone 2), after reading ~40 real r/nba comments from late-May 2026 playoff threads. Updated before each stretch feature (section 8).

## 1. Community

**Community:** r/nba — the main NBA subreddit (~17M members), specifically comments in Post Game Threads, news threads, and discussion posts from the 2025–26 season and playoffs.

**Why it's a good fit:** r/nba's comment sections mix four very different kinds of writing in the same thread: people breaking down *why* a team won with stats and film, people declaring someone "overrated" or "washed" with nothing behind it, people yelling about a call that just happened, and people making jokes. The community itself cares about this distinction — "source?", "ratio", "hot take", "nephew behavior", and "this is actually a good analysis" are common replies, and the subreddit's own culture (r/nbadiscussion exists as a spinoff specifically because r/nba is seen as too hot-take-heavy) shows regulars notice discourse quality. The variety is high and the boundaries are real but fuzzy, which makes it a meaningful classification task rather than a trivial one.

**Summary:** TakeMeter classifies r/nba comments as `analysis`, `hot_take`, `reaction`, or `banter`. These distinctions matter because r/nba regulars constantly judge whether a comment is an argument worth engaging with, an unsupported take, a moment of emotion, or a joke — and a tool that could surface the `analysis` comments from a 5,000-comment Post Game Thread would be genuinely useful to people who want substance.

## 2. Labels

Observations from the first read-through of 40 comments that shaped these labels:
- Roughly a third of comments were jokes/sarcasm ("They got that DAWG in them — and by dawg I mean so much spyware"). A taxonomy without a humor label would force these into `reaction` or `hot_take` and poison both, so `banter` became its own label.
- A handful (~10%) were not takes at all: pure logistics/questions ("How can I watch this if I don't have ESPN?", "Where are you finding playoff-specific EPM?"). Rather than an `other` bucket, these are **skipped as out of scope** and the skip rate is reported (see §4).
- Real `analysis` is rare in random comments (~10%), so collection has to target threads where it appears (see §4).

| Label | Definition |
|---|---|
| `analysis` | The post makes a basketball claim **and** supports it with specific, checkable evidence — stats, concrete game events, tactical detail, or a historical comparison — that actually does the reasoning. |
| `hot_take` | The post confidently asserts an evaluative opinion about players, teams, or the league with no real support, or with support that is vague or decorative. |
| `reaction` | The post expresses an in-the-moment feeling (hype, frustration, disbelief, praise) about a specific play, game, or news item without making a broader claim that outlives the moment. |
| `banter` | Humor is the point: jokes, memes, puns, sarcasm, or riffs where any opinion is only implied and the post is written to be funny rather than to persuade. |

### `analysis`
- "Yeah it really wasn't close but Boston won 64 games for a reason. They beat up the East as they should and Luka was already hobbled coming into the Finals. … only game 3 was kind of close towards the end." — claim (not close) backed by record, injury, and game-by-game evidence.
- "If it's the Spurs maybe. Not for OKC though. SGA is the only player on their [team] who's played more than 30 mpg in the last 2 games. They're stupid deep." — claim (OKC won't be tired) backed by a specific minutes stat.
- Unsure case: "The Knicks and by extension Trae Young (who I will remind you still isn't good in Dyckman)" — references a specific fact, but it's a jab, not an argument. → `hot_take` (see rule A).

### `hot_take`
- "SGA is so hated here that he managed to make reddit upvote a post with AI-generated content in it." — broad claim about the community, no support.
- "He's a great villain because we all agree with his pettiness but he's also the most easily hateable person and player." — confident evaluation, no evidence.
- Unsure case: "SGA's game is efficient and beautiful … except that he flops like a little b**** all the time. I actually thought I'd seen it all until last night" — general claim (outlives the moment) but triggered by last night's game. → `hot_take` (rule B).

### `reaction`
- "Chuck is a gem, I'ma miss him when he retires man." — feeling about news, no claim to argue with.
- "Grudge avenged!! CHAMPS BABY! (Been reading through my old comments and just saw this)" — pure celebration of a result.
- Unsure case: "Just want a competitive game. Cavs played 3 good quarters where they legitimately had the Knicks frustrated…" — has a hint of observation, but the purpose is a hope/feeling. → `reaction`.

### `banter`
- "They got that DAWG in them — and by dawg I mean so much spyware." — pun, pure humor.
- "His face was a real danger to that guy's elbow! True basketball terrorist behavior!" — sarcasm; the opinion (that was a bad foul call) is only implied.
- Unsure case: "If it ain't broke, don't fix it. We have a lightly used Dalton Knecht if you'd like to trade." — joke, but also a real trade-value dig. → `banter` (rule C).

**Mutual exclusivity check:** Each label answers a different question about the post's *purpose*: persuade with evidence (`analysis`), persuade without it (`hot_take`), express a feeling (`reaction`), or be funny (`banter`). The pairs most likely to overlap are `hot_take`↔`reaction` (emotional posts often contain a verdict) and `hot_take`↔`banter` (sarcasm often encodes a take). Both have explicit rules below.

## 3. Hard Edge Cases

**Hardest anticipated edge case: emotional verdicts right after a game — `reaction` vs. `hot_take`.**
Example: "Luka is washed. That was the worst playoff performance I've ever seen." It's clearly in-the-moment emotion, but it also states a general claim ("washed").

**Rule B (reaction vs. hot_take):** Ask "would this sentence still be a claim someone could argue with next week?" If the post makes a general evaluative claim about a player/team (washed, overrated, best ever, fraud, should be traded), label `hot_take` even if it's emotional. If it only describes/feels about what just happened ("what a game", "refs are killing us tonight", "I can't believe he missed that"), label `reaction`. → The Luka example is `hot_take`.

**Rule A (analysis vs. hot_take):** If the evidence would still support the claim with the opinion framing removed, and there's more than one piece of it or the one piece is genuinely load-bearing, label `analysis`. If the evidence is a single cherry-picked stat or a vague gesture ("look at his numbers"), label `hot_take`.

**Rule C (banter vs. anything):** If the literal text is a joke/sarcasm and the opinion has to be inferred, label `banter`. If a post makes a sincere claim and adds a joke at the end, label it by the sincere claim.

Other rules:
- Very short posts ("lol", "this", "W"): skip as out of scope — there's no content to classify.
- Pure questions, logistics, and off-topic chat (TV subscriptions, personal stories unrelated to basketball): skip as out of scope; report the skip rate.
- Mixed posts: label by the post's dominant purpose (what most of the text is doing).

## 4. Data Collection Plan

- **Source:** public r/nba comments from the Arctic Shift research archive of Reddit (read-only public API; Reddit's own JSON endpoints block unauthenticated requests). Threads from Jan–June 2026: Post Game Threads (heavy `reaction`/`banter`), news threads (`hot_take`), and discussion/stat posts (the best place for `analysis`).
- **Method:** `scripts/collect_arctic.py` samples at most ~10 comments per thread across 40+ threads so no single thread dominates; `scripts/label.py` for annotation; `scripts/stats.py` for distribution checks.
- **Target:** ~350 collected → ≥ 250 usable after skipping out-of-scope posts. Goal ≥ 20% per label (~50+ each).
- **If a label is underrepresented after 200:** `analysis` is the expected shortfall. Fix by pulling additional comments from discussion/stat-heavy threads and filtering for longer comments (>200 chars), not by relabeling borderline posts.
- **Skipped:** deleted/removed, bots/AutoModerator, < 25 chars, pure questions/logistics/off-topic, non-English.

## 5. Evaluation Metrics

- **Macro-F1 (primary):** the four classes are not equally common and `analysis` is the rarest yet most valuable class. Accuracy can look fine while the model ignores `analysis` entirely; macro-F1 weights each class equally, so a collapse on one label shows up.
- **Per-class precision and recall, especially for `analysis`:** for a "surface the good comments" tool, `analysis` **precision** matters most — if the tool highlights a hot take as analysis, users stop trusting it. `hot_take` recall matters for a moderation-style use.
- **Accuracy:** reported for comparison with the baseline, but not the success criterion.
- **Confusion matrix:** to see *direction* of errors — specifically whether `reaction`→`hot_take` and `banter`→`hot_take` (the anticipated hard boundaries) dominate.
- Caveat: with ~15% of ~250 examples, the test set is ~40 posts, so each example is ~2.5 points of accuracy. Differences under ~5 points are within noise and won't be over-interpreted.

## 6. Definition of Success

- Fine-tuned **macro-F1 ≥ 0.60** on the held-out test set, **and no class F1 below 0.45**.
- Fine-tuned model **beats the Groq zero-shot baseline by ≥ 5 points macro-F1** — otherwise fine-tuning isn't worth it over a prompt.
- **`analysis` precision ≥ 0.70** (the tool shouldn't mislabel takes as analysis).

**"Good enough" for a real community tool:** a "show me the analysis" filter on Post Game Threads, where precision on `analysis` ≥ 0.70 means at least 7 of 10 highlighted comments are genuinely substantive. That's useful even if recall is modest, because the alternative is scrolling thousands of comments.

## 7. AI Tool Plan

- **Label stress-testing:** Give Claude the four definitions + rules A–C and ask for 8 posts that sit on the `reaction`/`hot_take` and `banter`/`hot_take` boundaries. Any generated post that can't be labeled with one rule means the definition is tightened before annotation.
- **Annotation assistance:** Yes — Claude Code pre-labels every collected comment using the definitions in `labels.json`, writing a rationale for hard ones into the `notes` column. Every row is marked in the `annotator` column (`claude-prelabel`), then reviewed by me; any label I change is recorded as `human-corrected`. Disclosed in the README.
- **Failure analysis:** After evaluation, give Claude the list of misclassified test posts (text, true label, predicted label, confidence) and ask for recurring patterns (length, sarcasm, label pair, profanity/intensity). Each proposed pattern is verified by counting how many errors actually fit it; patterns with fewer than 3 supporting errors are discarded.

## 8. Stretch Feature Plans

_Updated after the core evaluation and before starting stretch work._

Status going in: fine-tuned macro-F1 0.596 vs baseline 0.565; `reaction` F1 0.21. The stretch work is chosen to explain *why*, not just to add features.

- [x] **Confidence calibration.** Bin test predictions by max softmax probability (<0.5, 0.5–0.7, 0.7–0.9, ≥0.9) and report accuracy and mean confidence per bin, plus expected calibration error. Hypothesis: class weights plus the early (epoch 4) checkpoint make the model *under*confident. Success = accuracy rises monotonically with confidence.
- [x] **Error pattern analysis.** Group errors by (true → predicted) pair and by post length (<80 / 80–200 / >200 chars). Test four candidate patterns proposed by the AI (length, banter↔reaction, profanity, "lol" markers) and keep only those that hold up in the counts. Also check whether the length-filtered top-up batches created a length/label correlation in the training data.
- [x] **Deployed interface.** Gradio app (`app/app.py`) loading `./model`, showing label and all four class probabilities, with built-in examples for the demo video.
- [x] **Annotator agreement (model-vs-model substitute).** A second model (zero-shot `gpt-oss-20b`, same definitions) labels all 389 posts. Report percent agreement and Cohen's kappa, and break down disagreements by label pair. Also use the disagreements as the human-review queue. This is *not* human inter-annotator reliability, and is reported as such.
- [ ] **Inter-annotator reliability (human).** Not done: it needs a second human annotator. Plan if added: a friend labels 40 random posts from `data/splits/test.csv` blind, then report Cohen's kappa against the existing labels, with expected disagreement concentrated on reaction↔hot_take (rule B).

## 9. Revisions After Collection (log)

- **Data source:** Reddit's JSON endpoints return 403 for requests without a login, so collection uses the Arctic Shift archive of the same public comments.
- **Skip rate:** 17.6%, not ~10%. Mostly user-vs-user insult chains in discussion threads.
- **Imbalance:** after one top-up round, `analysis` is 17% and `reaction` 13% (<20%). Handled with class-weighted loss rather than a third collection round.
- **Baseline model:** Groq retired `llama-4-scout-17b-16e-instruct`, so `openai/gpt-oss-20b` is used instead.
- **Default hyperparameters (3 epochs) collapsed to the majority class** (val macro-F1 0.16). Configs were compared on validation only; the chosen one is 8 epochs, lr 3e-5, class weights, with the best checkpoint at epoch 4.
- **Human review (after first results):** a second annotator (`gpt-oss-20b`) disputed 142 of 389 pre-labels; I reviewed all 142 and changed 38 (14 moved to out of scope). The dataset is now 375 posts. Splits were regenerated, and the sweep, final training and baseline were all re-run on the corrected data.
- **Result change:** on the corrected data and new split, the baseline wins overall (macro-F1 0.605 vs 0.557), reversing the pre-review result. The per-class pattern (fine-tuned far better on `analysis`, the LLM better on tone labels) held in both runs, so that is treated as the reliable finding.
