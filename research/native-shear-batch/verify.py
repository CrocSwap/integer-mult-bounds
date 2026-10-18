#!/usr/bin/env python3
"""Exact private-only native shear batching. Python 3.10+, standard library."""

import collections
from fractions import Fraction
import itertools
import json
from pathlib import Path
import random


ROOT = Path(__file__).resolve().parent
MATRIX = (5, 30, 11, 14)  # Target rows, source zero in the low bit.
TARGETS, SOURCES, PRIVATE = 4, 5, 9


def require(condition, message):
    if not condition:
        raise ValueError(message)


def span(vectors):
    values = {0}
    for vector in vectors:
        values |= {v ^ vector for v in tuple(values)}
    return values


def combination(mask, vectors):
    value = 0
    for j, vector in enumerate(vectors):
        if mask >> j & 1:
            value ^= vector
    return value


def fixture():
    rng = random.Random(52)
    for attempt in range(1, 1001):
        rows = tuple(rng.getrandbits(5) for _ in range(4))
        if len(span(rows)) == 8 and all(rows) and rows[0] | rows[1] | rows[2] | rows[3] == 31:
            return rows, attempt
    raise ValueError("fixture stopping rule exhausted")


def census():
    space = span(MATRIX)
    weight = sum(v.bit_count() for v in MATRIX)
    best = None
    histogram = collections.Counter()
    sample_sets = 0
    for samples in itertools.combinations(range(1 << SOURCES), 4):
        if span([b ^ samples[0] for b in samples[1:]]) != space:
            continue
        sample_sets += 1
        coefficients = {combination(c, samples): c for c in range(16) if c.bit_count() % 2 == 0}
        require(len(coefficients) == 8, "nonunique affine coordinates")
        reads = tuple(sum(((coefficients[row] >> j) & 1) << i for i, row in enumerate(MATRIX))
                      for j in range(4))
        read_cost = sum(a.bit_count() for a in reads)
        for order in itertools.permutations(range(4)):
            states = tuple(samples[j] for j in order)
            source_cost = sum((a ^ b).bit_count() for a, b in zip((0,) + states, states + (0,)))
            total = source_cost + read_cost + weight
            histogram[total] += 1
            candidate = (total, states, tuple(reads[j] for j in order), source_cost, read_cost)
            if best is None or candidate < best:
                best = candidate
    separate = None
    basis_count = 0
    for basis in itertools.combinations(sorted(space - {0}), 3):
        if span(basis) != space:
            continue
        basis_count += 1
        coefficients = {combination(c, basis): c for c in range(8)}
        reads = tuple(sum(((coefficients[row] >> j) & 1) << i for i, row in enumerate(MATRIX))
                      for j in range(3))
        total = 2 * sum(b.bit_count() for b in basis) + 2 * sum(a.bit_count() for a in reads) + weight
        candidate = (total, basis, reads)
        if separate is None or candidate < separate:
            separate = candidate
    return {
        "sample_sets": sample_sets,
        "ordered_schedules": sum(histogram.values()),
        "xor_histogram": {str(k): v for k, v in sorted(histogram.items())},
        "best": {"xor_scans": best[0], "source_states": list(best[1]), "target_reads": list(best[2]),
                 "source_scans": best[3], "private_read_scans": best[4], "direct_scans": weight,
                 "queries": 8, "affine_events": 48},
        "separate": {"bases": basis_count, "xor_scans": separate[0], "basis": list(separate[1]),
                     "target_reads": list(separate[2]), "queries": 12, "affine_events": 72},
    }


def emit(states, reads):
    program = []
    previous = 0
    for state, targets in zip(states, reads):
        for j in range(SOURCES):
            if (previous ^ state) >> j & 1:
                program.append(["xor", PRIVATE, TARGETS + j])
        program.append(["query", PRIVATE, 1])
        for i in range(TARGETS):
            if targets >> i & 1:
                program.append(["xor", i, PRIVATE])
        program.append(["query", PRIVATE, -1])
        previous = state
    for j in range(SOURCES):
        if previous >> j & 1:
            program.append(["xor", PRIVATE, TARGETS + j])
    for i, row in enumerate(MATRIX):
        for j in range(SOURCES):
            if row >> j & 1:
                program.append(["xor", i, TARGETS + j])
    return program


