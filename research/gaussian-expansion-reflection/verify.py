"""Check the new reflection substitution and run the unchanged complete caller."""
import argparse
import ast
from dataclasses import FrozenInstanceError
from fractions import Fraction
import hashlib
import json
from math import isqrt
from pathlib import Path
import statistics
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
from adapter import (complete_replay, reflected_expansion, replace_expansion,
                     require, runtime)
from benchmark import bindings


def signature(matrix):
    return [[(x.lo, x.hi, x.bits) for x in row] for row in matrix]


def literal_expansion(module, s, t, alpha, bits, radius):
    matrix = module.zeros(t, s, bits)
    pi = module.pi_interval(bits)
    for k in range(t):
        center = Fraction(s * k, t)
        start = center.numerator // center.denominator - radius
        stop = module.ceildiv(center.numerator, center.denominator) + radius
        for j in range(start, stop + 1):
            exponent = (Fraction(j) - center) ** 2 / alpha ** 2
            matrix[k][j % s] += module.exp_negative(pi * exponent) / (2 * alpha)
        matrix[k] = [module.Interval(x.lo, x.hi + 1, bits) for x in matrix[k]]
    return matrix


def geometry_checks():
    pairs = terms = 0
    for s in range(2, 17):
        for t in range(s + 1, 25):
            for radius in (1, 2, 7):
                for k in range(t // 2 + 1, t):
                    a, b = Fraction(s * k, t), Fraction(s * (t - k), t)
                    lower = a.numerator // a.denominator - radius
                    upper = -((-a.numerator) // a.denominator) + radius
                    low_b = b.numerator // b.denominator - radius
                    high_b = -((-b.numerator) // b.denominator) + radius
                    require((s - upper, s - lower) == (low_b, high_b),
                            "exact reflected truncation endpoints")
                    for j in range(lower, upper + 1):
                        require((j - a) ** 2 == (s - j - b) ** 2,
                                "identical exact exponential argument")
                        require((s - j) % s == (-j) % s,
                                "correct cyclic reflection slot")
                        terms += 1
                    pairs += 1
    return {"reflected_row_pairs": pairs, "exact_term_bijections": terms}


def interval_checks():
    fixtures = ((3, 4, 2, 48), (5, 8, 2, 48), (7, 16, 3, 64),
                (5, 9, 2, 48), (6, 10, 3, 64))
    entries = saved = 0
    with runtime("baseline") as (modules, _, _):
        module = modules["gaussian"]
        for s, t, alpha, bits in fixtures:
            radius = alpha * (isqrt(bits + 16) + 2)
            expected = literal_expansion(module, s, t, alpha, bits, radius)
            counts = dict.fromkeys(("expansion_terms", "computed_rows",
                                   "reflected_rows", "constructors"), 0)
            actual = reflected_expansion(module, counts, s, t, alpha, bits, radius)
            require(signature(actual) == signature(expected), "all interval endpoints identical")
            require(len({id(row) for row in actual}) == t, "distinct mutable row lists")
            entries += s * t
            saved += counts["reflected_rows"]
        wanted = signature(expected)
        mutations = [list(row) for row in wanted]
        mutations[-1] = list(wanted[1])
        require(mutations != wanted, "omitting cyclic coordinate reversal is detected")
        mutations = [list(row) for row in wanted]
        mutations[-1] = list(wanted[2])
        require(mutations != wanted, "wrong partner row is detected")
        mutations = [list(row) for row in wanted]
        lo, hi, bits = mutations[-1][0]
        mutations[-1][0] = (lo, hi - 1, bits)
        require(mutations != wanted, "omitted outward tail unit is detected")
        try:
            actual[-1][0].lo = 0
        except FrozenInstanceError:
            pass
        else:
            raise ValueError("reused interval objects must be immutable")
    return {"fixtures": len(fixtures), "identical_entries": entries,
            "reflected_rows": saved, "semantic_controls": 4}


def rejected_controls():
    controls = 0
    for source in ("x = 1", "class GaussianLine: pass", "class GaussianLine:\n def __init__(self): pass"):
        try:
            replace_expansion(ast.parse(source))
        except ValueError:
            controls += 1
        else:
            raise ValueError("changed source layout accepted")
    try:
        with runtime("unknown"):
            raise RuntimeError("unreachable")
    except ValueError:
        controls += 1
    return controls


def measured_evidence():
    report = json.loads((PACKAGE / "BENCHMARK.json").read_text())
    require(report["bindings"] == bindings(), "benchmark executable/source bindings")
    require(report["errors"] == 0 and len(report["records"]) == 10, "ten successful timed replays")
    require(len({r["stdout_sha256"] for r in report["records"]}) == 1, "timed scientific output")
    for index, row in enumerate(report["records"]):
        require(row["mode"] == ("baseline", "reflected")[index % 2]
                and row["returncode"] == 0 and row["seconds"] > 0, "alternating completed samples")
    for mode in ("baseline", "reflected"):
        selected = [r for r in report["records"] if r["mode"] == mode]
        times = [r["seconds"] for r in selected]
        summary = report["summary"][mode]
        require(summary["median_seconds"] == statistics.median(times)
                and summary["minimum_seconds"] == min(times)
                and summary["maximum_seconds"] == max(times), "recomputed measurement summary")
        require(all(r["counts"] == summary["counts"] for r in selected), "deterministic measured work")
    expected = 100 * (1 - report["summary"]["reflected"]["median_seconds"] /
                      report["summary"]["baseline"]["median_seconds"])
    require(report["summary"]["reduction_percent"] == expected, "derived percentage")
    return report["summary"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-unmeasured", action="store_true")
    args = parser.parse_args()
    geometry = geometry_checks()
    intervals = interval_checks()
    controls = rejected_controls()
    baseline, before = complete_replay("baseline")
    reflected, after = complete_replay("reflected")
    require(baseline == reflected, "complete scientific stdout unchanged")
    require(before["exp_negative_calls"] > after["exp_negative_calls"], "strict exact work reduction")
    require(after["constructors"] == 8 and after["reflected_rows"] == 60,
            "all eight completed setup paths used the replacement")
    summary = None if args.allow_unmeasured else measured_evidence()
    files = ("adapter.py", "run.py", "verify.py", "benchmark.py", "SOURCES.json", "VERIFY.json")
    receipt = {"status": "PASS_GAUSSIAN_EXPANSION_REFLECTION", "geometry": geometry,
               "intervals": intervals, "source_layout_controls": controls,
               "before": before, "after": after, "complete_products_per_side": 289,
               "stdout_sha256": hashlib.sha256(baseline.encode()).hexdigest(),
               "bindings": {p: hashlib.sha256((PACKAGE / p).read_bytes()).hexdigest() for p in files},
               "measurement": summary}
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
