# Demo video script (3–5 min)

Setup before recording: `source .venv/bin/activate && python app/app.py`, open http://127.0.0.1:7860, and have the README open on GitHub.

**0:00–0:30 · What it is.** "TakeMeter classifies r/nba comments into four labels by purpose: analysis (argued with evidence), hot_take (asserted without it), reaction (in-the-moment feeling), and banter (the joke is the point). Fine-tuned DistilBERT on 375 labeled comments, compared to a zero-shot LLM."

**0:30–2:30 · Classify 5 posts live in the app** (label + confidence visible each time):

1. ✅ **Correct, narrate why:** paste this test-set post, which the model never trained on:
   > I don't hate it for the Bucks because on draft night they have access to 3 picks and a swap, but they won't have any contracts to make trades with. So, if they can't make a trade for a wing that will help them now, a Kuzma, KPJ, and Gary Harris trade for Ja is low risk, high reward.

   Expect **analysis** (~0.7–0.8). Narrate: "The claim is that a Ja trade is low-risk for Milwaukee, and every step rests on checkable facts: three picks and a swap, no tradeable contracts. Take away 'I don't hate it' and the argument still stands. That's our rule A. Long, evidence-heavy posts are exactly what this model is best at."
2. Built-in example: "Wemby is already the best defender in the league and it isn't close." Expect **hot_take ~0.59**, correct: a bold claim with zero evidence.
3. Built-in example: "That man is married with 3 kids. He gone gone." Expect **banter ~0.38**, correct but barely: reaction is at ~0.36. "Short posts are a coin flip between banter and reaction for this model."
4. ❌ **Incorrect, narrate what went wrong:** the built-in example "If it's the Spurs maybe. Not for OKC though. SGA is the only player on their team who's played more than 30 mpg in the last 2 games. They're stupid deep". Expect **hot_take ~0.60** when it's really analysis.
   Narrate: "This is analysis: the claim is that OKC won't be tired, backed by a specific minutes stat. The model says hot_take because it's short and opens with a hedge. Our error analysis found it mostly learned *length*: accuracy is 82% on long posts vs 46% on short ones, and 63% of analysis training posts are over 200 characters, partly because our top-up sampling filtered by length."
5. ❌ Built-in example: "Grudge avenged!! CHAMPS BABY!" Expect **banter ~0.50** when it's a reaction (pure celebration). "Short and all-caps reads as a joke to the model. The LLM baseline is much better at tone."

**2:30–4:00 · Walk through the README evaluation report.**
- Results table: the baseline wins overall (0.684 acc / 0.605 macro-F1 vs 0.561 / 0.557), but fine-tuned wins analysis F1 0.70 vs 0.17. The LLM called 10 of 11 analysis posts hot_take.
- Confusion matrices: the baseline dumps everything uncertain into hot_take; the fine-tuned model's biggest error is hot_take → banter (8).
- Success criteria: met 0 of 4. Plus the stability point: before the label review, a different split gave the opposite overall winner, so with ~57 test posts only the per-class pattern is reliable.
- Reflection: learned length and specificity, not purpose; the LLM listens to tone; neither weighs the evidence. The fix is to break the length shortcut and tighten rule A to "checkable" evidence.

**4:00–4:30 · Wrap:** hyperparameters (defaults collapsed to the majority class; class weights; lowest-val-loss checkpoint). Annotation: Claude pre-labeled, a second model flagged 142 disputes, and I reviewed all 142 and changed 38.