def column_census():
    """Cross-check by enumerating target bases and solving source coordinates."""
    columns = tuple(sum(((row >> j) & 1) << i for i, row in enumerate(MATRIX))
                    for j in range(SOURCES))
    space = span(columns)
    histogram = collections.Counter()
    for basis in itertools.permutations(sorted(space - {0}), 3):
        coordinates = {combination(c, basis): c for c in range(8)}
        if len(coordinates) != 8:
            continue
        differences = tuple(sum(((coordinates[col] >> i) & 1) << j for j, col in enumerate(columns))
                            for i in range(3))
        reads = basis + (basis[0] ^ basis[1] ^ basis[2],)
        for offset in range(1 << SOURCES):
            states = tuple(offset ^ d for d in differences) + (offset,)
            travel = sum((a ^ b).bit_count() for a, b in zip((0,) + states, states + (0,)))
            cost = travel + sum(a.bit_count() for a in reads) + sum(row.bit_count() for row in MATRIX)
            histogram[str(cost)] += 1
    return dict(histogram)


def inverse(program):
    return [[op, dst, -src if op == "query" else src] for op, dst, src in reversed(program)]


def symbolic(program, initial=None):
    rows = [{(i, 0)} for i in range(PRIVATE + 1)] if initial is None else [set(r) for r in initial]
    for op, dst, src in program:
        if op == "query":
            require(dst == PRIVATE and src in (-1, 1), "query outside private row")
            rows[dst] = {(i, degree + src) for i, degree in rows[dst]}
        elif op == "xor":
            require((dst == PRIVATE and TARGETS <= src < PRIVATE) or
                    (0 <= dst < TARGETS and TARGETS <= src <= PRIVATE), "illegal VALUE operation")
            rows[dst] ^= rows[src]
        else:
            raise ValueError("unknown operation")
    return rows


def expected_symbolic():
    rows = [{(i, 0)} for i in range(PRIVATE + 1)]
    for i, mask in enumerate(MATRIX):
        for j in range(SOURCES):
            if mask >> j & 1:
                rows[i] ^= {(TARGETS + j, 0), (TARGETS + j, 1)}
    return rows


def lowered(address, missing_child=False):
    # PR521's chronological ADDRESS lowering, also recorded by PR677.
    a = list(address)
    a[2] -= a[0]
    a[3] += a[0]
    a[5] = (a[5] + 5 * a[0] - a[2] - a[3]) / 4
    if not missing_child:
        a[0], a[5] = a[5], a[0]
    a[2] += a[0]
    a[3] -= a[0]
    a[5] = -4 * a[5] + 3 * a[0] + a[2] + a[3]
    return tuple(a)


def lowered_inverse(address):
    a = list(address)
    a[5] = (-a[5] + 3 * a[0] + a[2] + a[3]) / 4
    a[3] += a[0]
    a[2] -= a[0]
    a[0], a[5] = a[5], a[0]
    a[5] = 4 * a[5] - 5 * a[0] + a[2] + a[3]
    a[3] -= a[0]
    a[2] += a[0]
    return tuple(a)


def direct_address(a, modulus):
    delta = (a[0] - a[2] - a[3] + a[5]) * pow(4, -1, modulus)
    return tuple((x + s * delta) % modulus for x, s in zip(a, (1, 0, 1, -1, 0, -1)))


def permutation(modulus):
    addresses = list(itertools.product(range(modulus), repeat=6))
    indexes = {a: i for i, a in enumerate(addresses)}
    push = [indexes[direct_address(a, modulus)] for a in addresses]
    require(len(set(push)) == len(addresses), "ADDRESS map not bijective")
    for a, index in zip(addresses, push):
        value = lowered(tuple(map(Fraction, a)))
        reduced = tuple(int(v.numerator * pow(v.denominator, -1, modulus)) % modulus for v in value)
        require(reduced == addresses[index], "lowering differs from direct ADDRESS map")
    return push


def full_columns(program, push):
    volume = len(push)
    original = [[1 << (row * volume + col) for col in range(volume)] for row in range(PRIVATE + 1)]
    rows = [list(row) for row in original]
    pull = [0] * volume
    for src, dst in enumerate(push):
        pull[dst] = src

    def run(word):
        for op, dst, src in word:
            if op == "query":
                mapping = pull if src == 1 else push
                rows[dst] = [rows[dst][i] for i in mapping]
            else:
                rows[dst] = [a ^ b for a, b in zip(rows[dst], rows[src])]

    run(program)
    for i in range(PRIVATE + 1):
        for col in range(volume):
            expected = original[i][col]
            if i < TARGETS:
                for j in range(SOURCES):
                    if MATRIX[i] >> j & 1:
                        expected ^= original[TARGETS + j][col] ^ original[TARGETS + j][pull[col]]
            require(rows[i][col] == expected, "full-domain endpoint mismatch")
    run(inverse(program))
    require(rows == original, "full-domain inverse mismatch")
    return (PRIVATE + 1) * volume


