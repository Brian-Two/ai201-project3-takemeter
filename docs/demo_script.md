# Demo video script (3–5 min)

Setup before recording: `source .venv/bin/activate && python app/app.py`, open http://127.0.0.1:7860, and have README.md open in the GitHub tab.

**0:00–0:30 · What it is.** "TakeMeter classifies r/nba comments into four labels by purpose: analysis (argued with evidence), hot_take (asserted without it), reaction (in-the-moment feeling), and banter (the joke is the point). Fine-tuned DistilBERT on 389 labeled comments, compared to a zero-shot LLM."

**0:30–2:30 · Classify 5 posts live in the app** (label + confidence visible each time):

1. ✅ **Correct, narrate why:** paste this test-set post, which the model never trained on:
   > I'm just stating how they can be skewed. Also yes, just 2 years ago the nuggets literally ran Jokic for 80% of his minutes with AT LEAST 3 other starters on the court outside of him. I'm not saying NBA rotations are always the same, but on/off is a metric that needs substance behind it because some stars get a lot of their minutes with bench guys, and other stars are almost exclusively ran with the starting lineup

   Expect **analysis ~0.86**. Narrate: "The claim is that on/off stats can mislead, and it's backed by a checkable fact about Jokic's lineups. Strip out the 'I'm just stating' attitude and the argument still stands. That's our rule A, so analysis is right, and it's the model's most confident kind of prediction."
2. Built-in example: "Wemby is already the best defender in the league and it isn't close." Expect **hot_take ~0.64**, correct: a bold claim with zero evidence.
3. Built-in example: "Grudge avenged!! CHAMPS BABY!" Expect **reaction ~0.46**: pure celebration. Point out that banter is close behind (~0.40). The model is unsure between the two short, casual labels.
4. ❌ **Incorrect, narrate what went wrong:** the built-in example "If it's the Spurs maybe. Not for OKC though. SGA is the only player on their team who's played more than 30 mpg in the last 2 games. They're stupid deep". Expect **hot_take ~0.63** when it's really analysis.
   Narrate: "This is analysis: the claim is that OKC won't be tired, backed by a specific minutes stat. The model says hot_take because it's short and opens with a hedge. Our error analysis found the model mostly learned *length*: 68% of analysis training posts are over 200 characters, and accuracy on long posts is 93% vs 45% on short ones. Our length-filtered top-up sampling made that worse."
5. Built-in example: "That man is married with 3 kids. He gone gone." A test-set **error**: true banter, predicted reaction ~0.42. "Its most common mistake, 6 times on the test set: short jokes get called reactions."

**2:30–4:00 · Walk through the README evaluation report.**
- Results table: fine-tuned 0.644 acc / 0.596 macro-F1 vs baseline 0.627 / 0.565. "One more correct example, within noise."
- Per-class: analysis F1 0.86 vs 0.47, a huge win; reaction 0.21 vs 0.50, a big loss.
- Confusion matrices: the baseline dumps things into hot_take; fine-tuned errors pile into reaction.
- Success criteria table: met 1 of 4 (analysis precision). "So it works as a 'show me the analysis' filter, not as a general classifier."
- Reflection: learned specificity and length, not purpose. The next fixes are to break the length shortcut in the data and consider merging reaction and banter.

**4:00–4:30 · Wrap:** hyperparameter story (defaults collapsed to the majority class; class weights; picked the lowest-val-loss checkpoint over the top score), plus the AI usage disclosure (Claude pre-labeled, reviewed with `label.py --review`).
