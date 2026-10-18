#!/usr/bin/env python3
# Copyright 2026 Nick Petalas. Licensed under Apache-2.0.
"""Constructive formal-word controls for the mixed-target compression lemma."""

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

MAX_ROLES = 12
MAX_CALLS = 12
ZERO = (Fraction(0),) * 9


def require(condition, message):
    if not condition:
        raise ValueError(message)


def binary_basis(vectors):
    pivots = {}
    selected = []
    for original in vectors:
        value = original
        for pivot in sorted(pivots, reverse=True):
            if value & (1 << pivot):
                value ^= pivots[pivot]
        if value:
            pivots[value.bit_length() - 1] = value
            selected.append(original)
    return tuple(selected)


def rational_rank(rows):
    work = [list(row) for row in rows]
    pivot = 0
    for column in range(9):
        found = next((i for i in range(pivot, len(work)) if work[i][column]), None)
        if found is None:
            continue
        work[pivot], work[found] = work[found], work[pivot]
        scale = work[pivot][column]
        work[pivot] = [x / scale for x in work[pivot]]
        for i in range(pivot + 1, len(work)):
            scale = work[i][column]
            work[i] = [a - scale * b for a, b in zip(work[i], work[pivot], strict=True)]
        pivot += 1
    return pivot


def identity(n):
    return tuple(1 << i for i in range(n))


def add(a, b):
    return tuple(x ^ y for x, y in zip(a, b, strict=True))


def multiply(a, b):
    result = []
    for row in a:
        value = 0
        for i in range(len(b)):
            if row & (1 << i):
                value ^= b[i]
        result.append(value)
    return tuple(result)


def action(matrix, vector):
    return sum(((row & vector).bit_count() % 2) << i for i, row in enumerate(matrix))


def frame_add(a, b):
    return tuple(x + y for x, y in zip(a, b, strict=True))


def accumulate(output, exponent, coefficient):
    updated = add(output.get(exponent, (0,) * len(coefficient)), coefficient)
    if any(updated):
        output[exponent] = updated
    else:
        output.pop(exponent, None)


def expand(word, n):
    """Multiply full matrices in F2[(M3(Q),+)], without address specialization."""
    output = {ZERO: identity(n)} if n else {}
    for frame, projector in word:
        following = {}
        for exponent, coefficient in output.items():
            affected = multiply(coefficient, projector)
            accumulate(following, exponent, add(coefficient, affected))
            accumulate(following, frame_add(exponent, frame), affected)
        output = following
    return output


def validate(word, n):
    require(type(n) is int and 0 <= n <= MAX_ROLES, "role limit")
    require(len(word) <= MAX_CALLS, "call limit")
    for frame, projector in word:
        require(len(frame) == 9 and all(type(x) is Fraction for x in frame), "rational frame")
        rows = [frame[i:i + 3] for i in (0, 3, 6)]
        # Pad three-wide rows for the fixed nine-column rank routine.
        require(rational_rank([tuple(row) + (Fraction(0),) * 6 for row in rows]) == 1,
                "rank-one address")
        require(len(projector) == n, "projector shape")
        require(all(type(row) is int and 0 <= row < (1 << n) for row in projector),
                "binary projector")
        require(len(binary_basis(projector)) == 1, "rank-one projector")
        require(multiply(projector, projector) == projector, "idempotent projector")


def diagonal_targets(output, n):
    targets = []
    for i in range(n):
        seen = []
        for exponent, coefficient in output.items():
            require(coefficient[i] & ~(1 << i) == 0, "off-diagonal endpoint")
            if coefficient[i]:
                seen.append(exponent)
        require(len(seen) == 1, "nonmonomial endpoint")
        targets.append(seen[0])
    return tuple(targets)


def coordinates(basis):
    table = {0: 0}
    for i, vector in enumerate(basis):
        previous = list(table.items())
        for value, encoding in previous:
            require(value ^ vector not in table, "independent image basis")
            table[value ^ vector] = encoding | (1 << i)
    return table


def restrict(projector, basis, table):
    r = len(basis)
    columns = []
    for vector in basis:
        image = action(projector, vector)
        require(image in table, "invariant image space")
        columns.append(table[image])
    return tuple(sum(((column >> i) & 1) << j for j, column in enumerate(columns))
                 for i in range(r))


