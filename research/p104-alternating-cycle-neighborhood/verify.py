#!/usr/bin/env python3
"""Exact local search over short alternating cycles of the PR3013 matching."""

import json
import hashlib
import runpy
from collections import Counter
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SCREEN = ROOT / "research/p104-rematched-dependency-screen"
FLAG_CHECKER = ROOT / "research/p104-fixed-matching-flag-consistency/verify.py"
WITNESS = PACKAGE / "WITNESS.json"
EXPECTED = PACKAGE / "RESULT.json"


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def authenticated_local_json(path):
    records = json.loads((PACKAGE / "SOURCES.json").read_text())["files"]
    pins = {row["path"]: row["sha256"] for row in records if row["usage"] == "input"}
    raw = (ROOT / path).read_bytes()
    require(
        hashlib.sha256(raw).hexdigest() == pins[path],
        "source input SHA256: " + path,
    )
    return json.loads(raw)


def load():
    api = runpy.run_path(str(SCREEN / "verify.py"))
    certificate, word, fixture = api["inputs"]()
    paths = api["data_paths"](word)
    frames = api["cover_frames"](certificate, paths)
    graph = frames[-1]
    pairing = authenticated_local_json(
        "research/p104-rematched-dependency-screen/WITNESS.json"
    )["pairing"]
    api["check_pairing"](pairing, graph)
    matrix = api["correction"](fixture)
    return api, paths, frames, graph, pairing, matrix


def bounds_reads_writes(api, frames, paths, dimension, slot, arrival):
    bound = api["intervals"](frames, [(slot, arrival)], dimension)[0]
    reads = sum(
        1 << source
        for source in range(104)
        if any(api["fits"](bound, dimension, f) for f in paths[f"X{source}"])
    )
    writes = sum(
        1 << target
        for target in range(104)
        if any(api["fits"](bound, dimension, f) for f in paths[f"Y{target}"])
    )
    return bound, reads, writes


def make_cache(api, paths, frames, graph, pairing):
    size = len(pairing)
    baseline_edges = list(enumerate(pairing))
    baseline_bounds = [None]
    base_layers = []
    for dimension in range(1, 9):
        bounds = api["intervals"](frames, baseline_edges, dimension)
        baseline_bounds.append(bounds)
        adjacency = [1 << i for i in range(size)]
        reads = [0] * size
        writes = [0] * size
        for i, bound in enumerate(bounds):
            reads[i] = sum(
                1 << source
                for source in range(104)
                if any(api["fits"](bound, dimension, f) for f in paths[f"X{source}"])
            )
            writes[i] = sum(
                1 << target
                for target in range(104)
                if any(api["fits"](bound, dimension, f) for f in paths[f"Y{target}"])
            )
            for j in range(i):
                if api["contact"](bound, bounds[j], dimension):
                    adjacency[i] |= 1 << j
                    adjacency[j] |= 1 << i
        base_layers.append((adjacency, reads, writes))

    cache = {}
    for slot, arrivals in enumerate(graph):
        for arrival in arrivals:
            for dimension in range(1, 9):
                bound, reads, writes = bounds_reads_writes(
                    api, frames, paths, dimension, slot, arrival
                )
                contacts = sum(
                    1 << other
                    for other, other_bound in enumerate(baseline_bounds[dimension])
                    if api["contact"](bound, other_bound, dimension)
                )
                cache[(dimension, slot, arrival)] = (bound, reads, writes, contacts)
    return baseline_bounds, base_layers, cache


def incremental_report(api, paths, matrix, pairing, changed, base_layers, cache):
    size = len(pairing)
    changed_mask = sum(1 << slot for slot in changed)
    edges = list(enumerate(pairing))
    layers = []
    for dimension, (base_adjacency, base_reads, base_writes) in enumerate(base_layers, 1):
        adjacency = base_adjacency.copy()
        reads = base_reads.copy()
        writes = base_writes.copy()
        for slot in changed:
            for neighbor in api["bits"](base_adjacency[slot], size):
                adjacency[neighbor] &= ~(1 << slot)
            adjacency[slot] = 1 << slot
            _, reads[slot], writes[slot], contacts = cache[
                (dimension, slot, pairing[slot])
            ]
            contacts &= ~changed_mask
            adjacency[slot] |= contacts
            for neighbor in api["bits"](contacts, size):
                adjacency[neighbor] |= 1 << slot
        for offset, left in enumerate(changed):
            left_bound = cache[(dimension, left, pairing[left])][0]
            for right in changed[offset + 1 :]:
                right_bound = cache[(dimension, right, pairing[right])][0]
                if api["contact"](left_bound, right_bound, dimension):
                    adjacency[left] |= 1 << right
                    adjacency[right] |= 1 << left
        layers.append((adjacency, reads, writes))
    return api["report"](edges, layers, paths, matrix)


