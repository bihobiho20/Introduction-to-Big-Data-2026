# Task 3 · Same Memory, Fewer Mistakes

**Files** — `task3_budget.py` · harness `bench.py` (**do not edit the harness**)
**Theory** — §4.4.2
**Kind** — improvement · runs anywhere

---

## What you are given

`NaiveFilter` is a membership filter in a fixed number of bits. It works, and it
makes far more mistakes than it needs to with the memory it was handed.

You get **exactly the same bits**. Make fewer mistakes.

```bash
python3 bench.py
python3 bench.py --yours
```

```
  80,000 bits  ·  8,000 items inserted  ·  200,000 queried
```

Ten bits per item, and the harness tells you the item count before you start —
so there is no excuse for guessing.

**Where the baseline lands:**

```
  baseline   false positives  19,023  ( 9.511%)   false negatives     0   bits 80,000
```

One in ten queries comes back wrong.

## Requirements

| # | Requirement |
|---|---|
| R1 | `YourFilter(n_bits, seed)` with `add`, `__contains__`, `memory_bits()` |
| R2 | `bench.py` unmodified |
| R3 | `memory_bits()` ≤ the budget, and it must count **all** of your memory |
| R4 | **Zero false negatives** |
| R5 | Lower false-positive rate than the baseline |
| R6 | In `observation.md`: the theoretical minimum rate for 10 bits per item, and whether you reached it |

R4 is not negotiable. The entire value of this structure is that "no" means no.
A filter that scores better by occasionally forgetting something has not improved
anything, it has broken the contract.

R3 exists because counting only some of your memory is not an optimisation.

## Grading

| | Requirement |
|---|---|
| pass | R1–R5, more than 5% better |
| good | ≥ **50%** better |
| **strong** | false-positive rate ≤ **0.9%** |

The "strong" bar is set where it is for a reason: with m/n = 10 there is a
**floor**, and it is around 0.82%. You are being asked to reach the optimum, not
to beat it. §4.4.2 will tell you which parameter to set and what to set it to —
there is one derivative between you and the answer.

## The harder question, which is worth more than the grade

The harness tells you n before you start. **A real stream does not.**

You do not have to implement anything for this, but `observation.md` asks: what
would you do when you cannot know how many items are coming? Name what goes
wrong if you guess too low, and what you waste if you guess too high.

## What to write in `observation.md`

- Which parameter you changed and the value you chose, with the derivation
- R6: the floor for 10 bits per item, and how close you got
- What you would do if n were unknown
