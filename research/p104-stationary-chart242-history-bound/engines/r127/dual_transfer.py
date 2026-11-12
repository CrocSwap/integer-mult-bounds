"""Transfer the exact chart-242 separator across a granted normalized exit."""
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "plan/PRICE.json": "87be0ba80c11d6dcb7f9d62117db8bccea6a47234a77590ebd2e05968ea19a2d",
    "inputs/R125-INDEPENDENT.json": "b258d523358a047ea0e3d817f4eec3a30bf93739268b013fc1f7c5ee095dfc91",
    "inputs/R126-PRICE.json": "9a3ce52bda81c4046dc2751dddcf490360500dec976c692f84eb6814cbe85402",
    "inputs/R126-AGREEMENT.json": "01e5064c748550bb47ceeee761b33a0eba86a9b2bc4b2ea6d5014bdd543d7f17",
}


def unique(items):
    obj = dict(items)
    if len(obj) != len(items):
        raise ValueError("duplicate JSON key")
    return obj


def read(rel):
    data = (ROOT / rel).read_bytes()
    if sha256(data).hexdigest() != PINS[rel]:
        raise ValueError(f"changed dependency {rel}")
    return loads(data, object_pairs_hook=unique)


def support(dual, cohort, pivot):
    return set(dual).intersection(cohort) == {pivot}


def main():
    assert __debug__
    new, old, geometry, agreement = map(read, PINS)
    assert len({new["head"], old["head"], geometry["head"]}) == 1
    assert old["maximal_bank"] == new["maximal_bank"] == geometry["maximal_bank"]
    assert old["maximal_cut"] == new["maximal_cut"] == geometry["maximal_cut"] == 45472
    assert old["dual"] == geometry["dual"] and Fraction(old["dual_on_target"]) == 1
    assert new["funded_exit"] == [1123, 245, 127, 1]
    assert new["paid_delta"] == {"1": 17} and new["target_delta"] == {"4": 17, "5": 17, "8": -17}
    assert Fraction(new["probe_complete_margin"][0]) > 0
    pivot = 1123
    dual = {int(i): Fraction(q) for i, q in old["dual"].items()}
    prior = set(geometry["cohort"])
    later = set(new["new_cohort"])
    assert len(prior) == 15 and len(later) == 616 and dual[pivot] == 1
    assert support(dual, prior, pivot) and support(dual, later, pivot)
    forbidden = next(i for i in dual if i != pivot)
    assert not support(dual, later | {forbidden}, pivot)
    dots = [sum(dual.get(int(i), 0) * Fraction(q) for i, q in v.items())
            for v in old["projected_columns"]]
    assert len(dots) == len(new["maximal_bank"]) == 20 and not any(dots)
    print(dumps({
        "head": new["head"], "caller": new["caller"], "pins": PINS,
        "status": "funded exit still separated", "funded_exit": new["funded_exit"],
        "dual": old["dual"], "dual_on_pivot": "1", "dual_on_maximal_columns": list(map(str, dots)),
        "old_cohort_intersection": sorted(set(dual) & prior),
        "funded_cohort_intersection": sorted(set(dual) & later),
        "topology_agreement_fields": sorted(agreement),
        "controls": ["new cohort admitting a dual exterior coordinate invalidates transfer"],
        "scope": "Grant a legal normalized rank-one exit preserving every guarded coordinate; chart-242 history and all other paid paths remain fixed.",
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
