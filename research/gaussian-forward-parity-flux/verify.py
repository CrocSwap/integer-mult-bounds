#!/usr/bin/env python3
"""Exact finite corroboration of the written parity-flux theorem.

The universal claim is proved in PROOF.md, not inferred from these cases.
No predecessor executable, floating point, network or external package is used.
"""
from collections import deque
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json

H = ((1, 1, 1, 1), (1, -1, 1, -1),
     (1, 1, -1, -1), (1, -1, -1, 1))
J = (1, 1, 1, -1)
S = (1, -1, -1, 1)
UNITS = tuple(tuple(sign if i == j else 0 for i in range(4))
              for j in range(4) for sign in (-1, 1))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(x, y):
    return tuple(a + b for a, b in zip(x, y))


def norm2(x):
    return sum(a * a for a in x)


def mv(matrix, x):
    return tuple(sum(a * b for a, b in zip(row, x)) for row in matrix)


def divide(x, denominator):
    require(all(a % denominator == 0 for a in x), "nonintegral division")
    return tuple(a // denominator for a in x)


def ideal_even(x):
    return divide(mv(H, x), 2)


def transformed_output2(y):
    """2 E^T y, in original integer input/output coordinates."""
    return mv(H, tuple(a * b for a, b in zip(J, y)))


def original_odd_input(t2):
    """R(t2/2), using 4x = 2t2 - s(s^T t2)."""
    dot = sum(a * b for a, b in zip(S, t2))
    return divide(tuple(2 * a - b * dot for a, b in zip(t2, S)), 4)


def original_odd_output(v2):
    """E(v2/2), using 4y = J H v2."""
    return divide(tuple(a * b for a, b in zip(J, mv(H, v2))), 4)


def gap_leq(m, n, p, q):
    """Decide sqrt(m)-sqrt(n) <= p/q exactly, for m,n,p>=0,q>0."""
    require(min(m, n, p) >= 0 and q > 0, "invalid root comparison")
    if m <= n:
        return True
    a = (m - n) * q * q - p * p
    return a <= 0 or a * a <= 4 * p * p * q * q * n


def integer_neighbors(x):
    """Enumerate the complete error-one neighborhood in original coordinates."""
    h = mv(H, x)
    choices = [range(-(-(a - 2) // 2), (a + 2) // 2 + 1) for a in h]
    return tuple(y for y in product(*choices)
                 if sum((2 * b - a) ** 2 for a, b in zip(h, y)) <= 4)


def color(t2):
    require(all(a % 2 for a in t2), "not a half-grid point")
    return sum(t2) % 4 // 2  # 1=A, 0=B.


def in_cube(t2, n):
    return max(map(abs, t2)) <= n


def is_corner(t2, n):
    return all(abs(a) == n for a in t2)


def check_coordinates():
    eye4 = tuple(tuple(4 if i == j else 0 for j in range(4)) for i in range(4))
    require(tuple(mv(H, col) for col in H) == eye4, "H orthogonality")
    count = 0
    for x in product(range(-3, 4), repeat=4):
        ns = integer_neighbors(x)
        if sum(x) % 2:
            require(len(ns) == 16, "odd neighbor count")
            require(sum(sum(y) % 2 == 0 for y in ns) == 8, "odd/even split")
            t2 = tuple(2 * a - s * sum(b * c for b, c in zip(S, x))
                       for a, s in zip(x, S))
            require(color(t2) == 1 and original_odd_input(t2) == x,
                    "odd source coordinates")
            for y in ns:
                v2 = transformed_output2(y)
                d = tuple(a - b for a, b in zip(v2, t2))
                if sum(y) % 2:
                    require(color(v2) == 0 and norm2(d) == 4
                            and sum(a != 0 for a in d) == 1, "odd unit edge")
                else:
                    require(all(abs(a) == 1 for a in d), "mixed corner edge")
        else:
            u = ideal_even(x)
            require(len(ns) == 9 and u in ns and sum(u) % 2 == 0,
                    "even neighborhood")
            require(all(y == u or sum(y) % 2 for y in ns), "even change parity")
        count += 1
    # U=L C+ S in the original Gaussian coordinate convention.
    c2 = ((1, -1, 1, 1), (1, 1, -1, 1),
          (1, 1, 1, -1), (-1, 1, 1, 1))
    c_right = tuple(tuple(a * s for a, s in zip(row, (1, -1, 1, 1)))
                    for row in c2)
    lhs = (c_right[0], c_right[2],
           tuple(-a for a in c_right[3]), c_right[1])
    require(lhs == H, "Gaussian signed-permutation transfer")
    return count


def check_cubes():
    receipts = []
    mixed_edges = 0
    narrow_annulus_witness = None
    for n in (3, 5, 7, 9):
        pts = tuple(product(range(-n, n + 1, 2), repeat=4))
        aa = tuple(t for t in pts if color(t) == 1)
        bb = {t for t in pts if color(t) == 0}
        corners = {t for t in bb if is_corner(t, n)}
        require(len(aa) == len(bb) == (n + 1) ** 4 // 2, "color capacity")
        require(len(corners) == 8, "corner count")
        actual_neighbors = set()
        outside_edges = 0
        equality_edges = 0
        for t2 in aa:
            x = original_odd_input(t2)
            require(norm2(t2) == 4 * norm2(x), "source norm transport")
            for y in integer_neighbors(x):
                if sum(y) % 2:
                    v2 = transformed_output2(y)
                    if gap_leq(norm2(y), norm2(x), 3, 10):
                        require(in_cube(v2, n), "unexpected cube escape")
                        require(v2 not in corners, "unexpected admitted corner")
                        actual_neighbors.add(v2)
                    if not in_cube(v2, n):
                        outside_edges += 1
                        require(not gap_leq(norm2(y), norm2(x), 1, 2),
                                "escape at half-unit slack")
                    if v2 in corners:
                        equality_edges += 1
                        require(norm2(y) == n * n
                                and norm2(x) == n * n - n + 1,
                                "corner equality boundary")
                elif n <= 5:
                    # Every possible second image of the charged even input,
                    # still in original coordinates; no asserted cube formula
                    # is used to construct these cases.
                    e = ideal_even(y)
                    require(sum(e) % 2 == 0 and ideal_even(e) == y,
                            "charged exact even input")
                    for u in UNITS:
                        ye = add(y, u)
                        v2 = transformed_output2(ye)
                        d = tuple(a - b for a, b in zip(v2, t2))
                        require(all(a in (-2, 0, 2) for a in d),
                                "two-edge coordinate bound")
                        require(in_cube(v2, n + 2), "two-edge annulus")
                        if (narrow_annulus_witness is None
                                and not in_cube(v2, n)
                                and gap_leq(norm2(y), norm2(x), 3, 10)
                                and gap_leq(norm2(ye), norm2(e), 3, 10)):
                            narrow_annulus_witness = {
                                "N": n, "odd_input": x, "even_output": y,
                                "charged_even_input": e, "charged_output": ye,
                                "t2": t2, "v2": v2}
                        mixed_edges += 1
        require(equality_edges == 32, "all equality edges must be retained")
        require(len(actual_neighbors) <= len(aa) - 8, "Hall deficit")
        receipts.append({"N": n, "A": len(aa), "B": len(bb),
                         "complete_delta_3_10_neighbors": len(actual_neighbors),
                         "Hall_deficit": len(aa) - len(actual_neighbors),
                         "escaping_unit_edges_rejected_at_half": outside_edges,
                         "corner_edges_at_exact_threshold": equality_edges})
    require(narrow_annulus_witness is not None,
            "no control for erroneous same-cube charging")
    return receipts, mixed_edges, narrow_annulus_witness


def hopcroft_karp(adjacency):
    """Deterministic finite matching search, used only for a positive control."""
    left_match = [-1] * len(adjacency)
    right_match = {}
    inf = len(adjacency) + 1
    while True:
        dist = [inf] * len(adjacency)
        queue = deque()
        for u, v in enumerate(left_match):
            if v < 0:
                dist[u] = 0
                queue.append(u)
        found = False
        while queue:
            u = queue.popleft()
            for v in adjacency[u]:
                mate = right_match.get(v)
                if mate is None:
                    found = True
                elif dist[mate] == inf:
                    dist[mate] = dist[u] + 1
                    queue.append(mate)
        if not found:
            break

        def dfs(u):
            for v in adjacency[u]:
                mate = right_match.get(v)
                if mate is None or (dist[mate] == dist[u] + 1 and dfs(mate)):
                    left_match[u] = v
                    right_match[v] = u
                    return True
            dist[u] = inf
            return False

        gained = sum(dfs(u) for u, v in enumerate(left_match) if v < 0)
        require(gained > 0, "matching progress")
    return left_match


def verify_matching(inputs, outputs):
    require(len(outputs) == len(inputs) == len(set(inputs)), "matching domain")
    require(len(set(outputs)) == len(outputs), "duplicate output")
    for x, y in zip(inputs, outputs):
        require(sum((2 * b - a) ** 2 for a, b in zip(mv(H, x), y)) <= 4,
                "non-error-one matching edge")
        require(gap_leq(norm2(y), norm2(x), 3, 10), "outward slack violation")


def expect_reject(fn, label):
    try:
        fn()
    except ValueError:
        return label
    raise ValueError("control was accepted: " + label)


def finite_unrestricted_control():
    radius = 5
    inputs = tuple(x for x in product(range(-radius, radius + 1), repeat=4)
                   if norm2(x) <= radius * radius)
    output_ids = {}
    outputs = []
    adjacency = []
    fixed_adjacency = []
    for x in inputs:
        row = []
        fixed = []
        for y in integer_neighbors(x):
            if gap_leq(norm2(y), norm2(x), 3, 10):
                if y not in output_ids:
                    output_ids[y] = len(outputs)
                    outputs.append(y)
                row.append(output_ids[y])
                if sum(x) % 2 or y == ideal_even(x):
                    fixed.append(output_ids[y])
        adjacency.append(row)
        fixed_adjacency.append(fixed)
    assignment = hopcroft_karp(adjacency)
    require(all(v >= 0 for v in assignment), "unrestricted finite control failed")
    matched = tuple(outputs[v] for v in assignment)
    verify_matching(inputs, matched)  # Separate from the matching algorithm.
    held = hopcroft_karp(fixed_adjacency)
    held_size = sum(v >= 0 for v in held)
    require(held_size < len(inputs), "exact-input restriction control failed")
    f = dict(zip(inputs, matched))
    changed = {e: transformed_output2(y)
               for e, y in f.items() if sum(e) % 2 == 0 and y != ideal_even(e)}
    k = {n: sum(in_cube(v, n) for v in changed.values()) for n in (1, 3, 5)}
    odd_cube = tuple(original_odd_input(t) for t in
                     product(range(-3, 4, 2), repeat=4) if color(t) == 1)
    # Certify the restricted maximum independently of the search algorithm:
    # adjoin every even exact source whose fixed output could be used by
    # an odd cube input. The resulting explicit Hall set has deficiency 8.
    exact_sources = {ideal_even(y) for x in odd_cube for y in integer_neighbors(x)
                     if sum(y) % 2 == 0
                     and gap_leq(norm2(y), norm2(x), 3, 10)}
    hall_inputs = set(odd_cube) | exact_sources
    input_ids = {x: i for i, x in enumerate(inputs)}
    require(hall_inputs <= set(inputs), "Hall closure outside finite ball")
    hall_outputs = {v for x in hall_inputs
                    for v in fixed_adjacency[input_ids[x]]}
    require(len(hall_inputs) - len(hall_outputs) == 8, "restricted Hall witness")
    require(held_size == len(inputs) - 8,
            "restricted matching does not attain its certified Hall upper bound")
    exits = [x for x in odd_cube if sum(f[x]) % 2 == 0]
    for x in exits:
        e = ideal_even(f[x])
        require(e in f and e in changed and in_cube(changed[e], 5),
                "finite closure for parity charge")
    q3 = sum(is_corner(v, 3) for v in changed.values())
    require(len(exits) - k[3] + q3 >= 8, "finite capacity charge")
    require(len(exits) <= k[5] and q3 <= k[3] - k[1],
            "finite annular charges")
    require(k[5] - k[1] >= 8, "finite flux bound")
    duplicate = list(matched)
    duplicate[1] = duplicate[0]
    nonlocal_edge = list(matched)
    nonlocal_edge[0] = add(nonlocal_edge[0], (4, 0, 0, 0))
    controls = [
        expect_reject(lambda: verify_matching(inputs, duplicate), "duplicate output"),
        expect_reject(lambda: verify_matching(inputs, nonlocal_edge), "nonlocal edge"),
    ]
    pairs = [[list(x), list(y)] for x, y in zip(inputs, matched)]
    digest = sha256(json.dumps(pairs, separators=(",", ":")).encode()).hexdigest()
    return {"radius": radius, "inputs": len(inputs),
            "unrestricted_matching_size": len(inputs),
            "matching_with_all_even_inputs_fixed": held_size,
            "restricted_Hall_inputs": len(hall_inputs),
            "restricted_Hall_neighbors": len(hall_outputs),
            "changed_even_inputs": len(changed),
            "K": k, "O_3": len(exits), "q_3": q3,
            "matching_sha256": digest,
            "scope": "Finite positive/negative control; not an infinite map.",
            "rejected_controls": controls}


def check_thresholds():
    cases = 0
    for q in range(1, 31):
        for p in range((q - 1) // 2 + 1):
            delta = Fraction(p, q)
            if delta >= Fraction(1, 2):
                continue
            for n in range(3, 82, 2):
                # c_N > delta is equivalent to sqrt(N²-N+1) < N-delta.
                direct = Fraction(n * n - n + 1) < (n - delta) ** 2
                cutoff = n * (1 - 2 * delta) > 1 - delta * delta
                require(direct == cutoff, "cutoff equivalence")
                cases += 1
    require(not gap_leq(78, 73, 0, 1) and gap_leq(78, 73, 3, 10),
            "finite-threshold comparison")
    require(not gap_leq(9, 7, 3, 10), "N=3 strict corner exclusion")
    # Large symbolic cutoffs exercise arbitrary integer size without enumeration.
    for bits in (8, 32, 128, 512, 2048):
        den = 1 << bits
        delta = Fraction(1, 2) - Fraction(1, den)
        threshold = (1 - delta * delta) / (1 - 2 * delta)
        n = max(3, threshold.numerator // threshold.denominator + 1)
        n += 1 - n % 2
        require(n * (1 - 2 * delta) > 1 - delta * delta, "large onset")
    return cases


def main():
    coordinates = check_coordinates()
    cubes, edge_count, annulus = check_cubes()
    finite = finite_unrestricted_control()
    thresholds = check_thresholds()
    receipt = {
        "status": "PASS_GAUSSIAN_FORWARD_PARITY_FLUX",
        "claim": "Written all-input theorem; finite corroboration only here.",
        "coordinate_inputs": coordinates, "cubes": cubes,
        "two_edge_choices": edge_count,
        "same_cube_charge_counterexample": annulus,
        "finite_unrestricted_control": finite,
        "rational_cutoff_cases": thresholds,
        "large_integer_cutoff_bit_sizes": [8, 32, 128, 512, 2048],
        "boundary_controls": [
            "At delta=c_N, all 32 corner incoming edges are admitted.",
            "At delta=1/2, corner exclusion fails; no lower bound above 1/2.",
            "Using C_N instead of C_(N+2) for the two-edge charge fails.",
            "A finite unrestricted error-one injection has forward slack <=3/10.",
            "Holding its exact even inputs fixed prevents a complete matching."
        ],
        "no_new_kappa": True
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
