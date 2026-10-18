#!/usr/bin/env python3
"""Finite R439 mini-node synthesis. Ryan Haines; substantial Codex assistance.

Apache-2.0. The verifier does not import this generator.
"""
import argparse
import gzip
import hashlib
import json
import random
from collections import deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
WORD_SHA256 = "e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f"
BASE = "66849e1475c930fd7732b1a0067ffee7e1e95f60"
SEED = 17


def require(condition, message):
    if not condition:
        raise ValueError(message)


def exposures(columns):
    return sum(1 << col for col in columns)


def graph(k):
    """Backward suffix C; prepending d += s adds column d to column s."""
    identity = tuple(1 << i for i in range(k))
    start = (identity, exposures(identity))
    distances, parents = {start: 0}, {start: None}
    queue = deque([start])
    edges = [(d, s) for d in range(k) for s in range(k) if d != s]
    random.Random(SEED).shuffle(edges)
    while queue:
        state = queue.popleft()
        cols, seen = state
        for d, s in edges:
            changed = list(cols)
            changed[s] ^= changed[d]
            changed = tuple(changed)
            after = changed, seen | exposures(changed)
            if after not in distances:
                distances[after] = distances[state] + 1
                parents[after] = (state, (d, s))
                queue.append(after)
    return start, distances, parents


def representations(mask, k):
    """Shortest XOR sum of available nonzero output column patterns."""
    paths, queue = {0: ()}, deque([0])
    available = [p for p in range(1, 1 << k) if mask >> p & 1]
    while queue:
        value = queue.popleft()
        for pattern in available:
            nxt = value ^ pattern
            if nxt not in paths:
                paths[nxt] = paths[value] + (pattern,)
                queue.append(nxt)
    require(len(paths) == 1 << k, "exposure patterns fail to span")
    return paths


def node(word, frame, data):
    indices = [i for i, gate in enumerate(word["A"]) if gate[0] == frame]
    require(indices == list(range(indices[0], indices[-1] + 1)), "noncontiguous node")
    old = [word["A"][i] for i in indices]
    destinations = [d for _, d, _ in old]
    require(len(set(destinations)) == len(destinations), "repeated destination")
    external = sorted({s for _, _, ss in old for s in ss} - set(destinations))
    wires = destinations + external
    rows = {r: 1 << i for i, r in enumerate(wires)}
    for _, d, ss in old:
        for s in ss:
            rows[d] ^= rows[s]
    k = len(destinations)
    output_columns = tuple(sum(((rows[d] >> j) & 1) << i
                               for i, d in enumerate(destinations)) for j in range(k))
    patterns = [sum(((rows[d] >> (k + j)) & 1) << i
                    for i, d in enumerate(destinations)) for j in range(len(external))]
    start, distances, parents = data
    candidates = []
    for state, length in distances.items():
        cols, mask = state
        if cols == output_columns:
            reps = representations(mask, k)
            candidates.append((length + sum(len(reps[p]) for p in patterns), length, mask))
    total, length, mask = min(candidates)
    final = output_columns, mask
    states, gates = [final], []
    while states[-1] != start:
        before, gate = parents[states[-1]]
        states.append(before)
        gates.append(gate)
    states.reverse()
    gates.reverse()
    injections = [[] for _ in states]
    for j, pattern in enumerate(patterns):
        for part in representations(mask, k)[pattern]:
            at = next(i for i, (cols, _) in enumerate(states) if part in cols)
            d = states[at][0].index(part)
            injections[at].append((destinations[d], external[j]))
    backward = []
    for i, reads in enumerate(injections):
        backward.extend(reads)
        if i < len(gates):
            d, s = gates[i]
            backward.append((destinations[d], destinations[s]))
    circuit = [[frame, d, [s]] for d, s in reversed(backward)]
    require(len(circuit) == total, "circuit cost differs from search")
    return {
        "frame": frame, "original_a_indices": indices,
        "destinations": destinations, "external": external,
        "linear_columns": list(output_columns), "input_patterns": patterns,
        "original_xors": sum(len(ss) for _, _, ss in old),
        "minimum_xors": total, "destination_xors": length,
        "terminal_exposure_mask": mask,
        "terminal_costs": [list(row) for row in sorted(candidates)],
        "replacement": circuit,
    }


def generate():
    raw = (ROOT / WORD).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == WORD_SHA256, "source word hash mismatch")
    word = json.loads(gzip.decompress(raw))
    groups = {k: graph(k) for k in (2, 3)}
    nodes = []
    for frame in (507, 508, 509, 506):  # rotation by seed 17 modulo four
        k = sum(g[0] == frame for g in word["A"])
        nodes.append(node(word, frame, groups[k]))
    paths = [WORD, "research/e8-bit-p111-tuned/code/xcheck_p.py",
             "research/e8-bit-carrier-skeleton/code/bit/export_records.py",
             "research/e8-bit-carrier-skeleton/code/bit/regression/stage_cohort.py",
             "research/e8-bit-carrier-skeleton/code/bit/checkers/columns_h.cpp",
             "research/e8-bit-carrier-skeleton/code/bit/checkers/columns_k.cpp",
             "research/e8-bit-carrier-skeleton/code/bit/checkers/legality_h.cpp",
             "research/e8-bit-carrier-skeleton/code/bit/checkers/json.hpp"]
    return {
        "schema": "p111-interleaved-mini-nodes/1",
        "status": "finite bit circuit construction; no new kappa",
        "base_commit": BASE, "assignment_seed": SEED,
        "supplier_pr": 589,
        "supplier_head": "a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46",
        "comparison_pr": 728,
        "comparison_head": "d454ae19fdd474b4dfa7bd2c28bbe5b0996365fb",
        "comparison_minima": {"506": 14, "507": 11, "508": 11, "509": 9},
        "source_sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths},
        "search_class": "All destination transvections and read-only external injections, "
                        "in arbitrary order and number; same wires, same single frame, no extra work.",
        "stopping_rule": "Exhaust both reachable finite state graphs, without a depth or time truncation.",
        "graphs": {str(k): [[list(cols), mask, distance]
                            for (cols, mask), distance in sorted(groups[k][1].items())]
                   for k in (2, 3)},
        "nodes": sorted(nodes, key=lambda record: record["frame"]),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    output = parser.add_mutually_exclusive_group(required=True)
    output.add_argument("--write", type=Path, help="new certificate path; never overwritten")
    output.add_argument("--check", action="store_true", help="recompute the committed certificate")
    args = parser.parse_args()
    result = generate()
    if args.check:
        require(result == json.loads((HERE / "CERTIFICATE.json").read_text(encoding="utf-8")),
                "regenerated certificate differs")
    else:
        with args.write.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
    print("PASS_P111_INTERLEAVED_SEARCH states=7+859 minima=13,9,9,8")


if __name__ == "__main__":
    main()
