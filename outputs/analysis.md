## Overall

| Model | Accuracy | Macro F1 |
|---|---|---|
| Groq zero-shot (gpt-oss-20b) | 0.627 | 0.565 |
| Fine-tuned DistilBERT | 0.644 | 0.596 |
| Majority class (always `hot_take`) | 0.475 | — |

## Per-class (test set, n=59)

| Label | Support | Baseline P | Baseline R | Baseline F1 | Fine-tuned P | Fine-tuned R | Fine-tuned F1 |
|---|---|---|---|---|---|---|---|
| analysis | 10 | 0.57 | 0.40 | 0.47 | 0.82 | 0.90 | 0.86 |
| hot_take | 28 | 0.62 | 0.82 | 0.71 | 0.80 | 0.71 | 0.75 |
| reaction | 7 | 0.60 | 0.43 | 0.50 | 0.17 | 0.29 | 0.21 |
| banter | 14 | 0.70 | 0.50 | 0.58 | 0.64 | 0.50 | 0.56 |

## Confusion matrix — fine-tuned (rows = true, columns = predicted)

| true \ pred | analysis | hot_take | reaction | banter | total |
|---|---|---|---|---|---|
| **analysis** | 9 | 1 | 0 | 0 | 10 |
| **hot_take** | 1 | 20 | 4 | 3 | 28 |
| **reaction** | 1 | 3 | 2 | 1 | 7 |
| **banter** | 0 | 1 | 6 | 7 | 14 |

## Confusion matrix — baseline

| true \ pred | analysis | hot_take | reaction | banter | total |
|---|---|---|---|---|---|
| **analysis** | 4 | 6 | 0 | 0 | 10 |
| **hot_take** | 3 | 23 | 1 | 1 | 28 |
| **reaction** | 0 | 2 | 3 | 2 | 7 |
| **banter** | 0 | 6 | 1 | 7 | 14 |

## Calibration (fine-tuned)

| Confidence | Predictions | Accuracy | Mean confidence |
|---|---|---|---|
| < 0.50 | 29 | 0.41 | 0.44 |
| 0.50–0.70 | 21 | 0.86 | 0.58 |
| 0.70–0.90 | 9 | 0.89 | 0.79 |

Expected calibration error (4 bins): 0.125

## Error patterns (21 errors / 59)

| true → predicted | count |
|---|---|
| banter → reaction | 6 |
| hot_take → reaction | 4 |
| reaction → hot_take | 3 |
| hot_take → banter | 3 |
| hot_take → analysis | 1 |
| reaction → analysis | 1 |
| reaction → banter | 1 |
| analysis → hot_take | 1 |
| banter → hot_take | 1 |

| Length | n | Accuracy |
|---|---|---|
| short (<80) | 20 | 0.45 |
| medium (80–200) | 24 | 0.62 |
| long (>200) | 15 | 0.93 |

| Predicted label | times predicted | true count |
|---|---|---|
| analysis | 11 | 10 |
| hot_take | 25 | 28 |
| reaction | 12 | 7 |
| banter | 11 | 14 |

## All fine-tuned errors

| # | true | pred | conf | text |
|---|---|---|---|---|
| 1 | banter | reaction | 0.53 | From championship locker room to Ace Ventura sequel. You can't make this shit up. |
| 2 | reaction | hot_take | 0.58 | It’s pretty cool that the top four First Team are international players. |
| 3 | banter | reaction | 0.42 | That man is married with 3 kids. He gone gone. |
| 4 | hot_take | reaction | 0.33 | He folded like a lawn chair during that apology tour after the club incident. You can agree with what he says but it means fuck all if he’s a gigantic pussy |
| 5 | banter | reaction | 0.50 | Weird how that’s almost exactly like me, except in inches |
| 6 | reaction | hot_take | 0.52 | It’ll be interesting to see how this new team does against teams that have historically given us trouble. |
| 7 | hot_take | analysis | 0.48 | Lukas defense has been over hated for a while now cus of the viral lowlights, and on top of that a single guard is never the reason for a teams defensive successes or failures |
| 8 | reaction | analysis | 0.76 | I remember a late-night game at Sacramento in March of '19 where he went nuclear in the 4th quarter and led them back from 25 down, with Atkinson going with DLo, Kurucs, Treveon Graham, Dudley and RHJ the whole quarter. … |
| 9 | hot_take | banter | 0.43 | would hate to see where the rockets are without him if he tries to leave this year |
| 10 | hot_take | reaction | 0.47 | Sucked out the energy of the entire team honestly. Everyone needs to cover for him on defense. |
| 11 | banter | reaction | 0.43 | No title shot, but glad to see they are at least having fun in south beach |
| 12 | hot_take | reaction | 0.42 | Real ones will remember he was an X factor during that bucks championship run. Never looked the same after the bubble |
| 13 | banter | reaction | 0.45 | What were the dinosaurs like, unc? |
| 14 | reaction | banter | 0.48 | imagine his body develops like Giannis, slow and steady |
| 15 | hot_take | reaction | 0.43 | Commanders is actually even worse |
| 16 | analysis | hot_take | 0.39 | Fox went nuclear and the blazers couldn’t stop turning the ball over. |
| 17 | banter | hot_take | 0.38 | Turns out KAT and Josh Hart are handy players to have available |
| 18 | hot_take | banter | 0.39 | You could just as easily say that Wemby clearly isn’t in pain lol after a moment he gets up like nothing happened |
| 19 | hot_take | banter | 0.37 | Better angle for sure. Doesn’t look like a travel there. |
| 20 | reaction | hot_take | 0.50 | It would've been a nice consolation prize at least, sort of like J-Lin winning a ring with the Raptors after years of injuries. But Dirk and the Mavs dashed those dreams. |
| 21 | banter | reaction | 0.43 | So he was just hating on the celts. Makes sense. |
