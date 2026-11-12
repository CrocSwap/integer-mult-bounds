"""Price adjacent equal-chart public MOVE compression on the exact #7334 source."""
from collections import Counter
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
COPIES = 17


def unique(items):
    data = dict(items)
    assert len(data) == len(items), "duplicate key"
    return data


def read(path):
    raw = (ROOT / path).read_bytes()
    assert sha256(raw).hexdigest() == PINS[path], path
    return raw


def main():
    assert __debug__
    raw = decompress(read("inputs/7334-WORD.json.gz"))
    assert sha256(raw).hexdigest() == PAYLOAD
    w = loads(raw, object_pairs_hook=unique)
    b = loads(read("inputs/R92-PRICE.json"), object_pairs_hook=unique)
    read("inputs/pricing.py")
    cost = run_path(str(ROOT / "inputs/pricing.py"))["cost"]
    assert (b["head"], b["caller_head"]) == (HEAD, CALLER)
    tape = w["program"]
    assert (w["public"], len(tape)) == (1501, 76466)
    pairs = []
    for k, (a, c) in enumerate(zip(tape, tape[1:])):
        if a[0] != "MOVE" or c[0] != "MOVE" or a[4] or c[4] or a[2:4] != c[2:4] or a[1] == c[1]:
            continue
        assert a[1] < w["public"] and c[1] < w["public"]
        rank = len(w["frames"][a[3]]) - len(w["frames"][a[2]])
        assert rank > 0
        pairs.append([k, a[1], c[1], a[2], a[3], rank])
    counts = Counter(x[-1] for x in pairs)
    assert counts == {1: 7, 3: 4, 4: 1, 5: 17}
    assert len({i for p in pairs for i in (p[0],p[0]+1)}) == 2*len(pairs)
    candidate = min(pairs, key=lambda p: (-p[-1],p[0]))
    assert candidate == [32944, 625, 624, 3, 117, 5]
    old_paid = {int(r): n for r, n in b["old_paid"].items()}
    old_targets = {int(r): n for r, n in b["old_targets"].items()}
    assert (sum(old_paid.values()), sum(old_targets.values())) == (110519, 22461)
    stock = Counter(old_targets)
    stock.subtract(old_paid)
    assert sum(r*n for r,n in stock.items()) == 1424
    k, probe = Q(b["old_crossing_upper"]), Q(b["probe"])
    delta = {candidate[-1]: COPIES}
    full = stock.copy()
    full.update(delta)
    gross = cost(delta, k)
    margin = cost(full, probe)
    whole = {r: COPIES*n for r,n in counts.items()}
    # Two charged writes, six conservative local map/metadata slots and four scalar units.
    ordinary = 782715464 + COPIES*(2*340+6*1000+4)
    assert 0 < gross[0] <= gross[1] and margin[0] > 0 and ordinary < 10**9
    print(dumps({
        "head": HEAD, "caller": CALLER, "pins": PINS, "native_calls": COPIES,
        "candidate": candidate, "literal_pair_count": len(pairs), "pairs": pairs,
        "distinct_pair_ranks": counts, "new_paid_children": 0,
        "complete_paid_count_if_realized": sum(old_paid.values())-COPIES,
        "productive_count_if_realized": sum(old_targets.values()),
        "signed_histogram_delta": delta, "relaxed_whole_signed_delta": whole,
        "relaxed_whole_gross_upper_interval": cost(whole, k),
        "one_pair_gross_interval": gross, "complete_margin_at_probe": margin,
        "old_crossing_upper": str(k), "probe": str(probe),
        "ordinary_source_units_provisional_upper": ordinary,
        "ordinary_source_units_allowance": 10**9,
        "qualification": "price only: exact zero-column action and all-size lowering still required"
    }, sort_keys=True, indent=2, default=str))


if __name__ == "__main__":
    main()
