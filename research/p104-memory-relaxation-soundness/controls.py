#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exhaust a small geometric domain and exercise the stated support contract."""

import json
from collections import deque
from itertools import product
from pathlib import Path

from memory import (
    ZERO,
    Model,
    bitmap,
    insert,
    layer_relations,
    propagate,
    require,
    span,
)
from verify import archived, authenticate

HERE = Path(__file__).resolve().parent


def small_geometry():
    lines = [span([v]) for v in range(1, 8)]
    planes = sorted(
        {span([v, w]) for v in range(1, 8) for w in range(v + 1, 8)}, key=bitmap
    )
    flags = [
        (ZERO, line, plane, frozenset(range(8)))
        for line in lines
        for plane in planes
        if line <= plane
    ]
    require(
        (len(lines), len(planes), len(flags)) == (7, 7, 21), "complete small geometry"
    )
    return tuple(lines + planes), flags


def partial_model(flags, reveal, snapshots):
    bounds = []
    for dimension in (1, 2):
        layer = []
        for helper, flag in enumerate(flags):
            known = [0, 3] + [d for d in (1, 2) if reveal >> (2 * helper + d - 1) & 1]
            low = max(d for d in known if d <= dimension)
            high = min(d for d in known if d >= dimension)
            layer.append((flag[low], flag[high]))
        bounds.append(tuple(layer))
    paths = tuple((frame,) for frame in snapshots)
    return Model(tuple(bounds), paths, paths)


def literal_graph(flags, snapshots):
    """BFS on actual equal frames; no interval or memory routine is called."""
    nodes = [(helper, d) for helper in range(len(flags)) for d in (1, 2)]
    adjacency = {node: set() for node in nodes}
    for helper, dimension in nodes:
        if dimension == 1:
            adjacency[helper, 1].add((helper, 2))
        for peer in range(len(flags)):
            if flags[helper][dimension] == flags[peer][dimension]:
                adjacency[helper, dimension].add((peer, dimension))
    outputs = [1 << t for t in range(len(snapshots))]  # direct equal-frame X/Y
    for source, frame in enumerate(snapshots):
        reached = {node for node in nodes if flags[node[0]][node[1]] == frame}
        queue = deque(reached)
        for _ in range(len(nodes)):
            if not queue:
                break
            node = queue.popleft()
            for neighbor in adjacency[node] - reached:
                reached.add(neighbor)
                queue.append(neighbor)
        require(not queue, "bounded BFS completed")
        for target, target_frame in enumerate(snapshots):
            if any(flags[h][d] == target_frame for h, d in reached):
                outputs[target] |= 1 << source
    return outputs


def historical_toy(namespace, model, full):
    """Run the unchanged core except for its output-break repair."""

    def intervals(_frames, _edges, dimension):
        return [
            (bitmap(low), bitmap(high)) for low, high in model.bounds[dimension - 1]
        ]

    namespace["intervals"] = intervals
    layers = []
    for dimension in range(1, len(model.bounds) + 1):
        adjacency, reads, writes = layer_relations(model, dimension)
        layers.append(
            (
                [sum(1 << h for h in row) for row in adjacency],
                [sum(1 << s for s in row) for row in reads],
                [sum(1 << t for t in row) for row in writes],
            )
        )
    paths = {f"{kind}{i}": [] for kind in "XY" for i in range(104)}
    for kind, chains in (("X", model.sources), ("Y", model.targets)):
        paths.update(
            {f"{kind}{i}": [bitmap(f) for f in chain] for i, chain in enumerate(chains)}
        )
    direct = [
        sum(
            1 << s for s, chain in enumerate(model.sources) if set(chain) & set(targets)
        )
        for targets in model.targets
    ]
    output = namespace["propagate_with_subspace_memory_bitmap"](
        (),
        [(h, h) for h in range(len(model.bounds[0]))],
        layers,
        paths,
        direct + [0] * (104 - len(direct)),
        full_memory=full,
    )
    return output[: len(model.targets)]


