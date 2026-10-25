#!/usr/bin/env python3
"""Task 2 supplement: lower support on a larger, separately labelled dataset.

The provided bench.py and PlainApriori remain unchanged. Stop at a declared
memory/time budget instead of exhausting physical RAM. Standard library only.

    python task2_stress.py
"""
import argparse
import gc
import json
import random
import time
import tracemalloc
from datetime import datetime, timezone
from itertools import accumulate
from pathlib import Path

from task2_explosion import machine
from task3_pcy import PlainApriori

OUT = Path(__file__).with_name("out")


def build(basket_count, item_count, seed=246):
    """Same Zipf weights, basket sizes and planted-pair rule as bench.build.

    Precompute cumulative weights to avoid rebuilding them for every draw.
    With 20,000 baskets and 2,000 items this equals bench.build() exactly.
    """
    rng = random.Random(seed)
    items = list(range(item_count))
    cumulative = list(accumulate(1 / (i + 1) ** 0.8 for i in items))
    planted = [(rng.randrange(300), rng.randrange(300)) for _ in range(25)]
    planted = [(a, b) for a, b in planted if a != b]
    baskets = []
    for _ in range(basket_count):
        k = max(2, int(rng.gauss(20, 4)))
        basket = set(rng.choices(items, cum_weights=cumulative, k=k))
        if rng.random() < 0.08:
            basket.update(rng.choice(planted))
        baskets.append(basket)
    return baskets


class BudgetExceeded(Exception):
    pass


class MonitoredBaskets:
    """Re-iterable input; check budgets between baskets without changing counts."""

    def __init__(self, baskets, byte_limit, seconds_limit):
        self.baskets = baskets
        self.byte_limit = byte_limit
        self.seconds_limit = seconds_limit
        self.started = time.perf_counter()
        self.pass_number = 0
        self.baskets_in_pass = 0

    def check(self):
        _, peak = tracemalloc.get_traced_memory()
        if peak >= self.byte_limit:
            raise BudgetExceeded("python_allocation_budget")
        if time.perf_counter() - self.started >= self.seconds_limit:
            raise BudgetExceeded("elapsed_time_budget")

    def __iter__(self):
        self.pass_number += 1
        self.baskets_in_pass = 0
        for i, basket in enumerate(self.baskets):
            if i % 256 == 0:
                self.check()
            yield basket
            self.baskets_in_pass = i + 1
        self.check()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--supports", default="400,200,100,50,25,12,6,3,1")
    parser.add_argument("--baskets", type=int, default=100_000)
    parser.add_argument("--items", type=int, default=20_000)
    parser.add_argument("--max-mib", type=int, default=1024)
    parser.add_argument("--max-seconds", type=float, default=60)
    args = parser.parse_args()
    try:
        supports = [int(s) for s in args.supports.split(",")]
    except ValueError:
        parser.error("supports must be comma-separated positive integers")
    if (not supports or min(supports) < 1 or args.baskets < 1
            or args.items < 300 or args.max_mib < 1 or args.max_seconds <= 0):
        parser.error("positive sizes/budgets and at least 300 items are required")

    OUT.mkdir(exist_ok=True)
    report = {
        "machine": machine(),
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": {"baskets": args.baskets, "items": args.items,
                    "seed": 246, "average_draws": 20,
                    "distribution": "Zipf exponent 0.8; same planted-pair rule as bench"},
        "budget": {"peak_python_bytes": args.max_mib * 2**20,
                   "algorithm_seconds": args.max_seconds,
                   "check_interval_baskets": 256, "checked_after_result": True},
        "measurement": (
            "Additional traced Python allocations, including output, excluding "
            "prebuilt input. Elapsed time includes tracing/checks, excludes generation. "
            "Budget stop is NOT a physical RAM exhaustion measurement. "
            "Interrupted runs have no final frequent-pair answer."),
        "runs": []}
    print("Building separately labelled stress data...", flush=True)
    baskets = build(args.baskets, args.items)
    print(f"{len(baskets):,} baskets, {args.items:,} items; "
          f"budget {args.max_mib} MiB / {args.max_seconds:g}s", flush=True)
    for support in supports:
        gc.collect()
        algo = PlainApriori(support)
        source = MonitoredBaskets(baskets, args.max_mib * 2**20, args.max_seconds)
        tracemalloc.start()
        status, reason, answer_count = "completed", None, None
        try:
            pairs = algo.run(source)
            answer_count = len(pairs)
            source.check()
        except BudgetExceeded as exc:
            status = "completed_over_budget" if answer_count is not None else "stopped"
            reason = str(exc)
        elapsed = time.perf_counter() - source.started
        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        row = {"support": support, "status": status, "stop_reason": reason,
               "frequent_pairs": answer_count, "peak_counters": algo.peak_counters,
               "peak_bytes": peak_bytes, "seconds": elapsed,
               "pass_number": source.pass_number,
               "baskets_completed_in_pass": source.baskets_in_pass,
               "budget_checked_after_result": answer_count is not None}
        report["runs"].append(row)
        with (OUT / "stress.json").open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(row, flush=True)
        if answer_count is not None:
            del pairs
        if status != "completed":
            break


if __name__ == "__main__":
    main()
