#!/usr/bin/env python3
"""Week 6 · Task 2 — Lower the threshold until your machine says no.

Textbook §6.1, §6.2.

Support is a knob, and turning it down is how you find the interesting rules.
It is also how you run out of memory, and where that happens is a fact about
your laptop rather than about the algorithm.

    python3 task2_explosion.py --supports 400,200,100,50,25
    python3 task2_explosion.py --supports 12,6            # careful

Lower the threshold until something gives. Write down where and what.
"""
import argparse, json, os, platform, time, tracemalloc
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def machine():
    info = {"platform": platform.platform(),
            "processor": platform.processor() or platform.machine(),
            "python": platform.python_version(),
            "logical_cpus": os.cpu_count()}
    if os.name == "nt":
        import ctypes
        import winreg

        class MemoryStatus(ctypes.Structure):
            _fields_ = [("length", ctypes.c_ulong),
                        ("load", ctypes.c_ulong)] + [
                            (name, ctypes.c_ulonglong) for name in
                            ("total_phys", "avail_phys", "total_page",
                             "avail_page", "total_virtual", "avail_virtual",
                             "avail_extended")]

        status = MemoryStatus()
        status.length = ctypes.sizeof(status)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            info.update(ram_bytes=status.total_phys,
                        available_ram_bytes=status.avail_phys)
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as key:
                info["processor"] = winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
        except OSError:
            pass  # Keep platform.processor() if the registry is unavailable.
    return info


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--supports", default="400,200,100,50,25")
    a = p.parse_args()
    try:
        supports = [int(x) for x in a.supports.split(",")]
        if not supports or any(s < 1 for s in supports):
            raise ValueError
    except ValueError:
        p.error("--supports must be comma-separated positive integers")
    os.makedirs(OUT, exist_ok=True)

    import bench
    from task3_pcy import PlainApriori
    baskets = bench.build()

    path = os.path.join(OUT, "explosion.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            prior = json.load(f)
    else:
        prior = {"runs": []}
    prior["machine"] = machine()
    prior["dataset"] = {"seed": bench.SEED, "baskets": bench.BASKETS,
                        "items": bench.ITEMS, "average_draws": bench.AVG}
    prior["measurement"] = (
        "tracemalloc peak of algorithm allocations, excluding prebuilt baskets; "
        "elapsed time includes tracing overhead, not total process RAM")

    for support in supports:
        algo = PlainApriori(support)
        tracemalloc.start()
        t0 = time.perf_counter()
        pairs = algo.run(baskets)
        elapsed = time.perf_counter() - t0
        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        row = {"support": support, "frequent_pairs": len(pairs),
               "peak_counters": algo.peak_counters, "seconds": elapsed,
               "peak_bytes": peak_bytes,
               "recorded_at_utc": datetime.now(timezone.utc).isoformat()}
        prior["runs"].append(row)
        # Preserve completed measurements even if a later run is interrupted.
        with open(path, "w", encoding="utf-8") as f:
            json.dump(prior, f, indent=2, ensure_ascii=False)
        print(f"  support {support:>5}   pairs {len(pairs):>7,}   "
              f"counters {algo.peak_counters:>10,}   "
              f"{elapsed:>7.2f}s   {peak_bytes / 1e6:>8.1f} MB", flush=True)
        del pairs
    print(f"\n  -> out/explosion.json  ({len(prior['runs'])} run(s))")
    print("  Keep halving the support until it is unbearable. Record where.")


if __name__ == "__main__":
    main()
