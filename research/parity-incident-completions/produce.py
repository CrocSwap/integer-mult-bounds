#!/usr/bin/env python3
"""Enumerate all minimum sandwiches of the radical-one ParitySide(10) nodes.

Producer uses row reduction and characteristic vectors. The independent checker
uses literal vector sets and tests residuals, not this module's geometry code.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from experiments.parity_side import ParitySide

BASE = "407d52ff15b2217b6e22bce44728b4c3907b6515"
H = 10


def require(ok, message):
    if not ok:
        raise ValueError(message)


def dot(a, b):
    return (a & b).bit_count() & 1


def basis(rows):
    pivots = {}
    for value in rows:
        for p in sorted(pivots, reverse=True):
            if value >> p & 1:
                value ^= pivots[p]
        if value:
            p = value.bit_length() - 1
            for q in pivots:
                if pivots[q] >> p & 1:
                    pivots[q] ^= value
            pivots[p] = value
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def reduce_mod(value, rows):
    for row in rows:
        if value >> (row.bit_length() - 1) & 1:
            value ^= row
    return value


def gram(rows):
    return [sum(dot(x, y) << j for j, y in enumerate(rows)) for x in rows]


def characteristic(rows):
    n = len(rows)
    equations = [g | (dot(v, v) << n) for g, v in zip(gram(rows), rows)]
    # Gauss-Jordan on a full-rank n-by-n Gram matrix.
    for column in range(n):
        pivot = next(i for i in range(column, n) if equations[i] >> column & 1)
        equations[column], equations[pivot] = equations[pivot], equations[column]
        for i in range(n):
            if i != column and equations[i] >> column & 1:
                equations[i] ^= equations[column]
    result = 0
    for i, row in enumerate(rows):
        if equations[i] >> n & 1:
            result ^= row
    return result


def graph_data(circuit):
    sources, targets = {}, {n: set() for n in circuit.active}
    for n in sorted(circuit.active):
        args = circuit.args[n]
        sources[n] = (sources[abs(args[0])] | sources[abs(args[1])]
                      if args else {circuit.inputs[n - 1]})
    for t, n in circuit.outputs.items():
        targets[abs(n)].add(t)
    for n in sorted(circuit.active, reverse=True):
        if circuit.args[n]:
            for child in circuit.args[n]:
                targets[abs(child)].update(targets[n])
    return sources, targets


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def produce():
    c = ParitySide(H)
    sources, targets = graph_data(c)
    records, obstructed, nondegenerate = [], [], 0
    for n in sorted(c.active):
        A, B = basis(sorted(sources[n])), basis(sorted(targets[n]))
        require(all(dot(a, b) == 0 for a in A for b in B), "nonorthogonal spans")
        radical = len(A) - len(basis(gram(A)))
        if len(basis(A + B)) < len(A) + len(B):
            obstructed.append(n)
            continue
        if not radical:
            nondegenerate += 1
            continue
        require(radical == 1, "domain has changed: radical is not one")
        candidates = sorted({reduce_mod(z, A) for z in range(1 << H)
                             if all(not dot(z, b) for b in B)})
        frames = []
        for z in candidates:
            U = basis(A + (z,))
            if len(U) != len(A) + 1 or len(basis(gram(U))) != len(U):
                continue
            w = characteristic(U)
            source_bad = [w] if len(U) > 1 and w in sources[n] else []
            complement_w = ((1 << H) - 1) ^ w
            target_bad = ([complement_w] if H - len(U) > 1 and
                          complement_w in targets[n] else [])
            frames.append(dict(extra=z, characteristic=w,
                               source_bad=source_bad, target_bad=target_bad))
        require(frames, "feasible radical-one node has no minimum completion")
        record = dict(node=n, source_basis=list(A), target_basis=list(B),
                      minimum_dimension=len(A) + 1, frames=frames)
        if not any(not f["source_bad"] and not f["target_bad"] for f in frames):
            repair = None
            for frame in frames:
                z = frame["extra"]
                U = basis(A + (z,))
                for w in sorted({reduce_mod(v, U) for v in range(1 << H)
                                 if all(not dot(v, b) for b in B)}):
                    W = basis(U + (w,))
                    if len(W) != len(A) + 2 or len(basis(gram(W))) != len(W):
                        continue
                    cw = characteristic(W)
                    if (len(W) > 1 and cw in sources[n]) or (
                            H - len(W) > 1 and ((1 << H) - 1) ^ cw in targets[n]):
                        continue
                    repair = dict(dimension=len(W), extra_basis=[z, w])
                    break
                if repair is not None:
                    break
            if repair is None and H - len(B) == len(A) + 3:
                # In this fixed domain the remaining repairable cases have
                # one target line, and their full target-perp is dimension 9.
                # Check the characteristic witness rather than assume this.
                W = basis(v for v in range(1 << H) if all(not dot(v, b) for b in B))
                require(len(basis(gram(W))) == len(W), "degenerate maximal repair")
                cw = characteristic(W)
                if not (len(W) > 1 and cw in sources[n]) and not (
                        H - len(W) > 1 and ((1 << H) - 1) ^ cw in targets[n]):
                    extras, current = [], A
                    for v in W:
                        if reduce_mod(v, current):
                            extras.append(v)
                            current = basis(current + (v,))
                    repair = dict(dimension=len(W), extra_basis=extras)
            # Null means no larger dimension fits; the minimum-frame census
            # then proves impossibility, rather than a failed repair search.
            require(repair is not None or H - len(B) == len(A) + 1,
                    "unresolved node: larger frames remain unchecked: " + str(n))
            record["repair"] = repair
        records.append(record)
    histogram = Counter()
    totals = Counter()
    for record in records:
        frames = record["frames"]
        safe = sum(not f["source_bad"] and not f["target_bad"] for f in frames)
        histogram[(record["minimum_dimension"], len(frames), safe)] += 1
        totals["frames"] += len(frames)
        totals["safe_frames"] += safe
        totals["source_rejected_frames"] += sum(bool(f["source_bad"]) for f in frames)
        totals["target_rejected_frames"] += sum(bool(f["target_bad"]) for f in frames)
        totals["nodes_with_safe_minimum"] += bool(safe)
        totals["nodes_without_safe_minimum"] += not safe
        if not safe:
            totals["one_extra_dimension_repairs"] += (record["repair"] is not None and
                record["repair"]["dimension"] == record["minimum_dimension"] + 1)
            totals["two_extra_dimension_repairs"] += (record["repair"] is not None and
                record["repair"]["dimension"] == record["minimum_dimension"] + 2)
            totals["no_incident_safe_frame"] += record["repair"] is None
    dag = dict(inputs=list(c.inputs),
               args=[[n, list(c.args[n]) if c.args[n] else None] for n in sorted(c.active)],
               outputs=sorted([t, n] for t, n in c.outputs.items()))
    pins = {}
    for module in list(sys.modules.values()):
        filename = getattr(module, "__file__", None)
        if filename:
            path = Path(filename).resolve()
            if path.is_relative_to(ROOT / "scripts") and path.suffix == ".py":
                pins[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return dict(format=1, base_commit=BASE, seed=47, h=H,
                source_sha256=dict(sorted(pins.items())),
                dag_sha256=hashlib.sha256(canonical(dag)).hexdigest(),
                summary=dict(active_nodes=len(c.active), nondegenerate_nodes=nondegenerate,
                             impossible_nodes=obstructed, enumerated_nodes=len(records),
                             **dict(totals),
                             histogram=[list(key) + [count] for key, count in sorted(histogram.items())]),
                records=records)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = produce()
    # One complete node record per line makes changes to the finite census
    # inspectable without a many-thousand-line indentation-only artifact.
    fields = []
    for key, value in sorted(result.items()):
        if key == "records":
            rendered = "[\n" + ",\n".join("    " + json.dumps(row, sort_keys=True)
                                         for row in value) + "\n  ]"
        else:
            rendered = json.dumps(value, sort_keys=True)
        fields.append("  " + json.dumps(key) + ": " + rendered)
    args.out.write_text("{\n" + ",\n".join(fields) + "\n}\n", encoding="utf-8", newline="\n")
    print(json.dumps(result["summary"], sort_keys=True))
