#!/usr/bin/env python3
"""Binary split-pivot transition certificate; standard library, no external reads.

codyw912, with substantial OpenAI Codex (GPT-6 Astra) assistance.
Seven-state numerical targets: Mihir Srivastava, PR4689, exact head cited below.
Apache-2.0. No GL4 or GL5 generator is used.
"""

import json
from collections import Counter
from fractions import Fraction
from functools import cache


class CertificateError(ValueError):
    """A mathematical premise or certificate equality failed."""


def require(condition, message):
    if not condition:
        raise CertificateError(message)


# Expectations transcribed from Mihir's table, not previously observed here.
TABLE_SOURCE = "https://github.com/CrocSwap/integer-mult-bounds/blob/3a72fbad148294aa9ca7f900a48dbb10e64232be/research/schur-residual-orbits/README.md"
S = (0, 0, 4, 8)
TS = ((0, 0, 4, 8), (0, 0, 4, 9), (0, 2, 0, 8),
      (0, 2, 2, 8), (0, 4, 4, 8), (0, 4, 4, 9), (0, 6, 0, 8))
# b, z, orbit, successful orbit elements, header weight, full-guard headers
EXPECTED = ((1, 36, 560, 100, 20160, 3600),
            (3, 4, 5040, 468, 60480, 5616),
            (126, 1, 20160, 366, 2540160, 46116),
            (18, 1, 20160, 816, 362880, 14688),
            (3, 4, 5040, 468, 60480, 5616),
            (3, 4, 5040, 270, 60480, 3240),
            (18, 1, 20160, 816, 362880, 14688))
EXPECTED_TRANSITIONS = ((60, 600), (44, 312), (30, 61), (34, 136),
                        (44, 312), (36, 180), (34, 136))
EXPECTED_DEPTHS = ((280, 180, 100), (3192, 1380, 468),
                   (15120, 4674, 366), (14448, 4896, 816),
                   (3192, 1380, 468), (3528, 1242, 270),
                   (14448, 4896, 816))


def dot(x, y):
    return (x & y).bit_count() & 1


def apply(matrix, vector):
    return sum(dot(row, vector) << i for i, row in enumerate(matrix))


def columns(vectors, n):
    return tuple(sum(((v >> i) & 1) << j for j, v in enumerate(vectors))
                 for i in range(n))


def identity(n):
    return tuple(1 << i for i in range(n))


def multiply(a, b):
    return columns(tuple(apply(a, apply(b, 1 << j)) for j in range(len(b))), len(a))


def add(a, b):
    return tuple(x ^ y for x, y in zip(a, b))


def independent_basis(vectors):
    span = {0}
    basis = []
    for v in vectors:
        if v not in span:
            basis.append(v)
            span |= {x ^ v for x in span}
    return tuple(basis)


def rank(vectors):
    return len(independent_basis(vectors))


def coordinates(basis):
    result = {0: 0}
    for i, v in enumerate(basis):
        require(v not in result, "dependent coordinate basis")
        result.update({x ^ v: c | (1 << i) for x, c in tuple(result.items())})
    return result


def inverse(matrix):
    n = len(matrix)
    coords = coordinates(tuple(apply(matrix, 1 << j) for j in range(n)))
    require(len(coords) == 1 << n, "singular change of basis")
    return columns(tuple(coords[1 << j] for j in range(n)), n)


def conjugate(matrix, basis_matrix):
    return multiply(inverse(basis_matrix), multiply(matrix, basis_matrix))


def gl_order(n):
    result = 1
    for i in range(n):
        result *= (1 << n) - (1 << i)
    return result


@cache
def splits(n):
    return tuple((a, beta) for a in range(1, 1 << n)
                 for beta in range(1, 1 << n) if dot(beta, a))


def admitted(a_matrix, b_matrix):
    for a, beta in splits(len(a_matrix)):
        if dot(beta, apply(a_matrix, a)) and dot(beta, apply(b_matrix, a)):
            yield a, beta


def restriction(matrix, a, beta, omit_correction=False):
    """Intrinsic map on ker(beta), independently checked against block Schur."""
    n = len(matrix)
    require(multiply(matrix, matrix) == matrix, "request is not idempotent")
    require(dot(beta, a) == dot(beta, apply(matrix, a)) == 1, "not an admitted split")
    basis = independent_basis(x for x in range(1, 1 << n) if not dot(beta, x))
    coords = coordinates(basis)
    pivot_image = apply(matrix, a)
    images = []
    for x in basis:
        image = apply(matrix, x)
        if not omit_correction and dot(beta, image):
            image ^= pivot_image
        require(image in coords, "intrinsic Schur image left ker(beta)")
        images.append(coords[image])
    residual = columns(tuple(images), n - 1)
    header = columns((a,) + basis, n)
    block = conjugate(matrix, header)
    require(block[0] & 1, "literal pivot was zero")
    schur = tuple((block[i] >> 1) ^ ((block[0] >> 1) if block[i] & 1 else 0)
                  for i in range(1, n))
    require(residual == schur, "intrinsic restriction disagrees with block Schur")
    require(multiply(residual, residual) == residual, "residual lost idempotency")
    require(rank(residual) == rank(matrix) - 1, "Schur rank decrement failed")
    return residual


