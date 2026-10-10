"""Summarise bench runs: python3 -I bench/summary.py [run-id ...]  (default: all in runs/bench/*.jsonl)"""
import json, glob, os, sys, statistics
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs", "bench")
ids = sys.argv[1:] or sorted(os.path.basename(p)[:-6] for p in glob.glob(os.path.join(root, "*.jsonl")))
runs = {}
for r in ids:
    p = os.path.join(root, r + ".jsonl")
    if os.path.exists(p):
        runs[r] = {}
        for l in open(p):
            d = json.loads(l); runs[r][d["task"]] = d       # last row per task wins
tasks = sorted({t for r in runs.values() for t in r})
print(f"{'task':<14}" + "".join(f"{r[:22]:>24}" for r in runs))
for t in tasks:
    row = f"{t:<14}"
    for r in runs:
        d = runs[r].get(t)
        row += f"{('-' if not d else ('PASS' if d['passed'] else 'FAIL') + ' ' + str(d['seconds']) + 's'):>24}"
    print(row)
print("-" * (14 + 24 * len(runs)))
for label, fn in (("passed", lambda ds: f"{sum(d['passed'] for d in ds)}/{len(ds)}"),
                  ("total s", lambda ds: str(sum(d['seconds'] for d in ds))),
                  ("median s", lambda ds: str(int(statistics.median(d['seconds'] for d in ds))) if ds else "-"),
                  ("timeouts", lambda ds: str(sum(d['delegate_rc'] == 2 for d in ds)))):
    print(f"{label:<14}" + "".join(f"{fn(list(runs[r].values())):>24}" for r in runs))
