"""Check the complete source chronology, exact owner incidence and physical bank operations."""

import argparse
from collections import Counter
from io import BytesIO
from pathlib import Path
import sys


def check(predecessor):
    sys.path.insert(0, str(predecessor.resolve()))
    from compiler_cut import source_rule
    from periodic import Job
    from raw_binary import Banks, BinarySource
    from streaming_routes import cold_swap_tape, work_tapes

    # Each input is an independent scalar basis vector, constant on every address.
    # A permutation fixes such a vector. This verifier does not validate nonconstant payload routing.
    class Incidence:
        dimension = 134

        def __init__(self):
            self.values = {}
            self.calls = Counter()
            self.issued = 0

        def zero(self):
            i = self.issued
            self.issued += 1
            self.values[i] = 0
            self.calls["zero"] += 1
            return i

        def clone(self, owner):
            out = self.zero()
            self.values[out] = self.values[owner]
            self.calls["clone"] += 1
            return out

        def retire(self, owner, *, require_zero=False):
            assert not require_zero or not self.values[owner]
            del self.values[owner]
            self.calls["retire"] += 1

        def route(self, owner, word):
            assert owner in self.values
            self.calls["route"] += 1
            self.calls["routed factors"] += len(word)

        def xor(self, target, source):
            self.values[target] ^= self.values[source]
            self.calls["xor"] += 1

        def swap(self, a, b):
            self.values[a], self.values[b] = self.values[b], self.values[a]
            self.calls["swap"] += 1

    src = source_rule().word
    v = Incidence()
    raw = BinarySource(v)
    inputs = []
    for i, port in enumerate(src.targets):
        v.values[i] = 1 << i
        inputs.append((port.tag, Job(i, tuple(range(port.rank)))))
    v.issued = len(inputs)
    paid = 0
    for (tag, placed), original in zip(raw.raw(inputs, 1), src.paid, strict=True):
        assert tag == original.tag and len(placed.axes) == original.rank
        assert placed.owner in v.values
        paid += 1
    assert paid == 107460
    assert len(v.values) == len(inputs) == 20706
    assert all(v.values[i] == 1 << i for i in range(len(inputs)))
    assert {key: v.calls[key] for key in ("zero", "retire", "clone", "route", "xor", "swap")} == {
        "zero": 128388,
        "retire": 128388,
        "clone": 444,
        "route": 57396,
        "xor": 1203282,
        "swap": 64884,
    }
    print(
        "actual source",
        paid,
        "paid arrivals;",
        len(inputs),
        "independent scalar returns;",
        dict(v.calls),
        flush=True,
    )

    with work_tapes(1) as (backing,):
        b = Banks(backing, 2, 2, 2, 2, cold_swap_tape)
        a, c = b.zero(), b.zero()
        one = bytes((i * 55 + i // 3 + 27) & 255 for i in range(b.volume))
        two = bytes((i * 13 - i // 7 + 11) & 255 for i in range(b.volume))

        def observe(owner):
            out = BytesIO()
            b.read(owner, out)
            return out.getvalue()

        b.install(a, BytesIO(one))
        b.install(c, BytesIO(two))
        d = b.clone(a)
        b.xor(c, d)
        assert observe(c) == bytes(x ^ y for x, y in zip(one, two, strict=True))
        b.swap(c, a)
        assert observe(c) == one and observe(d) == one
        word = (("add", 1, 0, 1), ("swap", 0, 1))
        b.route(d, word)
        assert observe(d) != one
        b.route(d, (("swap", 0, 1), ("add", 1, 0, -1)))
        assert observe(d) == one
        b.xor(d, c)
        b.retire(d, require_zero=True)
        e = b.zero()
        assert e == d and observe(e) == bytes(b.volume)
        print(
            "opaque backing",
            b.capacity,
            "owners of",
            b.volume,
            "bytes; nontrivial lifted route and return",
            flush=True,
        )


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("predecessor", type=Path)
    check(p.parse_args().predecessor)
