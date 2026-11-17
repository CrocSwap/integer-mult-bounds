#!/usr/bin/env python3
"""Check exact aggregation certificates, not the cited projector lemmas."""

import argparse
import hashlib
import itertools
import json
import math
from collections import Counter
from fractions import Fraction as F
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
MAX_BYTES = 65536
SCIENTIFIC_FILES = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_bytes(path):
    with path.open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    require(len(data) <= MAX_BYTES, f"oversized input: {path}")
    return data


def digest(path):
    return hashlib.sha256(read_bytes(path)).hexdigest()


def source_hashes():
    sources = json.loads(read_bytes(PACKAGE / "SOURCES.json"))
    require(len(sources["files"]) == 6, "unexpected source inventory")
    result = {}
    for row in sources["files"]:
        if row["usage"] == "input":
            name = row["path"]
            require(name.startswith("research/") and ".." not in name, "source path")
            result[name] = digest(ROOT / name)
            require(result[name] == row["sha256"], f"source mismatch: {name}")
    require(len(result) == 2, "expected two cited proof inputs")
    return result


def rank_rows(n, sites):
    """Rows mean coefficient dot (rank(P_i)/q) >= rhs."""
    require(n in range(4, 13, 2), "finite fixture dimension outside declared bound")
    require(len(sites) == 5 and tuple(sorted(set(sites))) == sites, "five distinct sites")
    require(all(0 <= i <= n for i in sites), "site out of range")
    rows = {}
    for i in sites:
        rows[f"floor:{i}"] = ({i: 1}, 2)
        if 0 < i < n and i % 2 == 0:
            rows[f"even:{i}"] = ({i: 1}, 4)
    for size, floor in ((3, 7), (4, 10)):
        for subset in itertools.combinations(sites, size):
            rows["subset:" + ",".join(map(str, subset))] = (dict.fromkeys(subset, 1), floor)
    odds = [i for i in sites if 0 < i < n and i % 2]
    for i in odds:
        for j in odds:
            if i != j:
                rows[f"odd:{i}:{j}"] = ({i: 2, j: 1}, 8)
        for endpoint in (0, n):
            far = (endpoint == 0 and i >= 3) or (endpoint == n and i <= n - 3)
            if endpoint in sites and far:
                rows[f"far:{i}:{endpoint}"] = ({i: 2, endpoint: 1}, 8)
    return rows


def certificate(n, sites):
    evens = [i for i in sites if 0 < i < n and i % 2 == 0]
    if evens:
        i = evens[0]
        rest = ",".join(str(j) for j in sites if j != i)
        return {f"even:{i}": F(1), f"subset:{rest}": F(1)}, F(14), "even"
    odds = [i for i in sites if 0 < i < n and i % 2]
    ends = [i for i in sites if i in (0, n)]
    if not ends:
        weights = {f"odd:{i}:{j}": F(1, 12) for i in odds for j in odds if i != j}
        return weights, F(40, 3), "zero-endpoints"
    if len(ends) == 1:
        endpoint = ends[0]
        near = 1 if endpoint == 0 else n - 1
        a = near if near in odds else odds[0]
        far = [i for i in odds if i != a]
        weights = {f"odd:{a}:{i}": F(1, 9) for i in far}
        weights.update({f"odd:{i}:{a}": F(1, 9) for i in far})
        weights.update({f"far:{i}:{endpoint}": F(1, 3) for i in far})
        return weights, F(40, 3), "one-endpoint"
    a, b, c = odds
    weights = {f"far:{a}:{n}": F(1, 2), f"far:{c}:0": F(1, 2),
               f"far:{b}:0": F(1, 4), f"far:{b}:{n}": F(1, 4),
               "floor:0": F(1, 4), f"floor:{n}": F(1, 4)}
    return weights, F(13), "two-endpoints"


