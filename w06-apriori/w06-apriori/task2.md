# Task 2 · Lower the Threshold Until Your Machine Says No

**File** — `task2_explosion.py`
**Theory** — §6.1, §6.2
**Kind** — **measurement. Where it breaks is a fact about your laptop.**

---

## Why this task exists

Support is a knob. Turning it down is how you find the interesting rules, and it
is also how you run out of memory. The two are the same action, and this task is
about feeling where the boundary is on the machine in front of you.

## What to do

```bash
python3 task2_explosion.py --supports 400,200,100,50,25
python3 task2_explosion.py --supports 12,6
python3 task2_explosion.py --supports 3        # be ready to stop it
```

| # | Requirement |
|---|---|
| A1 | At least **five** support values, spanning a 16× range |
| A2 | Keep halving until it is genuinely unpleasant. **Record that support and what ran out** |
| A3 | Tabulate peak counters against support → `out/explosion.md` |
| A4 | Counters do not grow linearly as support falls. Give the growth you actually measured — is it roughly doubling per halving, or worse? |
| A5 | Frequent pairs found against support: plot it too. **It grows differently from the counters** — say how, and why that gap is the whole problem |
| A6 | Your machine: CPU, RAM, what else was running |

A5 is the point. The number of *answers* grows slowly; the number of *counters
you need to find them* grows fast. Everything in §6.3 is about that gap.

## A warning

At low supports this will get slow and memory-hungry before it errors. Watch
your memory, and stop it rather than freezing your laptop. **Stopping early and
recording where is the correct outcome** — "I stopped at support 3 because the
process reached 6 GB" is a complete answer.

## Pass condition

`out/explosion.json` has five or more supports with your machine recorded, and
`out/explosion.md` answers A2–A6.

```bash
python3 test_tasks.py --task 2
```

## What to write in `observation.md`

- The support where it became unbearable, and what ran out first
- A4: your measured growth rate for counters
- A5: how differently the answer count grew, and what that gap means for anyone
  who wants "just a slightly lower threshold"
