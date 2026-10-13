#!/usr/bin/env python3
"""Week 4 · does your work pass?"""
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
        m = importlib.import_module("task1_sketches")
    except Exception as e:
        return record(1, "task1_sketches.py imports", FAIL, repr(e))
    try:
        rc = m.verify()
    except Exception as e:
        return record(1, "verify runs", FAIL, repr(e))
    record(1, "all four checks", PASS if rc == 0 else FAIL)


def test_task2():
    path = os.path.join(OUT, "limits.json")
    if not os.path.exists(path):
        return record(2, "out/limits.json exists", FAIL, "run task2_limits.py")
    data = json.load(open(path))
    sizes = sorted({r["n"] for r in data.get("runs", [])})
    record(2, "A1 four or more sizes", PASS if len(sizes) >= 4 else FAIL, str(sizes))
    if sizes:
        span = max(sizes) / min(sizes)
        record(2, "A1 spans 16x or more", PASS if span >= 16 else FAIL, f"{span:.0f}x")
    record(2, "A6 machine recorded",
           PASS if data.get("machine", {}).get("platform") else FAIL)
    record(2, "out/limits.md exists",
           PASS if os.path.exists(os.path.join(OUT, "limits.md")) else FAIL)


def test_task3():
    try:
        bench = importlib.import_module("bench")
        mod = importlib.import_module("task3_budget")
    except Exception as e:
        return record(3, "modules import", FAIL, repr(e))
    inserted, absent = bench.build()
    base = bench.run(mod.NaiveFilter, "baseline", inserted, absent)
    try:
        mine = bench.run(mod.YourFilter, "yours", inserted, absent)
    except NotImplementedError:
        return record(3, "YourFilter implemented", FAIL, "still a stub")
    except RuntimeError as e:
        return record(3, "R3 within the bit budget", FAIL, str(e))
    except Exception as e:
        return record(3, "YourFilter runs", FAIL, repr(e))
    record(3, "R4 zero false negatives", PASS if mine["fn"] == 0 else FAIL,
           f"{mine['fn']}")
    cut = 1 - mine["rate"] / base["rate"] if base["rate"] else 0
    record(3, "R5 lower false-positive rate", PASS if cut > 0.05 else FAIL,
           f"{mine['rate']:.3%} from {base['rate']:.3%}")
    record(3, "near the 0.82% floor", PASS if mine["rate"] <= 0.009 else SKIP,
           f"{mine['rate']:.3%}")
    record(3, "R6 floor derivation in observation.md", SKIP, "graded by a human")


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
