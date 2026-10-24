#!/usr/bin/env python3
"""Exact independent matrix oracle and bounded constructive checks.

Krzysztof Wojt with OpenAI Codex assistance. Apache-2.0.
No predecessor code, files, network, external solver or package dependencies.
"""

import argparse
from collections import Counter, deque
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

import algebra


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def omega(u, v, n):
    # Deliberately literal, separate from the constructor's packed formula.
    answer = 0
    for i in range(n):
        answer ^= ((u >> i) & 1) * ((v >> (i + n)) & 1)
        answer ^= ((v >> i) & 1) * ((u >> (i + n)) & 1)
    return answer


def act(matrix, vector):
    return sum(((row & vector).bit_count() % 2) << i
               for i, row in enumerate(matrix))


def multiply(left, right):
    rows = []
    for mask in left:
        row = 0
        for j, value in enumerate(right):
            if mask & (1 << j):
                row ^= value
        rows.append(row)
    return tuple(rows)


def literal_turn(n, axis):
    m = 2 * n
    functional = sum(omega(1 << j, axis, n) << j for j in range(m))
    return tuple((1 << i) ^ (functional if axis & (1 << i) else 0)
                 for i in range(m))


def word_matrix(n, axes):
    result = tuple(1 << i for i in range(2 * n))
    for axis in axes:
        check(type(axis) is int and 0 < axis < (1 << (2 * n)), "invalid word axis")
        result = multiply(literal_turn(n, axis), result)
    return result


def symplectic(matrix, n):
    return all(omega(act(matrix, 1 << i), act(matrix, 1 << j), n)
               == omega(1 << i, 1 << j, n)
               for i in range(2 * n) for j in range(2 * n))


def cayley(n):
    # Complete matrix enumeration is separate from the word BFS.
    m = 2 * n
    matrices = {rows for rows in product(range(1, 1 << m), repeat=m)
                if all(omega(rows[i], rows[j], n) == omega(1 << i, 1 << j, n)
                       for i in range(m) for j in range(m))}
    identity = tuple(1 << i for i in range(m))
    distance = {identity: 0}
    queue = deque([identity])
    turns = tuple(literal_turn(n, a) for a in range(1, 1 << m))
    while queue:
        current = queue.popleft()
        for generator in turns:
            following = multiply(generator, current)
            if following not in distance:
                distance[following] = distance[current] + 1
                queue.append(following)
    check(set(distance) == matrices, "matrix enumeration and BFS disagree")
    check(len(distance) == (6 if n == 1 else 720), "group order mismatch")
    expected = {0: 1, 1: 3, 2: 2} if n == 1 else {
        0: 1, 1: 15, 2: 85, 3: 225, 4: 274, 5: 120}
    check(dict(Counter(distance.values())) == expected, "Cayley distance census mismatch")
    return distance


def span(basis):
    values = {0}
    for vector in basis:
        values |= {value ^ vector for value in values}
    return frozenset(values)


def basis_of(values):
    basis = []
    generated = frozenset({0})
    for vector in sorted(values):
        if vector not in generated:
            basis.append(vector)
            generated = span(basis)
    return tuple(basis)


def subspaces(m):
    spaces = {frozenset({0})}
    for _ in range(m):
        enlarged = set(spaces)
        for space in spaces:
            for vector in range(1, 1 << m):
                enlarged.add(frozenset(set(space) | {u ^ vector for u in space}))
        spaces = enlarged
    check(len(spaces) == (5 if m == 2 else 67), "subspace census mismatch")
    return sorted(spaces, key=lambda s: (len(s), tuple(sorted(s))))


def independent_form(n, source, target):
    # Enumerate the complete small U; no constructor elimination is used.
    pairs = {0: 0}
    for u, v in zip(source, target):
        pairs.update({old ^ u: image ^ v for old, image in tuple(pairs.items())})
    lifts = {u ^ v: u for u, v in pairs.items()}
    displacement = basis_of(lifts)
    rows = tuple(sum(omega(lifts[x], y, n) << j for j, y in enumerate(displacement))
                 for x in displacement)
    return len(displacement), len(basis_of(rows))


def verify_endpoint(n, source, target, axes):
    matrix = word_matrix(n, axes)
    check(symplectic(matrix, n), "word is not symplectic")
    check(tuple(act(matrix, u) for u in source) == tuple(target), "literal endpoint mismatch")
    return matrix


