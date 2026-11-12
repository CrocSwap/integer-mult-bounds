"""Exact upper quote for the highest-ranked pair after roots 0/18."""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}


def read(path):
    raw = (ROOT / path).read_bytes()
    assert sha256(raw).hexdigest() == PINS[path]
    return raw


def main():
    for path in PINS:
        read(path)
    base = loads(read("inputs/R92-PRICE.json"))
    caller = loads(read("inputs/CALLER.json"))
    ranks = [1 + 8 * sum(row[2:]) for row in caller["types"]["A"]["diagonal"]]
    assert sorted(ranks)[-4:] == [73, 73, 137, 137]
    assert (ranks[0], ranks[17]) == (137, 73)
    delta = Counter({1: 192, 72: 96, 73: -96, 136: 96, 137: -96})
    cost = run_path(str(ROOT / "inputs/pricing.py"))["cost"]
    stock = Counter({int(r): n for r, n in base["old_targets"].items()})
    stock.subtract({int(r): n for r, n in base["old_paid"].items()})
    stock.update(delta)
    assert sum(r * n for r, n in stock.items()) == 1424
    quote = {
        "roots": [0, 17], "ranks": [137, 73], "signed_histogram_delta": delta,
        "head": base["head"], "caller_head": base["caller_head"], "pins": PINS,
        "gross_at_crossing_upper": cost(delta, Fraction(base["old_crossing_upper"])),
        "complete_at_probe": cost(stock, Fraction(base["probe"])),
    }
    assert quote["gross_at_crossing_upper"][0] > 0
    assert quote["complete_at_probe"][0] > 0
    print(dumps(quote, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    assert __debug__
    main()
