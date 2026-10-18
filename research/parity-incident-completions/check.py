#!/usr/bin/env python3
"""Independently check the pinned, finite ParitySide(10) incident certificate.

Geometry uses XOR-closed sets in F_2^10, never the producer's row reduction,
Gram matrices, or characteristic-vector residual classification. The circuit
constructor is shared and pinned; leaf and output reachability are rebuilt.
No files are written. Failed checks raise exceptions even under python -O.
"""
import argparse
from collections import Counter
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "407d52ff15b2217b6e22bce44728b4c3907b6515"
DAG_SHA256 = "13bd7da6b47bfee17213acb2eb1120fbe7324a3ece0691f8139d358149c70040"
SOURCE_SHA256 = {
    "scripts/binary_phase_frames.py": "4148cfa313cf050ed25296e8db36d35871520b8318fd086c7d1facf0c6af67d7",
    "scripts/certify.py": "2348d95008276c5d5764f7e028c3918e484582cd589bd4d9b82919161745e53e",
    "scripts/exclusion_circuit.py": "b253f9d7318becda1c1f3b24e2287ed44a9c27fcea00cf9d531afb950d0457a0",
    "scripts/experiments/disjoint_tensor.py": "102dd59bf96033f96ba0dab4c2aba77b3a7a73b67b0f96929ff8b20a98b91cd8",
    "scripts/experiments/mixed_point_circuit.py": "f509362b5031976a22af351fd158ae0b4520fa4f286a5176ec37023d672a7ddc",
    "scripts/experiments/parity_side.py": "1363ebf82d4c39e458e7bede8253688271008374db70ed4284df84253c8d092b",
    "scripts/paired_exclusion_circuit.py": "8f05f04cf06217befd6d0ee0f2d7d0c5c5eb32cfab8c9a8ca7917fd6d620b7d2",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def dot(x, y):
    return (x & y).bit_count() % 2


def span(vectors):
    result = {0}
    for x in vectors:
        result |= {x ^ y for y in result}
    return frozenset(result)


def dimension(space):
    size = len(space)
    require(size > 0 and size & (size - 1) == 0, "not a binary subspace size")
    return size.bit_length() - 1


def canonical_basis(space):
    # For each leading-bit position, the smallest vector has all other pivot
    # bits cleared. This obtains the canonical basis by set inspection alone.
    leaders = {}
    for x in space - {0}:
        p = x.bit_length()
        leaders[p] = min(x, leaders.get(p, x))
    result = [leaders[p] for p in sorted(leaders, reverse=True)]
    require(span(result) == space and len(result) == dimension(space),
            "canonical basis does not span")
    return result


class Geometry:
    def __init__(self, h):
        self.h = h
        self.universe = frozenset(range(1 << h))
        self.odd = frozenset(x for x in self.universe if dot(x, x))
        self.hyperplanes = tuple(frozenset(y for y in self.universe if not dot(x, y))
                                 for x in self.universe)

    @lru_cache(maxsize=None)
    def perp(self, space):
        result = self.universe
        for x in canonical_basis(space):
            result = result & self.hyperplanes[x]
        require(len(result) * len(space) == len(self.universe), "perpendicular size")
        return result

    def nondegenerate(self, space):
        return space & self.perp(space) == {0}

    def characteristic(self, space):
        # Ambient characteristic is the all-ones vector. Its projection into
        # U is found by literal intersection, not by solving Gram equations.
        omega = (1 << self.h) - 1
        choices = space & {omega ^ x for x in self.perp(space)}
        require(len(choices) == 1, "characteristic is not unique")
        value = next(iter(choices))
        require(all(dot(value, x) == dot(x, x) for x in space), "characteristic identity")
        return value

    def residual_failures(self, space, incident_labels):
        bad = []
        for label in sorted(incident_labels):
            # This explicitly constructs every actual residual. A zero
            # residual is admissible; a positive-dimensional alternating one
            # is not. No characteristic comparison decides this predicate.
            residual = space & self.hyperplanes[label]
            if residual != {0} and residual.isdisjoint(self.odd):
                bad.append(label)
        return bad

    def extensions(self, A, allowed):
        require(A <= allowed, "source span is not in target perpendicular")
        remaining = set(allowed - A)
        while remaining:
            z = min(remaining)
            coset = {z ^ a for a in A}
            require(coset <= remaining, "partial extension coset")
            remaining.difference_update(coset)
            U = A | coset
            require(len(U) == 2 * len(A), "extension dimension")
            if self.nondegenerate(U):
                yield z, U


def validate_vector_list(value, h, label):
    require(type(value) is list, label + ": expected a list")
    require(all(type(x) is int and 0 <= x < (1 << h) for x in value),
            label + ": invalid vector")
    require(len(value) == len(set(value)), label + ": duplicate vector")


def rebuild_graph(circuit):
    active = set(circuit.active)
    sources = {}
    # Independent traversal from each node to its leaves; this does not read
    # the constructor's cached supports or producer's forward label unions.
    for node in sorted(active):
        leaves, seen, pending = set(), set(), [node]
        while pending:
            child = pending.pop()
            if child in seen:
                continue
            require(child in active, "reachability left the active DAG")
            seen.add(child)
            args = circuit.args[child]
            if args:
                require(all(0 < abs(x) < child for x in args), "non-topological edge")
                pending.extend(abs(x) for x in args)
            else:
                require(1 <= child <= len(circuit.inputs), "unknown source leaf")
                leaves.add(circuit.inputs[child - 1])
        sources[node] = leaves
    targets = {node: set() for node in active}
    reached = set()
    for target, signed_node in circuit.outputs.items():
        seen, pending = set(), [abs(signed_node)]
        while pending:
            node = pending.pop()
            if node in seen:
                continue
            require(node in active, "output traversal left active DAG")
            seen.add(node)
            targets[node].add(target)
            if circuit.args[node]:
                pending.extend(abs(x) for x in circuit.args[node])
        reached.update(seen)
    require(reached == active, "inactive or omitted output ancestor")
    # Recompute signed integer coefficients from the arguments. In particular,
    # do not invoke ParitySide.verify(), whose assertions disappear under -O.
    coefficients = {}
    for node in sorted(active):
        args = circuit.args[node]
        if not args:
            coefficients[node] = {circuit.inputs[node - 1]: 1}
            continue
        row = {}
        for signed_child in args:
            child_row = coefficients[abs(signed_child)]
            require(row.keys().isdisjoint(child_row), "overlapping addition supports")
            sign = 1 if signed_child > 0 else -1
            row.update({label: sign * value for label, value in child_row.items()})
        require(set(row) == sources[node], "signed support disagrees with leaf traversal")
        coefficients[node] = row
    require(len(circuit.inputs) == 120 and set(circuit.outputs) == set(circuit.inputs),
            "unexpected source/target kernel domain")
    for target, signed_node in circuit.outputs.items():
        row = coefficients[abs(signed_node)]
        sign = 1 if signed_node > 0 else -1
        for source in circuit.inputs:
            intersection = (source & target).bit_count()
            expected = 1 if intersection == 0 else -1 if intersection == 2 else 0
            require(sign * row.get(source, 0) == expected,
                    "signed kernel entry differs for %d,%d" % (source, target))
    return sources, targets


def check(certificate):
    require(type(certificate) is dict, "certificate is not an object")
    require(set(certificate) == {"format", "base_commit", "seed", "h", "source_sha256",
                                "dag_sha256", "summary", "records"}, "top-level fields")
    require(type(certificate["format"]) is int and certificate["format"] == 1, "format")
    require(certificate["base_commit"] == BASE, "base commit")
    require(type(certificate["seed"]) is int and certificate["seed"] == 47, "seed")
    require(type(certificate["h"]) is int and certificate["h"] == 10, "h")
    require(certificate["source_sha256"] == SOURCE_SHA256, "source hash manifest differs")
    for filename, digest in SOURCE_SHA256.items():
        require(hashlib.sha256((ROOT / filename).read_bytes()).hexdigest() == digest,
                "source hash mismatch: " + filename)
    # Only the pinned constructor is reused. Its transitive imports include
    # binary_phase_frames, but none of that module's geometry is called here.
    sys.path.insert(0, str(ROOT / "scripts"))
    from experiments.parity_side import ParitySide
    circuit = ParitySide(10)
    dag = dict(inputs=list(circuit.inputs),
               args=[[n, list(circuit.args[n]) if circuit.args[n] else None]
                     for n in sorted(circuit.active)],
               outputs=sorted([t, n] for t, n in circuit.outputs.items()))
    require(certificate["dag_sha256"] == DAG_SHA256, "certificate DAG hash differs")
    require(hashlib.sha256(canonical(dag)).hexdigest() == DAG_SHA256, "rebuilt DAG hash differs")
    sources, targets = rebuild_graph(circuit)
    geometry = Geometry(10)
    records = certificate["records"]
    require(type(records) is list, "records must be a list")
    require(all(type(r) is dict and type(r.get("node")) is int for r in records),
            "record must contain integer node")
    ids = [r["node"] for r in records]
    require(ids == sorted(set(ids)), "duplicate or unordered records")
    by_node = {r["node"]: r for r in records}
    expected_nodes, impossible, nondegenerate = [], [], 0
    totals, histogram = Counter(), Counter()
    one_extra_safe_spaces = 0
    for node in sorted(circuit.active):
        A, B = span(sources[node]), span(targets[node])
        Bperp = geometry.perp(B)
        require(A <= Bperp, "nonorthogonal source/target spans")
        if A & B != {0}:
            impossible.append(node)
            continue
        radical = A & geometry.perp(A)
        if radical == {0}:
            nondegenerate += 1
            continue
        require(len(radical) == 2, "unexpected radical dimension")
        expected_nodes.append(node)
        require(node in by_node, "missing record for node " + str(node))
        record = by_node[node]
        prefix = "node %d: " % node
        for field, space in (("source_basis", A), ("target_basis", B)):
            validate_vector_list(record.get(field), 10, prefix + field)
            require(record[field] == canonical_basis(space), prefix + field + " differs")
        minimum = dimension(A) + 1
        require(type(record.get("minimum_dimension")) is int and
                record["minimum_dimension"] == minimum, prefix + "minimum dimension")
        frames = record.get("frames")
        require(type(frames) is list, prefix + "frames is not a list")
        expected_frames, minimum_spaces = [], []
        for z, U in geometry.extensions(A, Bperp):
            complement = geometry.perp(U)
            source_bad = geometry.residual_failures(U, sources[node])
            target_bad = geometry.residual_failures(complement, targets[node])
            expected_frames.append(dict(extra=z, characteristic=geometry.characteristic(U),
                                        source_bad=source_bad, target_bad=target_bad))
            minimum_spaces.append(U)
        require(expected_frames, prefix + "no minimum completion")
        # Canonical JSON comparison also rejects bools masquerading as ints,
        # extra fields, duplicated frames, changed labels and reordered rows.
        require(canonical(frames) == canonical(expected_frames), prefix + "frame enumeration differs")
        safe = sum(not f["source_bad"] and not f["target_bad"] for f in expected_frames)
        fields = {"node", "source_basis", "target_basis", "minimum_dimension", "frames"}
        if safe:
            require(set(record) == fields, prefix + "unexpected record fields")
        else:
            require(set(record) == fields | {"repair"}, prefix + "missing repair classification")
            repair = record["repair"]
            if repair is None:
                require(dimension(Bperp) == minimum, prefix + "unproved impossibility")
                totals["no_incident_safe_frame"] += 1
            else:
                require(type(repair) is dict and set(repair) == {"dimension", "extra_basis"},
                        prefix + "repair fields")
                validate_vector_list(repair["extra_basis"], 10, prefix + "repair basis")
                U = span(list(A) + repair["extra_basis"])
                repair_dimension = dimension(U)
                require(type(repair["dimension"]) is int and
                        repair["dimension"] == repair_dimension, prefix + "repair dimension")
                require(repair_dimension == dimension(A) + len(repair["extra_basis"]),
                        prefix + "dependent repair vectors")
                require(A <= U <= Bperp and geometry.nondegenerate(U), prefix + "invalid repair sandwich")
                require(not geometry.residual_failures(U, sources[node]), prefix + "repair source residual")
                require(not geometry.residual_failures(geometry.perp(U), targets[node]),
                        prefix + "repair target residual")
                if repair_dimension == minimum + 1:
                    safe_extensions = set()
                    for minimal_U in minimum_spaces:
                        for _, extension in geometry.extensions(minimal_U, Bperp):
                            if (not geometry.residual_failures(extension, sources[node]) and
                                    not geometry.residual_failures(geometry.perp(extension), targets[node])):
                                safe_extensions.add(extension)
                    expected_count = {4: 16, 5: 4}.get(dimension(B))
                    require(len(safe_extensions) == expected_count,
                            prefix + "one-extra-dimension completion census")
                    one_extra_safe_spaces += len(safe_extensions)
                    totals["one_extra_dimension_repairs"] += 1
                else:
                    require(repair_dimension == minimum + 2, prefix + "unexpected repair cost")
                    # Any nondegenerate U' containing radical-one A contains a
                    # minimum nondegenerate U: pair the radical with a vector
                    # of U'. A one-dimensional nondegenerate extension of U
                    # needs an odd vector in U^perp intersect B^perp. Enumerate
                    # that actual set for EVERY minimum U to exclude min+1.
                    for minimal_U in minimum_spaces:
                        allowed = geometry.perp(minimal_U) & Bperp
                        require(allowed.isdisjoint(geometry.odd), prefix + "unproved two-dimension lower bound")
                    totals["two_extra_dimension_repairs"] += 1
        histogram[(minimum, len(expected_frames), safe)] += 1
        totals["frames"] += len(expected_frames)
        totals["safe_frames"] += safe
        totals["source_rejected_frames"] += sum(bool(f["source_bad"]) for f in expected_frames)
        totals["target_rejected_frames"] += sum(bool(f["target_bad"]) for f in expected_frames)
        totals["nodes_with_safe_minimum"] += bool(safe)
        totals["nodes_without_safe_minimum"] += not safe
    require(ids == expected_nodes, "record set differs from radical-one feasible domain")
    require(len(expected_nodes) == 692 and totals["frames"] == 3096, "domain count changed")
    require(one_extra_safe_spaces == 168, "one-extra-dimension census total")
    summary = dict(active_nodes=len(circuit.active), nondegenerate_nodes=nondegenerate,
                   impossible_nodes=impossible, enumerated_nodes=len(expected_nodes),
                   **dict(totals),
                   histogram=[list(key) + [count] for key, count in sorted(histogram.items())])
    require(canonical(certificate["summary"]) == canonical(summary), "summary differs from checked records")
    return dict(status="PASS_PARITY_INCIDENT_COMPLETIONS", verified=True,
                one_extra_safe_frame_census=one_extra_safe_spaces, **summary)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=HERE / "CERTIFICATE.json")
    args = parser.parse_args()
    certificate = json.loads(args.certificate.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    result = check(certificate)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