def compress(word, n):
    validate(word, n)
    original = expand(word, n)
    targets = diagonal_targets(original, n)
    active = tuple(i for i, frame in enumerate(targets) if frame != ZERO)
    images = [1 << i for i in active]
    active_mask = sum(images)
    for _, projector in word:
        # Remove active components so the extra basis vectors are truly dirty.
        images.extend(action(projector, 1 << i) & ~active_mask for i in range(n))
    basis = binary_basis(images)
    table = coordinates(basis)
    reduced = tuple((frame, restrict(projector, basis, table)) for frame, projector in word)
    validate(reduced, len(basis))
    expected = tuple(targets[i] for i in active) + (ZERO,) * (len(basis) - len(active))
    require(diagonal_targets(expand(reduced, len(basis)), len(basis)) == expected,
            "compressed endpoint")
    d = rational_rank([frame for frame, _ in word])
    s = rational_rank(list(targets))
    scalar_dimension = len(binary_basis(sum(row << (n * i) for i, row in enumerate(p))
                                        for _, p in word))
    bound = len(word) - d + s
    require(len(active) <= len(basis) <= scalar_dimension <= bound, "dimension bound")
    return reduced, basis, {"calls": len(word), "roles": n, "active": len(active),
                           "paid_span": d, "target_span": s, "scalar_span": scalar_dimension,
                           "compressed_roles": len(basis), "role_bound": bound}


def embed(basis, vector):
    output = 0
    for i, value in enumerate(basis):
        if vector & (1 << i):
            output ^= value
    return output


def vector_oracle(word, initial):
    """Separate left-action oracle, using vectors instead of matrix products."""
    values = {ZERO: initial} if initial else {}
    for frame, projector in reversed(word):
        following = {}
        for exponent, vector in values.items():
            moved = action(projector, vector)
            for target, value in ((exponent, vector ^ moved), (frame_add(exponent, frame), moved)):
                following[target] = following.get(target, 0) ^ value
        values = {key: value for key, value in following.items() if value}
    return values


def check_oracle(word, n, reduced, basis):
    full = expand(word, n)
    for i in range(n):
        expected = {key: action(value, 1 << i) for key, value in full.items()
                    if action(value, 1 << i)}
        require(vector_oracle(word, 1 << i) == expected, "full input-column oracle")
    for i, vector in enumerate(basis):
        expected = {key: embed(basis, value)
                    for key, value in vector_oracle(reduced, 1 << i).items()}
        require(vector_oracle(word, vector) == expected, "restriction oracle")


def unit(i, j, scale=1):
    return tuple(Fraction(scale) if index == 3 * i + j else Fraction(0) for index in range(9))


def coordinate_projector(n, i):
    return tuple(1 << i if j == i else 0 for j in range(n))


def conjugate(word, n):
    # Each simultaneous row/column transvection is a genuine scalar conjugation.
    result = word
    for i in range(n - 1):
        shear = list(identity(n))
        shear[i] ^= 1 << (i + 1)
        result = tuple((a, multiply(multiply(shear, p), shear)) for a, p in result)
    return result


def fixtures():
    n = 12
    sharp = [(unit(i, i), coordinate_projector(n, i)) for i in range(3)]
    for role, (i, j) in enumerate(((0, 1), (0, 2), (1, 2)), 3):
        p = coordinate_projector(n, role)
        sharp.extend(((unit(i, j, Fraction(1, 2)), p), (unit(i, j, Fraction(-1, 2)), p)))
    mixed = []
    for role in range(3):
        for column in range(3):
            frame = unit(column, column)
            if role == 1 and column == 0:
                frame = frame_add(frame, unit(1, 0))
            if role == 2 and column == 1:
                frame = frame_add(frame, unit(2, 1))
            mixed.append((frame, coordinate_projector(n, role)))
    p = coordinate_projector(n, 3)
    dirty = [*mixed, (unit(0, 2, Fraction(1, 2)), p),
             (unit(0, 2, Fraction(-1, 2)), p)]
    even = [(unit(i, i, Fraction(1, 2)), coordinate_projector(n, i))
            for i in range(3) for _ in range(2)]
    # Conjugate each cancelling pair, not the active calls. Its endpoint is still
    # identity, but its image and reads can now mix active and dirty coordinates.
    output = {}
    for name, word in (("sharp", sharp), ("mixed_invertible", mixed),
                       ("mixed_with_dirt", dirty), ("even_target_classes", even)):
        changed = []
        for a, projector in word:
            transformed = projector
            if any(projector[3:]):
                _, transformed = conjugate(((a, projector),), n)[0]
            changed.append((a, transformed))
        output[name] = tuple(changed)
    p = tuple(9 if i == 0 else 0 for i in range(n))
    q = tuple(9 if i == 3 else 0 for i in range(n))
    r = tuple(24 if i == 3 else 0 for i in range(n))
    require(multiply(p, q) != multiply(q, p), "noncommuting roundtrip")
    prefix = ((unit(0, 1), p), (unit(0, 2), q), (unit(1, 2), r))
    inverse = tuple((tuple(-x for x in a), projector) for a, projector in reversed(prefix))
    direct = tuple((unit(i, i), coordinate_projector(n, 0)) for i in range(3))
    output["noncommuting_roundtrip"] = prefix + inverse + direct
    output["empty"] = ()
    return output


