"""Preprice one owned lifetime with two unobserved intermediate writes."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "inputs/R80-REVERSE.json": "12c31ae16b9a364fd84c16d2f76cee873ab279984eb88e1cf1568be905c8f010",
    "inputs/BENCHMARK.json": "004331cff6ca8644489d7b7084e5c67439d74a2d283e4d64a9fdb9f88679253d",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
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
    assert __debug__
    docs = []
    for rel, expected in PINS.items():
        raw = (ROOT / rel).read_bytes()
        if sha256(raw).hexdigest() != expected:
            raise ValueError(f"changed dependency {rel}")
        if rel.endswith(".json"):
            docs.append(loads(raw, object_pairs_hook=unique))
    inventory, bench, prior = docs
    assert inventory["complete"] and inventory["neighbor_pairs"] == len(inventory["pairs"]) == 9
    assert inventory["head"] == bench["head"] == prior["head"]
    assert inventory["word_sha256"] == prior["word_sha256"]
    row, = [x for x in inventory["pairs"] if not x["opposite_direction"]
            and len(x["intervening"]) == 2
            and all(op == "ADD" and access == "destination" for _, op, access in x["intervening"])]
    assert row["key"] == [41996, 44242, 1531] and row["lifetime"] == [32607, 44247]
    assert row["charts"] == [594, 117, 534] and row["paid_ranks"] == [4, 1]
    assert [x[0] for x in row["intervening"]] == [41997, 44241]
    paid, target = hist(prior["old_paid"]), hist(prior["old_targets"])
    old = target.copy()
    old.subtract(paid)
    delta = {1: -17, 4: -17, 5: 17}
    paid.update(delta)
    new = target.copy()
    new.subtract(paid)
    assert sum(paid.values()) == 110502 and sum(target.values()) == 22461
    assert sum(k * v for k, v in old.items()) == sum(k * v for k, v in new.items()) == 1424
    at, probe, fixed = map(Fraction, (prior["old_crossing_upper"], prior["probe"], prior["moonshot"]))
    assert at == Fraction(bench["crossing"][1]) and at < probe < Fraction(prior["retained_bit_premise"])
    cost = run_path(str(ROOT / "inputs/pricing.py"))["cost"]
    net = cost({k: -v for k, v in delta.items()}, at)
    probe_margin = cost(new, probe)
    assert probe_margin[0] > 0 and cost(new, at)[1] - 1 < 0
    print(dumps({
        "head": bench["head"], "caller": prior["caller_head"], "word_sha256": prior["word_sha256"],
        "pins": PINS, "old_crossing_upper": str(at), "probe": str(probe),
        "row": row, "bank_cuts": [[41996, 594], [44242, 534]], "compatible_edits": 1,
        "paid_delta": delta, "paid": sum(paid.values()), "productive": sum(target.values()),
        "surplus": 1424, "gain_at_old_crossing": list(map(str, net)),
        "complete_probe_margin": list(map(str, probe_margin)),
        "complete_fixed_target_upper": str(cost(new, fixed)[1]),
        "extra_rank_one_upper": str(cost(new, at)[1] - 1),
        "caps": {"windows": 1, "banks": 2, "events": 76466, "seconds": 20,
                 "prototype_seconds": 120},
        "scope": "One owned lifetime with two unobserved writes, fixed aggregate at one old endpoint.",
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
