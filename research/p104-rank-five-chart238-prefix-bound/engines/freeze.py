"""Select and price the untouched rank-five 3-to-238 endpoint group."""
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "inputs/R115-PRICE.json": "c04adfb199f6dbc25806d6062562c7d707b8fda8ad73f3ed818901248d25ffbf",
    "inputs/R115-GEOMETRY.json": "c2a4406cf7130a819189e8ceefb4bb6e09edd392eb56820f9fcadb0e9415ef4e",
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
    assert __debug__
    price, geom = map(read, PINS)
    assert price["head"] == geom["head"] == "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
    assert geom["status"] == "EXHAUSTED" and len(geom["candidate_rows"]) == 68
    group = [3, 238]
    cohort = next(g["roles"] for g in price["groups"] if g["endpoints"] == group)
    assert cohort == [325, 1087] and geom["selected_group"] == [3, 241]
    rows = [r for r in geom["candidate_rows"] if r["key"][2:] == group]
    assert len(rows) == len({tuple(r["key"]) for r in rows}) == 18
    assert all(r["pivots"] and not r["owned"] for r in rows)
    assert {r["key"][1] for r in rows} == {370, 375}
    at, moon = price["at_incumbent"], price["at_target"]
    assert price["paid_delta"] == {} and price["productive_delta"] == {"2": 17, "3": 17, "5": -17}
    assert Fraction(at["gross_one"][0]) > 0
    whole = 2 * Fraction(at["gross_one"][1])
    fixed_complete = Fraction(moon["old_margin"][1]) + 2 * Fraction(moon["gross_one"][1])
    print(dumps({
        "head": price["head"], "caller": price["caller"], "pins": PINS,
        "selected_group": group, "cohort": cohort, "paid_delta": {}, "productive_delta": price["productive_delta"],
        "one_gross": at["gross_one"], "two_compatible_upper": str(whole),
        "fixed_target": price["moonshot"], "fixed_target_complete_upper": str(fixed_complete),
        "unchanged_paid_positions": 110519, "productive_one": 22478, "surplus": 1424,
        "selected": [dict(r, key=r["key"][:2]) for r in rows],
        "unselected": [r["key"] for r in geom["candidate_rows"] if r["key"][2:] not in (group, [3, 241])],
        "caps": {"representatives": 18, "events_per_direction": 76466,
                 "modular_seconds": 25, "exact_pairs": 4, "exact_seconds": 35,
                 "prototype_seconds": 120},
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
