# Week 4 Lab · Mining Data Streams

**Theory** — 4-1 the stream model, sampling, filtering (§4.1 – §4.4) · 4-2 counting distinct, windows (§4.5 – §4.7)
**Submit to** — `w04-stream/out/`

The stream is longer than your memory, it goes past once, and you still have to
answer. Everything this week trades exactness for a bounded amount of space, and
the work is knowing precisely what you gave up.

```bash
cd w04-stream
```

| | Task | You build |
|---|---|---|
| 1 | Three sketches | Bloom filter, Flajolet-Martin, reservoir sampling |
| 2 | Find where exact stops fitting | a memory curve on your own machine |
| 3 | Same memory, fewer mistakes | a filter that reaches the theoretical floor |

Details and requirements are in **`task1.md`**, **`task2.md`**, **`task3.md`**.

## Running everything

```bash
python3 task1_sketches.py --verify
python3 task2_limits.py --sizes 100000,400000,1600000
python3 bench.py --yours
python3 test_tasks.py
```

## What to submit

| File | From |
|---|---|
| `task1_sketches.py` | your three sketches |
| `out/limits.json` · `out/limits.md` | the memory curve and where it broke |
| `task3_budget.py` · `out/bench.txt` | your filter and its numbers |
| `out/observation.md` | 2–3 lines per task |

```bash
python3 ../check.py w04
```

## No download needed

Tasks 1 and 3 use generated data with a fixed seed. Task 2 is about **your**
machine, so its numbers are not supposed to match anybody else's.
