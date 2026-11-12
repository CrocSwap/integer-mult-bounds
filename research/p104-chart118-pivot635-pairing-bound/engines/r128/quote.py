"""Authenticate and price just two existing chart-118 banks before decoding."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "inputs/R89-PRICE.json": "b4bf8e00a8289f03b1da731fb3ab563a771d88d875e0da73acf70954df2f2c56",
    "inputs/R89-PAIR.json": "4b8f2963ae0ef7bd357c3129e8287f79c5c1fccca6375c41e35fa01c476cb2ae",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "inputs/OLD-WITNESS.json": "5be60a09485041744919696121ae27e57a1aa9de437a2c4494d5fc569af4cdb4",
}
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
KEYS = [[39701, 118], [40853, 118]]


def unique(items):
    out = dict(items)
    if len(out) != len(items):
        raise ValueError("duplicate metadata key")
    return out


def checked(rel):
    raw = (ROOT / rel).read_bytes()
    if sha256(raw).hexdigest() != PINS[rel]:
        raise ValueError(f"changed dependency {rel}")
    return raw


def main():
    raw = {p: checked(p) for p in PINS}
    old, pairs, earlier = (loads(raw[p], object_pairs_hook=unique) for p in
                          ("inputs/R89-PRICE.json", "inputs/R89-PAIR.json", "inputs/OLD-WITNESS.json"))
    assert old["head"] == pairs["head"] == HEAD and old["caller_head"] == CALLER
    assert old["native_copies"] == 17 and old["empty_root_credits"] == 0
    assert (earlier["pivot"], earlier["cut_before"], earlier["frame"], earlier["boundary"]) == (635, 37473, 118, [3, 127])
    cohort = set(old["endpoint_cohort"])
    assert len(cohort) == 615 and 635 in cohort and 631 not in cohort
    assert set(map(int, earlier["c"])) <= cohort
    assert set(map(int, earlier["d"])) - cohort == {639} and Fraction(earlier["d"]["639"]) == -Fraction(1, 8)
    rows = [r for r in pairs["results"] if r["key"][1] == 118 and 635 in r["pivots"]]
    assert len(rows) == 74 and all(r["disposition"] == "rank drop" and not r["owned"] for r in rows)
    assert all(r["direct_terms"] == 0 for r in rows)
    selected = [r for key in KEYS for r in rows if r["key"] == key]
    unvisited = [r["key"] for r in rows if r["key"] not in KEYS]
    assert len(selected) == 2 and len(unvisited) == 72
    assert len({tuple(r["public"]) for r in rows}) == 2
    assert all(set(map(int, earlier[k])) <= set(selected[0]["public"]) for k in ("a", "b"))
    paid, targets = (Counter({int(r): n for r, n in old[k].items()}) for k in ("old_paid", "old_targets"))
    assert (sum(paid.values()), sum(targets.values())) == (110519, 22461)
    net = targets.copy()
    net.subtract(paid)
    delta = {4: 17, 5: 17, 9: -17}
    assert sum(r * n for r, n in delta.items()) == 0
    assert sum(r * n for r, n in net.items()) == old["signed_rank_surplus"] == 1424
    new = net.copy()
    new.update(delta)
    probe = Fraction(old["old_crossing_upper"]) + Fraction(1, 10**9)
    at, target = map(Fraction, [old["old_crossing_upper"], old["moonshot"]])
    cost = run_path(str(ROOT / "inputs/pricing.py"))["cost"]
    credit, price, moon = cost(delta, at), cost(new, probe), cost(new, target)
    debit = new.copy()
    debit[1] -= 1
    extra = cost(debit, Fraction(old["old_crossing_lower"]))
    assert credit[0] > 0 and price[0] > 0 and moon[1] < 0 and extra[1] < 0
    assert sum(targets.values())+sum(delta.values()) == 22478
    print(dumps(dict(head=HEAD, caller=CALLER, pins=PINS, selected=selected, unvisited=unvisited,
        endpoint_cohort=sorted(cohort), credit_at_crossing_upper=list(map(str, credit)),
        complete_probe=list(map(str, price)), probe=str(probe), complete_at_fixed_target=list(map(str, moon)),
        extra_rank_one_at_crossing_lower=list(map(str, extra)), complete_paid=110519, complete_productive=22478,
        target_delta=delta, paid_delta={}, surplus=1424, word_sha256=old["word_sha256"],
        max_compatible_edits=1, limits={"cases": 2, "runner_seconds": 35}, no_literal_decode=True),
        indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
