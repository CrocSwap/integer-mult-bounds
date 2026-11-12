"""Price a proper helper entrance absorption before inspecting the word."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"


def unique(items):
    result = dict(items)
    assert len(result) == len(items), "Duplicate JSON key"
    return result


def main():
    assert __debug__
    for name, digest in PINS.items():
        assert sha256((ROOT / name).read_bytes()).hexdigest() == digest
    base = loads((ROOT / "inputs/R92-PRICE.json").read_bytes(), object_pairs_hook=unique)
    assert base["head"] == HEAD and base["caller_head"] == CALLER
    paid, target = [Counter({int(r): n for r, n in base[k].items()})
                    for k in ("old_paid", "old_targets")]
    stock = target.copy()
    stock.subtract(paid)
    assert (paid.total(), target.total(), sum(r*n for r, n in stock.items())) == (110519, 22461, 1424)
    k = Q(base["old_crossing_upper"])
    cost = run_path(str(ROOT / "inputs/pricing.py"))["cost"]
    original = cost(stock, k)
    assert original[1] < 0

    cases = {}
    for r in range(2, 10):
        for d in range(1, r):
            delta = Counter({r: -17})
            delta.update([d]*(17) + [r-d]*(17))
            assert sum(rank*n for rank, n in delta.items()) == 0
            changed = stock.copy()
            changed.update(delta)
            gross = cost(delta, k)
            full = cost(changed, k)
            changed[1] -= 1
            extra = cost(changed, k)
            assert gross[0] > 0 and full[0] > 0 > extra[1]
            cases[f"{r}/{d}"] = {
                "paid_delta": {d: -17}, "target_delta": {r: -17, r-d: 17},
                "gross": [str(x) for x in gross],
                "full": [str(x) for x in full],
                "full_plus_one_rank_one": [str(x) for x in extra],
            }
    max_gross = max(Q(row["gross"][1]) for row in cases.values())
    assert max_gross == Q(cases["9/4"]["gross"][1])
    print(dumps({"head": HEAD, "caller": CALLER, "pins": PINS, "crossing_upper": str(k),
                 "gross_whole_stock_upper": str(1101*max_gross),
                 "one_edit_gross_upper": str(max_gross), "cases": cases,
                 "tested_candidates": 0, "whole_stock_relaxation_roles": 1101,
                 "scope": "One proper first MOVE absorbed per productive helper. No price credit for ordinary reductions. Grant all replacement ordinary costs zero in the optimistic upper."},
                indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
