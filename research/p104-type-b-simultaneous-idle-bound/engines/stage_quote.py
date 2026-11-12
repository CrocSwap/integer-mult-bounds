"""Price all simultaneous fixed-clock fusions and freeze a stagewise support gate."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from json import dumps
from math import comb
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = "inputs/r123_quote.py"
PREDECESSOR_SHA = "3a676f5d102c3aa02522937b85275b0fb16cfce98797c667370e85c91774e05c"


def matching(keys, odd, even, weights):
    states = {0: (Fraction(0), [])}
    for e, mask in even.items():
        following = states.copy()
        for seen, (score, edges) in states.items():
            for index, o in enumerate(odd):
                bit = 1 << index
                if seen & bit or (o, e) not in keys:
                    continue
                new = (score + weights[len(mask)], edges + [[o, e]])
                if seen | bit not in following or new[0] > following[seen | bit][0]:
                    following[seen | bit] = new
        states = following
    return max(states.values(), key=lambda row: row[0])


def hist(rows):
    return Counter({int(k): v for k, v in rows.items()})


def bill(edges, even):
    result = Counter()
    for _, e in edges:
        size = len(even[e])
        result.update({9: 8, 8 * size: 8, 8 * size + 9: -8})
    return result


def main():
    assert __debug__
    script = ROOT / PREDECESSOR
    if sha256(script.read_bytes()).hexdigest() != PREDECESSOR_SHA:
        raise ValueError("changed predecessor price engine")
    previous = run_path(str(script))
    source = ROOT / "r85"
    docs = previous["authenticated"](source)
    stock = docs["price/PRICE.json"]
    previous["inventory"](stock, docs["lead/RESULT.json"], docs["independent/RESULT.json"])
    even = {int(e): sorted(mask) for e, (_, mask) in stock["even_jobs"].items()}
    odd = {int(o): sorted(mask) for o, (_, mask) in stock["odd_jobs"].items()}
    keys = {(x["odd"], x["even"]) for x in stock["keys"]}
    tariff = run_path(str(source / "price/inputs/pricing.py"))["cost"]
    at = Fraction(stock["crossing"][1])
    target = Fraction(stock["moonshot"])
    paid, productive = hist(stock["complete_paid"]), hist(stock["complete_targets"])
    old = productive.copy()
    old.subtract(paid)
    assert (sum(paid.values()), sum(productive.values()), sum(r * n for r, n in old.items())) == (110519, 22461, 1424)
    by_size = stock["prices_by_even_mask_size"]
    optimum, edges = matching(keys, odd, even, {int(m): Fraction(row["credit"][1]) for m, row in by_size.items()})
    moon_credit, moon_edges = matching(keys, odd, even,
                                       {int(m): Fraction(row["target_credit"][1]) for m, row in by_size.items()})
    assert len(edges) == len(moon_edges) == len(odd) == 4
    assert optimum == Fraction(stock["whole_compatible_upper"])
    assert moon_credit == Fraction(stock["moonshot_whole_compatible_upper"])
    assert tariff(bill(edges, even), at)[1] <= optimum
    signed_delta = bill(edges, even)
    new = old.copy()
    new.update(signed_delta)
    assert sum(signed_delta.values()) == 32 and sum(r * n for r, n in new.items()) == 1424
    assert tariff(new, at + Fraction(1, 10**9))[0] > 0
    stages, relaxed = [], 0
    for j in range(1, 18):
        o = [clock for clock, mask in odd.items() if j not in mask]
        e = [clock for clock, mask in even.items() if j in mask]
        comparisons = sum(comb(len(odd), k) * comb(len(e), k) for k in range(1, 5))
        stages.append({"stage": j, "odd": sorted(o), "even": sorted(e), "relaxed_comparisons": comparisons})
        relaxed += comparisons
    assert relaxed == 26075
    print(dumps({
        "head": stock["head"], "caller": stock["caller_head"], "caller_sha256": stock["caller_sha256"],
        "pins": {PREDECESSOR: PREDECESSOR_SHA}, "r85_pins": previous["PINS"],
        "old_crossing_upper": str(at), "fixed_target": str(target),
        "whole_compatible_credit_upper": str(optimum),
        "complete_old_crossing_upper": str(tariff(old, at)[1] + optimum),
        "paid_count_at_upper_witness": 110487, "productive": 22461, "rank_surplus": 1424,
        "paid_delta_at_upper_witness": {r: -n for r, n in signed_delta.items() if n},
        "matching_witness": edges, "fixed_target_matching": moon_edges,
        "fixed_target_complete_upper": str(tariff(old, target)[1] + moon_credit),
        "relaxed_comparisons": relaxed, "stages": stages, "odd_masks": odd, "even_masks": even,
        "limits": {"stages": 17, "relaxed_comparisons": 26075, "seconds": 25,
                   "coupled_cases": 4096, "coupled_seconds": 35,
                   "formal_cases": 4, "formal_seconds": 35, "prototype_seconds": 90},
        "scope": "Up to four disjoint fixed-odd-clock Type B unions. Necessary stagewise projector equality; complete signed price is optimistic before any ancillary cost.",
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
