## Overall

| Model | Accuracy | Macro F1 |
|---|---|---|
| Groq zero-shot (gpt-oss-20b) | 0.684 | 0.605 |
| Fine-tuned DistilBERT | 0.561 | 0.557 |
| Majority class (always `hot_take`) | 0.456 | — |

## Per-class (test set, n=57)

| Label | Support | Baseline P | Baseline R | Baseline F1 | Fine-tuned P | Fine-tuned R | Fine-tuned F1 |
|---|---|---|---|---|---|---|---|
| analysis | 11 | 1.00 | 0.09 | 0.17 | 0.67 | 0.73 | 0.70 |
| hot_take | 26 | 0.60 | 1.00 | 0.75 | 0.67 | 0.54 | 0.60 |
| reaction | 6 | 0.83 | 0.83 | 0.83 | 0.50 | 0.50 | 0.50 |
| banter | 14 | 1.00 | 0.50 | 0.67 | 0.39 | 0.50 | 0.44 |

## Confusion matrix — fine-tuned (rows = true, columns = predicted)

| true \ pred | analysis | hot_take | reaction | banter | total |
|---|---|---|---|---|---|
| **analysis** | 8 | 3 | 0 | 0 | 11 |
| **hot_take** | 2 | 14 | 2 | 8 | 26 |
| **reaction** | 0 | 0 | 3 | 3 | 6 |
| **banter** | 2 | 4 | 1 | 7 | 14 |

## Confusion matrix — baseline

| true \ pred | analysis | hot_take | reaction | banter | total |
|---|---|---|---|---|---|
| **analysis** | 1 | 10 | 0 | 0 | 11 |
| **hot_take** | 0 | 26 | 0 | 0 | 26 |
| **reaction** | 0 | 1 | 5 | 0 | 6 |
| **banter** | 0 | 6 | 1 | 7 | 14 |

## Calibration (fine-tuned)

| Confidence | Predictions | Accuracy | Mean confidence |
|---|---|---|---|
| < 0.50 | 30 | 0.47 | 0.41 |
| 0.50–0.70 | 24 | 0.62 | 0.59 |
| 0.70–0.90 | 3 | 1.00 | 0.76 |

Expected calibration error (4 bins): 0.056

## Error patterns (25 errors / 57)

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

| Length | n | Accuracy |
|---|---|---|
| short (<80) | 24 | 0.46 |
| medium (80–200) | 22 | 0.55 |
| long (>200) | 11 | 0.82 |

| Predicted label | times predicted | true count |
|---|---|---|
| analysis | 12 | 11 |
| hot_take | 21 | 26 |
| reaction | 6 | 6 |
| banter | 18 | 14 |

## All fine-tuned errors

| # | true | pred | conf | text |
|---|---|---|---|---|
| 1 | banter | reaction | 0.50 | Hell yeah two super bowls already this season |
| 2 | analysis | hot_take | 0.62 | If you’re a second apron team out a bunch of FRPs you are essentially all-in on winning a championship immediately. So no I would not call getting swept or 4-1’d in the CFs a success at all. |
| 3 | hot_take | analysis | 0.69 | I’ve heard this theory and don’t buy it. Let’s say an average person shoots on a nerf hoop, same issue, you’re too big, ball is too light, you’re still making more baskets from 2 feet away than 3 feet, if you took hundre… |
| 4 | hot_take | reaction | 0.37 | Basketball reference is gonna say 82 gp that's literally all that matters |
| 5 | hot_take | banter | 0.37 | Every game was lost by a basket or two. Yall got swept cause Bron shot like shit |
| 6 | banter | analysis | 0.28 | Only 1992 more games and he catches Ripkin |
| 7 | banter | hot_take | 0.41 | Charania is fucking jokić. We know how these "sources" work now. |
| 8 | hot_take | banter | 0.35 | …from Kings fans who didn’t want to admit their team got fleeced. |
| 9 | hot_take | banter | 0.64 | cade is a tier above brunson at this point sorry buddy |
| 10 | hot_take | banter | 0.60 | Garrison Mathew’s is the GOAT at this.Theres a whole compilation on YT of him jumping almost 5 feet forward. |
| 11 | banter | hot_take | 0.43 | Bro this is an American sports sub. How tough you are depends on the color of your skin. Even if both dudes are from Europe lol |
| 12 | hot_take | analysis | 0.58 | I’m likely missing something but the simplest solution to these issues imo is just to extend the season in days to eliminate back to backs and allow for more recovery between games. Extend the season two or three or howe… |
| 13 | analysis | hot_take | 0.45 | Thread from the moment it was signed: https://www.reddit.com/r/nba/comments/1obpo0z/charania_denver_nuggets_guard_christian_braun_has/ Not a single top comment thought it was stupid. |
| 14 | banter | hot_take | 0.60 | better for the Wolves that Jokic isn't suspended. that's like 50 easy paint points sorted out |
| 15 | hot_take | banter | 0.35 | and is absolutely nothing like MJ |
| 16 | banter | hot_take | 0.43 | ykw sure whatever I guess this if fine it’s not like we needed someone who can actually play defense |
| 17 | reaction | banter | 0.34 | Embiid is a fucking warrior. |
| 18 | hot_take | banter | 0.60 | he'll get the $44mil max as an RFA...and DET will match |
| 19 | hot_take | banter | 0.41 | They need to go back to the blue and bronze this bs now has been ugly since day 1 |
| 20 | banter | analysis | 0.43 | Ok those were his lucky undies. Jokic is officially back. Nuggets in 7 with Jokic averaging 60/30/20 |
| 21 | hot_take | banter | 0.54 | would hate to see where the rockets are without him if he tries to leave this year |
| 22 | reaction | banter | 0.40 | Mf broke the 4th Wall on live tv |
| 23 | reaction | banter | 0.51 | Need to enjoy in the moment |
| 24 | hot_take | reaction | 0.43 | Chuck is really going through it this season |
| 25 | analysis | hot_take | 0.44 | Plus forget gabe hes taking laravia's minutes and for the past 3 months teams just havent been guarding him at all so it completely fucks our offense |
