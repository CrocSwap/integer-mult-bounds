"""Price-only quote and sealed affected-pivot stock for chart 1089."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parent / "inputs"
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
PINS = {
    "ADMITTED.json": "c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13",
    "RANK-STOCK.json": "4a7841699dd17688f6aada5c902a2a91e94558b2b1b4460c46b0e55aa95b3f9f",
    "pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "IDENTITIES.json": "f4d3f6ca2d87f8cd68c01ac9f77b69bd5a796f92bd567cea8afe3ac7c72e8e4b",
    "OCCUPANCY.json": "4c349e06b22bfebb431fab1c9ae04f0e798f398acc6fdd99591b49b1c95ef6ca",
    "AFFECTED-CHARTS.json": "587739d21541e7ffe01af9cb7e51abaa757ee69b580befe8bb768a81b614aa08",
    "derivative_check.py": "348c8b2de72f1f112cb1337eca9d29ca96c85a7ad903beecafb1a2a1221f408e",
}
PROTECTED = {319, 863, 1355, 1568}
TARGET = Q("0.0040075385047236")
BIT = Q("0.00376669")


def checked():
    files = {}
    for name, pin in PINS.items():
        data = (ROOT / name).read_bytes()
        if sha256(data).hexdigest() != pin:
            raise ValueError("changed pinned input " + name)
        files[name] = data
    return files


def hist(row):
    return Counter({int(k): v for k, v in row.items()})


def main():
    assert __debug__
    f = checked()
    admission, stock, ids, census, clocks = (loads(f[name]) for name in
        ("ADMITTED.json", "RANK-STOCK.json", "IDENTITIES.json", "OCCUPANCY.json", "AFFECTED-CHARTS.json"))
    assert admission["head"] == stock["head"] == census["head"] == clocks["comparator_head"] == HEAD
    assert admission["exit"] == 0 and ids["status"] == "PASS_INDEPENDENT_319_BLOCK" and ids["ranks"] == [3, 8, 9]
    assert ids["literal_candidate_clocks"] == [44588, 44627]
    cohort = set(census["endpoint_cohort"])
    assert len(cohort) == 615 and 1081 in cohort and 1081 in clocks["eligible_affected"]
    witnessed = []
    for key, row in clocks["new_snapshots"].items():
        occupants = {int(r) for r, chart in row["affected_charts"].items() if chart == 1089}
        if occupants & cohort - PROTECTED:
            assert occupants & cohort - PROTECTED == {1081} and occupants == {319, 1081}
            witnessed.append((int(key), 1089, 1081))
    witnessed.sort()
    assert witnessed == [(t, 1089, 1081) for t in range(44588, 44600)]
    lower, upper = map(Q, admission["crossing"])
    assert upper == Q(stock["crossing_upper"]) and lower < upper < BIT < TARGET
    old_paid, productive = hist(stock["old_complete_paid"]), hist(stock["complete_targets"])
    delta = Counter({3: 17, 6: 17, 9: -17})
    old, new = productive.copy(), productive.copy()
    old.subtract(old_paid)
    new.subtract(old_paid)
    new.update(delta)
    assert sum(old_paid.values()) == 110519 and sum(productive.values()) == 22461
    assert sum(productive.values()) + sum(delta.values()) == 22478
    assert sum(r * n for r, n in old.items()) == sum(r * n for r, n in new.items()) == 1424
    tariff = run_path(str(ROOT / "pricing.py"))
    cost = tariff["cost"]
    credit = cost(delta, upper)
    assert list(map(str, credit)) == stock["rank_prices"]["3+6"]["credit"]
    probe = upper + Q(1, 10**9)
    old_margin, new_margin = cost(old, probe), cost(new, probe)
    assert old_margin[1] < 0 < new_margin[0] and 0 < credit[0] <= credit[1] < 1
    charged = new.copy()
    charged[1] -= 1
    derivative = run_path(str(ROOT / "derivative_check.py"))["derivative"](new, lower, BIT, tariff)
    charged_lower = cost(charged, lower)
    assert derivative[1] < 0 and charged_lower[1] < 0
    target_credit, target_before, target_after = (cost(row, TARGET) for row in (delta, old, new))
    assert target_before[1] < target_after[1] < 0
    result = {
        "head": HEAD, "input_sha256": PINS, "crossing": [str(lower), str(upper)],
        "productive_delta": dict(delta), "paid_delta": {}, "stock": witnessed, "one_edit_cap": 1,
        "compatible_gross_upper_at_comparator": str(credit[1]), "credit": list(map(str, credit)),
        "complete_probe": str(probe), "old_probe_margin": list(map(str, old_margin)),
        "new_probe_margin": list(map(str, new_margin)), "charged_lower_margin": list(map(str, charged_lower)),
        "complete_derivative_through_BIT": list(map(str, derivative)), "BIT": str(BIT),
        "moonshot": str(TARGET), "moonshot_credit": list(map(str, target_credit)),
        "moonshot_before_margin": list(map(str, target_before)), "moonshot_after_margin": list(map(str, target_after)),
        "scope": "Affected pivot 1081, exact 3→127 rank-nine cohort, chart 1089 rank-three. Alternative cuts share one root. No WORD decoded. No physical or verified exponent result.",
    }
    print(dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
