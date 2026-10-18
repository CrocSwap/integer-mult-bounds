#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent finite audit of PR3148's literal allocation and packing cap."""

import argparse
import gzip
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

# -I excludes the script directory. Import only this resolved package, not cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from arithmetic import check_dual, check_primal, child_intervals, moment, require
from geometry import audit, journal_edits

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
ALLOC = ROOT / "research/rank7-joint-endframes/allocation"
LOCAL = {1: 2433, 2: 724, 3: 228, 4: 102, 5: 20, 8: 8}
INVENTORY = {4: 26, 5: 2, 6: 18, 7: 50, 8: 99, 9: 213}
EXPECTED_IDLE = {1: 173160, 3: 48951, 5: 13875, 48: 282569}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read(path):
    require(not path.is_symlink() and path.stat().st_size <= 2_000_000,
            "bounded regular JSON input")
    raw = path.read_bytes()
    if path.suffix == ".gz":
        with gzip.open(path, "rb") as stream:
            raw = stream.read(32_000_001)
        require(len(raw) <= 32_000_000, "bounded decompressed JSON")
    return json.loads(raw, object_pairs_hook=unique_object)


def authenticate():
    sources = read(PACKAGE / "SOURCES.json")
    for row in sources["files"]:
        if row["usage"] == "input":
            path = ROOT / row["path"]
            require(not path.is_symlink(), "regular pinned input")
            require(hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"],
                    "source bytes: " + row["path"])


def check_providers(providers):
    require(set(providers) == {"gauge44", "extra"}, "two named providers")
    for provider in providers.values():
        widths = provider["widths"]
        require(len(widths) == 408 and all(type(w) is int for w in widths),
                "literal ordered width array")
        require(dict(Counter(widths)) == INVENTORY, "provider width inventory")
        require({int(r): n for r, n in provider["actual_paid_profile"].items()}
                == LOCAL, "inherited per-call paid profile")


def allocation_result():
    base = read(PACKAGE / "vendor/FILL.json.gz")["rows"]
    journal = read(PACKAGE / "vendor/EXCHANGE.json")
    require(journal["base_head"] == "51eb9c4ee9e4722010d308aa3309e039d3940cc2",
            "journal base head")
    require(journal["base_fill_sha256"] == hashlib.sha256(
        (PACKAGE / "vendor/FILL.json.gz").read_bytes()).hexdigest(), "journal base fill")
    providers = read(PACKAGE / "vendor/PROVIDERS.json")
    check_providers(providers)
    args = (base, read(ALLOC / "ORDER.json"), read(ALLOC / "DISPATCH.json"),
            providers, read(ALLOC / "vendor/PLAN.json.gz"),
            read(ALLOC / "vendor/TEMPLATE.json.gz"))
    edits = journal_edits(base, journal)
    baseline_idle, _ = audit(*args, 1, {})
    idle, patterns = audit(*args, 10, edits)
    require(dict(idle) == EXPECTED_IDLE, "complete attained idle profile")
    delta = {r: idle[r] - 10 * baseline_idle[r]
             for r in set(idle) | set(baseline_idle)
             if idle[r] != 10 * baseline_idle[r]}
    require(delta == {1: 20, 3: 21, 5: -25, 39: -10, 48: 9},
            "allocation exchange delta")
    profile = Counter({r: 6660 * n for r, n in LOCAL.items()})
    profile.update(idle)
    require(sum(r * n for r, n in profile.items()) == 65088 * 740,
            "complete rank mass")
    baseline_profile = Counter({r: 666 * n for r, n in LOCAL.items()})
    baseline_profile.update(baseline_idle)
    require(sum(r * n for r, n in baseline_profile.items()) == 65088 * 74,
            "complete baseline rank mass")
    return profile, baseline_profile, idle, patterns, delta


