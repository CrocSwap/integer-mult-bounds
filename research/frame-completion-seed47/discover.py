#!/usr/bin/env python3
"""Produce minimum-rank frame sandwiches; no supplier or edge-legality claim."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from experiments.parity_side import ParitySide

BASE = "007664306fff84fbb1c9a1b4053b69f439764034"


def dot(x, y):
    return (x & y).bit_count() % 2


def basis(rows):
    """Deterministic low-pivot reduced row echelon basis."""
    pivots = {}
    for x in rows:
        for p, row in sorted(pivots.items()):
            if x >> p & 1:
                x ^= row
        if x:
            p = (x & -x).bit_length() - 1
            for q in pivots:
                if pivots[q] >> p & 1:
                    pivots[q] ^= x
            pivots[p] = x
    return [pivots[p] for p in sorted(pivots)]


def solve(equations, values, h):
    """One solution and a kernel basis of a binary linear system."""
    rows = [[a, b] for a, b in zip(equations, values)]
    pivots = []
    k = 0
    for p in range(h):
        found = next((j for j in range(k, len(rows)) if rows[j][0] >> p & 1), None)
        if found is None:
            continue
        rows[k], rows[found] = rows[found], rows[k]
        for j in range(len(rows)):
            if j != k and rows[j][0] >> p & 1:
                rows[j][0] ^= rows[k][0]
                rows[j][1] ^= rows[k][1]
        pivots.append(p)
        k += 1
    if any(not a and b for a, b in rows):
        raise ValueError("inconsistent constraints")
    particular = sum(rows[j][1] << p for j, p in enumerate(pivots))
    kernel = []
    for free in sorted(set(range(h)) - set(pivots)):
        v = 1 << free
        for j, p in enumerate(pivots):
            v |= ((rows[j][0] >> free) & 1) << p
        kernel.append(v)
    return particular, kernel


def linear_combination(rows, coefficients):
    out = 0
    for i, row in enumerate(rows):
        if coefficients >> i & 1:
            out ^= row
    return out


def radical(A):
    gram = [sum(dot(a, b) << j for j, b in enumerate(A)) for a in A]
    _, kernel = solve(gram, [0] * len(A), len(A))
    return basis(linear_combination(A, c) for c in kernel)


def complete(A, B, h):
    """Return U or an explicit nonzero vector in A intersect B."""
    if any(dot(a, b) for a in A for b in B):
        raise ValueError("source and target spans are not orthogonal")
    R = radical(A)
    # Solve A-coefficients + B-coefficients = 0 for intersection witnesses.
    joined = A + B
    equations = [sum(((v >> i) & 1) << j for j, v in enumerate(joined))
                 for i in range(h)]
    _, relations = solve(equations, [0] * h, len(joined))
    if relations:
        common = linear_combination(A, relations[0])
        if not common:
            raise ValueError("dependent input basis")
        return R, None, common
    partners = []
    for i in range(len(R)):
        rhs = [int(i == j) for j in range(len(R))] + [0] * len(B)
        partner, _ = solve(R + B, rhs, h)
        partners.append(partner)
    U = basis(A + partners)
    if len(U) != len(A) + len(R) or radical(U):
        raise ValueError("completion construction failed")
    return R, U, None


def canonical_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def produce():
    h = 8 + 2 * (47 % 2)
    circuit = ParitySide(h)
    # Obtain future target labels by a separate traversal from each output.
    targets = {node: [] for node in circuit.active}
    for target, output in circuit.outputs.items():
        todo, seen = [abs(output)], set()
        while todo:
            node = todo.pop()
            if node in seen:
                continue
            seen.add(node)
            targets[node].append(target)
            if circuit.args[node]:
                todo.extend(abs(child) for child in circuit.args[node])
    records = []
    for node in sorted(circuit.active):
        positive, negative = circuit.support[node]
        support = positive | negative
        A = basis(label for i, label in enumerate(circuit.inputs) if support >> i & 1)
        B = basis(targets[node])
        R, U, common = complete(A, B, h)
        records.append(dict(node=node, source_basis=A, target_basis=B,
                            radical_dimension=len(R), feasible=U is not None,
                            frame_basis=U, common_vector=common))
    dag = dict(inputs=list(circuit.inputs),
               args=[[n, list(circuit.args[n]) if circuit.args[n] else None]
                     for n in sorted(circuit.active)],
               outputs=sorted([t, n] for t, n in circuit.outputs.items()))
    pins = {}
    for module in list(sys.modules.values()):
        filename = getattr(module, "__file__", None)
        if filename:
            path = Path(filename).resolve()
            if path.is_relative_to(ROOT / "scripts") and path.suffix == ".py":
                pins[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    feasible = [r for r in records if r["feasible"]]
    counts = Counter((len(r["source_basis"]), r["radical_dimension"], len(r["frame_basis"]))
                     for r in feasible)
    summary = dict(active_nodes=len(records), inputs=len(circuit.inputs),
                   binary_nodes=sum(circuit.args[n] is not None for n in circuit.active),
                   output_copies=len(circuit.outputs), feasible_nodes=len(feasible),
                   obstructed_nodes=len(records) - len(feasible),
                   degenerate_source_nodes=sum(r["radical_dimension"] > 0 for r in records),
                   completable_degenerate_nodes=sum(r["radical_dimension"] > 0 for r in feasible),
                   feasible_radical_dimension_sum=sum(r["radical_dimension"] for r in feasible),
                   feasible_rank_histogram=[list(key) + [count] for key, count in sorted(counts.items())])
    return dict(format=1, base_commit=BASE, seed=47, h=h, source_sha256=dict(sorted(pins.items())),
                dag_sha256=canonical_digest(dag), records=records, summary=summary)


if __name__ == "__main__":
    result = produce()
    # One node per line keeps the certificate diff directly inspectable.
    parts = []
    for key, value in sorted(result.items()):
        if key == "records":
            rendered = "[\n" + ",\n".join("    " + json.dumps(row, sort_keys=True)
                                          for row in value) + "\n  ]"
        else:
            rendered = json.dumps(value, sort_keys=True)
        parts.append("  " + json.dumps(key) + ": " + rendered)
    print("{\n" + ",\n".join(parts) + "\n}")
