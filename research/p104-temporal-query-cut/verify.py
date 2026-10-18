#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact temporal communication cut; no producer/compiler imports.

A frame class at a cut is a complete directed communication graph. Saturating
that class therefore permits any number of extra common-chart linear gates,
not merely the scalar edges in the source witness. The two scans independently
follow the two directions of time. Native child rank is NOT wire capacity.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
FIXTURE = "research/p104-native-channel/inputs/P104-FIXTURE.json"
CUT = 2429  # Before zero-based event 2429, the first D-helper transport.
QUERIES = frozenset("Q" + str(i) for i in range(8))
PROFILE = {1: 1074, 2: 58, 3: 86, 4: 104, 5: 48, 6: 24, 7: 8, 8: 8}


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def span(vectors):
    """Literal XOR closure, independent of basis ordering or elimination."""
    covered = {0}
    for vector in vectors:
        need(type(vector) is int and 0 < vector < 512, "frame coordinate")
        need(vector not in covered, "dependent frame basis")
        covered.update(x ^ vector for x in tuple(covered))
    return tuple(sorted(covered))


def classes(frames):
    groups = defaultdict(list)
    for name, frame in frames.items():
        groups[frame].append(name)
    return groups.values()


def close(active, frames):
    """One closure suffices: equality classes are disjoint complete graphs."""
    for group in classes(frames):
        if active.intersection(group):
            active.update(group)


def family_counts(names):
    return dict(sorted(Counter(name.rstrip("0123456789") for name in names).items()))


def load_sources():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    inputs = {}
    for pin in manifest["files"]:
        if pin["usage"] == "input":
            raw = (ROOT / pin["path"]).read_bytes()
            need(sha256(raw).hexdigest() == pin["sha256"], "source pin: " + pin["path"])
            inputs[pin["path"]] = raw
    return json.loads(inputs[SOURCE]), json.loads(inputs[FIXTURE])["section4_explicit_P104"]


def geometry(fixture):
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.add(tuple(row))
    for signs in product((-1, 1), repeat=7):
        if signs.count(-1) % 2 == 0:
            roots.add((1, *signs))
    removed = {tuple(row) for row in fixture["F0"] + fixture["C"]}
    need(len(roots) == 120 and len(removed) == 16 and removed <= roots, "P104 root fixture")
    ports = sorted(roots - removed)
    need(len(ports) == 104, "104 live roots")
    # These are doubled real coordinates, so RR^t has a denominator of four.
    gram = [[Q(sum(a * b for a, b in zip(x, y)), 4) for y in ports] for x in ports]
    coordinate_gram = [[Q(sum(row[i] * row[j] for row in ports), 4)
                        for j in range(8)] for i in range(8)]
    need(coordinate_gram == [[Q(26 * (i == j)) for j in range(8)] for i in range(8)],
         "P104 tight-frame identity R^t R = 26 I")
    return ports, gram