@cache
def H(a_matrix, b_matrix, k):
    """Exact complete-header recurrence, retaining the ordered matrix pair."""
    n = len(a_matrix)
    require(len(b_matrix) == n and 0 <= k <= n, "invalid recurrence dimension/depth")
    require(multiply(a_matrix, a_matrix) == a_matrix
            and multiply(b_matrix, b_matrix) == b_matrix, "projectors required")
    if k == 0:
        return gl_order(n)
    return sum(H(restriction(a_matrix, a, beta), restriction(b_matrix, a, beta), k - 1)
               for a, beta in admitted(a_matrix, b_matrix))


def block_diagonal(u, v):
    return (u[0], u[1], v[0] << 2, v[1] << 2)


def block_equations(t, u, v):
    e, f = tuple(x & 3 for x in t[:2]), tuple(x >> 2 for x in t[:2])
    g, h = tuple(x & 3 for x in t[2:]), tuple(x >> 2 for x in t[2:])
    return (multiply(u, e) == multiply(e, u)
            and multiply(u, f) == multiply(f, v)
            and multiply(v, g) == multiply(g, u)
            and multiply(v, h) == multiply(h, v))


def block_catalogue():
    # Only GL2 is generated: its two nonzero, unequal columns give six elements.
    gl2 = tuple(columns((x, y), 2) for x in range(1, 4)
                for y in range(1, 4) if x != y)
    require(len(gl2) == gl_order(2) == 6, "GL2 domain mismatch")
    catalogue = {}
    stabilizers = []
    for state, t in enumerate(TS):
        stabilizer = []
        for u in gl2:
            for v in gl2:
                k = block_diagonal(u, v)
                centralizes = block_equations(t, u, v)
                require(centralizes == (multiply(t, k) == multiply(k, t)),
                        "block equations lost a constraint")
                if centralizes:
                    stabilizer.append(k)
                normalized_t = multiply(k, multiply(t, inverse(k)))
                if normalized_t in catalogue:
                    require(catalogue[normalized_t][0] == state,
                            "ordered representatives have intersecting block orbits")
                else:
                    catalogue[normalized_t] = (state, k)
        require(len(stabilizer) == EXPECTED[state][1], "wrong block stabilizer order")
        stabilizers.append(stabilizer)
    return catalogue, stabilizers


def classify(s, t, catalogue):
    n = len(s)
    kernel = independent_basis(x for x in range(1, 1 << n) if apply(s, x) == 0)
    image = independent_basis(apply(s, 1 << j) for j in range(n))
    c = columns(kernel + image, n)
    require(conjugate(s, c) == S, "kernel/image normalization failed")
    normalized_t = conjugate(t, c)
    require(normalized_t in catalogue, "residual outside seven proved block orbits")
    state, k = catalogue[normalized_t]
    witness = multiply(c, k)
    require(rank(witness) == 4, "singular state intertwiner")
    require(multiply(s, witness) == multiply(witness, S)
            and multiply(t, witness) == multiply(witness, TS[state]),
            "ordered state intertwiner failed")
    return state, witness


def outer(u, phi, n):
    return tuple(phi if (u >> i) & 1 else 0 for i in range(n))


def rank_one(matrix):
    n = len(matrix)
    require(rank(matrix) == 1 and multiply(matrix, matrix) == matrix,
            "rank-one projector required")
    u = next(apply(matrix, 1 << j) for j in range(n) if apply(matrix, 1 << j))
    phi = sum(int(apply(matrix, 1 << j) != 0) << j for j in range(n))
    require(dot(phi, u) == 1 and outer(u, phi, n) == matrix, "rank-one factorization failed")
    return u, phi


def invariant(r, t):
    u, phi = rank_one(r)
    v, psi = rank_one(t)
    return (int(u == v), int(phi == psi), dot(phi, v), dot(psi, u))


def constraint_count(vectors, n, ignore_odd_relations=False):
    # Rank of [v_i | 1] exceeding rank of [v_i] detects inconsistent RHS.
    coefficient_rank = rank(vectors)
    if not ignore_odd_relations and rank(tuple(v | (1 << n) for v in vectors)) != coefficient_rank:
        return 0
    return 1 << (n - coefficient_rank)


