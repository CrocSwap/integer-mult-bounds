"""Price fixed same-direction owned MOVE pairs with exactly one ADD."""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
from json import dumps, loads
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/ADMITTED.json": "c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13",
    "inputs/READBACK.json": "337668788fb39ec9575887f9c5faf438a880471f78d936357dabf7deeac5de82",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "inputs/R80-REVERSE.json": "12c31ae16b9a364fd84c16d2f76cee873ab279984eb88e1cf1568be905c8f010",
    "inputs/R80-COMPARE.json": "f06d6c49823f06421928ff3b9d73d34332c0040f148926dc25df609a7e3220a8",
    "inputs/R80-FORWARD.json": "db293c67c896f54788681b7a8a9fec5f13da0e31fe5b3dd65fbe30e370ff1d2e",
}


def unique(pairs):
    value = dict(pairs)
    if len(value) != len(pairs):
        raise ValueError("duplicate JSON key")
    return value


def histogram(item):
    result = Counter({int(rank): count for rank, count in item.items()})
    assert len(result) == len(item)
    assert all(rank > 0 and type(count) is int and count > 0 for rank, count in result.items())
    return result


def interval(values):
    return list(map(str, values))


def main():
    assert __debug__
    raw = {}
    for name, pin in PINS.items():
        raw[name] = (ROOT / name).read_bytes()
        if sha256(raw[name]).hexdigest() != pin:
            raise ValueError(f"changed dependency {name}")

    def read(name):
        return loads(raw[f"inputs/{name}.json"], object_pairs_hook=unique)

    base, admission = read("READBACK"), read("ADMITTED")
    reverse, forward, reconciled = (read(f"R80-{name}") for name in ("REVERSE", "FORWARD", "COMPARE"))
    head = admission["head"]
    assert head == base["head"] == reverse["head"] == forward["head"]
    assert admission["exit"] == 0 and admission["status"] == "independently_reproduced_comparable"
    assert base["caller_head"] == admission["caller"]
    assert admission["inputs"]["WORD.json.gz"] == reverse["word_sha256"] == forward["word_sha256"]
    assert base["copies"] == 17 and not base["empty_root_credits"]
    assert reverse["complete"] and forward["status"] == "EXHAUSTED"
    assert reverse["neighbor_pairs"] == len(reconciled["matched"]) == 9
    assert reconciled["input_sha256"] == {
        "lead/RESULT.json": PINS["inputs/R80-FORWARD.json"],
        "independent/RESULT.json": PINS["inputs/R80-REVERSE.json"],
    }
    paid, targets = histogram(base["paid"]), histogram(base["targets"])
    signed = targets.copy()
    signed.subtract(paid)
    assert (sum(paid.values()), sum(targets.values()), sum(r*n for r,n in signed.items())) == (110519, 22461, 1424)
    cost = run_path(str(ROOT / "inputs/pricing.py"))["cost"]
    old_kappa = Fraction(base["new_raw_interval"][1])
    price_probe = old_kappa + Fraction(1, 10**9)
    moonshot = Fraction("0.0040075385047236")
    assert cost(signed, old_kappa)[1] < 0 and cost(signed, price_probe)[1] < 0

    forward_by_key = {tuple(x["key"]): x for x in forward["consecutive_same_lifetime_pairs"]}
    candidates = []
    for row in reverse["pairs"]:
        if row["opposite_direction"] or len(row["intervening"]) != 1:
            continue
        clock, opcode, access = row["intervening"][0]
        if opcode != "ADD":
            continue
        first, second, owner = row["key"]
        born, cleared = row["lifetime"]
        c = forward_by_key[owner, born, first, second]
        assert not c["turn"] and c["frames"] == row["charts"] and c["blocker"][0] == clock
        opcode, dest, source, coefficient, chart = c["blocker"][1]
        assert opcode == "ADD" and chart == row["charts"][1] and Fraction(coefficient)
        assert (owner == dest and access == "destination") or (owner == source and access == "source")
        assert dest != source and first < clock < second
        a, b = row["paid_ranks"]
        assert a + b == abs(row["ranks"][-1] - row["ranks"][0])
        delta = Counter()
        delta[a] -= 17
        delta[b] -= 17
        delta[a+b] += 17
        candidates.append({
            "move_clocks": [first, second], "owner": owner, "owner_lifetime": [born, cleared],
            "chart_path": row["charts"], "paid_old": [a, b], "paid_new": a+b,
            "owner_access": access, "peer": dest if access == "source" else source,
            "literal_ADD": [clock, [dest, source, coefficient, chart]],
            "paid_delta": dict(sorted(delta.items())), "target_delta": {},
            "cut_windows_pre_event": {"entrance": [first, second], "exit": [first+1, second]},
        })
    assert len(candidates) == 5

    def quote(group):
        debit = Counter()
        for candidate in group:
            debit.update(candidate["paid_delta"])
        changed_paid = paid.copy()
        changed_paid.update(debit)
        assert min(changed_paid.values()) > 0
        changed = targets.copy()
        changed.subtract(changed_paid)
        assert sum(changed_paid.values()) == sum(paid.values()) - 17*len(group)
        assert sum(r*n for r,n in changed.items()) == 1424
        lower, upper = cost(changed, price_probe)
        assert 0 < lower <= upper
        gross = {r:-n for r,n in debit.items()}
        with_extra = changed.copy()
        with_extra[1] -= 1
        return {
            "paid_positions": sum(changed_paid.values()), "paid": dict(sorted(changed_paid.items())),
            "productive_positions": sum(targets.values()), "rank_surplus": 1424,
            "empty_root_credits": 0,
            "paid_delta": {r:n for r,n in sorted(debit.items()) if n},
            "gross_at_crossing": interval(cost(gross, old_kappa)),
            "gross_at_moonshot": interval(cost(gross, moonshot)),
            "complete_margin_at_crossing": interval(cost(changed, old_kappa)),
            "complete_margin_at_probe": interval((lower, upper)),
            "complete_margin_with_one_extra_rank_one_at_crossing": interval(cost(with_extra, old_kappa)),
            "complete_margin_at_moonshot": interval(cost(changed, moonshot)),
        }

    for candidate in candidates:
        candidate["quote"] = quote([candidate])
    all_groups = []
    for size in range(1, len(candidates)+1):
        for group in combinations(candidates, size):
            if all(a["move_clocks"][-1] < b["move_clocks"][0] for a,b in zip(group, group[1:])):
                all_groups.append(group)
    assert len(all_groups) == 31 and len(all_groups[-1]) == 5
    whole = quote(all_groups[-1])
    assert Fraction(whole["complete_margin_at_moonshot"][1]) < 0
    assert all(Fraction(c["quote"]["complete_margin_with_one_extra_rank_one_at_crossing"][1]) < 0
               for c in candidates)
    print(dumps({
        "head": head, "caller_head": admission["caller"], "word_sha256": reverse["word_sha256"],
        "input_sha256": PINS, "old_crossing_upper": str(old_kappa), "price_probe": str(price_probe),
        "old_complete_margin_at_crossing": interval(cost(signed, old_kappa)),
        "old_complete_margin_at_moonshot": interval(cost(signed, moonshot)), "candidates": candidates,
        "one_edit_gross_upper_at_crossing": str(max(Fraction(c["quote"]["gross_at_crossing"][1]) for c in candidates)),
        "whole_compatible_relaxation": whole, "nonempty_disjoint_matchings": len(all_groups),
        "candidate_count": 5, "typed_end_placements": 10, "first_runner_seconds": 20, "build_cap": 1,
        "scope": "Uses sealed nine-pair R80 receipts only. Prices one alternative per pair, grants any support and added ordinary cost free, no new word decode or support search."
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