def cycles_of_length(outgoing, length):
    result = []
    size = len(outgoing)
    for start in range(size):
        path = [start]
        used = {start}

        def visit():
            if len(path) == length:
                if start in outgoing[path[-1]]:
                    result.append(tuple(path))
                return
            for vertex in outgoing[path[-1]]:
                if vertex <= start or vertex in used:
                    continue
                used.add(vertex)
                path.append(vertex)
                visit()
                path.pop()
                used.remove(vertex)

        visit()
    return result


def one_helper_flag_census(api, certificate, word, fixture, pairing):
    paths = api["data_paths"](word)
    frames = api["cover_frames"](certificate, paths)
    api["check_pairing"](pairing, frames[-1])
    edges = list(enumerate(pairing))
    layers = api["interval_layers"](frames, edges, paths)
    matrix = api["correction"](fixture)
    required = [
        sum(1 << source for source in range(104) if matrix[target][source])
        for target in range(104)
    ]
    direct = [
        sum(
            1 << source
            for source in range(104)
            if set(paths[f"X{source}"]) & set(paths[f"Y{target}"])
        )
        for target in range(104)
    ]
    helper = 91
    quotient = api["quotient_spaces"]()
    cosets = api["coset_masks"](
        frames[1][helper], frames[2][edges[helper][1]]
    )
    choices = {
        dimension: api["allowed_frames"](
            frames, edges[helper], dimension, cosets, quotient
        )
        for dimension in range(3, 7)
    }
    plans = [api["layer_plan"](layer) for layer in layers]
    prepared = {
        dimension: [
            api["layer_plan"](
                api["freeze_helper"](
                    layers[dimension - 1],
                    frames,
                    edges,
                    paths,
                    dimension,
                    frame,
                )
            )
            for frame in choices[dimension]
        ]
        for dimension in range(3, 7)
    }
    missing_counts = Counter()
    passing = 0
    total = 0
    first_passing = None
    for indices in api["full_flags"](choices):
        trial = plans.copy()
        for dimension, choice_index in zip(range(3, 7), indices, strict=True):
            trial[dimension - 1] = prepared[dimension][choice_index]
        outputs = api["propagate"](trial, direct)
        missing = sum(
            (required_mask & ~output_mask).bit_count()
            for required_mask, output_mask in zip(required, outputs, strict=True)
        )
        missing_counts[missing] += 1
        if missing == 0 and first_passing is None:
            first_passing = {
                "indices_3_to_6": list(indices),
                "frame_bases_3_to_6": [
                    api["frame_basis"](choices[dimension][index])
                    for dimension, index in zip(range(3, 7), indices, strict=True)
                ],
            }
        passing += missing == 0
        total += 1
    require(total == 9765, "complete helper91 full-flag census")
    return {
        "full_flags": total,
        "passing_flags": passing,
        "minimum_missing": min(missing_counts),
        "missing_histogram": dict(sorted(missing_counts.items())),
        "first_passing_flag": first_passing,
    }