def rejected(call, message):
    try:
        call()
    except ValueError:
        return
    raise ValueError("negative control accepted: " + message)


def controls(program, result):
    mutations = {}
    first_read = next(i for i, e in enumerate(program) if e[0] == "xor" and e[2] == PRIVATE)
    mutations["omit dirty compensation"] = program[:first_read] + program[first_read + 1:]
    last_restore = max(i for i, e in enumerate(program) if e[0] == "xor" and e[1] == PRIVATE)
    mutations["omit private restoration"] = program[:last_restore] + program[last_restore + 1:]
    mutations["omit direct source term"] = program[:-1]
    changed = [e[:] for e in program]
    changed[0][2] = -1
    mutations["reverse first query"] = changed
    changed = [e[:] for e in program]
    changed[0][1] = 0
    mutations["query DATA target"] = changed
    changed = [e[:] for e in program]
    changed[-1][2] = TARGETS + ((changed[-1][2] - TARGETS + 1) % SOURCES)
    mutations["wrong source"] = changed
    for name, word in mutations.items():
        rejected(lambda word=word: require(symbolic(word) == expected_symbolic(), name), name)
    bad_basis = tuple(Fraction(i == 0) for i in range(6))
    rejected(lambda: require(lowered(bad_basis, True) == lowered(bad_basis), "missing recursive child"), "missing recursive child")
    corrupted = json.loads(json.dumps(result))
    corrupted["best"]["queries"] -= 1
    rejected(lambda: require(corrupted == result, "underpriced certificate"), "underpriced certificate")
    # A semantically neutral pair must still pay both scans.
    padded = program + [["xor", 0, TARGETS], ["xor", 0, TARGETS]]
    require(symbolic(padded) == expected_symbolic(), "neutral positive control failed")
    require(sum(e[0] == "xor" for e in padded) == result["best"]["xor_scans"] + 2,
            "neutral pair was not charged")
    return len(mutations) + 2


def main():
    require(fixture() == (MATRIX, 6), "seed fixture mismatch")
    result = census()
    require(column_census() == result["xor_histogram"], "row/column census disagreement")
    certificate = json.loads((ROOT / "CERTIFICATE.json").read_text())
    require(certificate["matrix_rows"] == list(MATRIX), "certificate target mismatch")
    require(certificate["census"] == result, "certificate census mismatch")
    best = result["best"]
    program = emit(best["source_states"], best["target_reads"])
    require(certificate["program"] == program, "certificate program mismatch")
    require(sum(e[0] == "query" for e in program) == best["queries"], "wrong query invoice")
    require(sum(e[0] == "xor" for e in program) == best["xor_scans"], "wrong XOR invoice")
    require(symbolic(program) == expected_symbolic(), "Laurent endpoint mismatch")
    require(symbolic(inverse(program), symbolic(program)) == [{(i, 0)} for i in range(PRIVATE + 1)],
            "Laurent inverse mismatch")
    # Rational columns prove this fixed linear lowering for arbitrary ADDRESS values.
    for j in range(6):
        unit = tuple(Fraction(i == j) for i in range(6))
        delta = (unit[0] - unit[2] - unit[3] + unit[5]) / 4
        expected = tuple(x + s * delta for x, s in zip(unit, (1, 0, 1, -1, 0, -1)))
        require(lowered(unit) == expected, "rational lowering mismatch")
        require(lowered_inverse(expected) == unit, "inverse lowering mismatch")
    push = permutation(3)
    columns = full_columns(program, push)
    # An independent full order-five ADDRESS census checks modular specialization.
    require(len(permutation(5)) == 15625, "order-five coverage mismatch")
    negative = controls(program, result)
    print("PASS_NATIVE_SHEAR_BATCH schedules=5376 queries=12->8 xor_scans=36->30 "
          f"columns={columns} negative_controls={negative} no_new_kappa")


if __name__ == "__main__":
    main()
