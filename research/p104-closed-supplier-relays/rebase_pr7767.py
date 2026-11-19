#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Apply or invert a literal graph patch based on the serialized #7767 word."""

import argparse
from fractions import Fraction
from functools import cache
from graphlib import TopologicalSorter
import gzip
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = "eb8a9cbf477308f8baa949a780a5a3b6d998ff9a64934591839a4b5690186702"
JOINT = "126352b5e607b9d8a5863a02ee667de389655e81cfa4175e70e1aa5d0a264771"
SCHEMA = "p104-pr7767-base-patch/v1"
FIELDS = {"first_output", "frames", "initial", "final", "moves", "forms", "schedule"}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return sha256(encoded(value)).hexdigest()


def read_bytes(path):
    data = Path(path).read_bytes()
    return gzip.decompress(data) if data.startswith(b"\x1f\x8b") else data


def read(path):
    return json.loads(read_bytes(path))


def load_graph(path):
    raw = read_bytes(path)
    graph = json.loads(raw)
    need(raw == encoded(graph), f"noncanonical graph bytes in {path}")
    return graph


def write(path, data):
    path = Path(path)
    path.write_bytes(gzip.compress(data, mtime=0) if path.suffix == ".gz" else data)


@cache
def span(frame):
    out = {0}
    for v in frame:
        need(type(v) is int and 0 < v < 512 and v not in out, "invalid chart basis")
        out |= {v ^ x for x in out}
    return out


@cache
def coefficient(value):
    q = Fraction(value)
    need(q and str(q) == value, f"noncanonical coefficient {value!r}")


def inventory(graph):
    moves = {k: [a, b] for k, a, b in graph["moves"]}
    rows = {k: dict(row) for k, row in graph["forms"]}
    need(list(moves) == sorted(moves) and len(moves) == len(graph["moves"]), "move ordering")
    need(list(rows) == sorted(rows) and len(rows) == len(graph["forms"]), "form ordering")
    need(all([d for d, _ in row] == sorted(rows[k]) for k, row in graph["forms"]), "donor ordering")
    return moves, rows


def assemble(prior, moves, rows, initial, final):
    first, frames = prior["first_output"], prior["frames"]
    spans = [span(tuple(frame)) for frame in frames]

    def chart(i):
        need(type(i) is int and 0 <= i < len(spans), f"invalid chart {i!r}")
        return spans[i]

    available = {~i: a for i, a in enumerate(initial)}
    sources = {first + i: b for i, b in enumerate(final)}
    need(len(initial) == len(final) and len(initial) < first, "owner layout")
    for tag in (*initial, *final):
        chart(tag)
    for key, (a, b) in moves.items():
        need(type(key) is int and 0 <= key < first, f"paid key {key!r}")
        u, v = chart(a), chart(b)
        need(u < v or v < u, f"strict paid nesting {key}")
        available[key], sources[key] = b, a
    need(rows.keys() == sources.keys(), "complete bank and terminal row inventory")
    for key, row in rows.items():
        for d, q in row.items():
            need(type(d) is int and available.get(d) == sources[key], f"nonlocal row {key}, donor {d}")
            coefficient(q)
    ordered_rows = {k: [[d, q] for d, q in sorted(rows[k].items())] for k in sorted(rows)}
    schedule = list(TopologicalSorter({k: [d for d, _ in row if d >= 0]
                                     for k, row in ordered_rows.items()}).static_order())
    return dict(first_output=first, frames=frames, initial=initial, final=final,
                moves=[[k, *moves[k]] for k in sorted(moves)], forms=list(map(list, ordered_rows.items())),
                schedule=schedule)


def graph_validation(graph):
    need(graph.keys() == FIELDS, "graph schema")
    moves, rows = inventory(graph)
    need(graph == assemble(graph, moves, rows, graph["initial"], graph["final"]), "noncanonical native schedule")


def ordered(entries):
    keys = [row[0] for row in entries]
    need(keys == sorted(set(keys)), "change keys must be ordered and unique")


def to_direction(before, after, reverse):
    return (after, before) if reverse else (before, after)


def changed_values(values, edits, reverse, label):
    ordered(edits)
    for key, before, after in edits:
        old, new = to_direction(before, after, reverse)
        need(old != new and values.get(key) == old, f"{label} preimage {key}")
        if new is None:
            del values[key]
        else:
            values[key] = new


