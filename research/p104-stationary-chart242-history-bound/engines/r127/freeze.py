"""Complete quote for a funded rank-eight exit on the exact chart-242 pivot."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "inputs/R126-PRICE.json": "9a3ce52bda81c4046dc2751dddcf490360500dec976c692f84eb6814cbe85402",
    "inputs/R126-LEAD.json": "3cd954cc83cb77bdc4851922868dd5964a39bbada1ad10e802e3e74ae3613797",
    "inputs/R97-EXACT.json": "95d34e468683aa64e19d3e4d62745b9fc1d4305b00d25054b34bb5a668639b4b",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}


def unique(items):
    doc = dict(items)
    if len(doc) != len(items):
        raise ValueError("duplicate JSON key")
    return doc


def read(rel):
    raw = (ROOT / rel).read_bytes()
    if sha256(raw).hexdigest() != PINS[rel]:
        raise ValueError(f"changed dependency {rel}")
    return loads(raw, object_pairs_hook=unique) if rel.endswith(".json") else None


def hist(rows):
    return Counter({int(k): v for k, v in rows.items()})


def main():
    a, topology, exact, prior, _ = map(read, PINS)
    assert len({x["head"] for x in (a, topology, exact, prior)}) == 1
    assert topology["closed_without_new_columns"] and topology["counts"] == {"public exit": 12}
    assert a["maximal_bank"] == topology["maximal_bank"]
    row, = [r for r in exact["results"] if r["key"] == [41740, 242]]
    assert row["prefix_pure_basis"] == [{"a": {"1123": "1"}, "c": {"1123": "1"}}]
    assert not row["owned"] and row["endpoint_pairing_matrix"] == [["0"]]
    eligible = set(prior["endpoint_cohort"])
    assert len(eligible) == 615 and 1123 not in eligible
    paid, target = hist(prior["old_paid"]), hist(prior["old_targets"])
    old = target.copy()
    old.subtract(paid)
    paid.update({1: 17})
    target.update({4: 17, 5: 17, 8: -17})
    new = target.copy()
    new.subtract(paid)
    delta = new.copy()
    delta.subtract(old)
    assert sum(r * v for r, v in delta.items()) == 0
    assert sum(paid.values()) == 110536 and sum(target.values()) == 22478
    assert sum(r * n for r, n in new.items()) == 1424
    at, probe, fixed = map(Fraction, (prior["old_crossing_upper"], prior["probe"], prior["moonshot"]))
    assert at < probe < Fraction(prior["retained_bit_premise"])
    cost = run_path(str(ROOT / "inputs/pricing.py"))["cost"]
    credit, margin = cost(delta, at), cost(new, probe)
    assert margin[0] > 0 > cost(new, at)[1] - 1
    print(dumps({
        "head": a["head"], "caller": a["caller"], "pins": PINS, "word_sha256": a["word_sha256"],
        "retirement": a["retirement"], "funded_exit": [1123, 245, 127, 1],
        "new_cohort": sorted(eligible | {1123}), "static_bank": row["public"],
        "maximal_cut": a["maximal_cut"], "maximal_bank": a["maximal_bank"],
        "paid_delta": {1: 17}, "target_delta": {4: 17, 5: 17, 8: -17},
        "paid": sum(paid.values()), "productive": sum(target.values()), "rank_surplus": 1424,
        "one_compatible_edit": 1, "credit_at_old_upper": list(map(str, credit)),
        "probe_complete_margin": list(map(str, margin)),
        "extra_rank_one_upper": str(cost(new, at)[1] - 1),
        "fixed_target_complete_upper": str(cost(new, fixed)[1]),
        "limits": {"metadata_bank_seconds": 5, "native_bank_seconds": 35, "native_keys": 20,
                   "max_injections": 16, "prototype_seconds": 120},
        "scope": "One #7161-style funded exit for pivot1123, exact chart242 stationary support, no change to any other paid path.",
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    assert __debug__
    main()
