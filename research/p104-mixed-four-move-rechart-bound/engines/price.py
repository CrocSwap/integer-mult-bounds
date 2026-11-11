"""Whole stock price of one chart change supported by four existing paid moves."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import runpy
import sys

ADAPTER = "37cffc5f28dda64a125e5ecbd9f4c8d112296c9a21511b8d363b1c0ce362695f"
OWNED_MOVES = 47


def quote(root):
    adapter = root / "entrance_price.py"
    assert sha256(adapter.read_bytes()).hexdigest() == ADAPTER
    exact = runpy.run_path(str(adapter))["quote"](root)
    kappa = Fraction(exact["crossing_upper"])
    cost = runpy.run_path(str(root / "inputs/7298/pricing.py"))["cost"]
    values = {r: cost({r: 1}, kappa) for r in range(1, 9)}
    paid, targets = exact["paid"], exact["targets"]
    net = Counter(targets)
    net.subtract(paid)
    old = cost(net, kappa)
    assert exact["copies"] == 17 and old[1] < 0
    partitions = []
    for total in range(2, 17):
        center = [total//2, (total+1)//2]
        min_part = max(1, total-8)
        extreme = [min_part, total-min_part]
        raw = Counter(center)
        raw.subtract(extreme)
        delta = {r: 17*n for r, n in raw.items() if n}
        quote = cost(delta, kappa)
        assert sum(r*n for r, n in delta.items()) == sum(delta.values()) == 0
        partitions.append(dict(total=total, center=center, extreme=extreme,
                               directed_credit=list(map(str, quote))))
    max_pair = max(Fraction(r["directed_credit"][1]) for r in partitions)
    maximum = 2 * max_pair
    assert maximum < 1
    example = net.copy()
    example.update({2: 68, 1: -34, 3: -34})
    example_quote = cost(example, kappa)
    assert example_quote[0] > 0
    return dict(head=exact["head"], caller=exact["caller"], word_sha256=exact["input_sha256"]["inputs/7314/WORD.json.gz"],
                inputs=exact["input_sha256"] | {"entrance_price.py":ADAPTER}, crossing_upper=str(kappa),
                paid=paid, targets=targets, copies=17, signed_rank_surplus=1424, empty_credits=0,
                comparator_margin=list(map(str, old)), values={r:list(map(str, v)) for r,v in values.items()},
                partition_caps=partitions, example_margin=list(map(str, example_quote)),
                old_owned_paid=OWNED_MOVES, structural_key_upper=OWNED_MOVES,
                max_disjoint_edits=OWNED_MOVES//2, one_edit_optimistic_upper=str(maximum),
                all_disjoint_optimistic_upper=str(maximum*(OWNED_MOVES//2)),
                one_raw_rank_one_excess_upper=str(old[1]+maximum-1))


if __name__ == "__main__":
    print(json.dumps(quote(Path(sys.argv[1])), indent=2, sort_keys=True))
