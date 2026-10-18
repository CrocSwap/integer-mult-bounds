#!/usr/bin/env python3
"""Exact edge census for pointwise-minimum frames of ParitySide(10)."""

from collections import Counter
from functools import cache
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from experiments.parity_side import ParitySide

H = 10
SIZE = 1 << H
ONES = SIZE - 1
ODD = sum(1 << x for x in range(SIZE) if x.bit_count() & 1)
ORTH = tuple(sum(1 << y for y in range(SIZE) if not (x & y).bit_count() & 1)
             for x in range(SIZE))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def dot(x, y):
    return (x & y).bit_count() & 1


def basis(rows):
    pivots = {}
    for x in rows:
        for p in sorted(pivots, reverse=True):
            if x >> p & 1:
                x ^= pivots[p]
        if x:
            p = x.bit_length() - 1
            for q in pivots:
                if pivots[q] >> p & 1:
                    pivots[q] ^= x
            pivots[p] = x
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


@cache
def vectors(rows):
    result = [0]
    for x in rows:
        result += [y ^ x for y in result]
    return tuple(sorted(result))


@cache
def space(rows):
    return sum(1 << x for x in vectors(rows))


@cache
def perp(rows):
    result = (1 << SIZE) - 1
    for x in rows:
        result &= ORTH[x]
    return result


@cache
def characteristic(rows):
    equations = [sum(dot(x, y) << j for j, y in enumerate(rows))
                 | (dot(x, x) << len(rows)) for x in rows]
    for j in range(len(rows)):
        pivot = next(i for i in range(j, len(rows)) if equations[i] >> j & 1)
        equations[j], equations[pivot] = equations[pivot], equations[j]
        for i in range(len(rows)):
            if i != j and equations[i] >> j & 1:
                equations[i] ^= equations[j]
    value = 0
    for j, x in enumerate(rows):
        if equations[j] >> len(rows) & 1:
            value ^= x
    return value


def graph_data(c):
    sources, targets = {}, {n: set() for n in c.active}
    for n in sorted(c.active):
        args = c.args[n]
        sources[n] = (sources[abs(args[0])] | sources[abs(args[1])]
                      if args else {c.inputs[n - 1]})
    for target, n in c.outputs.items():
        targets[abs(n)].add(target)
    for n in sorted(c.active, reverse=True):
        for child in c.args[n] or ():
            targets[abs(child)].update(targets[n])
    return sources, targets


def local_frames(source, target):
    A, B = basis(sorted(source)), basis(sorted(target))
    SA, PB = space(A), perp(B)
    require(SA & PB == SA, "source/target orthogonality")
    if SA & space(B) != 1:
        return (), "common_span", len(A), 0
    radical = SA & perp(A)
    r = radical.bit_count().bit_length() - 1
    require(r <= 1, "fixed DAG radical exceeds the enumerated domain")
    if not r:
        candidates = {A}
    else:
        candidates = {basis((*A, z)) for z in range(SIZE)
                      if PB >> z & 1 and (radical & ORTH[z]) == 1}
    require(candidates, "completion criterion contradicted")
    valid = []
    for U in sorted(candidates):
        require(len(U) == len(A) + r and space(U) & perp(U) == 1,
                "minimum completion is not nondegenerate")
        chi = characteristic(U)
        safe = ((len(U) <= 1 or chi not in source)
                and (len(U) >= H - 1 or (ONES ^ chi) not in target))
        # Literal residuals independently check the characteristic criterion.
        residuals = [space(U) & ORTH[s] for s in source]
        residuals += [perp(U) & ORTH[t] for t in target]
        direct = all(R == 1 or R & ODD for R in residuals)
        require(bool(safe) == bool(direct), "incident residual disagreement")
        if safe:
            valid.append(U)
    return tuple(valid), "feasible" if valid else "incident", len(A) + r, len(candidates)


def edge_kind(U, V):
    if space(U) & space(V) != space(U):
        return "not_nested"
    if U == V or characteristic(U) != characteristic(V):
        return "legal"
    return "alternating"