def check_dual(rows, sites, weights, target):
    require(len(weights) <= 20, "certificate too large")
    coefficients = dict.fromkeys(sites, F(0))
    rhs = F(0)
    for name, weight in weights.items():
        require(name in rows, f"uncited or inapplicable inequality: {name}")
        require(weight >= 0, "negative dual weight")
        row, bound = rows[name]
        for site, coefficient in row.items():
            coefficients[site] += weight * coefficient
        rhs += weight * bound
    require(all(0 <= x <= 1 for x in coefficients.values()), "overweight rank variable")
    require(rhs >= target, "overstated lower bound")
    return rhs, coefficients


def check_primal(rows, sites, ranks, target):
    require(set(ranks) == set(sites), "primal site inventory")
    require(all(x >= 0 for x in ranks.values()), "negative rank")
    for row, bound in rows.values():
        require(sum(coefficient * ranks[i] for i, coefficient in row.items()) >= bound,
                "primal violates a cited rank inequality")
    require(sum(ranks.values()) == target, "wrong primal objective")


def must_reject(kind, *args):
    try:
        if kind == "dual":
            check_dual(*args)
        elif kind == "primal":
            check_primal(*args)
        else:
            raise RuntimeError("unknown rejection-control kind")
    except ValueError:
        return
    raise ValueError("a false-certificate control was accepted")


def controls():
    sites = (0, 1, 3, 5, 6)
    rows = rank_rows(6, sites)
    weights, target, _ = certificate(6, sites)
    bad = dict(weights)
    bad["floor:0"] = F(-1)
    must_reject("dual", rows, sites, bad, target)
    bad = {name: 2 * weight for name, weight in weights.items()}
    must_reject("dual", rows, sites, bad, target)
    bad = dict(weights)
    bad["far:1:0"] = F(1, 4)
    must_reject("dual", rows, sites, bad, target)
    must_reject("dual", rows, sites, weights, target + F(1, 100))
    bad_rows = dict(rows)
    bad_rows["far:1:6"] = ({1: 2, 6: 1}, 7)
    must_reject("dual", bad_rows, sites, weights, target)
    bad_ranks = {0: F(2), 1: F(2), 3: F(3), 5: F(3), 6: F(2)}
    must_reject("primal", rows, sites, bad_ranks, F(12))
    return 6


def finite_checks():
    counts = Counter()
    primal_count = 0
    for n in range(4, 13, 2):
        for sites in itertools.combinations(range(n + 1), 5):
            rows = rank_rows(n, sites)
            weights, target, kind = certificate(n, sites)
            rhs, coefficients = check_dual(rows, sites, weights, target)
            require(rhs == target and all(x == 1 for x in coefficients.values()),
                    "certificate must give the displayed exact sum")
            require(target >= 13, "uncovered five-stage placement")
            counts[kind] += 1
            if kind != "even":
                ranks = {i: F(2 if i in (0, n) else 3) for i in sites}
                if kind != "two-endpoints":
                    ranks = dict.fromkeys(sites, F(8, 3))
                check_primal(rows, sites, ranks, target)
                primal_count += 1
    require(sum(counts.values()) == sum(math.comb(n + 1, 5) for n in range(4, 13, 2)),
            "placement coverage")
    return dict(sorted(counts.items())), primal_count


def make_result():
    inputs = source_hashes()
    counts, primals = finite_checks()
    return {"claim_type": "scoped-proof", "uniform_rank_lower_bound": "13q",
            "attainment": "unresolved; relaxation witnesses are not projectors",
            "finite_dimensions": list(range(4, 13, 2)), "placement_counts": counts,
            "relaxation_primal_checks": primals, "rejection_controls": controls(),
            "source_sha256": inputs,
            "package_sha256": {name: digest(PACKAGE / name) for name in SCIENTIFIC_FILES}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = make_result()
    path = PACKAGE / "RESULT.json"
    if args.write_result:
        serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
        require(path.write_text(serialized, encoding="utf-8") == len(serialized), "short receipt write")
    else:
        require(json.loads(read_bytes(path)) == result, "receipt mismatch")
    print("PASS_FIVE_STAGE_RANK_BUDGET", json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