def finite_census(n):
    distances = cayley(n)
    counts = Counter()
    for space in subspaces(2 * n):
        source = basis_of(space)
        restrictions = {}
        for matrix, distance in distances.items():
            target = tuple(act(matrix, u) for u in source)
            restrictions[target] = min(restrictions.get(target, 99), distance)
        for target, minimum in restrictions.items():
            r, br = independent_form(n, source, target)
            counts["all_restrictions"] += 1
            check(minimum >= 2 * r - br, "residual-nullity floor failed")
            generic = algebra.reduction_word(n, source, target)
            verify_endpoint(n, source, target, generic)
            check(len(generic) <= 2 * r, "generic two-per-rank bound failed")
            if br != 0 and (r, br) != (2, 1):
                continue
            solved = algebra.exact_completion(n, source, target)
            check(solved["minimum"] == minimum, "exact Cayley minimum mismatch")
            check((solved["displacement_rank"], solved["form_rank"]) == (r, br),
                  "independent residual data mismatch")
            verify_endpoint(n, source, target, solved["axes"])
            counts[f"exact_r{r}_b{br}"] += 1
            for i in range(len(solved["axes"])):
                short = solved["axes"][:i] + solved["axes"][i + 1:]
                matrix = word_matrix(n, short)
                check(tuple(act(matrix, u) for u in source) != target,
                      "omitted turn survived")
                counts["rejected_omissions"] += 1
    expected = 16 if n == 1 else 10096
    check(counts["all_restrictions"] == expected, "restriction count mismatch")
    if n == 2:
        check(counts["exact_r2_b0"] == 30 and counts["exact_r2_b1"] == 1890,
              "singular rank-two census mismatch")
    return dict(sorted(counts.items()))


def larger_fixtures():
    counts = Counter()
    for n in range(2, algebra.MAX_QUBITS + 1):
        for r in range(1, n // 2 + 1):
            source = tuple(1 << j for j in range(n)) + tuple(
                1 << (n + j) for j in range(2 * r, n))
            target = tuple((1 << j) ^ ((1 << (r + j)) if j < r else 0)
                           for j in range(n)) + source[n:]
            counts["zero_form_nilpotent_with_fixed_spectators"] += gauged_checks(n, source, target, 2 * r)
            counts["zero_form_disjoint_source_and_displacement"] += gauged_checks(
                n, source[:r], target[:r], 2 * r)
        for pairs in range(1, n // 2 + 1):
            source = tuple(1 << j for j in range(n))
            target = list(source)
            for i in range(pairs):
                a, b = source[2 * i:2 * i + 2]
                target[2 * i], target[2 * i + 1] = b, a ^ b
            counts["zero_form_order_three"] += gauged_checks(n, source, tuple(target), 4 * pairs)
        if n >= 3:
            source = (1, 1 << n, 1 << (n + 2))
            target = (1 ^ (1 << 1), 1 << n, (1 << (n + 2)) ^ (1 << 2))
            counts["rank_one_form"] += gauged_checks(n, source, target, 3)
    return dict(sorted(counts.items()))


def gauged_checks(n, source, target, minimum):
    count = 0
    for seed in range(4):
        axes = tuple(1 + ((19 * seed + 13 * j + j * j) % ((1 << (2 * n)) - 1))
                     for j in range(2 * n + seed))
        gauge = word_matrix(n, axes)
        left = tuple(act(gauge, u) for u in source)
        right = tuple(act(gauge, v) for v in target)
        solved = algebra.exact_completion(n, left, right)
        check(solved["minimum"] == minimum, "larger expected minimum failed")
        verify_endpoint(n, left, right, solved["axes"])
        count += 1
    return count


def controls():
    invalid = (
        (True, (), ()), (0, (), ()), (10, (), ()),
        (2, (True,), (1,)), (2, (0,), (1,)), (2, (16,), (1,)),
        (2, (1,), ()), (2, (1, 1), (1, 2)),
        (2, (1, 2), (1, 1)), (2, (1, 4), (1, 2)),
        (1, (1,), (2,)),
    )
    for args in invalid:
        try:
            algebra.exact_completion(*args)
        except ValueError:
            continue
        raise RuntimeError("invalid or out-of-scope input accepted")
    try:
        word_matrix(2, (0,))
    except RuntimeError:
        return len(invalid) + 1
    raise RuntimeError("zero axis accepted")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()
    counts = {"dimension_2": finite_census(1), "dimension_4": finite_census(2),
              "larger_fixtures": larger_fixtures(), "rejection_controls": controls()}
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "algebra.py", "verify.py")
    root = Path(__file__).resolve().parent
    hashes = {name: sha256((root / name).read_bytes()).hexdigest() for name in names}
    report = {"status": "PASS_SINGULAR_PARTIAL_PAULI_COMPLETION", "counts": counts,
              "source_sha256": hashes,
              "scope": "Unsigned finite corroboration and witnesses; uniform theorem in PROOF.md. No physical cost or new kappa."}
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.write_report:
        (root / "RESULT.json").write_text(rendered, encoding="utf-8")
    else:
        stored = (root / "RESULT.json").read_bytes()
        check(len(stored) <= 1048576, "oversized receipt")
        check(json.loads(stored) == report, "stored report differs from recomputation")
    print(rendered, end="")


if __name__ == "__main__":
    main()
