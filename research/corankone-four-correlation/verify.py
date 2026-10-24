#!/usr/bin/env python3
"""Exact finite component of the four-request correlation proof.

Produced by Nick Petalas. Apache-2.0.
"""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


K = 4
BITS = 12
STATES = 1 << BITS
OFF = tuple((i, j) for i in range(K) for j in range(K) if i != j)
TERMS = {
    81: 1, 63: -12, 57: 24, 55: -8, 51: -24, 49: 18,
    47: -48, 45: 118, 43: -68, 41: 85, 39: -180, 37: 228,
    35: -336, 33: 399, 31: -444, 29: 502, 27: -548, 25: 523,
    23: -332, 21: 144, 19: -48, 17: 6,
}
FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
         "VERIFY.json", "verify.py")


def need(condition, message):
    if not condition:
        raise ValueError(message)


def rectangle(y, x):
    return sum(1 << bit for bit, (i, j) in enumerate(OFF)
               if (y >> i) & (x >> j) & 1)


def step_weights(zero_weight=31):
    """Enumerate all 256 factor pairs, retaining their disjoint supports."""
    weights = [0] * STATES
    for y in range(1 << K):
        for x in range(1 << K):
            if not y & x:
                weights[rectangle(y, x)] += 1
    need(weights[0] == 31 and sum(weights) == 81, "factor multiplicities")
    weights[0] = zero_weight
    return weights


def hadamard(weights):
    """The twelve bounded butterfly stages diagonalize XOR convolution."""
    need(len(weights) == STATES, "Hadamard input size")
    values = list(weights)
    for stage in range(BITS):
        width = 1 << stage
        for start in range(0, STATES, 2 * width):
            for offset in range(width):
                a, b = start + offset, start + offset + width
                left, right = values[a], values[b]
                values[a], values[b] = left + right, left - right
    return values


def literal_characters():
    """Evaluate the cited character sum directly over all 3^4 assignments."""
    masks = []
    for labels in product(range(3), repeat=K):
        mask = sum(1 << bit for bit, (i, j) in enumerate(OFF)
                   if labels[i] == 1 and labels[j] == 2)
        masks.append(mask)
    need(len(masks) == 81, "ternary domain size")
    return [sum(1 - 2 * ((character & mask).bit_count() % 2)
                for mask in masks) for character in range(STATES)]


def spectral_data():
    eigenvalues = hadamard(step_weights())
    need(eigenvalues == literal_characters(), "two character evaluations")
    signed = Counter()
    unsigned = Counter(eigenvalues)
    for character, value in enumerate(eigenvalues):
        signed[value] += 1 - 2 * (character.bit_count() % 2)
    signed = {value: count for value, count in signed.items() if count}
    need(signed == TERMS, "complete signed spectrum")
    need(sum(unsigned.values()) == STATES, "complete character domain")
    need(unsigned[81] == 1 and unsigned[63] == 12, "leading modes")
    need(min(eigenvalues) >= 0, "nonnegative spectrum")
    return signed, unsigned


def count(n, terms=TERMS):
    need(0 <= n <= 84, "declared count domain")
    numerator = sum(mult * value ** n for value, mult in terms.items())
    need(numerator % STATES == 0, "integral Fourier count")
    result = numerator // STATES
    need(result >= 0, "nonnegative count")
    return result


def walk_counts(maximum, zero_weight=31):
    """A separate integer convolution check, without diagonalization."""
    need(0 <= maximum <= 12, "bounded walk depth")
    moves = tuple((mask, weight) for mask, weight in
                  enumerate(step_weights(zero_weight)) if weight)
    state = [0] * STATES
    state[0] = 1
    results = [state[-1]]
    for _ in range(maximum):
        following = [0] * STATES
        for source, multiplicity in enumerate(state):
            if multiplicity:
                for mask, weight in moves:
                    following[source ^ mask] += multiplicity * weight
        state = following
        results.append(state[-1])
    return results


def fractions_at(m):
    need(4 <= m <= 85, "declared dimension domain")
    n, x = m - 1, 1 << m
    denominator = (2 ** (4 * m - 16)
                   * (x - 1) * (x - 2) * (x - 4) * (x - 8))
    joint = Fraction(count(n), denominator)
    marginal = Fraction(3 ** n, (x - 1) * 2 ** n)
    correction = Fraction((x - 1) ** 3, (x - 2) * (x - 4) * (x - 8))
    ratio = joint / marginal ** 4
    need(ratio == Fraction(STATES * count(n), 81 ** n) * correction,
         "ratio normalization including finite-GL correction")
    return joint, marginal, ratio


def proof_checks():
    tail = sum(abs(mult) for value, mult in TERMS.items() if value < 63)
    need(tail == 4083, "absolute signed tail mass")
    need(max(value for value in TERMS if value < 63) == 57, "tail radius")
    need(4083 * 57 ** 84 < 63 ** 84, "uniform spectral tail threshold")
    need(9 * 9 ** 84 < 14 ** 84, "finite-GL correction threshold")
    need(Fraction(15, 16) * Fraction(7, 8) * Fraction(3, 4)
         == Fraction(315, 512), "denominator lower bound")
    need(11 * 512 < 18 * 315, "correction bound constant")
    need(11 * 7 ** 84 < 9 ** 84, "positive uniform ratio upper bound")
    rows = []
    for m in range(4, 85):
        joint, marginal, ratio = fractions_at(m)
        need(joint < marginal ** 4, "strict four-event product inequality")
        rows.append({"m": m, "joint": str(joint), "ratio": str(ratio)})
    return rows


def controls():
    joint, marginal, ratio = fractions_at(5)
    need(joint == Fraction(1, 208320), "first positive dimension")
    need(joint != marginal ** 4, "independence control")
    need(ratio != Fraction(STATES * count(4), 81 ** 4),
         "finite-GL correction control")
    wrong = step_weights(1)
    need(hadamard(wrong)[0] != 81, "zero-factor multiplicity control")
    wrong_walk = walk_counts(5, zero_weight=1)
    need(wrong_walk[5] != count(5), "zero-factor changes a positive count")
    missing_mode = dict(TERMS)
    del missing_mode[63]
    need(sum(mult * value ** 4 for value, mult in missing_mode.items())
         != STATES * count(4), "leading negative mode control")
    return 5


def main():
    signed, unsigned = spectral_data()
    walks = walk_counts(12)
    need(walks == [count(n) for n in range(13)], "walk versus spectral count")
    rows = proof_checks()
    result = {
        "status": "PASS_CORANKONE_FOUR_CORRELATION",
        "claim_type": "scoped counting proof with exact finite component",
        "characters_enumerated": STATES,
        "signed_spectrum": sorted(signed.items(), reverse=True),
        "unsigned_spectrum": sorted(unsigned.items(), reverse=True),
        "walk_counts_n_0_through_12": walks,
        "finite_dimensions_checked": len(rows),
        "finite_comparisons": rows,
        "uniform_tail_starts_at_n": 84,
        "asymptotic_deficit_coefficient": 12,
        "controls": controls(),
    }
    package = Path(__file__).resolve().parent
    result["package_sha256"] = {
        name: sha256((package / name).read_bytes()).hexdigest() for name in FILES
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
