"""Bind forward/reverse closure and count every continuous public injection key."""
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "plan/PRICE.json": "9a3ce52bda81c4046dc2751dddcf490360500dec976c692f84eb6814cbe85402",
    "inputs/R125-INDEPENDENT.json": "b258d523358a047ea0e3d817f4eec3a30bf93739268b013fc1f7c5ee095dfc91",
    "inputs/R125-PRICE.json": "ac4207f548684468b9d09369f3a7866192ae9ffa5e3c3adb284b41bb3f61166d",
    "lead/RESULT.json": "3cd954cc83cb77bdc4851922868dd5964a39bbada1ad10e802e3e74ae3613797",
    "independent/RESULT.json": "e9593dcbb3211343388d0e6bc0b45777dbdb6640ffe7e1bac2c7dafca62fb645",
}


def unique(items):
    result = dict(items)
    if len(result) != len(items):
        raise ValueError("duplicate JSON key")
    return result


def read(path):
    raw = (ROOT / path).read_bytes()
    if sha256(raw).hexdigest() != PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return loads(raw, object_pairs_hook=unique)


def main():
    assert __debug__
    price, prior, old_price, forward, reverse = map(read, PINS)
    assert len({r["head"] for r in (price, prior, old_price, forward, reverse)}) == 1
    assert len({r["caller"] for r in (price, prior, old_price, forward, reverse)}) == 1
    assert forward["events"] == reverse["full_reverse_events"] == 76466
    assert forward["maximal_bank"] == reverse["maximal_inventory"]["public"] == prior["maximal_bank"] == price["maximal_bank"]
    assert forward["final_bank"] == reverse["final_inventory"]["public"]
    assert not reverse["maximal_inventory"]["owned"] and not reverse["final_inventory"]["owned"]
    assert forward["closed_without_new_columns"] and not forward["new_generator_keys"] and not reverse["generators"]
    assert forward["unresolved_tail_from"] is None and forward["timeout"] is None
    assert forward["counts"] == {"public exit": 12}
    assert forward["chart_contacts"] == [[r["clock"], r["event"], "public exit"] for r in reverse["contacts"]]
    assert all(r["kind"] == "public egress" for r in reverse["contacts"])
    assert reverse["copy_audit"] == [{"clock": 33805, "destination": 1525, "source": 770, "chart": 115, "preceding_write": 33804}]
    assert len(reverse["copy_audit"]) == forward["copy_owned_destinations"]
    maximum, end = price["maximal_cut"], reverse["final_cut"]
    assert maximum == forward["maximal_cut"] == reverse["maximal_cut"] == prior["maximal_cut"]
    assert (maximum, end) == (45472, 76466)
    assert prior["support_rank"] == price["prior_guarded_rank"] == 19
    assert prior["dual"] == price["dual"] and Q(prior["dual_on_target"]) == 1
    assert all(sum(Q(v)*Q(prior["dual"].get(axis, 0)) for axis, v in row.items()) == 0
               for row in prior["projected_columns"])

    banks = {r["cut"]: r["public"] for r in old_price["injection_banks"]}
    assert sorted(banks) == prior["cuts"] and len(banks) == 19
    assert sum(map(len, banks.values())) == 354
    start = old_price["retirement"]["cut"]
    cursor = start
    live = set(banks[start])
    early = 0
    for contact in prior["chronology"]:
        clock, event = contact["clock"], contact["event"]
        if clock >= maximum:
            break
        early += (clock + 1 - cursor) * len(live)
        cursor = clock + 1
        if event[0] == "MOVE":
            assert event[3] == 242 and not event[4]
            live.add(event[1])
        elif event[0] == "ADD":
            assert {event[1], event[2]} <= live and Q(event[-2])
        else:
            assert event[0] == "SCALE" and event[1] in live and Q(event[-2])
        assert sorted(live) == banks[cursor]
    assert cursor == maximum and sorted(live) == price["maximal_bank"]
    tail = 0
    for contact in reverse["contacts"]:
        clock, event = contact["clock"], contact["event"]
        assert sorted(live) == contact["public_before"]
        tail += (clock + 1 - cursor) * len(live)
        cursor = clock + 1
        live.remove(event[1])
        assert sorted(live) == contact["public_after"]
    tail += (end + 1 - cursor) * len(live)
    assert tail == reverse["public_cut_role_pairs"] and sorted(live) == forward["final_bank"]
    print(dumps({
        "head": price["head"], "caller": price["caller"], "pins": PINS,
        "interval_inclusive": [start, end], "maximal_cut": maximum,
        "all_public_cut_role_pairs": early + tail, "before_maximal_cut_pairs": early,
        "at_and_after_maximal_cut_pairs": tail, "public_egress_agreement": 12,
        "final_public": sorted(live), "frozen_banks": 19, "frozen_observations": 354,
        "guarded_rank": 19, "dual_on_target": prior["dual_on_target"], "unresolved": 0,
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
