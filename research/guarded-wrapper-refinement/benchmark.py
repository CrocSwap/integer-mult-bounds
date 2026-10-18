#!/usr/bin/env python3
"""Same-input Python semantic timing; not the fast physical C implementation."""
import argparse
from hashlib import sha256
import json
import platform
from pathlib import Path
from statistics import median
import sys
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify import collector_inputs, digest, executor_class, need
import frozen


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    need(args.runs >= 1, "positive repeat count")
    old = frozen.load()
    new = executor_class(old)
    recipe = old.SOURCE["recipes"][0]
    rows = []
    for sources, query, grid, beta in collector_inputs():
        times = {"baseline": [], "refined": []}
        answers = {}
        # Warm both; alternate order to reduce systematic order bias.
        for repeat in range(args.runs + 1):
            order = [("baseline", old.Executor), ("refined", new)]
            if repeat % 2:
                order.reverse()
            for name, constructor in order:
                executor = constructor(9, 512, d=2, spacing=1, suffix=0, outer=3)
                start = perf_counter()
                result = old.collector(executor, sources, query, grid, beta, recipe)
                elapsed = perf_counter() - start
                answers[name] = digest(result)
                if repeat:
                    times[name].append(elapsed)
            need(answers["baseline"] == answers["refined"], "same-input benchmark output")
        medians = {name: median(samples) for name, samples in times.items()}
        rows.append(dict(input_sha256=digest([sources, query, grid, beta]), output_sha256=answers["baseline"],
                         samples_seconds=times, medians_seconds=medians,
                         median_ratio=medians["baseline"] / medians["refined"]))
    result = dict(scope="Python semantic reference, complete N=512 collectors; no fast physical runtime claim",
                  python=sys.version, platform=platform.platform(), processor=platform.processor(),
                  source_sha256={name: sha256((Path(__file__).resolve().parent / name).read_bytes()).hexdigest()
                                 for name in ("direct.py", "frozen.py", "verify.py", "benchmark.py", "inputs/pr3131.tar")},
                  runs=args.runs, warmups_per_implementation=1, width=512,
                  backend_plan=dict(d=2, spacing=1, suffix=0, outer=3), cases=rows)
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded)
    print(encoded)


if __name__ == "__main__":
    main()
