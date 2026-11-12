"""Authenticate and price the one unvisited two-paid subdivision support bank."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "inputs/BENCHMARK.json": "004331cff6ca8644489d7b7084e5c67439d74a2d283e4d64a9fdb9f88679253d",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/R99-PRICE.json": "0eba831b917331f7a84f4d8a5da726577ed516f04c5f1b94671e031dd2c0b3b4",
    "inputs/R99-GEOMETRY.json": "c89976cd5f808c29ab13770e262b2d216f56b4e1703ef836c3438d60f40eb11b",
    "inputs/R99-SELECTION.json": "3a6f588eb597e56abfbfe568319fc81294d16d37f03f8b6159ba5b133dc2f416",
    "inputs/R99-MODULAR.json": "4d24d44be888a52ac93e589bf7a15978317395b0d3ddc6d96dd2e6d14bde5b44",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}


def unique(items):
    doc = dict(items)
    if len(doc) != len(items):
        raise ValueError("duplicate JSON key")
    return doc


def hist(data):
    return Counter({int(rank): count for rank, count in data.items()})


def main():
    docs = []
    for path, expected in PINS.items():
        raw = (ROOT / path).read_bytes()
        if sha256(raw).hexdigest() != expected:
            raise ValueError(f"changed dependency {path}")
        if path.endswith(".json"):
            docs.append(loads(raw, object_pairs_hook=unique))
    bench, prior, old_price, geo, select, modular = docs
    assert len({d["head"] for d in docs}) == 1
    assert select["geometry_sha256"] == PINS["inputs/R99-GEOMETRY.json"]
    assert geo["stage"] == "complete" and geo["timeout"] is None and geo["visited_cuts"] == 38967
    assert modular["counts"] == {"prefix exclusion": 16}
    assert len(select["unselected"]) == 1 and select["unselected"] == modular["unvisited"]
    row, = select["unselected"]
    assert row["anchors"] == [[42958, 1255], [43050, 572]]
    assert row["bank"]["key"] == [42958, 22] and row["chart"] is None
    intervals = [geo["pair_intervals"][i] for i in (22, 33, 44)]
    assert all(w["chart"] is None and w["first"] == 42958 and w["last"] == 42960 for w in intervals)
    representatives = [row["bank"]["key"], *row["aliases"]]
    raw_keys = [[t, w["pair"]] for t in range(42958, 42961) for w in intervals]
    assert representatives == raw_keys[:6]
    assert row["bank"]["public"] == row["bank"]["pivots"] == [572, 1255]
    assert row["bank"]["owned"] == []
    assert all(r in prior["endpoint_cohort"] for r in (572, 1255))
    assert len(prior["endpoint_cohort"]) == 615

    paid, target = hist(prior["old_paid"]), hist(prior["old_targets"])
    old = target.copy()
    old.subtract(paid)
    paid.update({1: 68, 2: -34})
    target.update({4: 17, 5: 17, 9: -17})
    assert paid == hist(old_price["new_paid"]) and target == hist(old_price["new_targets"])
    new = target.copy()
    new.subtract(paid)
    assert sum(r * n for r, n in old.items()) == sum(r * n for r, n in new.items()) == 1424
    change = new.copy()
    change.subtract(old)
    cost = run_path(str(ROOT / "inputs/pricing.py"))["cost"]
    at, probe, fixed = map(Fraction, (old_price["old_crossing_upper"], old_price["probe"], old_price["moonshot"]))
    assert at == Fraction(bench["crossing"][1])
    assert at < probe < Fraction(old_price["retained_bit_premise"])
    net = cost(change, at)
    candidate = cost(new, probe)
    assert list(map(str, net)) == old_price["one_net_at_crossing"]
    assert list(map(str, candidate)) == old_price["complete_probe"] and candidate[0] > 0
    extra = cost(new, at)[1] - 1
    assert extra < 0
    print(dumps({
        "pins": PINS, "head": bench["head"], "caller": old_price["caller_head"],
        "word_sha256": old_price["word_sha256"], "row": row, "intervals": intervals,
        "representative_keys": representatives, "raw_keys": raw_keys,
        "paid_delta": old_price["paid_delta"], "productive_delta": old_price["target_delta"],
        "paid": sum(paid.values()), "productive": sum(target.values()), "rank_surplus": 1424,
        "old_crossing_upper": str(at), "probe": str(probe), "probe_complete_margin": list(map(str, candidate)),
        "one_compatible_edit_net": list(map(str, net)), "extra_rank_one_upper": str(extra),
        "fixed_target": str(fixed), "fixed_target_complete_upper": str(cost(new, fixed)[1]),
        "caps": {"raw_keys": 9, "support_forms": 1, "events_per_direction": 76466,
                 "runner_seconds": 25, "exact_pairs": 1, "exact_seconds": 35, "prototype_seconds": 120},
        "scope": "One shared fresh rank-five bank, two fully charged rank-two subdivisions, one productive 4+5 split.",
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    assert __debug__
    main()