def main():
    api, paths, frames, graph, base, matrix = load()
    inverse = {arrival: slot for slot, arrival in enumerate(base)}
    outgoing = [[inverse[arrival] for arrival in row] for row in graph]
    baseline_bounds, base_layers, cache = make_cache(api, paths, frames, graph, base)

    base_full = api["report"](
        list(enumerate(base)),
        api["interval_layers"](frames, list(enumerate(base)), paths),
        paths,
        matrix,
    )
    base_fast = incremental_report(api, paths, matrix, base, [], base_layers, cache)
    require(base_full == base_fast, "incremental/full baseline controls")
    require(base_full["unreachable_required_pairs"] == 45, "baseline miss control")

    flag_api = runpy.run_path(str(FLAG_CHECKER))
    flag_inputs = flag_api["load_inputs"]()
    require(flag_inputs[:3] == api["inputs"](), "predecessor input agreement")
    published = flag_inputs[3]["pairing"]
    api["check_pairing"](published, graph)
    moved = [i for i, (a, b) in enumerate(zip(base, published, strict=True)) if a != b]
    published_fast = incremental_report(
        api, paths, matrix, published, moved, base_layers, cache
    )
    published_full = api["report"](
        list(enumerate(published)),
        api["interval_layers"](frames, list(enumerate(published)), paths),
        paths,
        matrix,
    )
    require(published_fast == published_full, "incremental/full PR3019 controls")
    require(published_full["unreachable_required_pairs"] == 0, "PR3019 support control")
    require(len(moved) == 4, "PR3019 alternating cycle size")
    counts, histogram, complete = {}, Counter(), []
    for length in (2, 3, 4):
        cycles = cycles_of_length(outgoing, length)
        counts[str(length)] = len(cycles)
        for cycle in cycles:
            candidate = base.copy()
            for index, slot in enumerate(cycle):
                candidate[slot] = base[cycle[(index + 1) % length]]
            changed = list(cycle)
            report = incremental_report(
                api, paths, matrix, candidate, changed, base_layers, cache
            )
            missing = report["unreachable_required_pairs"]
            histogram[str(missing)] += 1
            if missing == 0:
                api["check_pairing"](candidate, graph)
                complete.append({"cycle": list(cycle), "matching": candidate})
        print(
            json.dumps(
                {
                    "length": length,
                    "cycles": len(cycles),
                    "candidates_checked": sum(counts.values()),
                    "complete_found": len(complete),
                },
                sort_keys=True,
            ),
            flush=True,
        )

    detailed = []
    for item in complete:
        candidate = item["matching"]
        full_layers = api["interval_layers"](
            frames, list(enumerate(candidate)), paths
        )
        full = api["report"](
            list(enumerate(candidate)),
            full_layers,
            paths,
            matrix,
        )
        fast = incremental_report(
            api,
            paths,
            matrix,
            candidate,
            [
                slot
                for slot, (old, new) in enumerate(zip(base, candidate, strict=True))
                if old != new
            ],
            base_layers,
            cache,
        )
        require(full == fast, "incremental/full candidate replay")
        moved_slots = [
            slot
            for slot, (old, new) in enumerate(zip(base, candidate, strict=True))
            if old != new
        ]
        exact_flags = one_helper_flag_census(
            flag_api, flag_inputs[0], flag_inputs[1], flag_inputs[2], candidate
        )
        detailed.append(
            {
                "cycle": item["cycle"],
                "moved_slots": moved_slots,
                "full_interval_missing": full["unreachable_required_pairs"],
                "helper91_flag_census": exact_flags,
            }
        )
    witness = json.loads(WITNESS.read_text())
    require(set(witness) == {"schema_version", "cycle", "pairing"}, "witness schema")
    require(witness["schema_version"] == 1, "witness version")
    selected = next(
        (item for item in complete if item["cycle"] == witness["cycle"]), None
    )
    require(selected is not None, "selected candidate occurs in exact census")
    require(selected["matching"] == witness["pairing"], "selected matching witness")
    result = {
        "cycle_counts": counts,
        "total_candidates": sum(counts.values()),
        "baseline_missing": base_full["unreachable_required_pairs"],
        "pr3019_moved_slots": moved,
        "pr3019_missing": published_full["unreachable_required_pairs"],
        "improved_candidates": sum(
            count
            for missing, count in histogram.items()
            if int(missing) < base_full["unreachable_required_pairs"]
        ),
        "complete_candidates": detailed,
        "selected_cycle": witness["cycle"],
        "selected_pairing_sha256": hashlib.sha256(bytes(witness["pairing"])).hexdigest(),
    }
    expected = json.loads(EXPECTED.read_text())
    require(
        json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
        "exact typed receipt",
    )
    selected_flags = next(
        item["helper91_flag_census"]
        for item in detailed
        if item["cycle"] == witness["cycle"]
    )
    require(selected_flags["passing_flags"] > 0, "one-helper positive witness")
    print(
        "PASS_P104_ALTERNATING_CYCLE_NEIGHBORHOOD",
        f"cycles={sum(counts.values())}",
        f"complete={len(complete)}",
        f"helper91_flags={selected_flags['passing_flags']}",
        "no_new_kappa",
    )


if __name__ == "__main__":
    main()
