"""Freeze two-fusion keys and the complete directed price from sealed metadata."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
from json import dumps, loads
from pathlib import Path
from runpy import run_path

PINS = {
    "price/SHA256": "37e11ffc1979e090deb4e046e7b770339a3d9e1898fff8b5a04f4a70da70e383",
    "independent/SHA256": "cfcac30934a139cf120885ee210c0923b60f387ecb880f18ea92ff0d33a159ba",
    "price/PRICE.json": "33aad506112912ddf0721a2b007d9194eaa02e5792aceda2f9774f8838511262",
    "lead/RESULT.json": "bf0cbae853422e85788449b40ddc2fa807b042d8a357a56a7c7654dda51331e4",
    "independent/RESULT.json": "afec20386a8fbdc70d1b96998adbe18edace42a3e14a015e0eab5c09fc311617",
    "price/inputs/7334-ADMITTED.json": "c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13",
    "price/inputs/7334-READBACK.json": "337668788fb39ec9575887f9c5faf438a880471f78d936357dabf7deeac5de82",
    "price/inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "price/inputs/derivative_check.py": "348c8b2de72f1f112cb1337eca9d29ca96c85a7ad903beecafb1a2a1221f408e",
}
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
CALLER_SHA = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
TARGET = Fraction("0.0040075385047236")


def unique(pairs):
    obj = dict(pairs)
    if len(obj) != len(pairs):
        raise ValueError("duplicate metadata key")
    return obj


def authenticated(root):
    docs = {}
    for name, expected in PINS.items():
        raw = (root / name).read_bytes()
        if sha256(raw).hexdigest() != expected:
            raise ValueError(f"changed dependency {name}")
        if name.endswith(".json"):
            docs[name] = loads(raw, object_pairs_hook=unique)
    for name, members in [
        ("price/SHA256", ("price/PRICE.json", "price/inputs/7334-ADMITTED.json",
                         "price/inputs/7334-READBACK.json", "price/inputs/pricing.py",
                         "price/inputs/derivative_check.py")),
        ("independent/SHA256", ("independent/RESULT.json",)),
    ]:
        folder = str(Path(name).parent) + "/"
        entries = {}
        for line in (root / name).read_text().splitlines():
            digest, relative = line.split(maxsplit=1)
            if relative in entries:
                raise ValueError(f"duplicate manifest path {folder + relative}")
            entries[relative] = digest
        for member in members:
            assert entries[member.removeprefix(folder)] == PINS[member], member
    return docs


def bounds(approximation):
    return [str(endpoint) for endpoint in approximation]


def inventory(stock, lead, independent):
    odd = {int(clock): tuple(mask) for clock, (_, mask) in stock["odd_jobs"].items()}
    even = {int(clock): tuple(sorted(mask)) for clock, (_, mask) in stock["even_jobs"].items()}
    assert set(odd) == {1339, 1340, 2970, 2971}
    keys = {(row["odd"], row["even"]) for row in stock["keys"]}
    assert keys == {(o, e) for o in odd for e in even if set(odd[o]).isdisjoint(even[e])}
    assert len(keys) == len(stock["keys"]) == 180 and len(even) == 60
    assert independent["q"] == lead["q"] == 1
    assert independent["body"] == "unit" and lead["body"] == "all one"
    assert lead["price_sha256"] == independent["price_sha256"] == PINS["price/PRICE.json"]
    assert lead["caller_sha256"] == independent["caller_sha256"] == CALLER_SHA
    assert lead["head"] == independent["head"] == HEAD
    assert len(independent["outcomes"]) == len(lead["decisions"]) == len(keys)
    assert not independent["unvisited"] and not lead["unvisited"]
    assert {tuple(row["key"]) for row in independent["outcomes"]} == keys
    primary = {(row["key"]["odd"], row["key"]["even"]): row for row in lead["decisions"]}
    assert set(primary) == keys
    modulus = lead["modulus"]
    for row in independent["outcomes"]:
        field, coordinate, rational = row["exact_off_axis"]
        residue = Fraction(rational)
        counterpart = primary[tuple(row["key"])]
        assert row["status"] == counterpart["decision"] == "excluded"
        assert field == "column" and residue
        assert counterpart["outside_column"] == [
            coordinate - 36, residue.numerator * pow(residue.denominator, -1, modulus) % modulus,
        ]
    eligible = []
    distinct = 0
    for left, right in combinations(sorted(keys), 2):
        if left[0] == right[0] or left[1] == right[1]:
            continue
        distinct += 1
        if even[left[1]] == even[right[1]]:
            eligible.append({"fusions": [left, right], "even_mask": even[left[1]]})
    eligible.sort(key=lambda row: (-len(row["even_mask"]), row["fusions"]))
    by_size = Counter(len(row["even_mask"]) for row in eligible)
    assert distinct == 11938 and len(eligible) == 210
    assert by_size == {1: 184, 2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 4, 8: 2}
    return distinct, eligible, by_size


def signed(hist):
    return Counter({int(rank): multiplicity for rank, multiplicity in hist.items()})


def main():
    cli = ArgumentParser()
    cli.add_argument("--r85", type=Path, required=True)
    options = cli.parse_args()
    root = options.r85.resolve()
    doc = authenticated(root)
    stock, lead, exact = (doc[name] for name in ("price/PRICE.json", "lead/RESULT.json",
                                                "independent/RESULT.json"))
    admit = doc["price/inputs/7334-ADMITTED.json"]
    complete = doc["price/inputs/7334-READBACK.json"]
    assert admit["head"] == stock["head"] == complete["head"] == HEAD and admit["exit"] == 0
    assert admit["caller"] == stock["caller_head"] == complete["caller_head"] == CALLER
    assert admit["caller_sha256"] == stock["caller_sha256"] == CALLER_SHA
    assert stock["copies"] == complete["copies"] == 17 and stock["ports"] == 8
    paid, targets = signed(complete["paid"]), signed(complete["targets"])
    assert paid == signed(stock["complete_paid"]) and targets == signed(stock["complete_targets"])
    assert sum(paid.values()) == 110519 and sum(targets.values()) == 22461
    net = targets.copy()
    net.subtract(paid)
    assert sum(rank * count for rank, count in net.items()) == 1424
    assert complete["empty_root_credits"] == 0
    lo, hi = map(Fraction, admit["crossing"])
    assert (lo, hi) == tuple(map(Fraction, stock["crossing"]))
    assert (lo, hi) == tuple(map(Fraction, complete["new_raw_interval"]))
    bit = Fraction(complete["bit_premise"])
    assert bit == Fraction(stock["retained_BIT"])
    probe = hi + Fraction(1, 10**9)
    distinct, keys, by_size = inventory(stock, lead, exact)
    tariff = run_path(str(root / "price/inputs/pricing.py"))
    cost = tariff["cost"]
    derivative = run_path(str(root / "price/inputs/derivative_check.py"))["derivative"]
    prices = {}
    for size, count in sorted(by_size.items()):
        # Two call deletions per port: each old odd + even pair becomes one union.
        credit_hist = Counter({9: 16, 8 * size: 16, 8 * size + 9: -16})
        assert sum(credit_hist.values()) == 16
        assert sum(r * n for r, n in credit_hist.items()) == 0
        changed = net.copy()
        changed.update(credit_hist)
        assert sum(paid.values()) - sum(credit_hist.values()) == 110503
        credit, target_credit = cost(credit_hist, hi), cost(credit_hist, TARGET)
        old_quote, new_quote = cost(changed, hi), cost(changed, probe)
        assert 0 < credit[0] <= credit[1] and 0 < new_quote[0] <= new_quote[1]
        assert credit[1] == 2 * Fraction(stock["prices_by_even_mask_size"][str(size)]["credit"][1])
        assert target_credit[1] == 2 * Fraction(stock["prices_by_even_mask_size"][str(size)]["target_credit"][1])
        one, two = changed.copy(), changed.copy()
        one[1] -= 1
        two[1] -= 2
        debit_bounds = cost(two, lo)
        debit_slope = derivative(two, lo, bit, tariff)
        assert debit_bounds[1] < 0 and debit_slope[1] < 0
        prices[size] = {
            "keys": count,
            "paid_delta": {r: -n for r, n in credit_hist.items()},
            "gross_credit_at_old_upper": bounds(credit),
            "gross_credit_at_fixed_target": bounds(target_credit),
            "complete_margin_at_old_upper": bounds(old_quote),
            "complete_margin_at_probe": bounds(new_quote),
            "complete_margin_with_one_raw_rank_one_debit_at_old_upper": bounds(cost(one, hi)),
            "complete_margin_with_two_raw_rank_one_debits_at_old_lower": bounds(debit_bounds),
            "complete_derivative_with_two_debits_through_retained_BIT": bounds(debit_slope),
            "complete_margin_at_fixed_target": bounds(cost(changed, TARGET)),
        }
    assert all(Fraction(prices[m]["gross_credit_at_old_upper"][1]) <
               Fraction(prices[m+1]["gross_credit_at_old_upper"][1]) for m in range(1, 8))
    assert all(Fraction(prices[m]["gross_credit_at_fixed_target"][1]) <
               Fraction(prices[m+1]["gross_credit_at_fixed_target"][1]) for m in range(1, 8))
    largest = prices[8]
    assert Fraction(largest["complete_margin_at_fixed_target"][1]) < 0
    assert Fraction(largest["complete_margin_with_one_raw_rank_one_debit_at_old_upper"][0]) > 0
    print(dumps({
        "head": HEAD, "caller": CALLER, "caller_sha256": CALLER_SHA,
        "R85_path_pins": PINS, "scope": "Two disjoint fixed-odd-clock unions; no other edits",
        "old_crossing": bounds((lo, hi)), "price_probe": str(probe), "fixed_target": str(TARGET),
        "retained_BIT": str(bit), "complete_native_copies": 17, "Type_B_ports": 8,
        "old_complete_paid": paid, "complete_productive": targets, "new_paid_positions": 110503,
        "productive_fields": 22461, "rank_surplus": 1424, "empty_root_credit": 0,
        "all_disjoint_pair_placements": distinct, "unequal_mask_exclusions": distinct - len(keys),
        "equal_mask_keys": keys, "prices_by_even_mask_size": prices,
        "max_gross_at_old_upper": largest["gross_credit_at_old_upper"][1],
        "max_gross_at_fixed_target": largest["gross_credit_at_fixed_target"][1],
        "max_complete_margin_at_fixed_target": largest["complete_margin_at_fixed_target"][1],
        "first_gate": {"keys": 210, "runner_seconds": 25},
        "formal_gate": {"keys": 4, "runner_seconds": 35},
        "literal_word_or_caller_decoded": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
