"""Verify the exact rank-additive caller lane-capacity bound."""
from collections import Counter
from fractions import Fraction as F
import gzip
from hashlib import sha1, sha256
from itertools import combinations, pairwise
import json
from pathlib import Path
import runpy

PACKAGE = Path(__file__).resolve().parent
CALLER = "inputs/CALLER.json.gz"
INVOICE = "inputs/INVOICE-7277.json.gz"


def authenticate(raw, pin):
    blob = f"blob {len(raw)}\0".encode() + raw
    if sha256(raw).hexdigest() != pin["sha256"] or sha1(blob).hexdigest() != pin["git_blob"]:
        raise ValueError("changed pinned source")


def load_sources():
    pins = json.loads((PACKAGE / "PROVENANCE.json").read_bytes())
    assert set(pins) == {CALLER, INVOICE}
    sources = {}
    for name, pin in pins.items():
        raw = gzip.decompress((PACKAGE / name).read_bytes())
        authenticate(raw, pin)
        try:
            authenticate(raw + b"\n", pin)
        except ValueError:
            pass
        else:
            raise AssertionError("changed pinned source accepted")
        sources[name] = json.loads(raw)
    return pins, sources[CALLER], sources[INVOICE]


def common_window_groups(calls):
    # The greatest left endpoint of an overlapping group witnesses that group.
    endpoints = sorted({c["window"][0] for c in calls})
    groups = set()
    for time in endpoints:
        active = [c["clock"] for c in calls if c["window"][0] <= time <= c["window"][1]]
        assert len(active) <= 5
        for arity in range(2, len(active) + 1):
            groups.update(combinations(active, arity))
    return groups


def group_price(group, calls, power):
    ranks = [calls[i]["rank"] for i in group]
    low, high = power(sum(ranks))
    return sum(power(r)[0] for r in ranks) - high, sum(power(r)[1] for r in ranks) - low


def target_margin(invoice, calls, power):
    hist = invoice["price"]["after"]
    paid = Counter({int(r): n for r, n in hist["P"].items()})
    productive = Counter({int(r): n for r, n in hist["T"].items()})
    idle = Counter()
    for call in calls:
        idle[call["rank"]] += call["ports"]
    assert idle <= paid
    assert sum(paid.values()) == 110536 and sum(productive.values()) == 22461
    signed = productive.copy()
    signed.subtract(paid)
    assert sum(r * n for r, n in signed.items()) == hist["S"] == 1424
    return sum(n * power(r)[n >= 0] for r, n in signed.items())


def verify():
    assert __debug__
    pins, caller, invoice = load_sources()
    assert invoice["status"] == "PASS_TERMINAL_CUT_RECHART_CALLER"
    assert invoice["caller_sha256"] == pins[CALLER]["sha256"]
    assert F(invoice["claim"]) == F("0.003645669928698")
    independent = runpy.run_path(str(PACKAGE / "trace_and_price.py"))
    power = independent["power"]
    calls = independent["backward"](caller)
    broad = [c for c in calls if c["op"] == "IDLE_ODD"]
    narrow = sorted((c for c in calls if c["op"] == "IDLE_ONE"), key=lambda c: c["window"])
    assert len(calls) == 94 and len(broad) == 4 and len(narrow) == 90
    assert len({c["role"] for c in broad}) == 4
    assert all(c["window"] == [0, len(caller["events"])] for c in broad)
    assert all(c["rank"] == 9 and c["ports"] == 8 for c in broad)
    assert all(a["window"][1] < b["window"][0] for a, b in pairwise(narrow))

    cert = json.loads((PACKAGE / "CERTIFICATE.json").read_bytes())
    assert F(cert["target"]) == independent["K"]
    by_clock = {c["clock"]: c for c in calls}
    broad_ids = {c["clock"] for c in broad}
    charges = {row["call"]: F(row["charge"]) for row in cert["charges"]}
    assert len(charges) == len(cert["charges"]) == 4 and set(charges) == broad_ids
    assert len(set(charges.values())) == 1 and min(charges.values()) > 0
    assert all(row["ports"] == by_clock[row["call"]]["ports"] for row in cert["charges"])
    group_counts = Counter()
    for group in sorted(common_window_groups(calls)):
        group_counts[len(group)] += 1
        assert broad_ids.intersection(group)
        _, upper = group_price(group, by_clock, power)
        assert upper <= sum(charges.get(i, 0) for i in group)
    assert sum(group_counts.values()) == 1361
    assert {str(k): v for k, v in group_counts.items()} == cert["expected_groups_by_arity"]

    witness = max(narrow, key=lambda call: call["rank"])
    assert witness["rank"] == 64
    extremal_group = (*sorted(broad_ids), witness["clock"])
    witness_low, _ = group_price(extremal_group, by_clock, power)
    # Removing any one equal broad charge violates even a lower saving bound.
    assert sum(charges.values()) - min(charges.values()) < witness_low

    saving = sum(by_clock[i]["ports"] * charge for i, charge in charges.items())
    assert saving == F(cert["saving_upper"])
    margin = target_margin(invoice, calls, power)
    assert saving + margin == F(cert["target_margin_upper"]) < 0
    return {
        "status": "PASS_FIXED_CONTACT_IDLE_LANE_CAPACITY",
        "source_sha256": {name: pin["sha256"] for name, pin in pins.items()},
        "literal_calls": len(calls),
        "broad_calls": sorted(broad_ids),
        "broad_lane_capacity": sum(c["ports"] for c in broad),
        "narrow_disjoint_windows": len(narrow),
        "groups_by_arity": dict(group_counts),
        "groups": sum(group_counts.values()),
        "directed_savings_upper": str(saving),
        "directed_target_margin_upper": str(saving + margin),
        "directed_original_margin_upper": str(margin),
        "controls": ["REJECT_CHANGED_SOURCE", "REJECT_DROPPED_BROAD_LANE_CHARGE"],
        "unresolved": 0,
        "physical_sites": 0,
    }


if __name__ == "__main__":
    result = json.dumps(verify(), sort_keys=True, indent=2) + "\n"
    assert result == (PACKAGE / "AUDIT.json").read_text()
    print(result, end="")