def cap_result(profile, baseline_profile, idle, patterns):
    cert = read(PACKAGE / "vendor/CAP.json")
    all_patterns, basis, amounts, rhs = check_primal(cert, INVENTORY, LOCAL)
    primal_idle = Counter()
    for (_, _, rank), count in zip(basis, amounts, strict=True):
        if rank:
            primal_idle[rank] += count
    require({int(r): Fraction(n) for r, n in cert["idle_per_replica"].items()}
            == primal_idle, "serialized primal idle")
    require(all(idle[r] == 740 * primal_idle[r]
                for r in set(idle) | set(primal_idle)), "literal equals primal moment")
    lower, upper = Fraction(cert["cap_lower"]), Fraction(cert["cap_upper"])
    require(0 < lower < upper < Fraction(1, 100) and
            upper - lower == Fraction(1, 10**25), "stated cap root bracket")
    below = moment(profile, lower, 740)
    above = moment(profile, upper, 740)
    require(below[1] < 1 < above[0], "independent square-root root enclosure")
    tight, margin = check_dual(all_patterns, basis, rhs, child_intervals(lower, upper))
    require(set(patterns) <= set(tight), "every literal bin is dual-tight")
    for capacity, per_replica in zip((8, 16, 32, 48), (672, 448, 448, 448), strict=True):
        require(sum(n for (c, _), n in patterns.items() if c == capacity)
                == 740 * per_replica, "literal capacity counts match relaxation")
    headline = Fraction((lower * 10**24).__floor__(), 10**24)
    headline -= Fraction(1, 10**46) + Fraction(1, 10**70)
    previous = Fraction(read(PACKAGE / "vendor/BASELINE.json")["kappa"])
    require(headline > previous, "strict reported endpoint comparison")
    baseline_lower = Fraction((previous * 10**25).__floor__(), 10**25)
    baseline_upper = baseline_lower + Fraction(1, 10**25)
    require(moment(baseline_profile, baseline_lower, 74)[1] < 1 <
            moment(baseline_profile, baseline_upper, 74)[0],
            "independent literal T74 baseline root enclosure")
    require(lower > baseline_upper, "strict allocation-only moment gain")
    return {"root": [str(lower), str(upper)],
            "baseline_root": [str(baseline_lower), str(baseline_upper)],
            "root_gain_interval": [str(lower - baseline_upper),
                                   str(upper - baseline_lower)],
            "strict_patterns": 2539,
            "tight_patterns": 12, "minimum_reduced_cost_lower": str(margin),
            "moment_below_upper": str(below[1]), "moment_above_lower": str(above[0]),
            "reported_claim": str(headline), "reported_gain": str(headline - previous),
            "necessary_replica_divisor": 20}


def verify():
    authenticate()
    profile, baseline_profile, idle, patterns, delta = allocation_result()
    cap = cap_result(profile, baseline_profile, idle, patterns)
    return {"status": "PASS_INDEPENDENT_COUPLED_CAP", "source_head":
            "f2927a4b8afcf0701a6b945e14f30de1d94f5176", "roles": 2717280,
            "calls": 6660, "bins": 740 * 18 * 112, "journal_edits": 145,
            "profile": dict(sorted(profile.items())), "idle": dict(sorted(idle.items())),
            "idle_delta": dict(sorted(delta.items())), "cap": cap,
            "physical_families": 896 * 740 + 408 + 8 + 91 + 2,
            "patterns": [[c, list(ns), n] for (c, ns), n in sorted(patterns.items())],
            "scope": "Independent allocation and pattern moment only; supplied local "
                     "profile/ordered widths inherited, native/outer/all-size unverified."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="emit receipt without writing")
    args = parser.parse_args()
    result = verify()
    encoded = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.emit:
        print(encoded, end="")
    else:
        require(json.loads(encoded) == read(PACKAGE / "RESULT.json"),
                "complete regenerated result")
        print(result["status"], "roles=2717280 patterns=2551 tight=12")


if __name__ == "__main__":
    main()
