# Task 3 · Make Pass Two Fit

**Files** — `task3_pcy.py` · harness `bench.py` (**do not edit the harness**)
**Theory** — §6.3 PCY
**Kind** — improvement · runs anywhere

---

## What you are given

`PlainApriori` does what Task 1 asked: drop infrequent items in pass one, then
count every pair of survivors. Much better than counting all pairs — and still
not enough, because the survivors are the *common* items and common items appear
together constantly.

```bash
python3 bench.py
python3 bench.py --yours
```

```
  20,000 baskets  ·  2,000 items  ·  support 50
```

**Where the baseline lands:**

```
  baseline     pairs  6397   peak counters    820,259     0.57s
```

820,000 counters to find 6,397 answers.

## How you are scored

**Peak pair counters held at once.** Not time — that is the thing that decides
whether the algorithm runs at all, and it is what §6.3 is about.

## Requirements

| # | Requirement |
|---|---|
| R1 | `YourAlgorithm(support)` with `run(baskets)` and `.peak_counters` |
| R2 | `bench.py` unmodified |
| R3 | **Exactly the same frequent pairs** as the baseline. Not a subset |
| R4 | Fewer peak counters |
| R5 | In `observation.md`: your bucket array was itself memory. Account for it honestly, and say at what data size PCY starts actually winning |

## Grading

| | Requirement |
|---|---|
| pass | R1–R4, more than 5% cut |
| good | ≥ **40%** cut |
| **strong** | ≥ **70%** cut |

A straightforward PCY gets about 99%. If you are far from that, check whether
your bitmap is doing any work — a filter that passes everything is not a filter.

## The idea

Pass one only needs one integer per item, and there are not many items. The rest
of your memory sits idle. §6.3 spends it: hash every pair you see **during pass
one** into a fixed array of buckets, and count buckets instead of pairs.

A bucket whose total is below the support threshold **cannot** contain a frequent
pair. In pass two you skip every pair landing in such a bucket — and the bucket
array collapses to one bit each before you need the memory for counters.

Two things to be careful of:

- a frequent bucket does **not** mean its pairs are frequent. It is a filter,
  not an answer
- `peak_counters` is on your honour. Count what you hold at the same time

## R5 · the honest accounting

Your bucket array holds a million-odd integers during pass one. The baseline's
peak was 820,000 counters. On *this* data, did you actually save memory, or did
you move it?

Then answer the real question: **at what data size does PCY start winning?** The
bucket array is a fixed cost and the counter count is not, so there is a
crossover. Say roughly where it is and what it depends on.

This is the most interesting question in the week and it is why R5 is a
requirement rather than a bonus.

## What to write in `observation.md`

- Your bucket count, and why you chose that number
- R5: the honest memory accounting, and where the crossover is
- What happened when you made the bucket array much smaller. Try it
