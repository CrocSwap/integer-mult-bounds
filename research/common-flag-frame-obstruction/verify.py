#!/usr/bin/env python3
"""Finite evidence for the common-flag obstruction; standard library only.

The universal theorem is in README.md. This executable checks examples,
not every circuit. Exponents stay in characteristic zero; coefficients are F2.
"""
import argparse
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import importlib.util
from itertools import product as tuples
import json
from pathlib import Path
import random
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def matrix(rows, n):
    require(len(rows) == n and all(len(row) == n for row in rows), "matrix dimensions")
    require(all(type(x) in (int, str, Q) for row in rows for x in row), "exact entries required")
    return [[Q(x) for x in row] for row in rows]


def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def sub(a, b):
    return [[x - y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def add(a, b):
    return [[x + y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def product(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def reduce_rows(rows, columns):
    a = [[Q(x) for x in row] for row in rows]
    r = 0
    for j in range(columns):
        pivot = next((k for k in range(r, len(a)) if a[k][j]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        scale = a[r][j]
        a[r] = [x / scale for x in a[r]]
        for k in range(len(a)):
            if k != r:
                scale = a[k][j]
                a[k] = [x - scale * y for x, y in zip(a[k], a[r])]
        r += 1
    return a, r


def rank(a):
    return reduce_rows(a, len(a[0]))[1]


def inverse(a):
    n = len(a)
    rows, r = reduce_rows([row + unit for row, unit in zip(a, eye(n))], n)
    require(r == n, "singular flag basis")
    return [row[n:] for row in rows]


def contract(candidate):
    """Reconstruct every physical edge, independently of the repository scorer."""
    w, m = candidate["W"], candidate["m"]
    require(type(w) is int and w >= 2 and type(m) is int and m >= 2, "invalid dimensions")
    gates = candidate["gates"]
    sources, sinks = candidate["source_frames"], candidate["sink_frames"]
    require(len(sources) == len(sinks) == w, "all-role terminals required")
    frames = [matrix(a, m) for a in sources + [g["frame"] for g in gates] + sinks]
    values, last, edges = [1 << j for j in range(w)], list(range(w)), []
    for index, gate in enumerate(gates):
        require(set(gate) == {"roles", "xors", "frame"}, "one common frame required; unsupported gate fields")
        roles = gate["roles"]
        require(roles and len(set(roles)) == len(roles), "distinct gate ports required")
        require(all(type(r) is int and 0 <= r < w for r in roles), "invalid gate ports")
        for role in roles:
            edges.append((last[role], w + index, role))
            last[role] = w + index
        for t, s in gate["xors"]:
            require(t in roles and s in roles and t != s, "XOR outside gate ports")
            values[t] ^= values[s]
    rho = candidate["rho"]
    require(len(rho) == w and all(type(r) is int for r in rho) and
            set(rho) == set(range(w)), "invalid permutation")
    require(all(values[rho[j]] == 1 << j for j in range(w)), "scalar permutation fails")
    for role in range(w):
        edges.append((last[role], w + len(gates) + role, role))
    require(all(sub(frames[w + len(gates) + rho[j]], frames[j]) == eye(m)
                for j in range(w)), "all-role endpoint fails")
    return frames, edges


def shift(row, exponent):
    """Multiply each F2 Laurent polynomial by a monomial (translation)."""
    return [frozenset(tuple(x + y for x, y in zip(term, exponent)) for term in poly)
            for poly in row]


def replay(candidate, characters, edges):
    """Exact coefficient replay, retaining all W independent input columns."""
    w = candidate["W"]
    zero = (Q(0),) * len(characters[0])
    unit = (Q(1),) + zero[1:]
    rows = [[frozenset({zero}) if i == j else frozenset() for j in range(w)]
            for i in range(w)]
    cursor = 0
    for gate in candidate["gates"]:
        for _ in gate["roles"]:
            u, v, role = edges[cursor]
            delta = tuple(b - a for a, b in zip(characters[u], characters[v]))
            rows[role] = shift(rows[role], delta)
            cursor += 1
        for t, s in gate["xors"]:
            rows[t] = [a ^ b for a, b in zip(rows[t], rows[s])]
    for u, v, role in edges[cursor:]:
        delta = tuple(b - a for a, b in zip(characters[u], characters[v]))
        rows[role] = shift(rows[role], delta)
    for source, target in enumerate(candidate["rho"]):
        expected = [frozenset({unit}) if j == source else frozenset() for j in range(w)]
        require(rows[target] == expected, "Laurent endpoint fails")
    active = [characters[u] != characters[v] for u, v, _ in edges]
    require(sum(active) >= w, "character edge count below W")
    return active


def receipt(candidate, frames, edges, character_lists):
    masks = [replay(candidate, char, edges) for char in character_lists]
    costs = [rank(sub(frames[v], frames[u])) for u, v, _ in edges]
    counts = [sum(mask) for mask in masks]
    diagonal_counts = [sum(mask[e] for mask in masks) for e in range(len(edges))]
    require(all(d <= r for d, r in zip(diagonal_counts, costs)), "diagonal rank inequality fails")
    baseline = candidate["W"] * candidate["m"]
    require(sum(costs) >= baseline, "common-flag rank bound fails")
    return dict(baseline=baseline, rank_mass=sum(costs), edge_ranks=costs,
                character_counts=counts,
                edge_character_masks=[sum(int(mask[e]) << j for j, mask in enumerate(masks))
                                      for e in range(len(edges))],
                nilpotent_rank_excess=sum(costs) - sum(counts))


def check_flag(candidate, basis, gauge):
    frames, edges = contract(candidate)
    m = candidate["m"]
    basis, gauge = matrix(basis, m), matrix(gauge, m)
    inv = inverse(basis)
    triangular = [product(product(inv, sub(a, gauge)), basis) for a in frames]
    require(all(a[i][j] == 0 for a in triangular for i in range(m) for j in range(i)),
            "supplied common flag is not preserved")
    characters = [[(a[i][i],) for a in triangular] for i in range(m)]
    return receipt(candidate, frames, edges, characters)


def word(w, rng):
    forward = [(1, 0), (2, 0)] + [tuple(rng.sample(range(w), 2)) for _ in range(4)]
    return forward + forward[::-1] + [(0, 1), (1, 0), (0, 1)]


def make_case(w, m, seed):
    rng = random.Random(seed)
    alphabet = [Q(-2, 3), Q(-1, 2), Q(0), Q(1, 2), Q(1), Q(2)]

    def triangular():
        return [[rng.choice(alphabet) if i <= j else Q(0) for j in range(m)] for i in range(m)]

    sources = [triangular() for _ in range(w)]
    rho = [1, 0] + list(range(2, w))
    sinks = [None] * w
    for j in range(w):
        sinks[rho[j]] = add(sources[j], eye(m))
    gates = [dict(roles=[t, s], xors=[[t, s]], frame=triangular()) for t, s in word(w, rng)]
    if m >= 3:
        # Fixed noncommuting nilpotents; the two gates share physical role 0.
        for index, (i, j) in enumerate([(0, 1), (1, 2)]):
            gates[index]["frame"] = [[Q(0)] * m for _ in range(m)]
            gates[index]["frame"][i][j] = Q(1)
    candidate = dict(W=w, m=m, rho=rho, gates=gates, source_frames=sources, sink_frames=sinks)
    return dict(candidate=candidate, basis=eye(m), gauge=[[Q(0)] * m for _ in range(m)])


def cases():
    result = {f"seed42_m{m}_W{w}": make_case(w, m, 42 + 10 * m + w)
              for m in (2, 3, 4) for w in (4, 5, 6)}
    plain = make_case(5, 3, 42)
    result["noncommuting_jordan"] = plain
    dense = deepcopy(plain)
    basis = matrix([[1, 1, 0], [0, 1, 1], [1, 0, 1]], 3)
    gauge = matrix([[0, 0, 1], [1, 0, 0], [0, 1, 0]], 3)
    inv = inverse(basis)

    def conjugate(a):
        return add(gauge, product(product(basis, a), inv))

    c = dense["candidate"]
    for key in ("source_frames", "sink_frames"):
        c[key] = [conjugate(a) for a in c[key]]
    for gate in c["gates"]:
        gate["frame"] = conjugate(gate["frame"])
    dense.update(basis=basis, gauge=gauge)
    result["conjugated_affine"] = dense
    grouped = deepcopy(plain)
    grouped["candidate"]["gates"] = [dict(
        roles=list(range(5)),
        xors=[update for gate in plain["candidate"]["gates"] for update in gate["xors"]],
        frame=[[Q(0)] * 3 for _ in range(3)])]
    result["grouped_five_port_gate"] = grouped
    result["sharp_untouched"] = dict(
        candidate=dict(W=3, m=2, rho=[0, 1, 2], gates=[],
                       source_frames=[[[0, 0], [0, 0]]] * 3, sink_frames=[eye(2)] * 3),
        basis=eye(2), gauge=[[0, 0], [0, 0]])
    return result


def rotation_candidate():
    case = make_case(5, 2, 42)
    c = case["candidate"]
    # An additive conversion preserving I, applied also to endpoint matrices.
    def rotate(a):
        return [[a[0][0], -a[0][1]], [a[0][1], a[0][0]]]
    for key in ("source_frames", "sink_frames"):
        c[key] = [rotate(a) for a in c[key]]
    for gate in c["gates"]:
        gate["frame"] = rotate(gate["frame"])
    return c


def check_rotation(candidate):
    """Check aI+bJ structure before using its exact Q(i) characters."""
    require(candidate["m"] == 2, "rotation dimension")
    frames, edges = contract(candidate)
    require(all(a[0][0] == a[1][1] and a[0][1] == -a[1][0] for a in frames),
            "rotation eigenvector equations fail")
    require(all(product(a, b) == product(b, a) for a in frames for b in frames),
            "rotation frames do not commute")
    require(any(a[1][0] != 0 for a in frames), "nonsplit example is trivial")
    chars = [[(a[0][0], sign * a[1][0]) for a in frames] for sign in (1, -1)]
    return receipt(candidate, frames, edges, chars)


def rotation_case():
    return check_rotation(rotation_candidate())


def verify_sources():
    pins = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    for name, digest in pins["base_files_sha256"].items():
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest,
                f"source pin mismatch: {name}")


def run():
    results = {name: check_flag(**case) for name, case in cases().items()}
    results["nonsplit_commuting"] = rotation_case()
    # A rank-one dense matrix invalidates the diagonal shortcut without a flag.
    require(rank([[1, 1], [1, 1]]) == 1, "nontriangular boundary control")
    triangular = [[[a, b], [0, d]] for a, b, d in tuples((-1, 0, 1), repeat=3)]
    histogram = {}
    for a in triangular:
        for b in triangular:
            delta = sub(a, b)
            determinant = delta[0][0] * delta[1][1]
            independent_rank = 2 if determinant else int(any(x for row in delta for x in row))
            diagonal = sum(delta[i][i] != 0 for i in range(2))
            require(rank(delta) == independent_rank >= diagonal, "triangular minor census")
            key = f"rank{independent_rank}_diagonal{diagonal}"
            histogram[key] = histogram.get(key, 0) + 1
    return dict(status="PASS_COMMON_FLAG_OBSTRUCTION", seed=42, cases=results,
                triangular_difference_census=dict(pairs=729, histogram=histogram),
                scope="Finite consistency checks; universal theorem is written separately",
                kappa="unchanged")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path, help="write a freshly derived receipt to a NEW file")
    args = parser.parse_args()
    verify_sources()
    result = run()
    spec = importlib.util.spec_from_file_location("flag_tests", HERE / "test_verify.py")
    tests = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tests)
    outcome = unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromModule(tests))
    require(outcome.wasSuccessful(), "negative controls failed")
    if args.emit:
        with args.emit.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads((HERE / "EXPECTED.json").read_text(encoding="utf-8"))
        require(result == expected, "certificate mismatch")
    print(f"PASS_COMMON_FLAG_OBSTRUCTION cases={len(result['cases'])} tests={outcome.testsRun} bound=s>=W*m kappa=unchanged")


if __name__ == "__main__":
    main()
