#!/usr/bin/env python3
"""Week 6 · does your work pass?"""
import argparse, importlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
sys.path.insert(0, HERE)
PASS, FAIL, SKIP = "PASS", "FAIL", "SKIP"
results = []


def record(task, name, status, detail=""):
    results.append((task, name, status, detail))
    print({PASS: "  ok  ", FAIL: " FAIL ", SKIP: " skip "}[status]
          + f" [{task}] {name}" + (f"  - {detail}" if detail else ""))


def test_task1():
    try:
        m = importlib.import_module("task1_apriori")
    except Exception as e:
        return record(1, "task1_apriori.py imports", FAIL, repr(e))
    try:
        rc = m.verify()
    except Exception as e:
        return record(1, "verify runs", FAIL, repr(e))
    record(1, "all five checks", PASS if rc == 0 else FAIL)


def test_task2():
    path = os.path.join(OUT, "explosion.json")
    if not os.path.exists(path):
        return record(2, "out/explosion.json exists", FAIL, "run task2_explosion.py")
    data = json.load(open(path))
    sup = sorted({r["support"] for r in data.get("runs", [])})
    record(2, "A1 five or more supports", PASS if len(sup) >= 5 else FAIL, str(sup))
    if sup:
        span = max(sup) / min(sup)
        record(2, "A1 spans 16x or more", PASS if span >= 16 else FAIL, f"{span:.0f}x")
    record(2, "A6 machine recorded",
           PASS if data.get("machine", {}).get("platform") else FAIL)
    record(2, "out/explosion.md exists",
           PASS if os.path.exists(os.path.join(OUT, "explosion.md")) else FAIL)


def test_task3():
    try:
        bench = importlib.import_module("bench")
        mod = importlib.import_module("task3_pcy")
    except Exception as e:
        return record(3, "modules import", FAIL, repr(e))
    baskets = bench.build()
    base = bench.run(mod.PlainApriori, "baseline", baskets)
    try:
        mine = bench.run(mod.YourAlgorithm, "yours", baskets, base["pairs"])
    except NotImplementedError:
        return record(3, "YourAlgorithm implemented", FAIL, "still a stub")
    except Exception as e:
        return record(3, "YourAlgorithm runs", FAIL, repr(e))
    record(3, "R3 identical frequent pairs",
           PASS if set(mine["pairs"]) == set(base["pairs"]) else FAIL)
    cut = 1 - mine["peak"] / base["peak"]
    record(3, "R4 fewer peak counters", PASS if cut > 0.05 else FAIL, f"{cut:.1%} cut")
    record(3, "R5 memory accounting in observation.md", SKIP, "graded by a human")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--task", type=int, choices=[1, 2, 3])
    a = p.parse_args()
    os.makedirs(OUT, exist_ok=True)
    for n, fn in [(1, test_task1), (2, test_task2), (3, test_task3)]:
        if a.task in (None, n):
            print(f"\n=== Task {n}")
            fn()
    print()
    failed = sum(1 for *_, s, _ in results if s == FAIL)
    skipped = sum(1 for *_, s, _ in results if s == SKIP)
    print(f"  {len(results) - failed - skipped} passed, {failed} failed, {skipped} skipped")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