def rank(matrix):
    rows = [[Q(value) for value in row] for row in matrix]
    pivot = 0
    for column in range(len(rows[0]) if rows else 0):
        found = next((i for i in range(pivot, len(rows)) if rows[i][column]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        value = rows[pivot][column]
        rows[pivot] = [entry / value for entry in rows[pivot]]
        for i in range(pivot + 1, len(rows)):
            if rows[i][column]:
                value = rows[i][column]
                rows[i] = [a - value * b for a, b in zip(rows[i], rows[pivot])]
        pivot += 1
        if pivot == len(rows):
            break
    return pivot


def determinant(matrix):
    rows = [[Q(value) for value in row] for row in matrix]
    answer = Q(1)
    for column in range(len(rows)):
        found = next((i for i in range(column, len(rows)) if rows[i][column]), None)
        if found is None:
            return Q(0)
        if found != column:
            rows[column], rows[found] = rows[found], rows[column]
            answer = -answer
        value = rows[column][column]
        answer *= value
        for i in range(column + 1, len(rows)):
            multiplier = rows[i][column] / value
            for j in range(column + 1, len(rows)):
                rows[i][j] -= multiplier * rows[column][j]
    return answer


def skeleton(word):
    """Validate every wire/lifetime and all recorded common-frame operations."""
    frames = {name: span(frame) for name, frame in word["initial_frames"].items()}
    need(family_counts(frames) == {"D": 32, "G": 32, "Q": 8, "X": 104, "Y": 104}, "initial inventory")
    paid, operations = Counter(), Counter()
    all_frames = set(frames.values())
    cut_frames = None
    for i, event in enumerate(word["program"]):
        if i == CUT:
            cut_frames = dict(frames)
        op = event[0]
        operations[op] += 1
        if op == "transport":
            _, name, old, new, child = event
            a, b = span(old), span(new)
            need(frames[name] == a, "transport old frame")
            need(set(a) <= set(b) or set(b) <= set(a), "nested transport")
            need(child == abs(len(old) - len(new)) > 0, "child rank")
            paid[child] += 1
            frames[name] = b
            all_frames.add(b)
        elif op == "zero":
            _, name, frame = event
            need(name == "C" and name not in frames, "private creation")
            frames[name] = span(frame)
        elif op == "erase":
            _, name, frame = event
            need(name == "C" and frames[name] == span(frame), "private erasure")
            del frames[name]
        elif op in ("copy", "add"):
            name, source = event[1:3]
            need(name != source and frames[name] == frames[source] == span(event[-1]), "common-frame event")
            if op == "add":
                Q(event[3])
        else:
            raise ValueError("unknown event")
    need(frames == {name: span(frame) for name, frame in word["final_frames"].items()}, "final frames")
    need(dict(paid) == PROFILE, "complete native boundary profile")
    need(len(word["program"]) == 4058 and operations == Counter(add=2624, transport=1410, zero=8, copy=8, erase=8), "complete event inventory")
    need(word["program"][CUT][:2] == ["transport", "D0"], "separator anchor")
    return cut_frames, len(all_frames)


def forward(word, cut_queries=None, extra_edge=None):
    """Reachability from all X inputs; optionally delete query wire crossings."""
    frames = {name: span(frame) for name, frame in word["initial_frames"].items()}
    active = {name for name in frames if name.startswith("X")}
    digest = sha256()
    at_cut = None
    edge_count = 0
    for i in range(len(word["program"]) + 1):
        # The cut is between the preceding event and this cut's free mixing.
        if i == CUT:
            at_cut = set(active)
            if cut_queries is not None:
                active.difference_update(cut_queries)
            if extra_edge is not None and extra_edge[0] in active:
                active.add(extra_edge[1])
        close(active, frames)
        edge_count += sum(len(group) * (len(group) - 1) for group in classes(frames))
        digest.update(canonical([i, sorted(active)]))
        if i == len(word["program"]):
            break
        event = word["program"][i]
        op = event[0]
        if op == "transport":
            frames[event[1]] = span(event[3])
        elif op == "zero":
            frames[event[1]] = span(event[2])
            active.discard(event[1])
        elif op == "erase":
            del frames[event[1]]
            active.discard(event[1])
        elif op == "copy" and event[2] in active:
            active.add(event[1])
        # Recorded ADD is subsumed by closure. Retaining the old COPY destination
        # is a deliberate relaxation of its zero/overwrite contract, never a loss
        # of a potential dependency.
    return at_cut, active, digest.hexdigest(), edge_count


def backward(word):
    """Reverse-time dependency cone of all final Y outputs, not an inverse word."""
    frames = {name: span(frame) for name, frame in word["final_frames"].items()}
    needed = {name for name in frames if name.startswith("Y")}
    digest = sha256()
    at_cut = None
    for i in range(len(word["program"]), -1, -1):
        close(needed, frames)
        digest.update(canonical([i, sorted(needed)]))
        if i == CUT:
            at_cut = set(needed)
        if i == 0:
            break
        event = word["program"][i - 1]
        op = event[0]
        if op == "transport":
            frames[event[1]] = span(event[2])
        elif op == "erase":
            frames[event[1]] = span(event[2])
            needed.discard(event[1])
        elif op == "zero":
            del frames[event[1]]
            needed.discard(event[1])
        elif op == "copy" and event[1] in needed:
            needed.add(event[2])
    return at_cut, needed, digest.hexdigest()


def scalar_replay(word, gram, fault=None):
    """Independent exact logical induction, including every arbitrary dirty input."""
    state = {name: {name: Q(1)} for name in word["initial_frames"]}
    query_rows = None
    for i, event in enumerate(word["program"]):
        if i == CUT:
            query_rows = [[state[name].get("X" + str(j), Q(0)) for j in range(104)]
                          for name in sorted(QUERIES)]
        op = event[0]
        if op == "zero":
            state[event[1]] = {}
        elif op == "erase":
            del state[event[1]]
        elif op == "copy":
            need(not state[event[1]], "copy destination zero")
            state[event[1]] = dict(state[event[2]])
        elif op == "add":
            name, source = event[1:3]
            coefficient = Q(event[3])
            if fault == "dirty_compensation" and i == 0:
                coefficient = 0
            if fault == "query_cleanup" and i == len(word["program"]) - 1:
                coefficient = 0
            for key, value in list(state[source].items()):
                result = state[name].get(key, Q(0)) + coefficient * value
                if result:
                    state[name][key] = result
                else:
                    state[name].pop(key, None)
    need(set(state) == set(word["initial_frames"]), "all private lifetimes closed")
    for name, row in state.items():
        expected = {name: Q(1)}
        if name.startswith("Y"):
            expected.update({"X" + str(j): value / 2 for j, value in enumerate(gram[int(name[1:])]) if value})
        need(row == expected, "all-column endpoint: " + name)
    need(rank(query_rows) == 8, "eight independent gathered source directions")
    return query_rows


def expect_failure(function, reason):
    try:
        function()
    except ValueError:
        return reason
    raise ValueError("accepted negative control: " + reason)


def result():
    word, fixture = load_sources()
    cut_frames, frame_count = skeleton(word)
    ports, gram = geometry(fixture)
    source_at_cut, final_cone, forward_digest, edge_count = forward(word)
    target_at_cut, initial_cone, backward_digest = backward(word)
    separator = source_at_cut & target_at_cut
    need(separator == QUERIES, "exact temporal intersection is all eight queries")
    _, cut_final, cut_digest, _ = forward(word, QUERIES)
    need(not any(name.startswith("Y") for name in cut_final), "query cut disconnects every target")
    need(all("Y" + str(i) in final_cone for i in range(104)), "uncut graph reaches every target")
    need(all("X" + str(i) in initial_cone for i in range(104)), "backward graph reaches every source")
    query_rows = scalar_replay(word, gram)
    pivots = []
    for i, row in enumerate(ports):
        if rank([ports[j] for j in pivots] + [row]) > len(pivots):
            pivots.append(i)
    need(len(pivots) == 8, "root coordinate rank")
    minor = determinant([[gram[i][j] / 2 for j in pivots] for i in pivots])
    need(minor != 0, "rank-eight attaining Gram minor")
    # R^t R=26I implies G^2=26G, hence (I-G/2)^-1=I-G/24.
    # Check every entry as well: this is not a numerical eigenvalue claim.
    for i in range(104):
        for j in range(104):
            square = sum(gram[i][k] * gram[k][j] for k in range(104))
            need(square == 26 * gram[i][j], "G squared tight-frame identity")
            need(-Q(13, 24) * gram[i][j] + square / 48 == 0, "residual exact inverse")
    controls = []
    for name in sorted(QUERIES):
        _, leak, _, _ = forward(word, QUERIES - {name})
        need(any(target.startswith("Y") for target in leak), "each omitted query must reopen a path")
        controls.append("omit_" + name + "_from_separator")
    # A deliberately prohibited cross-frame bypass tests the causal conclusion,
    # not source hashes. Reopening even one source->target edge defeats the cut.
    need(cut_frames["X0"] != cut_frames["Y0"], "bypass is genuinely cross-frame")
    _, leak, _, _ = forward(word, QUERIES, ("X0", "Y0"))
    need("Y0" in leak, "cross-frame bypass must reopen a target path")
    controls.append("cross_frame_bypass_reopens_cut")
    controls.append(expect_failure(lambda: scalar_replay(word, gram, "dirty_compensation"), "missing_dirty_compensation"))
    controls.append(expect_failure(lambda: scalar_replay(word, gram, "query_cleanup"), "missing_query_cleanup"))
    # Same dimension is not same frame: all eight cut query hyperplanes differ.
    need(len({cut_frames[name] for name in QUERIES}) == 8 and
         all(len(cut_frames[name]) == 256 for name in QUERIES), "distinct rank-eight query frames")
    for name in QUERIES:
        need(span(list(reversed(word["program"][next(i for i, e in enumerate(word["program"])
             if e[0] == "transport" and e[1] == name)][3]))) == cut_frames[name], "basis-independent frame equality")
    controls.append("reversed_basis_preserves_query_frames")
    return {
        "status": "PASS_P104_TEMPORAL_QUERY_CUT",
        "events": 4058,
        "cuts_saturated": 4059,
        "distinct_frame_subspaces": frame_count,
        "allowed_directed_common_frame_edges_over_all_cuts": edge_count,
        "separator_cut": CUT,
        "cut_convention": "after events0..2428; before event2429 and its following free mixing",
        "separator": sorted(separator),
        "source_reachable_at_cut": family_counts(source_at_cut),
        "target_coreachable_at_cut": family_counts(target_at_cut),
        "query_frame_bases": {name: next(e[3] for e in word["program"] if e[0] == "transport" and e[1] == name) for name in sorted(QUERIES)},
        "after_cut_deletion_final_reachable": family_counts(cut_final),
        "forward_trace_sha256": forward_digest,
        "backward_trace_sha256": backward_digest,
        "cut_trace_sha256": cut_digest,
        "source_target_rank_capacity_in_arrays": 8,
        "identity_rank_in_arrays": 104,
        "missing_source_directions_in_arrays": 96,
        "rank_eight_minor_ports": pivots,
        "rank_eight_channel_minor_determinant": str(minor),
        "query_source_matrix_sha256": sha256(canonical([[str(x) for x in row] for row in query_rows])).hexdigest(),
        "gram_relation": "G^2=26G",
        "residual_inverse": "(I-G/2)^-1=I-G/24",
        "residual_rank": 104,
        "all_logical_input_columns": 280,
        "restored_arbitrary_dirty_helpers": 72,
        "local_paid_profile": {str(k): v for k, v in PROFILE.items()},
        "local_paid_rank_mass": sum(k * v for k, v in PROFILE.items()),
        "controls": controls,
        "scope": "Sharp frozen chronological common-chart linear communication capacity, not a native paid-rank lower bound for changed itineraries, a supplier or a kappa claim."
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="emit regenerated mathematical payload without comparing RESULT.json")
    args = parser.parse_args()
    receipt = result()
    if not args.emit:
        expected = json.loads((HERE / "RESULT.json").read_text())
        need(canonical(receipt) == canonical(expected), "canonical regenerated result")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