def exhaustive():
    snapshots, flags = small_geometry()
    old = archived(True)
    fixtures = 0
    for pair in product(flags, repeat=2):
        exact = literal_graph(pair, snapshots)
        for reveal in range(16):
            model = partial_model(pair, reveal, snapshots)
            for full in (False, True):
                output, _peak = propagate(model, full)
                require(
                    all(
                        actual & allowed == actual
                        for actual, allowed in zip(exact, output, strict=True)
                    ),
                    "every literal path survives the relaxation",
                )
                require(
                    output == historical_toy(old, model, full),
                    "archived core correspondence",
                )
                if reveal == 15:
                    require(
                        output == exact,
                        "fully fixed frames are exact for untimed paths",
                    )
            fixtures += 1
    require(fixtures == 7056, "complete pair/revelation domain")
    return {
        "flags": 21,
        "flag_pairs": 441,
        "revelations_per_pair": 16,
        "fixtures": fixtures,
        "memory_modes": 2,
        "source_target_pairs": 196,
    }


def immediate_and_history():
    line, plane = span([1]), span([1, 2])
    other_plane = span([2, 4])
    # Acquire at helper 0, relay, then write at helper 1. Direct read at the
    # receiver is mandatory in a snapshot-complete equal-frame relaxation.
    same = Model((((line, line), (line, line)),), ((line,),), ((line,),))
    relations = layer_relations(same, 1)
    require(relations[1] == [[0], [0]], "fresh-read saturation at receiver")
    for full in (False, True):
        require(propagate(same, full)[0] == [1], "immediate read-relay support")
    # A signal acquired at line <1> cannot fit inside plane <2,4>. Forgetting
    # the acquisition frame creates a false positive, which one-step allows.
    history = Model(
        (((ZERO, frozenset(range(8))),), ((ZERO, frozenset(range(8))),)),
        ((line,),),
        ((other_plane,),),
    )
    require(propagate(history, True)[0] == [0], "full memory preserves frame history")
    require(
        propagate(history, False)[0] == [1], "one-step relaxation can forget history"
    )
    positive = Model(history.bounds, history.sources, ((plane,),))
    require(propagate(positive, True)[0] == [1], "nested positive history")
    return {
        "immediate": "receiver can read directly",
        "incompatible_full": [0],
        "incompatible_one_step": [1],
        "nested_full": [1],
    }


def multi_source_and_antichain():
    line = span([1])
    plane = span([1, 2])
    model = Model((((line, line),), ((plane, plane),)), ((line,), (line,)), ((plane,),))
    legacy, repaired = archived(False), archived(True)
    for full in (False, True):
        require(propagate(model, full)[0] == [3], "all independent sources retained")
        require(
            historical_toy(legacy, model, full) == [1], "legacy loses second source"
        )
        require(
            historical_toy(repaired, model, full) == [3], "repair retains both sources"
        )
    rows = [[int(i == j) for j in range(4)] for i in range(4)]
    for target, source, sign in (
        (3, 2, -1),
        (2, 0, 1),
        (2, 1, 1),
        (3, 2, 1),
        (2, 1, -1),
        (2, 0, -1),
    ):
        rows[target] = [
            a + sign * b for a, b in zip(rows[target], rows[source], strict=True)
        ]
    require(
        rows == [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [1, 1, 0, 1]],
        "six-ADD dirty-helper restoration identity",
    )
    memories = [span([1, 2]), span([2, 4])]
    insert(memories, span([1]))
    require(
        set(memories) == {span([1]), span([2, 4])}, "remove only dominated memories"
    )
    insert(memories, span([1, 4]))
    require(set(memories) == {span([1]), span([2, 4])}, "retain subset representative")
    return {"all_source_output": [3], "restored_shear": rows, "antichain": "passed"}


def main():
    authenticate()
    value = {
        "small_domain": exhaustive(),
        "frame_controls": immediate_and_history(),
        "source_and_pruning_controls": multi_source_and_antichain(),
    }
    expected = json.loads((HERE / "CONTROLS.json").read_text())
    require(
        json.dumps(value, sort_keys=True) == json.dumps(expected, sort_keys=True),
        "typed control receipt mismatch",
    )
    print(
        "PASS_P104_MEMORY_CONTROLS fixtures=7056 modes=2 pairs_per_fixture=196 errors=0"
    )


if __name__ == "__main__":
    main()
