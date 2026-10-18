#!/usr/bin/env python3
"""Replay and compare two code-disjoint exact prescribed-triple certificates.

Copyright 2026 woklerx. Apache-2.0. Substantial OpenAI Codex assistance.
"""
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def main():
    subprocess.run([sys.executable, "-B", str(HERE / "verify.py")], check=True)
    subprocess.run([sys.executable, "-B", str(HERE / "independent_check.py"),
                    "--check", str(HERE / "independent-results.json")], check=True)
    primary = json.loads((HERE / "CERTIFICATE.json").read_text(encoding="utf-8"))
    independent = json.loads((HERE / "independent-results.json").read_text(encoding="utf-8"))
    by_p = {case["p"]: case for case in primary["cases"]}
    for case in independent["results"]:
        main_case = by_p[case["p"]]
        histogram = Counter()
        for orbit in main_case["orbits"]:
            cost = orbit["minimum_deletions"]
            histogram["impossible" if cost is None else str(cost)] += orbit["multiplicity"]
        if dict(histogram) != case["minimum_deletion_histogram"]:
            raise ValueError(f"independent cost histogram mismatch at p={case['p']}")
        if main_case["triples_checked"] != case["labelled_triples_covered"]:
            raise ValueError("independent domain coverage mismatch")
    print("PASS_PRESCRIBED_TRIPLE_PACKAGE"
          f" partition_triples={sum(c['triples_checked'] for c in primary['cases'])}"
          f" independent_triples={sum(c['labelled_triples_covered'] for c in independent['results'])}"
          " no_new_kappa")


if __name__ == "__main__":
    main()
