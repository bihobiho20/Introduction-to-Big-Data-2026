# Task 1 · Answer Questions About a Stream You Cannot Store

**File** — `task1_sketches.py`
**Theory** — §4.3 sampling, §4.4 Bloom filters, §4.5 counting distinct elements
**Kind** — implementation · runs anywhere, no data needed

---

## What you are building

Three structures, each trading an exact answer for a bounded amount of space.
The job is not to get them working. It is to know **exactly what you traded**.

| | Question | Method |
|---|---|---|
| `BloomFilter` | have I seen this before? | §4.4 |
| `flajolet_martin` | how many *distinct* things went past? | §4.5 |
| `reservoir_sample` | give me k of them, uniformly | §4.3 |

## Requirements

| # | Requirement |
|---|---|
| R1 | The Bloom filter **never** has a false negative. Not rarely — never |
| R2 | `expected_fp_rate(n)` returns the §4.4.2 prediction, computed not measured |
| R3 | The measured false-positive rate matches that prediction |
| R4 | `flajolet_martin` lands within **a factor of two** of the true distinct count |
| R5 | `reservoir_sample` is uniform: every item has probability k/n, and you hold only k |
| R6 | One pass. None of these may store the stream |

R1 and R3 together are the real test. R1 is structural — if you ever have a false
negative, you built something else. R3 says your understanding of *why* it works
is good enough to predict its error rate before measuring it.

## About R4 and the factor of two

That tolerance is not generous, it is honest. Flajolet-Martin really is that
crude, and HyperLogLog exists because of it.

How you combine many hashes matters a great deal:

- averaging `2^R` directly is dominated by whichever hash got lucky — the values
  are exponential, so one outlier swamps everything
- the median is robust but can only ever be a power of two
- §4.5.3 suggests grouping and combining twice

Try more than one and look at what happens. Landing inside a factor of two
*reliably* is the requirement; getting closer is not expected.

## Pass condition

```bash
python3 task1_sketches.py --verify
```

Four checks: no false negatives, predicted rate matches measured, distinct
estimate within 2×, reservoir uniform across 4,000 trials.

## What to write in `observation.md`

- Why can a Bloom filter never have a false negative? One sentence, structural
- Your predicted and measured false-positive rates. If they differ, say why
- Which combining rule you used for Flajolet-Martin, and what the others gave you
- Reservoir sampling holds k items but has to be correct for a stream whose
  length it never learns. Where in your code does that actually happen?
