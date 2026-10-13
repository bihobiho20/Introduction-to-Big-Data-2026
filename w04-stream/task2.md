# Task 2 · Find the Size Where Exact Stops Being Possible

**File** — `task2_limits.py`
**Theory** — §4.1 the stream model, §4.5
**Kind** — **measurement. The number is about your machine, and nobody else's.**

---

## Why this task exists

"The exact answer does not fit" is easy to agree with and hard to feel. This task
makes you watch it happen: hold every distinct item in a `set`, raise the stream
size, and find where your own laptop stops coping.

You cannot look this number up and an agent cannot produce it for you. It depends
on your RAM, your Python, and what else you have open.

## What to do

```bash
python3 task2_limits.py --sizes 100000,400000,1600000
python3 task2_limits.py --sizes 6400000
python3 task2_limits.py --sizes 25000000        # if you dare
```

Each run records, for both the exact `set` and your Flajolet-Martin from Task 1:
wall time, peak memory, and the estimate's ratio to the truth.

| # | Requirement |
|---|---|
| A1 | At least **four** stream sizes, spanning a 16× range or more |
| A2 | Go until the exact version is genuinely unpleasant. **Record that size and what ran out — time or memory** |
| A3 | Tabulate memory against n for both methods → `out/limits.md` |
| A4 | The exact set's memory grows with n. Flajolet-Martin's does not. Confirm that from **your own numbers**, and give both growth rates |
| A5 | Report FM's accuracy ratio at each size. Does it get better or worse as n grows? |
| A6 | State your machine: CPU, RAM, what else was running |

A4 is the whole lesson in one measurement. One line goes up and the other is
flat, and you should be able to say roughly *how* flat — FM's memory is set by
the number of hashes, not by the data.

A5 is the honest counterweight: you did not get the flat line for free.

## The estimate is bad, and that is a result

FM lands within a factor of two, not within a few percent. If your ratios wander
between 0.6× and 1.7×, that is the method behaving normally. Report what you got
rather than the number you wanted, and say in `observation.md` whether a factor
of two is good enough for the question "how many distinct users visited today".

## Pass condition

`out/limits.json` has four or more sizes with your machine recorded, and
`out/limits.md` answers A2–A6.

```bash
python3 test_tasks.py --task 2
```

## If your machine is small

That is a finding. A laptop that cannot get past 2 million items tells you
something precise about constant factors. "I stopped at X because Y" with the
evidence is a complete answer.

## What to write in `observation.md`

- The size where exact became unbearable, and whether time or memory gave out first
- The two growth rates from A4
- Is a factor of two good enough for "how many distinct users visited today"?
  Give a case where it is and a case where it is not
