#!/usr/bin/env python3
"""Week 5 · Task 2 — How long does it take to converge, and on what?

Textbook §5.1, §5.2.

The textbook says PageRank converges. It does not say in how many iterations,
because the answer depends on beta, on the graph, and on what you are willing
to call "converged". Those three knobs are yours to turn, on your machine,
with a graph big enough that you can feel the cost.

    python3 task2_convergence.py --betas 0.5,0.7,0.85,0.95,0.99
    python3 task2_convergence.py --nodes 20000 --betas 0.85,0.95

Your timings are about your hardware. The iteration counts are not - those are
about the mathematics, and everybody should get the same ones.
"""
import argparse, json, os, platform, time

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
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                    r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as key:
                info["processor"] = winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
        except OSError:
            pass
        class MemoryStatus(ctypes.Structure):
            _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong)] + [
                (field, ctypes.c_ulonglong) for field in (
                    "total_physical", "available_physical", "total_pagefile",
                    "available_pagefile", "total_virtual", "available_virtual", "extended")]
        status = MemoryStatus()
        status.length = ctypes.sizeof(status)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            info["ram_bytes"] = status.total_physical
    return info


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--betas", default="0.5,0.7,0.85,0.95,0.99")
    p.add_argument("--nodes", type=int, default=None,
                   help="graph size; default is the harness graph")
    p.add_argument("--tol", type=float, default=1e-10)
    p.add_argument("--max-iter", type=int, default=5000)
    a = p.parse_args()
    os.makedirs(OUT, exist_ok=True)

    import bench
    if a.nodes:
        bench.NODES = a.nodes
    graph = bench.build()
    edges = sum(len(outs) for outs in graph.values())

    from task1_pagerank import pagerank

    rows = []
    for beta in [float(x) for x in a.betas.split(",")]:
        t0 = time.perf_counter()
        ranks = pagerank(graph, beta=beta, iterations=a.max_iter, tol=a.tol)
        elapsed = time.perf_counter() - t0
        iters = getattr(pagerank, "iterations", None)
        top = sorted(ranks.items(), key=lambda kv: -kv[1])[:10]
        rows.append({"beta": beta, "nodes": len(graph), "edges": edges,
                     "seed": bench.SEED, "tol": a.tol,
                     "iterations": iters, "seconds": elapsed,
                     "max_iter": a.max_iter, "l1_delta": pagerank.delta,
                     "converged": pagerank.delta < a.tol,
                     "top10": [k for k, _ in top]})
        print(f"  beta {beta:<5}  {str(iters):>4} iterations  {elapsed:>7.3f}s   "
              f"top: {', '.join(k for k, _ in top[:3])}")

    path = os.path.join(OUT, "convergence.json")
    prior = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {"runs": []}
    prior["machine"] = machine()
    prior["runs"].extend(rows)
    with open(path, "w", encoding="utf-8") as stream:
        json.dump(prior, stream, indent=2, ensure_ascii=False)
    print(f"\n  -> out/convergence.json  ({len(prior['runs'])} run(s))")


if __name__ == "__main__":
    main()
