"""Reproduce bucket-size and memory-crossover experiments (standard library)."""
import gc
import json
import time
import tracemalloc
from pathlib import Path

import bench
from task1_apriori import association_rules, frequent_singletons
from task3_pcy import PlainApriori, YourAlgorithm

OUT = Path(__file__).with_name("out")


def measured(algo, baskets):
    gc.collect()
    tracemalloc.start()
    start = time.perf_counter()
    pairs = algo.run(baskets)
    seconds = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return pairs, {"baskets": len(baskets), "support": algo.support,
                   "frequent_pairs": len(pairs),
                   "peak_counters": algo.peak_counters,
                   "peak_bytes": peak, "seconds_with_tracing": seconds}


def main():
    OUT.mkdir(exist_ok=True)
    baskets = bench.build()
    truth = PlainApriori(bench.SUPPORT).run(baskets)
    report = {"bucket_trials": [], "crossover": []}
    for n_buckets in (1 << 14, 1 << 17, 1 << 21):
        algo = YourAlgorithm(bench.SUPPORT, n_buckets)
        pairs, row = measured(algo, baskets)
        assert pairs == truth, "pair keys AND support counts must agree"
        row.update(n_buckets=n_buckets, bucket_bytes=algo.bucket_bytes,
                   bitmap_bytes=algo.bitmap_bytes,
                   frequent_buckets=algo.frequent_buckets, exact_counts=True)
        report["bucket_trials"].append(row)
        print("buckets", row, flush=True)
        del pairs
    for n in (100, 1000, 5000, 10000, 20000):
        sample = baskets[:n]
        base_pairs, base = measured(PlainApriori(bench.SUPPORT), sample)
        mine_pairs, mine = measured(YourAlgorithm(bench.SUPPORT), sample)
        assert mine_pairs == base_pairs
        report["crossover"].append({"baskets": n, "baseline": base,
                                     "pcy": mine, "exact_counts": True})
        print("crossover", n, base["peak_bytes"], mine["peak_bytes"], flush=True)
        del base_pairs, mine_pairs

    singles = frequent_singletons(baskets, bench.SUPPORT)
    rules = association_rules(baskets, bench.SUPPORT, 0)
    top = rules[0]
    reverse = next(rule for rule in rules
                   if rule[:2] == (top[1], top[0]))
    report["rules"] = {"highest": top, "reverse": reverse,
                       "singleton_counts": {str(i): singles[i] for i in top[:2]},
                       "frequent_singletons": len(singles),
                       "possible_surviving_pairs": len(singles) * (len(singles) - 1) // 2,
                       "brute_force_pairs": bench.ITEMS * (bench.ITEMS - 1) // 2}
    report["measurement"] = (
        "tracemalloc algorithm allocations including output; input baskets and "
        "reference answers prebuilt and excluded. Not total process RAM. "
        "Crossover uses fixed support 50 and prefixes of seed-246 data.")
    with (OUT / "pcy_memory.json").open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print("rules", report["rules"])


if __name__ == "__main__":
    main()
