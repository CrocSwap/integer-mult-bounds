#!/usr/bin/env python3
"""Prefix packing of the selected owner slices.

The checker recounts the pinned ledger. It does not replay phase events.
"""

import gzip
import hashlib
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_OWNER_SLICE_LEDGER rows=69120 width=537120 no_new_kappa"
OWNERS = "research/complex-t16-rare-pattern-exchanges/data/OWNERS.json.gz"
PLAN = "research/complex-t16-rare-pattern-exchanges/data/PLAN.json"
INDEPENDENT = "research/community-frontier1094-audit/INDEPENDENT1094.json"


def fail(message):
    raise SystemExit("FAIL_OWNER_SLICE_LEDGER " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def ledger():
    owners = json.loads(gzip.decompress((ROOT / OWNERS).read_bytes()))
    plan = json.loads((ROOT / PLAN).read_text(encoding="utf-8"))
    require(len(owners) == 69120, "the role count moved")
    groups = defaultdict(list)
    by_call = defaultdict(set)
    for row in owners:
        owner, child, port = row["owner_replica"], row["child"], row["port"]
        time = row["time"]
        require(0 <= port < 112 and 0 <= owner < 16, "an owner coordinate moved")
        require(0 <= time < 144 and plan["order"][time] == [row["stage"], row["replica"]], "a call identity moved")
        require(row["helper"] not in by_call[time], "a helper was repeated in one call")
        by_call[time].add(row["helper"])
        rank, eligible = plan["windows"][f"{owner},{child}"]
        require(time in eligible, "a slice left its window")
        require(row["width"] > 0 and row["offset"] >= 0 and row["offset"] + row["width"] <= rank, "a slice left its bin")
        family = owner * 896 + (2 * plan["pairs"][str(child)] + plan["sides"][str(child)]) * 112 + port
        require(row["family"] == family, "a family index moved")
        groups[owner, child, port].append(row)
    require(set(by_call) == set(range(144)), "a call is missing")
    require(all(helpers == set(range(480)) for helpers in by_call.values()), "a call lost a helper")
    capacities = Counter(rank for rank, _ in plan["windows"].values())
    capacities = {rank: count * 112 for rank, count in capacities.items()}
    require(capacities == {8: 10752, 16: 7168, 32: 7168, 48: 7168}, "the bin inventory moved")
    capacity = sum(rank * count for rank, count in capacities.items())
    width = sum(row["width"] for row in owners)
    require((capacity, width) == (774144, 537120), "the capacity mass moved")
    idle = Counter()
    for label, (rank, _) in plan["windows"].items():
        owner, child = map(int, label.split(","))
        for port in range(112):
            rows = sorted(groups[owner, child, port], key=lambda item: item["offset"])
            used = 0
            for row in rows:
                require(row["offset"] == used, "a slice left a gap")
                used += row["width"]
            require(used <= rank, "a bin overflowed")
            if rank > used:
                idle[rank - used] += 1
    shared = sum(1 for rows in groups.values() if len({row["time"] for row in rows}) > 1)
    witness = sorted(groups[0, 6, 85], key=lambda item: item["offset"])
    require([(row["time"], row["offset"], row["width"]) for row in witness] == [(9, 0, 9), (11, 9, 4), (13, 13, 9), (15, 22, 9)], "the witness slices moved")
    return dict(idle), shared, sum(row["width"] for row in witness)


def evaluate():
    require(sha256(ROOT / INDEPENDENT) == "301fb8a0e4ab7e3c383ff974c54c08178283b2a3453c5282757f692a3c7a4bfd", "independent drift")
    require(sha256(ROOT / OWNERS) == "87902c528dfab7d503dcf8a784260e3ab6fb7424c418a1820f7261f25be7b6bc", "owner drift")
    require(sha256(ROOT / PLAN) == "7bd786ba8e66408f02aa9ef446eaf20c1bfe981ea2e4dd1e5a929f0aa7767bc0", "plan drift")
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    independent = json.loads((ROOT / INDEPENDENT).read_text(encoding="utf-8"))
    idle, shared, witness_width = ledger()
    require(idle == {int(rank): count for rank, count in independent["owner"]["idle"].items()}, "the unused suffixes left the selected idle histogram")
    require(shared == 17217 and witness_width == 31, "the shared-bin count moved")
    return {
        "roles": 69120,
        "helpers_per_call": 480,
        "capacity": 774144,
        "allocated_width": 537120,
        "shared_bins": 17217,
        "witness_width": 31,
        "witness_remainder": 1,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
