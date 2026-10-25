# Task 1 · A-Priori, and Why the Second Pass Is the Whole Problem

**File** — `task1_apriori.py`
**Theory** — §6.1 market-basket model, §6.2 A-Priori, §6.1.3 confidence and lift
**Kind** — implementation · runs anywhere

---

## What you are building

With n items there are n(n−1)/2 pairs. For a supermarket's 10,000 items that is
50 million counters before you have read a single basket.

A-Priori's observation is one sentence: **a pair cannot be frequent unless both
of its items are frequent.** One extra pass buys a much smaller second pass, and
the rest of the chapter is consequences of that trade.

## Requirements

| # | Requirement |
|---|---|
| R1 | `frequent_singletons` returns `{item: count}` at or above the threshold |
| R2 | `frequent_pairs` counts **only** pairs whose items both survived pass one |
| R3 | `association_rules` returns `(antecedent, consequent, confidence, lift)`, sorted by confidence |
| R4 | Confidence of i → j is `support({i,j}) / support({i})`, and it is **not symmetric** |
| R5 | Lift is confidence divided by the consequent's own support fraction |

**R2 is what makes this A-Priori.** Counting every pair and filtering afterwards
gives the same answer while being exactly the thing A-Priori exists to avoid. It
will pass this harness. Task 3 measures whether you really did it.

## Pass condition

```bash
python3 task1_apriori.py --verify
```

Five checks against baskets small enough to count by hand — including that
`cola` and `egg`, which appear twice and once, never reach pass two.

## Why R5 is in here

`diaper → beer` has confidence 0.8, which sounds strong. Beer is in 5 of 7
baskets anyway, so its baseline is 0.71. The lift is 1.12 — the rule barely
tells you anything you did not already know from beer being popular.

A rule with high confidence and lift near 1 is a rule about a common item, not a
relationship. §6.1.3 is about that, and it is the most practically important
paragraph in the chapter.

## What to write in `observation.md`

- Confidence is not symmetric. Give the two confidences for one of your pairs
  and say which direction is the useful claim
- The highest-confidence rule you found, its lift, and whether you believe it
- With 2,000 items, how many pair counters would brute force need? How many does
  A-Priori need after pass one on this data? Give both numbers
