"""Exact corroboration of the shell lower theorem; standard library, no writes."""

import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def valuations(number):
    require(type(number) is int and 1 <= number <= 128, "integer domain")
    row = []
    for prime in (2, 3, 5, 7, 11, 13):
        exponent = 0
        for _ in range(8):
            if number % prime:
                break
            number //= prime
            exponent += 1
        row.append(exponent)
    require(number == 1, "unsupported prime")
    return tuple(row)


def rank(rows):
    require(len(rows) <= 8, "rank row limit")
    require(all(len(row) == 6 for row in rows), "valuation row shape")
    work = [[Fraction(x) for x in row] for row in rows]
    pivot = 0
    for column in range(6):
        candidates = [i for i in range(pivot, len(work)) if work[i][column]]
        if not candidates:
            continue
        selected = candidates[0]
        work[pivot], work[selected] = work[selected], work[pivot]
        divisor = work[pivot][column]
        work[pivot] = [x / divisor for x in work[pivot]]
        for i in range(pivot + 1, len(work)):
            factor = work[i][column]
            work[i] = [x - factor * y for x, y in zip(work[i], work[pivot])]
        pivot += 1
    return pivot


def independent_generators(base, alphabet):
    require(type(base) is int and 2 <= base <= 16, "base domain")
    require(len(alphabet) <= 6, "alphabet limit")
    rows = [valuations(base)]
    chosen = []
    for generator in alphabet:
        row = valuations(generator)
        if rank(rows + [row]) > len(rows):
            rows.append(row)
            chosen.append(generator)
    require(rank(rows) == len(rows), "independent basis")
    return tuple(chosen)


def ceil_log(base, value):
    require(2 <= base <= 16 and 1 <= value <= 128, "logarithm domain")
    power = 1
    for exponent in range(value.bit_length() + 1):
        if power >= value:
            return exponent
        power *= base
    raise ValueError("ceil logarithm bound")


def lift(base, level, raw):
    require(2 <= base <= 16 and 0 <= level <= 16, "lift domain")
    require(1 <= raw < base ** (level + 1), "strict upper endpoint")
    result = raw
    for _ in range(level + 1):
        if result >= base ** level:
            require(result < base ** (level + 1), "shell overshoot")
            return result
        result *= base
    raise ValueError("lift iteration bound")


def lower_witnesses(base, level, chosen):
    require(0 <= level <= 16 and len(chosen) <= 3, "witness domain")
    rows = [valuations(x) for x in (base,) + chosen]
    require(rank(rows) == len(rows), "dependent generators")
    heights = tuple(ceil_log(base, x) for x in chosen)
    height = max(heights, default=1)
    radius = level // height
    witnesses = []
    for exponents in itertools.product(range(radius + 1), repeat=len(chosen)):
        if sum(exponents) <= radius:
            raw = math.prod(g ** b for g, b in zip(chosen, exponents))
            witnesses.append(lift(base, level, raw))
    expected = math.comb(radius + len(chosen), len(chosen))
    require(len(witnesses) == expected, "stars and bars count")
    require(len(set(witnesses)) == expected, "injective shell map")
    return set(witnesses)


def closure(generators, upper):
    require(1 < upper <= 1_000_000, "closure capacity")
    require(len(generators) <= 7 and all(type(g) is int and 1 <= g <= 128
                                       for g in generators), "generator domain")
    members = {1}
    for generator in generators:
        if generator == 1:
            continue
        previous = tuple(members)
        for value in previous:
            power = value
            for _ in range(upper.bit_length()):
                if power >= upper:
                    break
                members.add(power)
                power *= generator
    return members


def literal_members(generators, upper):
    require(1 < upper <= 8_000, "literal capacity")
    require(len(generators) <= 7 and all(type(g) is int and 1 <= g <= 128
                                       for g in generators), "generator domain")
    reachable = bytearray(upper)
    reachable[1] = 1
    for value in range(2, upper):
        reachable[value] = any(
            g > 1 and value % g == 0 and reachable[value // g]
            for g in generators
        )
    return {value for value in range(1, upper) if reachable[value]}


def check_alphabets():
    counts = {"alphabets": 0, "shells": 0, "lower_witnesses": 0}
    alphabets = [a for size in range(3)
                 for a in itertools.combinations(range(2, 13), size)]
    alphabets += [(1, 2, 3), (2, 3, 5), (4, 6, 9), (6, 10, 15), (6, 35, 77)]
    for base, alphabet in itertools.product(range(2, 7), alphabets):
        generators = (base,) + alphabet
        chosen = independent_generators(base, alphabet)
        require(rank([valuations(g) for g in generators]) == len(chosen) + 1,
                "basis spans alphabet")
        upper = base ** 5
        members = closure(generators, upper)
        require(members == literal_members(generators, upper), "monoid oracles")
        previous_count = 0
        for level in range(5):
            shell = {x for x in members if base ** level <= x < base ** (level + 1)}
            witnesses = lower_witnesses(base, level, chosen)
            require(witnesses <= shell, "new constructive lower bound")
            require(len(shell) >= previous_count, "multiplication injection")
            previous_count = len(shell)
            counts["shells"] += 1
            counts["lower_witnesses"] += len(witnesses)
        counts["alphabets"] += 1
    return counts


def check_free_shells():
    counts = {"free_shells": 0, "free_points": 0}
    for base, chosen in ((2, (3,)), (4, (3,)), (6, (10,)), (2, (3, 5)),
                         (4, (6, 5)), (3, (2, 7)), (2, ())):
        require(rank([valuations(x) for x in (base,) + chosen]) == len(chosen) + 1,
                "free model independence")
        for level in range(7):
            upper = base ** (level + 1)
            if upper > 1_000_000:
                continue
            raw_products = closure(chosen, upper)
            images = {lift(base, level, raw) for raw in raw_products}
            complete = closure((base,) + chosen, upper)
            shell = {x for x in complete if base ** level <= x < upper}
            require(images == shell and len(images) == len(raw_products),
                    "exact free-monoid shell formula")
            counts["free_shells"] += 1
            counts["free_points"] += len(images)
    return counts


def check_controls():
    cases = ((independent_generators, (1, (2,))),
             (independent_generators, (2, (17,))),
             (independent_generators, (2, (2,) * 7)),
             (lower_witnesses, (2, 4, (4,))),
             (lower_witnesses, (2, -1, (3,))),
             (lift, (2, 4, 32)), (closure, ((2,), 1_000_001)))
    for function, arguments in cases:
        try:
            function(*arguments)
        except ValueError:
            continue
        raise ValueError("negative control accepted")
    require(not {x for x in closure((3,), 8) if 4 <= x < 8},
            "omitting the base can leave an empty shell")
    require(lower_witnesses(4, 3, ()) == {64}, "rank-one boundary")
    return len(cases) + 2


def main():
    counts = check_alphabets()
    counts.update(check_free_shells())
    counts["controls"] = check_controls()
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        path = package / name
        require(not path.is_symlink() and path.stat().st_size <= 524_288,
                "package source capacity")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    print(json.dumps({"status": "PASS_MULTIPLICATIVE_SHELL_SHARPNESS",
                      "counts": counts, "sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
