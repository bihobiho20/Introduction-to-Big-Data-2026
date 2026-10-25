# Week 6 Lab · Frequent Itemsets

**Theory** — 6-1 market-basket model, A-Priori (§6.1 – §6.2) · 6-2 PCY, limited-pass methods (§6.3 – §6.4)
**Submit to** — `w06-apriori/out/`

"People who buy X also buy Y" is easy to state and expensive to compute, because
the number of possible pairs is quadratic in the number of items. This week is
the standard way of not paying that, and the measurement of what it still costs.

```bash
cd w06-apriori
```

| | Task | You build |
|---|---|---|
| 1 | A-Priori and association rules | two passes, confidence and lift |
| 2 | Lower the threshold until it breaks | an explosion curve on your own machine |
| 3 | Make pass two fit | PCY, scored on peak counters |
| 4 | **optional** · SON, the MapReduce version | §6.4.4, and why 21× slower is still right |

Details and requirements are in **`task1.md`**, **`task2.md`**, **`task3.md`**.
Task 4 is **optional and not graded** — see **`task4.md`**.

## Running everything

```bash
python3 task1_apriori.py --verify
python3 task2_explosion.py --supports 400,200,100,50,25
python3 bench.py --yours
python3 test_tasks.py

python3 task4_son.py                 # optional
python3 task4_son.py --spark         # optional, needs Java 17 + PySpark
```

## What to submit

| File | From |
|---|---|
| `task1_apriori.py` | your A-Priori and rules |
| `out/explosion.json` · `out/explosion.md` | the curve and where it broke |
| `task3_pcy.py` · `out/bench.txt` | your PCY and its numbers |
| `out/observation.md` | 2–3 lines per task |

```bash
python3 ../check.py w06
```

## No download needed

Baskets are generated with a fixed seed, with a few pairs planted so there is
something real to find.
