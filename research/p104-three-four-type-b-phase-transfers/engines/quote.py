"""Predecode rank-multiset price and exact 3+3/4+4 Type B stock."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
from json import dumps, loads
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parent / "inputs"
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER_HEAD = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
TARGET = Q("0.0040075385047236")
PINS = {
    "R59-PRICE.json": "b73057381860987c6de1666205e91a0e3d116a8299d8aa425682f5960609c21f",
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "7334-ADMITTED.json": "c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13",
    "7334-READBACK.json": "337668788fb39ec9575887f9c5faf438a880471f78d936357dabf7deeac5de82",
    "derivative_check.py": "348c8b2de72f1f112cb1337eca9d29ca96c85a7ad903beecafb1a2a1221f408e",
}


def unique(rows):
    value = dict(rows)
    if len(rows) != len(value):
        raise ValueError("duplicate JSON input key")
    return value


def authenticated():
    files = {}
    for name, expected in PINS.items():
        raw = (ROOT / name).read_bytes()
        if sha256(raw).hexdigest() != expected:
            raise ValueError("changed input " + name)
        files[name] = raw
    return files


def ranks(data):
    return Counter({int(k): n for k, n in data.items()})


def delta_for(multiset):
    change = Counter()
    for m in multiset:
        change.update({9: 8, 8 * m: 8, 8: -8, 8 * m + 1: -8})
    assert sum(change.values()) == sum(r * v for r, v in change.items()) == 0
    return change


def combine(old, delta):
    result = old.copy()
    result.update(delta)
    return result


def interval(values):
    return list(map(str, values))


def main(args):
    files = authenticated()
    old = loads(files["R59-PRICE.json"], object_pairs_hook=unique)
    admission = loads(files["7334-ADMITTED.json"], object_pairs_hook=unique)
    readback = loads(files["7334-READBACK.json"], object_pairs_hook=unique)
    assert admission["head"] == readback["head"] == HEAD and admission["exit"] == 0
    assert admission["caller"] == readback["caller_head"] == old["caller_head"] == CALLER_HEAD
    assert admission["caller_sha256"] == old["input_sha256"]["inputs/7113/CALLER.json"] == PINS["7113-CALLER.json"]
    assert readback["copies"] == old["copies"] == 17 and readback["empty_root_credits"] == 0
    assert old["complete_targets"] == readback["targets"]
    odd = {int(k): v for k, v in old["odd_jobs"].items()}
    even = {int(k): v for k, v in old["even_jobs"].items()}
    assert sorted(odd) == [1339, 1340, 2970, 2971] and all(len(v[1]) == 1 for v in odd.values())
    assert len(even) == 26 and not odd.keys() & even.keys()
    assert Counter(len(v[1]) for v in even.values()) == {2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 4, 8: 2}

    paid, productive = ranks(readback["paid"]), ranks(readback["targets"])
    net = productive.copy()
    net.subtract(paid)
    assert sum(paid.values()) == 110519 and sum(productive.values()) == 22461
    assert sum(r * n for r, n in net.items()) == 1424
    lo, hi = map(Q, admission["crossing"])
    assert (lo, hi) == tuple(map(Q, readback["new_raw_interval"]))
    bit = Q(readback["bit_premise"])
    assert lo < hi < bit < TARGET
    tariff = run_path(str(ROOT / "pricing.py"))
    cost = tariff["cost"]
    current = cost(net, hi)
    assert current[1] < 0
    probe = hi + Q(1, 10**9)

    keys = []
    multiset_classes = {}
    by_count = {}
    for n, cases, classes in ((3, 10400, 83), (4, 14950, 203)):
        marks = []
        stock = Counter()
        for evens in combinations(sorted(even), n):
            m = tuple(sorted(len(even[t][1]) for t in evens))
            kind = ",".join(map(str, m))
            marks.append((evens, kind))
            stock[m] += 1
        assert len(stock) == classes
        groups = list(combinations(sorted(odd), n))
        for odds in groups:
            for evens, kind in marks:
                keys.append({"odd": odds, "even": evens, "price": kind})
        assert len(groups) * len(marks) == cases
        for m, count in sorted(stock.items()):
            delta = delta_for(m)
            candidate = combine(net, delta)
            new_paid = paid.copy()
            new_paid.subtract(delta)
            assert sum(new_paid.values()) == 110519 and all(v >= 0 for v in new_paid.values())
            credit, margin = cost(delta, hi), cost(candidate, hi)
            assert 0 < credit[0] <= credit[1] < 1 and margin[0] > 0
            multiset_classes[",".join(map(str, m))] = {
                "mask_sizes": m, "receiver_combinations": count, "keys": len(groups) * count,
                "paid_delta": {r: -v for r, v in delta.items() if v}, "credit": interval(credit),
                "complete_margin_at_crossing_upper": interval(margin),
                "complete_margin_at_probe": interval(cost(candidate, probe)),
                "added_paid_rank_one_upper_at_crossing": str(margin[1] - 1),
            }
        best = tuple(sorted((len(v[1]) for v in even.values()), reverse=True)[:n][::-1])
        best_delta = delta_for(best)
        new = combine(net, best_delta)
        charged = new.copy()
        charged[1] -= 1
        derivative = run_path(str(ROOT / "derivative_check.py"))["derivative"](charged, lo, bit, tariff)
        charged_lower = cost(charged, lo)
        assert derivative[1] < 0 and charged_lower[1] < 0
        worst_at_target = cost(new, TARGET)
        assert worst_at_target[1] < 0
        best_name = ",".join(map(str, best))
        assert Q(multiset_classes[best_name]["credit"][1]) == max(
            Q(r["credit"][1]) for r in multiset_classes.values() if len(r["mask_sizes"]) == n)
        by_count[n] = {
            "keys": cases, "classes": classes, "maximum_multiset": best,
            "compatible_gross_upper": multiset_classes[best_name]["credit"][1],
            "one_extra_rank_one_at_crossing_lower": interval(charged_lower),
            "maximum_complete_derivative_through_BIT": interval(derivative),
            "maximum_target_credit": interval(cost(best_delta, TARGET)),
            "maximum_target_margin": interval(worst_at_target),
        }
    assert len(keys) == 25350 and len(multiset_classes) == 286
    key_bytes = (dumps(keys, sort_keys=True, separators=(",", ":")) + "\n").encode()
    with args.keys_out.open("xb") as out:
        out.write(key_bytes)
    print(dumps({
        "head": HEAD, "caller_head": CALLER_HEAD, "caller_sha256": PINS["7113-CALLER.json"],
        "input_sha256": PINS, "keys_sha256": sha256(key_bytes).hexdigest(), "keys": len(keys),
        "odd_jobs": odd, "even_jobs": even, "prices_by_mask_multiset": multiset_classes,
        "stock_by_number_of_transfers": by_count, "complete_paid": paid, "complete_targets": productive,
        "signed_surplus": 1424, "copies": 17, "ports": 8, "empty_root_credit": 0,
        "crossing": [str(lo), str(hi)], "old_complete_margin": interval(current),
        "price_only_probe": str(probe), "old_probe_margin": interval(cost(net, probe)),
        "retained_BIT": str(bit), "fixed_moonshot": str(TARGET), "old_target_margin": interval(cost(net, TARGET)),
        "whole_compatible_upper": by_count[4]["compatible_gross_upper"],
        "limits": {"first_keys": 25350, "first_runner_seconds": 35, "first_cooperative_seconds": 32,
                   "nonunit_keys": 16, "nonunit_runner_seconds": 25, "formal_keys": 2,
                   "formal_runner_seconds": 60, "physical_keys": 1, "physical_runner_seconds": 90},
        "scope": "Only exactly 3 or 4 simultaneous fixed-clock transfers, no altered body masks, J blocks or owner roles. Price assumes no additional paid child and no ancillary costs. Caller authenticated without decode."
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--keys-out", type=Path, required=True)
    main(parser.parse_args())