def changed_boundary(values, edits, size, reverse, label):
    starting, ending = to_direction(*size, reverse)
    need(len(values) == starting, f"{label} count preimage")
    result = dict(enumerate(values))
    changed_values(result, edits, reverse, label)
    need(set(result) == set(range(ending)), f"{label} owner inventory")
    return [result[i] for i in range(ending)]


def change_graph(graph, stage, reverse=False):
    moves, rows = inventory(graph)
    changed_values(moves, stage["moves"], reverse, "move")
    ordered(stage["forms"])
    for key, before, after, edits in stage["forms"]:
        old, new = to_direction(before, after, reverse)
        need((key in rows) == old and type(old) is bool and type(new) is bool, f"form presence {key}")
        row = rows.get(key, {}).copy()
        changed_values(row, edits, reverse, f"coefficient in row {key}")
        if new:
            rows[key] = row
        else:
            need(not row, f"removed form still has coefficients {key}")
            del rows[key]
    changes = stage["boundaries"]
    initial, final = (changed_boundary(graph[k], changes[k]["edits"], changes[k]["lengths"], reverse, k)
                      for k in ("initial", "final"))
    return assemble(graph, moves, rows, initial, final)


def rename_banks(graph, entries, reverse=False):
    moves, rows = inventory(graph)
    keys = {}
    for old, new, pair in entries:
        source, target = to_direction(old, new, reverse)
        need(source not in keys and moves.get(source) == pair, f"rename source preimage {source}")
        need(target not in moves and target not in rows and target not in keys.values(), f"rename target occupancy {target}")
        keys[source] = target
    moved = {keys.get(k, k): v for k, v in moves.items()}
    renamed = {keys.get(k, k): {keys.get(d, d): q for d, q in row.items()} for k, row in rows.items()}
    return assemble(graph, moved, renamed, graph["initial"], graph["final"])


def apply(graph, patch, reverse=False):
    graph_validation(graph)
    need(patch["schema"] == SCHEMA and patch["input_graph_sha256"] == BASE and
         patch["output_graph_sha256"] == JOINT, "root patch pins")
    source, target = to_direction(BASE, JOINT, reverse)
    need(digest(graph) == source, "serialized #7767/joint word input")
    stages = reversed(patch["stages"]) if reverse else patch["stages"]
    for stage in stages:
        before, after = to_direction(stage["input_sha256"], stage["output_sha256"], reverse)
        need(digest(graph) == before, f"{stage['label']} stage input")
        if stage["kind"] == "paid_bank_names":
            graph = rename_banks(graph, stage["renames"], reverse)
        else:
            need(stage["kind"] == "graph_diff", f"unknown patch kind {stage['kind']}")
            graph = change_graph(graph, stage, reverse)
        need(digest(graph) == after, f"{stage['label']} stage output")
    need(digest(graph) == target, "final patch output")
    return graph


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=HERE / "PR7767-NATIVE.json.gz")
    parser.add_argument("--patch", type=Path, default=HERE / "PR7767-TO-JOINT.json.gz")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expect", type=Path, help="compare decompressed canonical output byte for byte")
    parser.add_argument("--reverse", action="store_true")
    args = parser.parse_args()
    need(args.output.resolve() not in {args.source.resolve(), args.patch.resolve()} and
         (args.expect is None or args.output.resolve() != args.expect.resolve()), "keep frozen inputs")
    source = load_graph(args.source)
    patch = read(args.patch)
    rebuilt = apply(source, patch, reverse=args.reverse)
    restored = apply(rebuilt, patch, reverse=not args.reverse)
    need(encoded(restored) == read_bytes(args.source), "reversible byte comparison")
    output = encoded(rebuilt)
    if args.expect is not None:
        need(output == read_bytes(args.expect), "expected native word byte comparison")
    write(args.output, output)
    print(json.dumps(dict(input_graph_sha256=digest(source), output_graph_sha256=sha256(output).hexdigest(),
                          inverse_byte_match=True, expected_byte_match=args.expect is not None,
                          paid_moves=len(rebuilt["moves"]), independent_owners=len(rebuilt["initial"])),
                     sort_keys=True))


if __name__ == "__main__":
    main()