def direct_edge_kind(U, V):
    if space(U) & space(V) != space(U):
        return "not_nested"
    residual = space(V) & perp(U)
    return "legal" if residual == 1 or residual & ODD else "alternating"


def all_frames(source, target):
    A, B = basis(sorted(source)), basis(sorted(target))
    require(H - len(B) - len(A) <= 3, "all-dimension search domain enlarged")
    allowed = perp(B)
    seen, todo = {A}, [A]
    while todo:
        U = todo.pop()
        for z in range(SIZE):
            if allowed >> z & 1 and not space(U) >> z & 1:
                V = basis((*U, z))
                if V not in seen:
                    seen.add(V)
                    todo.append(V)

    # A separate quotient-subspace enumeration checks completeness, not just witnesses.
    def closure(rows):
        result = {0}
        for x in rows:
            result |= {x ^ y for y in result}
        return result

    a_elements = closure(source)
    covered, quotient = set(a_elements), []
    for z in range(SIZE):
        if all(not dot(z, t) for t in target) and z not in covered:
            quotient.append(z)
            covered |= {x ^ z for x in covered}
    representatives = [0]
    for z in quotient:
        representatives += [x ^ z for x in representatives]
    direct = set()
    for mask in range(1, 1 << len(representatives), 2):
        labels = [i for i in range(len(representatives)) if mask >> i & 1]
        if all(mask >> (x ^ y) & 1 for x in labels for y in labels):
            elements = {a ^ representatives[i] for a in a_elements for i in labels}
            direct.add(sum(1 << x for x in elements))
    require(direct == {space(U) for U in seen}, "extension enumeration incomplete")

    valid = []
    for U in sorted(seen):
        if space(U) & perp(U) != 1:
            continue
        residuals = [space(U) & ORTH[s] for s in source]
        residuals += [perp(U) & ORTH[t] for t in target]
        if all(R == 1 or R & ODD for R in residuals):
            valid.append(U)
    return tuple(valid), len(seen)