def terminal_count(r, t, ignore_odd_relations=False):
    n = len(r)
    u, phi = rank_one(r)
    v, psi = rank_one(t)
    return sum(constraint_count((a, u, v), n, ignore_odd_relations)
               for a in range(1, 1 << n) if dot(phi, a) and dot(psi, a))


def terminal_classes():
    # (u, phi, v, psi); the last four have both flags zero in cross-bit order.
    factors = ((1, 1, 1, 1), (1, 1, 1, 3), (1, 1, 3, 1),
               (1, 1, 2, 2), (1, 1, 2, 3), (1, 3, 2, 2), (1, 3, 2, 7))
    expected = (10, 6, 6, 1, 3, 3, 4)
    table = {}
    representatives = {}
    for factors_i, g in zip(factors, expected):
        u, phi, v, psi = factors_i
        r, t = outer(u, phi, 3), outer(v, psi, 3)
        key = invariant(r, t)
        require(key not in table, "duplicate terminal invariant representative")
        require(terminal_count(r, t) == g == sum(1 for _ in admitted(r, t)),
                "terminal formula disagrees with independent split equations")
        table[key] = g
        representatives[key] = (r, t)
    # Exhaust all rank-one pairs, not all bases: 28^2 pairs in dimension three.
    projectors = tuple(outer(u, phi, 3) for u in range(1, 8)
                       for phi in range(1, 8) if dot(phi, u))
    counts = Counter()
    for r in projectors:
        for t in projectors:
            key = invariant(r, t)
            require(key in table, "missing sufficient invariant class")
            require(terminal_count(r, t) == table[key] == sum(1 for _ in admitted(r, t)),
                    "invariant terminal value is not constant")
            counts[key] += 1
    require(len(counts) == 7 and sum(counts.values()) == 784, "rank-one domain mismatch")
    require(counts == {(1, 1, 1, 1): 28, (1, 0, 1, 1): 84, (0, 1, 1, 1): 84,
                       (0, 0, 0, 0): 168, (0, 0, 0, 1): 168,
                       (0, 0, 1, 0): 168, (0, 0, 1, 1): 84},
            "rank-one invariant population mismatch")
    return table, representatives, counts


def key_text(key):
    return "".join(map(str, key))


def exact_quotient(a, b):
    require(b > 0 and a % b == 0, "nonintegral orbit fibre")
    return a // b


def validate_summary(rows, total, denominator):
    require(len(rows) == 7, "ordered state count changed")
    for row, target, depths, transition in zip(rows, EXPECTED, EXPECTED_DEPTHS, EXPECTED_TRANSITIONS):
        observed = tuple(row[k] for k in ("b", "z", "orbit", "f", "headers", "full_guard_headers"))
        require(observed == target, "cited state table mismatch")
        require(tuple(row["depths"]) == depths, "guard-depth distribution mismatch")
        require((row["m"], row["G"]) == transition, "transition totals mismatch")
    require(total == 93564 and denominator == 9999360, "complete full-guard count mismatch")


def reject(name, action):
    try:
        action()
    except CertificateError:
        return name
    raise CertificateError("mutation was accepted: " + name)


def check_partition(key, rows):
    seen = set()
    for row in rows:
        value = key(row)
        require(value not in seen, "lossy state identification")
        seen.add(value)


def rank_signature(pair):
    s, t = pair
    return (rank(s), rank(t), rank(multiply(s, t)), rank(multiply(t, s)),
            rank(add(s, t)), rank(add(multiply(s, t), multiply(t, s))))


