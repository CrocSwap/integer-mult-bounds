#!/usr/bin/env python3
# Copyright 2026 Nick Petalas. Licensed under Apache-2.0.
"""Exact generated-lattice and formal-endpoint controls for the written lemma."""

import argparse
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path

MAX_ROWS = 18
WIDTH = 9
MAX_BITS = 4096
ZERO = (Fraction(0),) * WIDTH


def require(condition, message):
    if not condition:
        raise ValueError(message)


def bounded(row):
    require(all(abs(x).bit_length() <= MAX_BITS for x in row), "integer capacity")
    return row


def bezout(a, b):
    """At most twice the bit capacity suffices for Euclid's decreasing remainders."""
    old, new, s, t, u, v = a, b, 1, 0, 0, 1
    for _ in range(2 * MAX_BITS + 1):
        if new == 0:
            sign = 1 if old >= 0 else -1
            return sign * old, sign * s, sign * t
        q, remainder = divmod(old, new)
        old, new, s, u, t, v = new, remainder, u, s - q * u, v, t - q * v
    raise ValueError("Euclid capacity")


def lattice_basis(rows):
    """Unimodular integer row operations, not rational row-space saturation."""
    require(0 <= len(rows) <= MAX_ROWS, "row capacity")
    require(all(len(row) == WIDTH for row in rows), "lattice shape")
    require(all(type(x) is int for row in rows for x in row), "integer lattice")
    work = [bounded(list(row)) for row in rows]
    pivot = 0
    for column in range(WIDTH):
        found = next((i for i in range(pivot, len(work)) if work[i][column]), None)
        if found is None:
            continue
        work[pivot], work[found] = work[found], work[pivot]
        for i in range(pivot + 1, len(work)):
            a, b = work[pivot][column], work[i][column]
            if not b:
                continue
            g, s, t = bezout(a, b)
            first, second = work[pivot], work[i]
            work[pivot] = bounded([s * x + t * y for x, y in zip(first, second, strict=True)])
            work[i] = bounded([(-b // g) * x + (a // g) * y
                               for x, y in zip(first, second, strict=True)])
        if work[pivot][column] < 0:
            work[pivot] = [-x for x in work[pivot]]
        for i in range(pivot):
            q = work[i][column] // work[pivot][column]
            work[i] = bounded([x - q * y for x, y in zip(work[i], work[pivot], strict=True)])
        pivot += 1
    require(not any(any(row) for row in work[pivot:]), "echelon invariant")
    return tuple(tuple(row) for row in work[:pivot])


def lattice_coordinates(basis, row):
    remaining = list(row)
    result = []
    for vector in basis:
        pivot = next(i for i, x in enumerate(vector) if x)
        q, remainder = divmod(remaining[pivot], vector[pivot])
        if remainder:
            return None
        result.append(q)
        remaining = [x - q * y for x, y in zip(remaining, vector, strict=True)]
    return None if any(remaining) else tuple(result)


def target_classes(frames, targets):
    require(1 <= len(frames) <= MAX_ROWS and len(targets) == 3, "frame capacity")
    values = [x for row in (*frames, *targets) for x in row]
    require(all(len(row) == WIDTH for row in (*frames, *targets)), "frame shape")
    require(all(type(x) is Fraction for x in values), "exact rational entries")
    require(all(abs(x.numerator) <= 65535 and x.denominator <= 65535 for x in values),
            "rational capacity")
    scale = math.lcm(*(x.denominator for x in values))
    require(scale.bit_length() <= 128, "denominator capacity")
    basis = lattice_basis([tuple(int(x * scale) for x in row) for row in frames])
    coordinates = [lattice_coordinates(basis, tuple(int(x * scale) for x in row))
                   for row in targets]
    require(all(row is not None for row in coordinates), "target outside generated lattice")
    classes = [tuple(x % 2 for x in row) for row in coordinates]
    return {"lattice_rank": len(basis), "scale": scale,
            "basis": [list(row) for row in basis],
            "target_coordinates": [list(row) for row in coordinates],
            "target_classes": [list(row) for row in classes],
            "uniform": classes[0] == classes[1] == classes[2]}


def eye(n):
    return tuple(1 << i for i in range(n))


def xor(a, b):
    return tuple(x ^ y for x, y in zip(a, b, strict=True))


def multiply(a, b):
    return tuple(sum_rows(b, row) for row in a)


def sum_rows(rows, mask):
    result = 0
    for i in range(len(rows)):
        if mask & (1 << i):
            result ^= rows[i]
    return result


def outer(x, y, n):
    return tuple(y if x & (1 << i) else 0 for i in range(n))


def rank_one(matrix):
    return len(set(matrix) - {0}) == 1


def frame_add(a, b):
    return tuple(x + y for x, y in zip(a, b, strict=True))


def accumulate(output, exponent, matrix):
    result = xor(output.get(exponent, (0,) * len(matrix)), matrix)
    if any(result):
        output[exponent] = result
    else:
        output.pop(exponent, None)


def expand(word, n):
    require(3 <= n <= 6 and len(word) <= MAX_ROWS, "word capacity")
    output = {ZERO: eye(n)}
    for frame, projector in word:
        require(rank_one(projector) and multiply(projector, projector) == projector,
                "rank-one scalar idempotent")
        following = {}
        for exponent, coefficient in output.items():
            affected = multiply(coefficient, projector)
            accumulate(following, exponent, xor(coefficient, affected))
            accumulate(following, frame_add(exponent, frame), affected)
        require(len(following) <= 4096, "formal support capacity")
        output = following
    return output


def endpoint(targets, n):
    output = {}
    for i in range(n):
        accumulate(output, targets[i] if i < 3 else ZERO, outer(1 << i, 1 << i, n))
    return output


def unit(i, j):
    return tuple(Fraction(int(k == 3 * i + j)) for k in range(WIDTH))


def scale_frame(frame, scalar):
    return tuple(x * scalar for x in frame)


def determinant(frame):
    a, b, c, d, e, f, g, h, i = frame
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def address_rank_one(frame):
    return any(frame) and all(frame[3 * i + k] * frame[3 * j + l]
                              == frame[3 * i + l] * frame[3 * j + k]
                              for i, j in itertools.combinations(range(3), 2)
                              for k, l in itertools.combinations(range(3), 2))


def example():
    e11, e22, e33, e12, e21 = (unit(i, j) for i, j in ((0, 0), (1, 1), (2, 2), (0, 1), (1, 0)))
    frames = (e11, e22, e33,
              frame_add(e11, scale_frame(e21, 2)), frame_add(e22, scale_frame(e21, 2)), e33,
              frame_add(e11, scale_frame(e12, 2)), frame_add(e22, scale_frame(e12, 2)), e33)
    targets = tuple(tuple(sum(row[k] for row in frames[start:start + 3]) for k in range(WIDTH))
                    for start in (0, 3, 6))
    require(all(address_rank_one(frame) for frame in frames), "rank-one example frames")
    require([determinant(frame) for frame in targets] == [1, 1, 1], "invertible example targets")
    return frames, targets


def lattice_oracle():
    """Independent literal integer combinations on a fixed two-coordinate domain."""
    pool = ((1, 0), (0, 1), (1, 1), (2, 0), (0, 2), (1, -1), (2, 2))
    cases = 0
    for a, b in itertools.product(pool, repeat=2):
        basis = lattice_basis([a + (0,) * 7, b + (0,) * 7])
        reachable = {(s * a[0] + t * b[0], s * a[1] + t * b[1])
                     for s, t in itertools.product(range(-16, 17), repeat=2)}
        for target in itertools.product(range(-4, 5), repeat=2):
            actual = lattice_coordinates(basis, target + (0,) * 7) is not None
            require(actual == (target in reachable), "integer-combination oracle mismatch")
            cases += 1
    # This gcd-one lattice needs all three generators to exhibit its unit.
    basis = lattice_basis([(x,) + (0,) * 8 for x in (6, 10, 15)])
    require(lattice_coordinates(basis, (1,) + (0,) * 8) == (1,), "three-generator gcd")
    return cases


def active_bases():
    result = []
    for columns in itertools.permutations(range(1, 8), 3):
        if len({sum_rows(columns, mask) for mask in range(8)}) != 8:
            continue
        s = tuple(sum(((columns[j] >> i) & 1) << j for j in range(3)) for i in range(3))
        inverse_columns = tuple(next(v for v in range(8) if sum_rows(columns, v) == 1 << i)
                                for i in range(3))
        inverse = tuple(sum(((inverse_columns[j] >> i) & 1) << j for j in range(3))
                        for i in range(3))
        pair = (s + (8,), inverse + (8,))
        require(multiply(*pair) == eye(4) and multiply(*reversed(pair)) == eye(4), "active basis inverse")
        result.append(pair)
    require(len(result) == 168, "complete active bases")
    return result


def invariant(matrix, subspace):
    return all(action(matrix, v) in subspace for v in subspace)


def action(matrix, vector):
    return sum(((row & vector).bit_count() % 2) << i for i, row in enumerate(matrix))


def split_controls():
    """Test mixed spectral coefficients, not just the identical target P."""
    bases = active_bases()
    partitions = ((0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 1, 2))
    accepted = rejected = mixed_basis = 0
    for x, y in itertools.product(range(1, 16), repeat=2):
        if (x & y).bit_count() % 2 != 1:
            continue
        q = outer(x, y, 4)
        # Only the new four-dimensional image case, x has a dirty component.
        if not x & 8:
            continue
        c = int(bool(y & 8))
        if c == 0:
            subspace = frozenset((0, 8))
        else:
            i = next(i for i in range(3) if not (x & y & (1 << i)))
            subspace = (frozenset((0, 1 << i)) if not y & (1 << i)
                        else frozenset(v for v in range(16) if not v & (1 << i)))
        require(invariant(q, subspace), "paid invariant subspace")
        for s, inverse in bases:
            for labels in partitions:
                spectra = []
                for label in sorted(set(labels)):
                    diagonal = tuple((1 << i) if i < 3 and labels[i] == label else 0
                                     for i in range(4))
                    spectra.append(multiply(multiply(s, diagonal), inverse))
                if not all(invariant(p, subspace) for p in spectra):
                    rejected += 1
                    continue
                pieces = [frozenset(action(p, v) for v in subspace) for p in spectra]
                dirty_piece = frozenset(v & 8 for v in subspace)
                reconstructed = {0}
                for piece in (*pieces, dirty_piece):
                    reconstructed = {a ^ b for a in reconstructed for b in piece}
                require(reconstructed == subspace, "spectral subspace reconstruction")
                active_dimension = sum((len(piece).bit_length() - 1) for piece in pieces)
                expected = 0 if c == 0 else (1 if len(subspace) == 2 else 2)
                require(active_dimension == expected, "one-plus-two active target split")
                accepted += 1
                mixed_basis += int(any(p[i] & ~(1 << i) for p in spectra for i in range(4)))
    require(accepted > 0 and rejected > 0 and mixed_basis > 0, "mixed split controls nonvacuous")
    return {"compatible": accepted, "incompatible": rejected, "nondiagonal_compatible": mixed_basis}


def evidence():
    frames, targets = example()
    fixtures = {}
    for name, scalar in (("integer", Fraction(1)), ("half_integral", Fraction(1, 2)),
                         ("all_entries_even", Fraction(2)), ("thirds", Fraction(-1, 3))):
        paid = tuple(scale_frame(frame, scalar) for frame in frames)
        target = tuple(scale_frame(frame, scalar) for frame in targets)
        classes = target_classes(paid, target)
        require(classes["uniform"] and any(classes["target_classes"][0]), "common nonzero class")
        word = tuple((frame, outer(1 << (i // 3), 1 << (i // 3), 5))
                     for i, frame in enumerate(paid))
        require(expand(word, 5) == endpoint(target, 5), "nine-call formal endpoint")
        require(expand(word[:-1], 5) != endpoint(target, 5), "omitted-call control")
        require(target_classes(tuple(reversed(paid)), target) == classes, "lattice order invariance")
        fixtures[name] = classes
    split_paid = tuple(scale_frame(frame, Fraction(1, 2)) for frame in frames for _ in range(2))
    even = target_classes(split_paid, targets)
    require(even["uniform"] and not any(even["target_classes"][0]), "zero common class")
    split_word = tuple((frame, outer(1 << (i // 6), 1 << (i // 6), 5))
                       for i, frame in enumerate(split_paid))
    require(expand(split_word, 5) == endpoint(targets, 5), "eighteen-call even-class endpoint")
    fixtures["zero_class_after_splitting"] = even
    nonuniform = (targets[0], scale_frame(targets[0], 2), scale_frame(targets[0], 3))
    require(not target_classes(frames, nonuniform)["uniform"], "unequal target-class control")
    # Prefix calls actually read arbitrary dirty coordinates and then undo them.
    p, q = outer(1 | 8, 1, 5), outer(1 | 16, 16, 5)
    prefix = ((frames[0], p), (frames[1], q), (scale_frame(frames[1], -1), q),
              (scale_frame(frames[0], -1), p))
    direct = tuple((frame, outer(1 << (i // 3), 1 << (i // 3), 5))
                   for i, frame in enumerate(frames))
    require(expand(prefix + direct, 5) == endpoint(targets, 5), "dirty roundtrip endpoint")
    require(expand(prefix[:-1] + direct, 5) != endpoint(targets, 5), "missing dirty restore")
    dirty_paid = tuple(frame for frame, _ in prefix + direct)
    require(target_classes(dirty_paid, targets)["uniform"], "dirty roundtrip parity")
    return {"fixtures": fixtures, "integer_oracle_cases": lattice_oracle(),
            "spectral_splits": split_controls(), "no_new_kappa": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate RESULT.json only")
    args = parser.parse_args()
    result = evidence()
    path = Path(__file__).with_name("RESULT.json")
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        path.write_text(payload, encoding="utf-8")
    else:
        require(path.read_text(encoding="utf-8") == payload, "RESULT.json mismatch")
    print("PASS_PARITY_UNIFORM_TARGETS " + json.dumps({
        "fixtures": len(result["fixtures"]), "integer_oracle_cases": result["integer_oracle_cases"],
        "spectral_splits": result["spectral_splits"], "no_new_kappa": True}, sort_keys=True))


if __name__ == "__main__":
    main()