def signed_kernel(c):
    values = {}
    for n in sorted(c.active):
        args = c.args[n]
        if args:
            a, b = args
            values[n] = tuple((1 if a > 0 else -1) * x + (1 if b > 0 else -1) * y
                              for x, y in zip(values[abs(a)], values[abs(b)]))
        else:
            values[n] = tuple(int(i == n - 1) for i in range(len(c.inputs)))
    checked = 0
    for target, output in c.outputs.items():
        for source, value in zip(c.inputs, values[abs(output)]):
            intersection = (source & target).bit_count()
            expected = 1 if intersection == 0 else -1 if intersection == 2 else 0
            require(value * (1 if output > 0 else -1) == expected, "signed kernel mismatch")
            checked += 1
    return checked


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def census():
    c = ParitySide(H)
    coefficients = signed_kernel(c)
    sources, targets = graph_data(c)
    frames, node_counts, dimensions = {}, Counter(), {}
    candidate_count = 0
    for n in sorted(c.active):
        frames[n], status, dimensions[n], count = local_frames(sources[n], targets[n])
        node_counts[status] += 1
        candidate_count += count
    edges, counts, pair_counts = [], Counter(), Counter()
    for v in sorted(c.active):
        for child in c.args[v] or ():
            u = abs(child)
            if not frames[u] or not frames[v]:
                counts["excluded_local_failure"] += 1
                continue
            kinds = Counter()
            for U in frames[u]:
                for V in frames[v]:
                    kind = edge_kind(U, V)
                    require(kind == direct_edge_kind(U, V), "edge residual disagreement")
                    kinds[kind] += 1
            pair_counts.update(kinds)
            status = ("legal" if kinds["legal"] else
                      "alternating_only" if kinds["alternating"] else "no_nesting")
            counts[status] += 1
            edges.append([u, v, dimensions[u], dimensions[v],
                          len(frames[u]), len(frames[v]),
                          kinds["legal"], kinds["alternating"], kinds["not_nested"]])
    failures = [e for e in edges if e[6] == 0]
    completed_failures = [e for e in failures if e[3] > len(basis(sources[e[1]]))]
    extended, extended_nodes = [], {}
    for e in completed_failures:
        u, v = e[:2]
        for n in (u, v):
            if n not in extended_nodes:
                extended_nodes[n] = all_frames(sources[n], targets[n])
        left, nl = extended_nodes[u]
        right, nr = extended_nodes[v]
        legal = [(U, V) for U in left for V in right if edge_kind(U, V) == "legal"]
        require(all(edge_kind(U, V) == direct_edge_kind(U, V) for U in left for V in right),
                "all-dimension edge residual disagreement")
        legal.sort(key=lambda pair: (len(pair[0]) + len(pair[1]), pair))
        witness = legal[0] if legal else None
        extended.append({"edge": [u, v], "extension_spaces": [nl, nr],
                         "legal_endpoint_frames": [len(left), len(right)],
                         "legal_pairs": len(legal),
                         "minimum_added_dimensions": (len(witness[0]) + len(witness[1]) - e[2] - e[3]
                                                       if witness else None),
                         "witness": witness})
    return {
        "h": H, "active_nodes": len(c.active), "node_counts": dict(node_counts),
        "signed_coefficients_checked": coefficients,
        "dag_sha256": digest({"args": c.args, "outputs": c.outputs}),
        "minimum_frames_before_incident_filter": candidate_count,
        "minimum_frames_after_incident_filter": sum(map(len, frames.values())),
        "edge_counts": dict(counts), "pair_counts": dict(pair_counts),
        "all_minimum_edge_rows_sha256": digest(edges),
        "minimum_failure_rows": failures,
        "extended_edges": extended,
        "extended_nodes": [{"node": n, "sources": sorted(sources[n]),
                            "targets": sorted(targets[n]), "extension_spaces": count,
                            "all_legal_frames": frames}
                           for n, (frames, count) in sorted(extended_nodes.items())],
        "all_dimension_edge_counts": dict(Counter("impossible" if e["witness"] is None else "repairable"
                                                   for e in extended)),
    }


def controls():
    # Concrete mutations of the transfer rule: ignoring alternation or containment.
    cases = [((7,), (7,), "legal"), ((7,), (11,), "not_nested"),
             ((41, 5, 3), (32, 8, 4, 2, 1), "alternating"),
             ((1,), (2, 1), "legal"), ((1,), (4, 2, 1), "legal")]
    for U, V, expected in cases:
        require(edge_kind(U, V) == expected == direct_edge_kind(U, V), "geometric control")
    mutants = [lambda U, V: "legal",
               lambda U, V: "legal" if space(U) & space(V) == space(U) else "not_nested",
               lambda U, V: "legal" if characteristic(U) != characteristic(V) else "alternating"]
    for mutant in mutants:
        require(any(mutant(U, V) != expected for U, V, expected in cases), "mutant survived")
    require(space((3,)) & perp((3,)) != 1, "radical accepted as nondegenerate")
    require(local_frames({7, 25}, {11, 21})[1] == "common_span", "common-span obstruction missed")
    return len(cases) + len(mutants) + 2


def source_check():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for path, expected in pins["runtime_source_sha256"].items():
        require(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected,
                "source pin mismatch: " + path)


def main():
    source_check()
    checked_controls = controls()
    result = census()
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    require(not sys.argv[1:], "usage: verify.py [--emit]")
    expected = json.loads((HERE / "CERTIFICATE.json").read_text())
    require(json.loads(json.dumps(result)) == expected, "certificate differs from exact census")
    print("PASS_PARITY_EDGE_COMPATIBILITY", json.dumps(result["edge_counts"], sort_keys=True),
          json.dumps(result["all_dimension_edge_counts"], sort_keys=True),
          "controls=" + str(checked_controls))


if __name__ == "__main__":
    main()