def controls(rows, catalogue, terminal_reps):
    results = []
    missing = [dict(row, full_guard_headers=row["b"] * row["G"]) for row in rows]
    results.append(reject("omitted_GL2_completion_factor",
                          lambda: validate_summary(missing, sum(r["full_guard_headers"] for r in missing), 9999360)))
    results.append(reject("omitted_GL4_completion_factor",
                          lambda: validate_summary([dict(r, headers=r["b"]) for r in rows], 93564, 9999360)))
    results.append(reject("commutator_only_state",
                          lambda: check_partition(lambda p: rank(add(multiply(*p), multiply(p[1], p[0]))),
                                                  ((S, TS[0]), (S, TS[2])))))
    require(rows[0]["G"] != rows[2]["G"], "commutator witness lost differing continuations")
    results.append(reject("product_sum_commutator_rank_state",
                          lambda: check_partition(rank_signature, ((S, TS[1]), (S, TS[4])))))
    # Transposition exchanges states 2/5. Swapping also merges distinct ordered
    # terminal classes 0001/0010, even though their terminal counts coincide.
    transpose = lambda m: columns(m, len(m))
    require(classify(transpose(S), transpose(TS[1]), catalogue)[0] == 4,
            "transpose witness no longer exchanges states 2 and 5")
    require(classify(transpose(S), transpose(TS[3]), catalogue)[0] == 6,
            "transpose witness no longer exchanges states 4 and 7")
    results.append(reject("transpose_identification",
                          lambda: require(classify(S, TS[1], catalogue)[0]
                                          == classify(transpose(S), transpose(TS[1]), catalogue)[0],
                                          "transpose is not an allowed intertwiner")))
    r, t = terminal_reps[(0, 0, 0, 1)]
    require(invariant(t, r) == (0, 0, 1, 0), "ordered cross-pairing witness failed")
    results.append(reject("unordered_requests",
                          lambda: require(invariant(r, t) == invariant(t, r), "ordered invariants differ")))
    r, t = terminal_reps[(0, 0, 0, 0)]
    require(constraint_count((3, 1, 2), 3) == 0, "odd relation accepted")
    results.append(reject("ignored_odd_terminal_relation",
                          lambda: require(terminal_count(r, t, True) == terminal_count(r, t),
                                          "inconsistent terminal RHS contributes spurious solutions")))
    results.append(reject("omitted_Schur_correction",
                          lambda: restriction((3, 0), 1, 1, omit_correction=True)))
    # The previous witness must have a nonzero correction on its kernel.
    results.append(reject("first_guard_substituted_for_full_guard",
                          lambda: validate_summary(rows, sum(r["headers"] for r in rows), 9999360)))
    return results


def main():
    catalogue, stabilizers = block_catalogue()
    terminal, terminal_reps, terminal_populations = terminal_classes()
    p0, q0 = (0, 2, 0, 8, 16), (0, 0, 4, 8, 16)
    initial = []
    weights = Counter()
    for a, beta in admitted(p0, q0):
        s, t = restriction(p0, a, beta), restriction(q0, a, beta)
        state, witness = classify(s, t, catalogue)
        weights[state] += 1
        initial.append({"a": a, "beta": beta, "state": state + 1, "intertwiner": witness})
    require(len(splits(5)) == 496 and len(initial) == 172, "initial split domain mismatch")
    require(gl_order(0) == 1 and gl_order(3) == 168 and gl_order(4) == 20160,
            "zero-guard completion order mismatch")
    require(H((), (), 0) == 1 and H((0,), (0,), 1) == 0,
            "empty completion or impossible guard mishandled")
    rows = []
    for state, t in enumerate(TS):
        transitions = Counter()
        for a, beta in admitted(S, t):
            r1, t1 = restriction(S, a, beta), restriction(t, a, beta)
            key = invariant(r1, t1)
            require(key in terminal, "unclassified next-pivot residual")
            require(terminal[key] == terminal_count(r1, t1), "terminal invariant lost a datum")
            transitions[key] += 1
        m = sum(transitions.values())
        g_sum = sum(weight * terminal[key] for key, weight in transitions.items())
        b, z = weights[state], len(stabilizers[state])
        full = gl_order(2) * g_sum
        require(full == H(S, t, 2), "invariant evaluation disagrees with direct split recurrence")
        depths = tuple(exact_quotient(x, z) for x in
                       (gl_order(4) - gl_order(3) * m, gl_order(3) * m - full, full))
        rows.append({"state": state + 1, "T": t, "b": b, "z": z,
                     "orbit": exact_quotient(gl_order(4), z), "f": exact_quotient(full, z),
                     "m": m, "G": g_sum, "H_4_2": full, "depths": depths,
                     "headers": b * gl_order(4), "headers_per_orbit_element": b * z,
                     "full_guard_headers": b * full,
                     "transitions": {key_text(key): transitions.get(key, 0) for key in sorted(terminal)},
                     "stabilizer_matrices": stabilizers[state]})
    total = sum(row["full_guard_headers"] for row in rows)
    denominator = len(splits(5)) * gl_order(4)
    validate_summary(rows, total, denominator)
    rejected = controls(rows, catalogue, terminal_reps)
    result = {"field": 2, "matrix_encoding": "integer rows, bit j is column j; ordered pairs",
              "expected_table_source": TABLE_SOURCE, "states": rows,
              "initial_split_certificates": initial,
              "terminal_classes": [{"invariant": key_text(key), "g": terminal[key],
                                    "rank_one_pair_population": terminal_populations[key]}
                                   for key in sorted(terminal)],
              "split_domains": {"n5": len(splits(5)), "n4": len(splits(4))},
              "admitted_initial_splits": len(initial), "first_guard_headers": sum(r["headers"] for r in rows),
              "full_guard_headers": total, "all_headers": denominator,
              "full_guard_fraction": str(Fraction(total, denominator)), "rejected_mutations": rejected}
    print(json.dumps(result, indent=2, sort_keys=True))
    print("PASS_SCHUR_INVARIANT_TRANSITIONS")


if __name__ == "__main__":
    main()
