"""Bind the same priced split and freeze the post-maximal-chart span test."""
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "inputs/R125-PRICE.json": "ac4207f548684468b9d09369f3a7866192ae9ffa5e3c3adb284b41bb3f61166d",
    "inputs/R125-LEAD.json": "344f2b6011fe464931de8883e64ed64420fa41728e744600b72a7b1e3b929656",
    "inputs/R125-INDEPENDENT.json": "b258d523358a047ea0e3d817f4eec3a30bf93739268b013fc1f7c5ee095dfc91",
}


def unique(items):
    out = dict(items)
    if len(out) != len(items):
        raise ValueError("duplicate JSON key")
    return out


def read(path):
    raw = (ROOT / path).read_bytes()
    if sha256(raw).hexdigest() != PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return loads(raw, object_pairs_hook=unique)


def main():
    price, lead, exact = map(read, PINS)
    assert len({doc["head"] for doc in (price, lead, exact)}) == 1
    assert len({doc["caller"] for doc in (price, lead, exact)}) == 1
    assert lead["status"] == "no guarded temporal span" and not lead["unresolved_frozen_form"]
    assert lead["injection_keys"] == exact["excluded_injection_keys"] == 354
    assert exact["status"] == "separated" and exact["support_rank"] == 19
    assert exact["maximal_cut"] == 45472 and len(exact["maximal_bank"]) == 20
    assert Fraction(exact["dual_on_target"]) == 1 and Fraction(exact["dual"]["1123"]) == 1
    assert lead["full_projection"]["residual"] == {"1123": "1"}
    for vector in exact["projected_columns"]:
        assert not sum(Fraction(exact["dual"].get(k, "0")) * Fraction(v) for k, v in vector.items())
    assert price["paid_delta"] == {} and price["productive_delta"] == {"4": 34, "8": -17}
    assert Fraction(price["complete_probe"][0]) > 0 > Fraction(price["extra_rank_one_complete_upper"])
    print(dumps({
        "head": price["head"], "caller": price["caller"], "word_sha256": price["word_sha256"], "pins": PINS,
        "retirement": price["retirement"], "maximal_cut": exact["maximal_cut"],
        "maximal_bank": exact["maximal_bank"], "prior_guarded_rank": exact["support_rank"],
        "dual": exact["dual"], "target": exact["target"], "cohort": price["cohort"],
        "in_scope_edits": 1, "paid": price["paid"], "productive_delta": price["productive_delta"],
        "paid_delta": price["paid_delta"], "one_gross": price["one_gross"], "complete_probe": price["complete_probe"],
        "fixed_target_complete_upper": price["fixed_target_complete_upper"],
        "extra_rank_one_complete_upper": price["extra_rank_one_complete_upper"],
        "limits": {"literal_events": 76466, "topology_seconds": 20, "new_generator_cap": 64,
                   "support_seconds": 35, "prototype_seconds": 120},
        "scope": "Same stationary difference buffer and fixed paid itinerary, grant all public injections from the certified maximal bank through final cut.",
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    assert __debug__
    main()
