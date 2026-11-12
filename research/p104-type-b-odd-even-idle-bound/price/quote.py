"""Predecode exact same-clock Type B odd/even idle fusion stock and price."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parent / "inputs"
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
TARGET = Q("0.0040075385047236")
PINS = {
    "R59-PRICE.json": "b73057381860987c6de1666205e91a0e3d116a8299d8aa425682f5960609c21f",
    "R53-PRICE.json": "86f779c3eeb43563793e6ccb2227257ef732b2ca12fbbde2f9099988f903a484",
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "7334-ADMITTED.json": "c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13",
    "7334-READBACK.json": "337668788fb39ec9575887f9c5faf438a880471f78d936357dabf7deeac5de82",
    "derivative_check.py": "348c8b2de72f1f112cb1337eca9d29ca96c85a7ad903beecafb1a2a1221f408e",
}


def check(condition, message):
    if not condition:
        raise ValueError(message)


def unique(rows):
    obj = dict(rows)
    check(len(obj) == len(rows), "duplicate JSON input key")
    return obj


def file(name):
    raw = (ROOT / name).read_bytes()
    check(sha256(raw).hexdigest() == PINS[name], "changed input " + name)
    return raw


def inv(profile):
    return Counter({int(r): n for r, n in profile.items()})


def delta(m):
    return Counter({9: 8, m * 8: 8, m * 8 + 9: -8})


def signed_copy(old, d):
    new = old.copy()
    new.update(d)
    return new


def text(qs):
    return [str(q) for q in qs]


def best_matching(odd, even, scores):
    ordered = sorted(odd)
    dp = {0: (Q(0), ())}
    for receiver, (_, stages) in sorted(even.items()):
        options = [(1 << i, donor) for i, donor in enumerate(ordered)
                   if set(stages).isdisjoint(odd[donor][1])]
        after = dp.copy()
        for occupied, (value, keys) in dp.items():
            for bit, donor in options:
                if occupied & bit:
                    continue
                key = occupied | bit
                candidate = (value + scores[len(stages)], tuple(sorted((*keys, (donor, receiver)))))
                if key not in after or candidate > after[key]:
                    after[key] = candidate
        dp = after
    return dp


def main():
    raw = {name: file(name) for name in PINS}
    r59, r53, admitted, r68 = (loads(raw[name], object_pairs_hook=unique) for name in
        ("R59-PRICE.json", "R53-PRICE.json", "7334-ADMITTED.json", "7334-READBACK.json"))
    check(admitted["head"] == r68["head"] == HEAD and admitted["exit"] == 0, "wrong comparator")
    check(r59["caller_head"] == r53["caller_head"] == admitted["caller"] == r68["caller_head"] == CALLER,
          "wrong caller")
    check(admitted["caller_sha256"] == PINS["7113-CALLER.json"] and r53["type_b_ports"] == 8 and r68["copies"] == 17,
          "wrong signed caller census")
    odd = {int(c): row for c, row in r59["odd_jobs"].items()}
    even = {c: [r, stages] for c, r, stages in r53["job_masks"]}
    check(len(odd) == 4 and len(even) == 60 and not odd.keys() & even.keys(), "wrong idle stock")
    check({c: [r, sorted(mask)] for c, (r, mask) in even.items() if len(mask) > 1} ==
          {int(c): [r, sorted(mask)] for c, (r, mask) in r59["even_jobs"].items()},
          "inconsistent larger even stock")
    check(sorted(odd) == [1339, 1340, 2970, 2971] and all(len(v[1]) == 1 for v in odd.values()),
          "wrong odd singleton stock")
    keys = [{"odd": o, "even": e, "size": len(b)} for o, (_, a) in sorted(odd.items())
            for e, (_, b) in sorted(even.items()) if set(a).isdisjoint(b)]
    counts = Counter(key["size"] for key in keys)
    check(len(keys) == 180 and counts == {1: 128, 2: 8, 3: 8, 4: 8, 5: 8, 6: 8, 7: 8, 8: 4},
          "wrong disjoint key count")
    check(any((p["odd"], p["even"]) == (1339, 2324) for p in keys), "missing overlap control")

    paid, targets = inv(r68["paid"]), inv(r68["targets"])
    net = targets.copy()
    net.subtract(paid)
    check((sum(paid.values()), sum(targets.values()), sum(r * n for r, n in net.items())) == (110519, 22461, 1424)
          and r68["empty_root_credits"] == 0, "wrong complete invoice")
    lo, hi = map(Q, admitted["crossing"])
    check((lo, hi) == tuple(map(Q, r68["new_raw_interval"])), "wrong exact crossing")
    bit = Q(r68["bit_premise"])
    tariff = run_path(str(ROOT / "pricing.py"))
    cost = tariff["cost"]
    probe = hi + Q(1, 10**9)
    prices, crossing_weights, target_weights = {}, {}, {}
    for m in sorted(counts):
        d = delta(m)
        check(sum(d.values()) == 8 and sum(r * n for r, n in d.items()) == 0, "wrong paid count or rank mass")
        candidate = signed_copy(net, d)
        credit, target_credit = cost(d, hi), cost(d, TARGET)
        margin, at_probe = cost(candidate, hi), cost(candidate, probe)
        new_cost = cost({8 * m + 9: 8}, hi)
        check(0 < credit[0] <= credit[1] < 1 and 0 < margin[0] and 0 < at_probe[0], "wrong price sign")
        crossing_weights[m], target_weights[m] = credit[1], target_credit[1]
        prices[m] = {"cases": counts[m], "paid_delta": {r: -n for r, n in d.items()},
                     "credit": text(credit), "target_credit": text(target_credit),
                     "complete_margin_at_crossing_upper": text(margin), "complete_margin_at_probe": text(at_probe),
                     "break_even_volume_before_ancillary_cost": text(
                         (1 + margin[0] / new_cost[1], 1 + margin[1] / new_cost[0]))}
    check(all(crossing_weights[a] < crossing_weights[a + 1] and target_weights[a] < target_weights[a + 1]
              for a in range(1, 8)), "bad concave credit ordering")
    on_old = best_matching(odd, even, crossing_weights)
    on_target = best_matching(odd, even, target_weights)
    best, match = max(on_old.values())
    target_upper, target_match = max(on_target.values())
    check(max(k.bit_count() for k in on_old) == len(match) == len(target_match) == 4, "wrong maximum stock")
    check(sorted(len(even[c][1]) for _, c in match) == [7, 7, 8, 8], "wrong maximum price group")
    whole_delta = Counter()
    for _, e in target_match:
        whole_delta.update(delta(len(even[e][1])))
    optimistic_target = cost(signed_copy(net, whole_delta), TARGET)
    check(optimistic_target[1] < 0 and cost(net, probe)[1] < 0, "wrong incumbent or moonshot sign")
    one_extra = signed_copy(net, delta(8))
    one_extra[1] -= 1
    derivative = run_path(str(ROOT / "derivative_check.py"))["derivative"](one_extra, lo, bit, tariff)
    extra_margin = cost(one_extra, lo)
    check(derivative[1] < 0 and extra_margin[1] < 0, "one edit paid debit not certified")
    print(dumps({
        "head": HEAD, "caller_head": CALLER, "caller_sha256": PINS["7113-CALLER.json"], "inputs": PINS,
        "crossing": [str(lo), str(hi)], "retained_BIT": str(bit), "moonshot": str(TARGET),
        "complete_paid": paid, "complete_targets": targets, "ports": 8, "copies": 17,
        "odd_jobs": odd, "even_jobs": even, "keys": keys, "prices_by_even_mask_size": prices,
        "stock": len(keys), "odd_jobs_degrees": dict(Counter(r["odd"] for r in keys)),
        "one_edit_optimistic_upper": str(crossing_weights[8]), "maximum_disjoint_pairs": 4,
        "whole_compatible_upper": str(best), "whole_upper_matching": match,
        "whole_upper_by_odd_mask": {mask: str(v[0]) for mask, v in on_old.items()},
        "old_margin_at_moonshot": text(cost(net, TARGET)),
        "moonshot_whole_compatible_upper": str(target_upper), "moonshot_matching": target_match,
        "moonshot_upper_full_margin": text(optimistic_target), "price_probe": str(probe),
        "one_edit_extra_rank_one_margin_at_lower": text(extra_margin),
        "one_edit_extra_rank_one_derivative_through_BIT": text(derivative),
        "limits": {"first_cases": 180, "first_seconds": 20, "next_cases": 12, "next_seconds": 25,
                   "formal_cases": 2, "formal_seconds": 60, "physical_cases": 1, "physical_seconds": 90},
        "scope": "One same-volume signed union at the retained odd clock. Matching upper forbids repeated literal sites and grants all other compatibility and ancillary work free. No caller decoded.",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
