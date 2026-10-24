#!/usr/bin/env python3
"""Exact corroboration for the equal-demand tariff; standard library only."""

import hashlib
import itertools
import json
from dataclasses import dataclass
from pathlib import Path


class VerificationError(Exception):
    """A mathematical or input-contract check failed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


@dataclass(frozen=True)
class Ring:
    size: int
    square_zero: bool = False

    def add(self, x: int, y: int) -> int:
        return x ^ y if self.square_zero else (x + y) % self.size

    def neg(self, x: int) -> int:
        return x if self.square_zero else (-x) % self.size

    def mul(self, x: int, y: int) -> int:
        if not self.square_zero:
            return x * y % self.size
        return ((x & 1) * (y & 1)) ^ ((x & 1) * (y & 6)) ^ ((y & 1) * (x & 6))


def check_ring(ring: Ring) -> int:
    require(2 <= ring.size <= 12, "ring size outside finite check domain")
    require(not ring.square_zero or ring.size == 8, "invalid square-zero encoding")
    triples = 0
    for x, y, z in itertools.product(range(ring.size), repeat=3):
        require(
            ring.add(ring.add(x, y), z) == ring.add(x, ring.add(y, z)), "additivity"
        )
        require(
            ring.mul(ring.mul(x, y), z) == ring.mul(x, ring.mul(y, z)), "associativity"
        )
        require(
            ring.mul(x, ring.add(y, z)) == ring.add(ring.mul(x, y), ring.mul(x, z)),
            "distributivity",
        )
        require(ring.mul(x, y) == ring.mul(y, x), "commutativity")
        triples += 1
    for x in range(ring.size):
        require(ring.add(x, ring.neg(x)) == 0, "additive inverse")
        require(ring.mul(x, 1) == x and ring.mul(1, x) == x, "multiplicative identity")
    return triples


def word_for(ring: Ring, q: int, demand: int, support: int, root: int) -> tuple:
    require(1 <= q <= 6 and 0 < demand < ring.size, "invalid equal-demand domain")
    require(0 < support < 1 << q and 0 <= root < q, "invalid source support")
    require(bool(support & (1 << root)), "root is not in insertion support")
    echoed = tuple(i for i in range(q) if not support & (1 << i))
    before = tuple(("E", i, root, ring.neg(1)) for i in echoed)
    after = tuple(("E", i, root, 1) for i in reversed(echoed))
    direct = tuple(
        ("P", i, -1, demand) for i in range(q) if i != root and support & (1 << i)
    )
    return before + (("P", root, -1, demand),) + after + direct


def execute(ring: Ring, word: tuple, rows: tuple, source: tuple) -> tuple:
    data = [list(row) for row in rows]
    for kind, dest, origin, coefficient in word:
        rhs = source if kind == "P" else data[origin]
        data[dest] = [
            ring.add(x, ring.mul(coefficient, y))
            for x, y in zip(data[dest], rhs, strict=True)
        ]
    return tuple(tuple(row) for row in data)


def inverse(ring: Ring, word: tuple) -> tuple:
    return tuple(
        (kind, dest, origin, ring.neg(coefficient))
        for kind, dest, origin, coefficient in reversed(word)
    )


def counts(word: tuple, q: int) -> tuple:
    source = [0] * q
    arrivals = [0] * q
    for kind, dest, _, _ in word:
        if kind == "P":
            source[dest] += 1
        else:
            arrivals[dest] += 1
    return tuple(source + arrivals)


def endpoint(ring: Ring, word: tuple, q: int, demand: int) -> None:
    rows = tuple(tuple(int(i == j) for j in range(q + 1)) for i in range(q))
    source = (0,) * q + (1,)
    expected = tuple(row[:-1] + (demand,) for row in rows)
    actual = execute(ring, word, rows, source)
    require(actual == expected, "wrong full formal endpoint")
    require(
        execute(ring, inverse(ring, word), actual, source) == rows, "inverse failed"
    )


def support_vector(q: int, support: int) -> tuple:
    return tuple(int(bool(support & (1 << i))) for i in range(q)) + tuple(
        0 if support & (1 << i) else 2 for i in range(q)
    )


def dot(left: tuple, right: tuple) -> int:
    return sum(x * y for x, y in zip(left, right, strict=True))


def closed_price(mu: tuple, c: tuple) -> int:
    require(len(mu) == len(c) and 1 <= len(mu) <= 6, "invalid price shape")
    require(
        all(type(x) is int and x > 0 for x in mu + c),
        "prices must be positive integers in the finite checker",
    )
    local = tuple(min(x, 2 * y) for x, y in zip(mu, c, strict=True))
    return sum(local) + min(x - y for x, y in zip(mu, local, strict=True))


def construction_checks() -> dict:
    rings = tuple(Ring(n) for n in range(2, 13)) + (Ring(8, True),)
    total = {
        "ring_triples": 0,
        "words": 0,
        "formal_columns": 0,
        "literal_assignments": 0,
    }
    for ring in rings:
        total["ring_triples"] += check_ring(ring)
        for q in range(1, 7):
            for demand in range(1, ring.size):
                for support in range(1, 1 << q):
                    for root in range(q):
                        if not support & (1 << root):
                            continue
                        word = word_for(ring, q, demand, support, root)
                        endpoint(ring, word, q, demand)
                        require(
                            counts(word, q) == support_vector(q, support),
                            "wrong aggregate count",
                        )
                        total["words"] += 1
                        total["formal_columns"] += 2 * (q + 1)
    ring = Ring(4)
    for support in range(1, 8):
        root = next(i for i in range(3) if support & (1 << i))
        word = word_for(ring, 3, 2, support, root)
        for dirt in itertools.product(range(4), repeat=4):
            rows = tuple((x,) for x in dirt[:3])
            source = (dirt[3],)
            expected = tuple(((x + 2 * dirt[3]) % 4,) for x in dirt[:3])
            actual = execute(ring, word, rows, source)
            require(actual == expected, "literal endpoint failed")
            require(
                execute(ring, inverse(ring, word), actual, source) == rows,
                "literal inverse failed",
            )
            total["literal_assignments"] += 1
    return total


def price_checks() -> dict:
    comparisons = 0
    exposed = 0
    for q in range(1, 7):
        vectors = tuple(support_vector(q, s) for s in range(1, 1 << q))
        for support in range(1, 1 << q):
            mu = tuple(1 if support & (1 << i) else 9 for i in range(q))
            c = (1,) * q
            values = tuple(dot(v, mu + c) for v in vectors)
            require(
                values.count(min(values)) == 1,
                "frontier vector is not uniquely exposed",
            )
            require(values[support - 1] == min(values), "wrong exposed support")
            require(
                closed_price(mu, c) == min(values),
                "closed formula disagrees with support minimum",
            )
            exposed += 1
        for seed in range(80):
            mu = tuple(1 + (seed * (2 * i + 1) + i * i) % 17 for i in range(q))
            c = tuple(1 + (seed * (i + 3) + 7 * i) % 13 for i in range(q))
            require(
                closed_price(mu, c) == min(dot(v, mu + c) for v in vectors),
                "heterogeneous tariff mismatch",
            )
            comparisons += 1
    return {"price_comparisons": comparisons, "exposed_vectors": exposed}


def oracle_step(state: tuple, gate: tuple) -> tuple:
    # Independent Z/4 interpreter on a flattened 3-by-4 affine matrix.
    dest, origin, coefficient = gate
    result = list(state)
    for column in range(4):
        value = int(column == 3) if origin == -1 else state[4 * origin + column]
        result[4 * dest + column] = (state[4 * dest + column] + coefficient * value) % 4
    return tuple(result)


def ball(start: tuple, gates: tuple, radius: int) -> set:
    require(0 <= radius <= 2 and len(gates) <= 27, "oracle bound exceeded")
    seen = {start}
    frontier = {start}
    for _ in range(radius):
        following = {oracle_step(state, gate) for state in frontier for gate in gates}
        frontier = following - seen
        seen.update(frontier)
    require(len(seen) <= 1 + 27 + 27**2, "oracle state capacity exceeded")
    return seen


def oracle_checks() -> dict:
    identity = tuple(int(i == j) for i in range(3) for j in range(4))
    target = tuple((2 if j == 3 else int(i == j)) for i in range(3) for j in range(4))
    counts_by_support = []
    for support in range(1, 8):
        # Only source prices are heterogeneous. All ADD prices are one.
        # A putatively cheaper word costs <= 4, so price-nine gates cannot occur.
        gates = tuple(
            (i, j, a)
            for i in range(3)
            for j in range(-1, 3)
            for a in range(1, 4)
            if i != j and (j != -1 or support & (1 << i))
        )
        optimum = 6 - support.bit_count()
        lower = optimum - 1
        left = ball(identity, gates, lower // 2)
        right = ball(target, gates, lower - lower // 2)
        require(not left.intersection(right), "a strictly cheaper complete word exists")
        word = word_for(Ring(4), 3, 2, support, (support & -support).bit_length() - 1)
        require(len(word) == optimum, "matching witness has wrong cost")
        mu = tuple(1 if support & (1 << i) else 9 for i in range(3))
        require(
            dot(counts(word, 3), mu + (1, 1, 1)) == optimum,
            "oracle witness price mismatch",
        )
        require(identity in ball(identity, gates, 0), "oracle zero-radius control")
        require(
            oracle_step(identity, gates[0]) in ball(identity, gates, 1),
            "oracle planted-hit control",
        )
        counts_by_support.append([support, len(left), len(right), optimum])
    return {"oracle_instances": counts_by_support}


def rejection_checks() -> int:
    ring = Ring(4)
    word = word_for(ring, 3, 2, 1, 0)
    bad_words = (word[1:], word[:-1], inverse(ring, word))
    rejected = 0
    for candidate in bad_words[:2]:
        try:
            endpoint(ring, candidate, 3, 2)
        except VerificationError:
            rejected += 1
        else:
            raise VerificationError("dirt corruption was accepted")
    # Demand 2 is self-negative in Z/4, so its inverse is a positive control.
    endpoint(ring, bad_words[2], 3, 2)
    for mu, c in (((0,), (1,)), ((True,), (1,)), ((1, 2), (1,)), ((), ())):
        try:
            closed_price(mu, c)
        except VerificationError:
            rejected += 1
        else:
            raise VerificationError("invalid price input was accepted")
    try:
        word_for(ring, 3, 0, 1, 0)
    except VerificationError:
        rejected += 1
    else:
        raise VerificationError("zero demand was accepted in the nonzero theorem")
    require(oracle_step((0,) * 12, (0, -1, 1)) != (0,) * 12, "source insertion control")
    return rejected


def main() -> None:
    result = construction_checks() | price_checks() | oracle_checks()
    result["rejection_controls"] = rejection_checks()
    package = Path(__file__).resolve().parent
    result["sha256"] = {
        name: hashlib.sha256((package / name).read_bytes()).hexdigest()
        for name in (
            "README.md",
            "TASK.json",
            "SOURCES.json",
            "VERIFY.json",
            "verify.py",
        )
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    print("PASS_EQUAL_NONUNIT_FANOUT")


if __name__ == "__main__":
    main()
