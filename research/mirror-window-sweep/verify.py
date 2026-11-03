#!/usr/bin/env python3
"""Check the new sweep against the complete direct window definition."""

import hashlib
import itertools
import json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

from windows import checked, mirror_windows

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def direct(targets, paid, stats=None):
    """zxv PR4483's direct pair/cell definition, with an observable counter.

    The funding guard is written directly instead of importing its interval
    library. No predecessor compiler, native or arithmetic suite is run.
    """
    checked(targets)
    checked(paid)
    cuts = sorted({Q(0), *(Q(1, k) for k in targets), *(Q(1, r) for r in paid)})
    cells, visits = [], 0
    for left, right in zip(cuts, cuts[1:]):
        x = (left + right)/2
        exits, sources = Counter(), Counter()
        for r, count in paid.items():
            for k, weight in targets.items():
                visits += 1
                if r > k and Q(1, r) < x <= Q(1, k):
                    exits[r*k] += count*weight
                if k > r and Q(1, k) < x <= Q(1, r):
                    sources[r*k] += count*weight
        if exits:
            if not sources:
                raise ValueError("boundary mirror window without source funding")
            cells.append((left, right, exits, sources))
    if stats is not None:
        stats.update(pair_classifications=visits, elementary_cells=len(cuts)-1,
                     emitted_cells=len(cells))
    return cells


def compare(targets, paid):
    old_error = new_error = None
    try:
        old = direct(targets, paid)
    except ValueError as error:
        old_error = str(error)
    try:
        new = mirror_windows(targets, paid)
    except ValueError as error:
        new_error = str(error)
    require(old_error == new_error, "funding/input rejection disagreement")
    if old_error is not None:
        return "rejected"
    require(old == new, "full cell/histogram disagreement")
    return "accepted"


def exhaustive():
    histograms = [{k+1: v for k, v in enumerate(values) if v}
                  for values in itertools.product(range(3), repeat=4) if any(values)]
    results = Counter()
    for targets in histograms:
        for paid in histograms:
            results[compare(targets, paid)] += 1
    require(sum(results.values()) == 6400, "complete histogram-pair coverage")
    return dict(results)


def canonical(cells):
    return [[str(left), str(right), sorted(exits.items()), sorted(sources.items())]
            for left, right, exits, sources in cells]


def retained_profiles():
    paths = ["research/higher-moment-strictification/RESULT.json",
             "research/compact-joint-compiler/arithmetic/RESULT.json"]
    results = {}
    for name, path in zip(("p7", "p16"), paths):
        raw = json.loads((ROOT/path).read_text())
        raw = raw["invoice_oracle"] if name == "p7" else raw
        targets = {int(k): v for k, v in raw["targets"].items()}
        paid = {int(k): v for k, v in raw["paid"].items()}
        old_stats, new_stats = {}, {}
        old = direct(targets, paid, old_stats)
        new = mirror_windows(targets, paid, new_stats)
        require(old == new, "retained full-output conformance: " + name)
        require(new_stats["pair_classifications"] < old_stats["pair_classifications"],
                "strict classification reduction")
        payload = json.dumps(canonical(new), separators=(",", ":")).encode()
        results[name] = {"direct": old_stats, "sweep": new_stats,
                         "complete_histograms_sha256": hashlib.sha256(payload).hexdigest()}
    return results


def boundary_controls():
    targets, paid = {2: 3, 4: 5}, {1: 7, 3: 11}
    before = (dict(targets), dict(paid))
    cells = mirror_windows(targets, paid)
    require(cells == [(Q(1, 3), Q(1, 2), Counter({6: 33}),
                       Counter({4: 35}))], "literal half-open fixture")
    require((targets, paid) == before, "input mutation")
    require(mirror_windows({2: 1}, {2: 1}) == [], "equal-rank contribution")
    require(compare({2: 1}, {3: 1}) == "rejected", "unfunded exit accepted")
    many = mirror_windows({2: 1, 4: 1, 6: 1}, {1: 1, 3: 1, 5: 1})
    saved = canonical(many)
    require(len(many) >= 2, "ownership fixture")
    many[0][2][999] = 1
    require(canonical(many)[1:] == saved[1:], "shared histogram snapshot")
    require(canonical(mirror_windows({2: 1, 4: 1, 6: 1}, {1: 1, 3: 1, 5: 1}))
            == saved, "cross-call state leakage")
    for invalid in ({}, {0: 1}, {2: -1}, {True: 1}, {2: True}, {2: 1.5}):
        require(compare(invalid, {1: 1}) == "rejected", "invalid input accepted")
    # A product collision must add multiplicities instead of deduplicating.
    require(compare({2: 7, 3: 11, 6: 13}, {1: 17, 2: 19, 3: 23}) == "accepted",
            "colliding product ranks")
    stats = {}
    require(mirror_windows({k: 1 for k in range(2, 66)}, {1: 1}, stats) == []
            and stats["pair_classifications"] == 64, "maximum support")
    require(compare({k: 1 for k in range(2, 67)}, {1: 1}) == "rejected", "support overflow")
    require(compare({10**12: 10**12}, {1: 1}) == "accepted", "maximum integer")
    require(compare({10**12+1: 1}, {1: 1}) == "rejected", "rank overflow")
    require(compare({2: 10**12+1}, {1: 1}) == "rejected", "count overflow")
    try:
        mirror_windows({2: 1}, {1: 1}, [])
    except ValueError:
        pass
    else:
        raise ValueError("invalid stats accepted")
    return 20


def authenticate():
    manifest = json.loads((PACKAGE/"SOURCES.json").read_text())
    hashes = {}
    for row in manifest["files"]:
        if row["usage"] == "input":
            digest = hashlib.sha256((ROOT/row["path"]).read_bytes()).hexdigest()
            require(digest == row["sha256"], "source hash: " + row["path"])
            hashes[row["path"]] = digest
    return hashes


def main():
    hashes = authenticate()
    coverage = exhaustive()
    profiles = retained_profiles()
    controls = boundary_controls()
    own_hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in sorted(PACKAGE.iterdir()) if p.is_file()}
    print(json.dumps({"claim_type": "scoped algorithmic equivalence and exact operation counts",
                      "exhaustive_histogram_pairs": coverage, "retained_profiles": profiles,
                      "controls": controls, "source_sha256": hashes,
                      "package_sha256": own_hashes}, sort_keys=True))
    print("PASS_MIRROR_WINDOW_SWEEP")


if __name__ == "__main__":
    main()
