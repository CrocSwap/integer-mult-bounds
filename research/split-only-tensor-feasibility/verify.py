#!/usr/bin/env python3
"""Exact finite corroboration of the split-only tensor feasibility theorem."""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from math import isqrt, prod
from pathlib import Path
import sys


BITS = 96
SCALE = 1 << BITS
FILES = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer_root(n, degree):
    require(type(n) is int and n >= 0, "invalid radicand")
    require(type(degree) is int and 1 <= degree <= 8, "invalid root degree")
    if degree == 2:
        return isqrt(n)
    low, high = 0, 1 << ((n.bit_length() + degree - 1) // degree)
    for _ in range(high.bit_length() + 1):
        if high - low <= 1:
            break
        middle = (low + high) // 2
        if middle**degree <= n:
            low = middle
        else:
            high = middle
    require(low**degree <= n < (low + 1)**degree, "root bracket failed")
    return low


def power_bounds(n, exponent):
    require(type(n) is int and 0 <= n < 1 << 1024, "power input outside replay domain")
    require(isinstance(exponent, Fraction) and 0 < exponent < 1, "invalid exponent")
    require(exponent.denominator <= 8, "exponent outside replay domain")
    a, b = exponent.numerator, exponent.denominator
    scaled = n**a << (BITS * b)
    root = integer_root(scaled, b)
    low = Fraction(root, SCALE)
    high = low if root**b == scaled else Fraction(root + 1, SCALE)
    return low, high


def profile_ok(profile):
    require(type(profile) is dict and 1 <= len(profile) <= 3, "invalid profile")
    for rank, count in profile.items():
        require(type(rank) is int and 1 <= rank <= 81, "invalid rank")
        require(type(count) is int and 1 <= count <= 8, "invalid multiplicity")


def tensor_histogram(profile, width):
    profile_ok(profile)
    require(type(width) is int and 1 <= width <= 64, "invalid tensor power")
    current = {1: 1}
    for _ in range(width):
        following = Counter()
        for left, multiplicity in current.items():
            for right, count in profile.items():
                following[left * right] += multiplicity * count
        current = dict(following)
        require(len(current) <= 5000, "histogram capacity exceeded")
    require(sum(current.values()) == sum(profile.values())**width, "job count drift")
    return current


def split_bounds(histogram, cap, exponent):
    require(type(cap) is int and 1 <= cap < 1 << 1024, "invalid cap")
    cap_low, cap_high = power_bounds(cap, exponent)
    low, high = Fraction(0), Fraction(0)
    for rank, count in histogram.items():
        quotient, remainder = divmod(rank, cap)
        rem_low, rem_high = power_bounds(remainder, exponent)
        low += count * (quotient * cap_low + rem_low)
        high += count * (quotient * cap_high + rem_high)
    return low, high


def check_one_job():
    checked = 0
    exponents = (Fraction(1, 4), Fraction(1, 3), Fraction(1, 2),
                 Fraction(2, 3), Fraction(3, 4), Fraction(7, 8))
    for exponent in exponents:
        powers = [power_bounds(n, exponent) for n in range(97)]
        for rank in range(1, 97):
            for cap in range(1, 33):
                low, high = split_bounds({rank: 1}, cap, exponent)
                q, r = divmod(rank, cap)
                if rank > cap:
                    require(low > powers[rank][1], "concave lower bound failed")
                else:
                    require((low, high) == powers[rank], "unsplit job changed")
                if r:
                    require(low > rank * powers[cap][1] / cap, "linear lower bound failed")
                else:
                    require((low, high) == (q * powers[cap][0], q * powers[cap][1]),
                            "exact full-block equality failed")
                require(high < rank * powers[cap][0] / cap + powers[rank][0],
                        "two-term upper bound failed")
                checked += 1
    return checked


def check_partition_optima():
    checked = 0
    for cap in range(1, 9):
        optimum = [(0,) * 9]
        for rank in range(1, 33):
            # Independent DP over every ordered capped integer partition.
            best = None
            for piece in range(1, min(cap, rank) + 1):
                candidate = tuple(a + b for a, b in
                                  zip(optimum[rank - piece], radical_vector(piece)))
                if best is None or radical_less(candidate, best):
                    best = candidate
            require(best is not None, "partition oracle has no candidate")
            optimum.append(best)
            q, r = divmod(rank, cap)
            greedy = tuple(q * a + b for a, b in
                           zip(radical_vector(cap), radical_vector(r)))
            require(best == greedy, "arbitrary-partition oracle disagrees")
            checked += 1
    return checked


def radical_vector(n):
    require(type(n) is int and 0 <= n <= 8, "radical outside oracle domain")
    vector = [0] * 9
    if n:
        for factor in range(isqrt(n), 0, -1):
            if n % (factor * factor) == 0:
                vector[n // (factor * factor)] = factor
                break
    return tuple(vector)


def radical_less(left, right):
    if left == right:
        return False
    low, high = Fraction(0), Fraction(0)
    for n, coefficient in enumerate(a - b for a, b in zip(left, right)):
        lo, hi = power_bounds(n, Fraction(1, 2))
        low += coefficient * (lo if coefficient >= 0 else hi)
        high += coefficient * (hi if coefficient >= 0 else lo)
    require(high < 0 or low > 0, "radical comparison did not separate")
    return high < 0


def profiles():
    result = []
    for counts in product(range(3), repeat=3):
        if any(counts):
            result.append({r: n for r, n in zip((1, 4, 9), counts) if n})
    require(len(result) == 26, "profile domain changed")
    return result


def check_histograms():
    checked, decisions, witnesses, max_width = 0, 0, 0, 0
    for profile in profiles():
        pt = sum(isqrt(r) * n for r, n in profile.items())
        p1 = sum(r * n for r, n in profile.items())
        for base in (1, 4, 9):
            rate = max(Fraction(pt), Fraction(p1, isqrt(base)))
            for width in range(1, 7):
                histogram = tensor_histogram(profile, width)
                low, high = split_bounds(histogram, base**width, Fraction(1, 2))
                require(low >= rate**width, "tensor lower rate failed")
                require(high <= pt**width + Fraction(p1, isqrt(base))**width,
                        "tensor upper rate failed")
                checked += 1
            for target in range(1, 33):
                decisions += 1
                if rate >= target:
                    # The universal lower bound excludes EVERY power.
                    continue
                for width in range(1, 65):
                    if 2 * rate**width < target**width:
                        break
                else:
                    raise ValueError("sufficient witness exceeded finite replay budget")
                histogram = tensor_histogram(profile, width)
                _, high = split_bounds(histogram, base**width, Fraction(1, 2))
                require(high < target**width, "constructed tensor witness failed")
                witnesses += 1
                max_width = max(max_width, width)
    return checked, decisions, witnesses, max_width


def check_literal_jobs():
    sequences, contexts = 0, 0
    for profile in profiles():
        atoms = tuple(r for r, n in profile.items() for _ in range(n))
        if len(atoms) > 4:
            continue
        for width in range(1, 5):
            literal = Counter()
            for sequence in product(atoms, repeat=width):
                literal[prod(sequence)] += 1
                sequences += 1
            require(dict(literal) == tensor_histogram(profile, width), "literal jobs disagree")
            for base in (2, 3):
                cap = base**width
                pieces = Counter()
                for rank, count in literal.items():
                    # Explicit pieces, rather than the quotient-weighted price.
                    remaining = rank
                    for _ in range(rank // cap + 1):
                        if not remaining:
                            break
                        piece = min(cap, remaining)
                        pieces[piece] += count
                        remaining -= piece
                    require(remaining == 0, "literal partition incomplete")
                price = [Fraction(0), Fraction(0)]
                for piece, count in pieces.items():
                    lo, hi = power_bounds(piece, Fraction(1, 2))
                    price[0] += count * lo
                    price[1] += count * hi
                require(tuple(price) == split_bounds(literal, cap, Fraction(1, 2)),
                        "literal partition price disagrees")
                contexts += 1
    return sequences, contexts


def check_boundaries():
    half = Fraction(1, 2)
    for width in range(1, 13):
        # Raw moment and rank-one surplus do not suffice at c=2.
        low, _ = split_bounds(tensor_histogram({9: 1}, width), 2**width, half)
        require(low > 6**width, "unsafe raw-moment-only rule survived")
        # Equality in the raw and linear bounds each blocks strict advantage.
        require(split_bounds(tensor_histogram({4: 2}, width), 9**width, half) ==
                (Fraction(4**width), Fraction(4**width)), "raw equality changed")
        require(split_bounds(tensor_histogram({16: 1}, width), 4**width, half) ==
                (Fraction(8**width), Fraction(8**width)), "linear equality changed")
    require(split_bounds({17: 1}, 4, half) == (9, 9), "first-power equality lost")
    require(split_bounds({289: 1}, 16, half) == (73, 73), "second-power win lost")
    require((17 // 4) * 2 == 8 < 9, "remainder control lost")
    return 39


def check_rejections():
    rejected = 0
    invalid = ({}, {0: 1}, {-1: 1}, {1: 0}, {1: -1}, {True: 1}, {1: True}, {82: 1})
    for profile in invalid:
        try:
            tensor_histogram(profile, 1)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid profile accepted")
    for exponent in (Fraction(0), Fraction(1), Fraction(-1, 2), Fraction(1, 9)):
        try:
            power_bounds(2, exponent)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid exponent accepted")
    for cap in (0, -1, True):
        try:
            split_bounds({1: 1}, cap, Fraction(1, 2))
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid cap accepted")
    return rejected


def main():
    require(len(sys.argv) == 1, "this verifier takes no arguments")
    report = {"one_job_splits": check_one_job(),
              "partition_optima": check_partition_optima()}
    hist, decisions, witnesses, width = check_histograms()
    report.update(histogram_checks=hist, feasibility_cases=decisions,
                  attaining_power_witnesses=witnesses, largest_witness_power=width)
    report["literal_sequences"], report["literal_partition_contexts"] = check_literal_jobs()
    report["boundary_checks"] = check_boundaries()
    report["rejected_inputs"] = check_rejections()
    root = Path(__file__).resolve().parent
    hashes = {}
    for name in FILES:
        with (root / name).open("rb") as stream:
            data = stream.read(256 * 1024 + 1)
        require(len(data) <= 256 * 1024, "package file exceeds receipt bound")
        hashes[name] = sha256(data).hexdigest()
    report["package_sha256"] = hashes
    print(json.dumps(report, sort_keys=True, indent=2))
    print("PASS_SPLIT_ONLY_TENSOR_FEASIBILITY")


if __name__ == "__main__":
    main()
