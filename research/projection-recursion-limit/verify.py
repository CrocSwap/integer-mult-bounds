#!/usr/bin/env python3
"""Exact corroboration for the scoped projection-recursion limit theorem."""

import argparse
from fractions import Fraction as Q
import hashlib
import json
from math import prod
from pathlib import Path
import sys

BASE = (0, 27456, 48576, 68320, 86592)
LIMIT = Q(439277, 149175)
PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def gaussian(k, r):
    require(0 <= r <= k <= 100, "Gaussian-binomial domain")
    numerator = prod(2 ** (k - i) - 1 for i in range(r))
    denominator = prod(2 ** (r - i) - 1 for i in range(r))
    value, remainder = divmod(numerator, denominator)
    require(remainder == 0, "nonintegral Gaussian binomial")
    return value


def reference_law(k):
    """Distance distribution; deficit order is its reversal."""
    require(1 <= k <= 100, "reference-law domain")
    total = prod(2 ** i + 1 for i in range(1, k + 1))
    values = tuple(Q(gaussian(k, r) * 2 ** (r * (r + 1) // 2), total)
                   for r in range(k + 1))
    require(sum(values) == 1, "reference law does not normalize")
    return values


def counts(k, r):
    """Cited integer recurrence, independently encoded in distance order."""
    require(1 <= k <= 100 and 0 <= r <= k, "count domain")
    same = 2 ** (k - r) - 1 + 4 ** k - 2 ** (k + r)
    one = 2 * (2 ** k - 2 ** (k - r)) + (2 ** r - 1) * 2 ** (k - 1)
    two = ((2 ** r - 1) * (2 ** (r - 1) - 1) * 2 ** (k - r)
           if r >= 2 else 0)
    result = {r: same, r - 1: one, r - 2: two}
    require(all(v >= 0 for v in result.values()), "negative count")
    require(sum(result.values()) == 4 ** k - 1, "incorrect row sum")
    return {s: v for s, v in result.items() if v}


def deficit_row(k, j):
    """New comparison-chain formulas, separate from counts()."""
    require(0 <= j <= k <= 100 and k >= 1, "deficit domain")
    size, z = 2 ** k, 2 ** j
    up = Q(size * size, 2 * z) - Q(3 * size, 2) + z
    up /= size * size - 1
    down = Q(z - 1 + size * size - size * size // z, size * size - 1)
    stay = 1 - up - down
    require(min(up, stay, down) >= 0, "negative transition")
    return up, stay, down


def homogeneous(j):
    require(0 <= j <= 100, "homogeneous domain")
    return Q(1, 2 ** (j + 1)), Q(1, 2 ** (j + 1)), 1 - Q(1, 2 ** j)


def multiplier(m, b):
    return Q((2 ** (b + 1) + 1) * (2 ** m - 1),
             (2 ** b - 1) * (2 ** (m + 1) + 1))


def limit_of(seed):
    b = len(seed) - 1
    law = reference_law(b)
    scale = Q(2 ** (b + 1) + 1, 2 * (2 ** b - 1))
    return scale * sum(law[r] * Q(seed[r], seed[1]) for r in range(b + 1))


def error_bound(m, b, maximum):
    k = m // 2
    require(b <= k < m, "error-bound split domain")
    c = Q(2 ** (b + 1) + 1, 2 ** b - 1)
    variation = Q(9, 2 * (m - k)) + Q(2) ** (2 - k)
    return maximum * (c * variation / 2 + 3 * c / (2 * (2 ** (m + 1) + 1)))


def row_matches_counts(k, j, row):
    expected = counts(k, k - j)
    return all(probability == Q(expected.get(k - 1 - j - offset, 0), 4 ** k - 1)
               for offset, probability in zip((1, 0, -1), row))


def check_kernels():
    rows = 0
    for k in range(1, 81):
        for j in range(k + 1):
            row = deficit_row(k, j)
            require(row_matches_counts(k, j, row), "coordinate mismatch")
            other = homogeneous(j)
            variation = sum(abs(x - y) for x, y in zip(row, other)) / 2
            require(variation <= Q(2, 2 ** k), "kernel-error bound")
            rows += 1
    return rows


def check_coherence():
    transitions = 0
    for k in range(2, 65):
        initial = reference_law(k)[::-1]
        reduced = [Q(0)] * k
        for j, probability in enumerate(initial):
            for offset, part in zip((1, 0, -1), deficit_row(k, j)):
                if part:
                    reduced[j + offset] += probability * part
        require(tuple(reduced) == reference_law(k - 1)[::-1], "coherence")
        transitions += 1
    return transitions


def check_stationary():
    weight = Q(1)
    moment = Q(0)
    normalizer = Q(1)
    for j in range(80):
        next_weight = weight / (2 ** (j + 1) - 1)
        require(weight * homogeneous(j)[0] == next_weight * homogeneous(j + 1)[2],
                "detailed balance")
        require(homogeneous(j)[0] + homogeneous(j + 1)[2] == 1, "monotonicity")
        if j >= 1:
            require(homogeneous(j)[0] - homogeneous(j)[2] <= -Q(1, 4), "drift")
        moment += (j + 1) * next_weight
        normalizer += next_weight
        weight = next_weight
    require(moment <= Q(9, 4) and normalizer >= 2, "mean bound")
    return 80


def evolve(seed, end):
    """Raw integer recurrence, with the new normalization checked at each step."""
    b = len(seed) - 1
    require(1 <= b < end <= 100 and seed[0] == 0 and seed[1] > 0, "seed domain")
    profile = tuple(seed)
    cap = seed[1]
    total = seed[1]
    tops = {b: Q(seed[-1], seed[1])}
    for k in range(b + 1, end + 1):
        profile = tuple(sum(count * profile[s] for s, count in counts(k, r).items())
                        for r in range(k + 1))
        cap *= (2 ** (k - 1) - 1) * (2 ** (k + 1) + 1)
        total *= 4 ** k - 1
        require(profile[1] == cap, "cap product")
        require(Q(total, cap) == multiplier(k, b), "telescoping normalization")
        tops[k] = Q(profile[-1], cap)
    return tops


def check_markov(seed, end):
    """Propagate full probability laws instead of the raw seed recurrence."""
    b = len(seed) - 1
    raw = evolve(seed, end)
    for m in range(b + 1, end + 1):
        probabilities = [Q(1)] + [Q(0)] * m
        for k in range(m, b, -1):
            reduced = [Q(0)] * k
            for j, probability in enumerate(probabilities):
                for offset, part in zip((1, 0, -1), deficit_row(k, j)):
                    if part:
                        reduced[j + offset] += probability * part
            probabilities = reduced
        expected = sum(p * Q(seed[b - j], seed[1])
                       for j, p in enumerate(probabilities))
        require(multiplier(m, b) * expected == raw[m], "Markov/raw mismatch")
    return end - b


def check_controls():
    """Reject concrete wrong formulas through the same exact identities."""
    require(limit_of(BASE) != Q(439278, 149175), "wrong-limit control")
    changed = list(BASE)
    changed[2] += 1
    require(limit_of(changed) != LIMIT, "seed-sensitivity control")
    require(multiplier(5, 4) != Q(4 ** 5 - 1, (2 ** 4 - 1) * (2 ** 6 + 1) + 1),
            "wrong-cap control")
    weights = reference_law(4)
    require(sum(weights[r] * Q(BASE[r], BASE[1]) for r in range(5)) != LIMIT,
            "missing-normalization control")
    row = list(deficit_row(5, 0))
    row[0] += Q(1, 100)
    row[1] -= Q(1, 100)
    require(not row_matches_counts(5, 0, row), "transition-corruption control")
    wrong = list(reference_law(5)[::-1])
    wrong[0], wrong[1] = wrong[1], wrong[0]
    reduced = [Q(0)] * 5
    for j, probability in enumerate(wrong):
        for offset, part in zip((1, 0, -1), deficit_row(5, j)):
            if part:
                reduced[j + offset] += probability * part
    require(tuple(reduced) != reference_law(4)[::-1], "wrong-law control")
    return 6


def evidence():
    source = "research/projection-recursion-check/README.md"
    source_hash = hashlib.sha256((ROOT / source).read_bytes()).hexdigest()
    pins = json.loads((PACKAGE / "SOURCES.json").read_text())
    pin = next(row for row in pins["files"] if row["path"] == source)
    require(source_hash == pin["sha256"], "source hash mismatch")
    require(limit_of(BASE) == LIMIT, "exact limit identity")
    kernels = check_kernels()
    coherence = check_coherence()
    stationary = check_stationary()
    tops = evolve(BASE, 80)
    maximum = Q(41, 13)
    bounded = 0
    for m in range(8, 81):
        require(abs(tops[m] - LIMIT) <= error_bound(m, 4, maximum), "limit enclosure")
        bounded += 1
    markov = check_markov(BASE, 18)
    general = 0
    for b in range(1, 7):
        seed = tuple([0] + [r * r + 3 for r in range(1, b + 1)])
        markov += check_markov(seed, b + 4)
        values = evolve(seed, 2 * b + 8)
        for m in range(2 * b, 2 * b + 9):
            if m > b:
                require(abs(values[m] - limit_of(seed)) <=
                        error_bound(m, b, Q(max(seed), seed[1])), "general-seed enclosure")
                general += 1
    return {"claim_type": "scoped recurrence proof with finite corroboration",
            "limit": str(LIMIT), "kernel_rows": kernels,
            "coherence_transitions": coherence, "stationary_indices": stationary,
            "seed_limit_enclosures": bounded, "general_seed_enclosures": general,
            "markov_raw_comparisons": markov, "failure_controls": check_controls(),
            "source_sha256": source_hash,
            "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "proof_sha256": hashlib.sha256((PACKAGE / "PROOF.md").read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print generated evidence instead of comparing it")
    args = parser.parse_args()
    result = evidence()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        require(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
                "evidence differs from generated RESULT.json")
        print("PASS_PROJECTION_RECURSION_LIMIT", json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, StopIteration) as error:
        print(f"FAIL_PROJECTION_RECURSION_LIMIT: {error}", file=sys.stderr)
        raise SystemExit(1) from error
