"""Directed predecode invoice for one owned chart-turn contraction."""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations_with_replacement
from json import dumps, loads
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/ADMITTED.json": "c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13",
    "inputs/READBACK.json": "337668788fb39ec9575887f9c5faf438a880471f78d936357dabf7deeac5de82",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "inputs/7277-OWNED.json": "f5df458b659a7fdcec6745d8a8ab583a0b94c3bd6d79acfaa5771c9263e0006c",
    "inputs/7277-CONTACTS.json": "4b5641bd6b4359466b89cf0f9f9a3b17c0fbcc533475caf9d1a0aa80672f5a1a",
}
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
LEGACY = "ed090b57ed88f8859e5ff4643645099e6ba856ea"


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def histogram(item):
    result = Counter({int(rank): count for rank, count in item.items()})
    assert len(result) == len(item)
    assert all(rank > 0 and type(count) is int and count > 0 for rank, count in result.items())
    return result


def main():
    assert __debug__
    raw = {}
    for name, pin in PINS.items():
        raw[name] = (ROOT / name).read_bytes()
        if sha256(raw[name]).hexdigest() != pin:
            raise ValueError(f"changed dependency {name}")

    def read(name):
        return loads(raw[f"inputs/{name}.json"], object_pairs_hook=unique)

    base, admitted = read("READBACK"), read("ADMITTED")
    owned, old_contacts = read("7277-OWNED"), read("7277-CONTACTS")
    assert base["head"] == admitted["head"] == HEAD
    assert admitted["exit"] == 0 and admitted["status"] == "independently_reproduced_comparable"
    assert base["caller_head"] == admitted["caller"]
    assert owned["scientific_head"] == old_contacts["head"] == LEGACY
    assert owned["scope_exhausted"] and old_contacts["next_contact_counts"] == {"ADD": 43, "SCALE": 4}
    stock = histogram(owned["paid_owned_histogram"])
    assert sum(stock.values()) == owned["paid_owned_moves"] == 47
    copies = base["copies"]
    assert copies == 17 and not base["empty_root_credits"]
    paid, targets = histogram(base["paid"]), histogram(base["targets"])
    assert (sum(paid.values()), sum(targets.values())) == (110519, 22461)
    signed = targets.copy()
    signed.subtract(paid)
    assert sum(r*n for r, n in signed.items()) == base["rank_surplus"] == 1424
    cost = run_path(str(ROOT / "inputs/pricing.py"))["cost"]
    crossing = Fraction(base["new_raw_interval"][1])
    probe = crossing + Fraction(1, 10**9)
    moonshot = Fraction("0.0040075385047236")
    assert cost(signed, crossing)[1] < 0

    def interval(values):
        return list(map(str, values))

    quotes = {}
    for a, b in combinations_with_replacement(sorted(stock), 2):
        if a == b and stock[a] < 2:
            continue
        delta = Counter()
        delta[a] -= copies
        delta[b] -= copies
        direct_rank = b - a
        if direct_rank:
            delta[direct_rank] += copies
        changed = signed.copy()
        changed.subtract(delta)
        at_crossing = cost(changed, crossing)
        at_probe = cost(changed, probe)
        assert at_crossing[0] > 0 and at_probe[0] > 0
        quotes[f"{a},{b}"] = {
            "paid_delta": {r:n for r,n in sorted(delta.items()) if n},
            "direct_rank": direct_rank,
            "paid_positions": sum(paid.values()) + sum(delta.values()),
            "productive_positions": sum(targets.values()),
            "rank_surplus": sum(r*n for r, n in changed.items()),
            "gross_at_crossing": interval(cost({r:-n for r,n in delta.items()}, crossing)),
            "complete_margin_at_crossing": interval(at_crossing),
            "complete_margin_at_probe": interval(at_probe),
        }

    def whole_upper(pairs, point):
        largest = Counter(sorted(stock.elements(), reverse=True)[:2*pairs])
        return str(cost({r:copies*n for r,n in largest.items()}, point)[1])

    print(dumps({
        "head": HEAD, "caller_head": admitted["caller"], "word_sha256": admitted["inputs"]["WORD.json.gz"],
        "input_sha256": PINS, "legacy_paid_owned_rank_stock": dict(stock),
        "legacy_next_contact_counts": old_contacts["next_contact_counts"],
        "old_complete_margin_at_crossing": interval(cost(signed, crossing)),
        "old_complete_margin_at_moonshot": interval(cost(signed, moonshot)),
        "old_crossing_upper": str(crossing), "price_probe": str(probe),
        "quotes": quotes, "one_edit_gross_upper_at_crossing":
            str(max(Fraction(q["gross_at_crossing"][1]) for q in quotes.values())),
        "compatible_upper_at_crossing": {str(n):whole_upper(n, crossing) for n in (4, 8, 23)},
        "compatible_upper_at_moonshot": {str(n):whole_upper(n, moonshot) for n in (4, 8, 23)},
        "build_cap": 1, "first_case_cap": 4, "runner_seconds_cap": 20,
        "scope": "Price only. Caps 4 and 8 conditional on respective start counts. The generic disjoint ceiling uses floor(47/2)=23. No word or site decoded."
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