def census():
    counts = []
    a = unit(0, 0)
    for n, horizon in ((2, 3), (3, 2)):
        projectors = []
        for x in range(1, 1 << n):
            for y in range(1, 1 << n):
                if (x & y).bit_count() % 2:
                    projectors.append(tuple(y if x & (1 << i) else 0 for i in range(n)))
        alphabet = tuple(itertools.product((a, unit(0, 0, Fraction(1, 2))), projectors))
        tested = accepted = 0
        for length in range(horizon + 1):
            for word in itertools.product(alphabet, repeat=length):
                tested += 1
                try:
                    diagonal_targets(expand(word, n), n)
                except ValueError:
                    continue
                reduced, basis, _ = compress(word, n)
                check_oracle(word, n, reduced, basis)
                accepted += 1
        counts.append({"roles": n, "horizon": horizon, "words": tested, "diagonal": accepted})
    return counts


def rejects(function, message):
    try:
        function()
    except ValueError:
        return
    raise ValueError("control accepted: " + message)


def controls():
    a = unit(0, 0)
    rejects(lambda: compress(((a, (2, 0)),), 2), "nilpotent scalar call")
    rejects(lambda: compress(((a, (1, 2)),), 2), "rank-two scalar call")
    rejects(lambda: compress(((ZERO, (1, 0)),), 2), "zero address")
    rejects(lambda: compress(((frame_add(a, unit(1, 1)), (1, 0)),), 2), "rank-two address")
    rejects(lambda: compress(((a, (3, 0)),), 2), "off-diagonal endpoint")
    rejects(lambda: compress(((a, (1, 0)),) * 13, 2), "call limit")
    rejects(lambda: compress((), 13), "role limit")
    rejects(lambda: compress(((a, (True, 0)),), 2), "Boolean row")
    rejects(lambda: restrict((3, 0), (2,), {0: 0, 2: 1}), "noninvariant restriction")
    rejects(lambda: coordinates((1, 1)), "dependent image basis")
    return 10


def receipt():
    results = {}
    for name, word in fixtures().items():
        reduced, basis, result = compress(word, 12)
        check_oracle(word, 12, reduced, basis)
        if name == "sharp":
            require(result["compressed_roles"] == result["role_bound"] == 6, "sharp fixture")
        if name.startswith("mixed"):
            targets = diagonal_targets(expand(word, 12), 12)
            for target in targets[:3]:
                rows = [target[i:i + 3] + (Fraction(0),) * 6 for i in (0, 3, 6)]
                require(rational_rank(rows) == 3, "invertible mixed target")
        result["basis"] = list(basis)
        result["restricted_projectors"] = [list(p) for _, p in reduced]
        results[name] = result
    return {"fixtures": results, "census": census(), "failure_controls": controls()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="replace the local result receipt")
    args = parser.parse_args()
    path = Path(__file__).resolve().with_name("RESULT.json")
    result = receipt()
    payload = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.write:
        path.write_text(payload, encoding="utf-8")
    require(json.loads(path.read_text(encoding="utf-8")) == result, "result receipt mismatch")
    print("PASS_MIXED_TARGET_REGISTER_COMPRESSION "
          f"fixtures={len(result['fixtures'])} controls={result['failure_controls']} "
          f"sha256={hashlib.sha256(payload.encode()).hexdigest()}")


if __name__ == "__main__":
    main()
