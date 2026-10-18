#!/usr/bin/env python3
"""Build a minimum-cost rooted-forest realization of the pinned R420 D map.

Public API: ``load_source(path=SOURCE_PATH)`` reads the pinned source;
``construct(word, seed=6, cuts=())`` returns independent candidate/recipe dicts.
Only candidate['D'] differs from the source. ``canonical_payload`` fixes JSON
hashing; ``extract_kernels``, ``minimum_spanning_tree``, and ``xor_metrics``
are pure-value helpers. No artifacts are written by this module.

An edge i--j costs |K_i xor K_j|+2; i--dummy costs |K_i|. Kruskal therefore
minimizes XOR count within this rooted-forest construction, not all circuits.
All new gates run at frame zero before A. The child-before-parent preparation
y_i ^= y_parent, followed by difference injection and reversed preparation,
implements y_i ^= K_i s for arbitrary initial targets and helper contents.
"""

from __future__ import annotations

import copy
import gzip
import hashlib
import json
from pathlib import Path


SOURCE_RELATIVE_PATH = "research/e8-bit-r420/data/bitE8mut-r420.json.gz"
SOURCE_PATH = Path(__file__).resolve().parents[2] / SOURCE_RELATIVE_PATH
BASE_COMMIT = "66849e1475c930fd7732b1a0067ffee7e1e95f60"
SOURCE_FILE_SHA256 = "9721a3819efd68307f66f00d84a952eb28eb7c3ad2ce79653ce295c98a764784"
SOURCE_CANONICAL_SHA256 = "e597e3885c0a8daa262afa5985ee2930443329126aece76d33159d81882bdcc2"
TARGET_COUNT = 120
HELPER_COUNT = 420
DUMMY_VERTEX = TARGET_COUNT
REGISTER_COUNT = 2 * TARGET_COUNT + HELPER_COUNT


def canonical_payload(value: object) -> bytes:
    """Canonical JSON: sorted keys, compact separators, ASCII, no NaN, no LF."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _integer(value: object, lower: int, upper: int) -> bool:
    return type(value) is int and lower <= value < upper


def _validate_gates(gates: object, name: str, frame_count: int) -> None:
    _require(isinstance(gates, list), f"{name}: expected a list of gates")
    for index, gate in enumerate(gates):
        prefix = f"{name}[{index}]"
        _require(isinstance(gate, list) and len(gate) == 3,
                 f"{prefix}: expected [frame, destination, sources]")
        frame, destination, sources = gate
        _require(_integer(frame, 0, frame_count), f"{prefix}: invalid frame")
        _require(_integer(destination, 0, REGISTER_COUNT), f"{prefix}: invalid destination")
        _require(isinstance(sources, list) and bool(sources), f"{prefix}: empty or invalid sources")
        _require(all(_integer(s, 0, REGISTER_COUNT) for s in sources), f"{prefix}: invalid source")
        _require(len(set(sources)) == len(sources), f"{prefix}: duplicate source")
        _require(destination not in sources, f"{prefix}: destination/source alias")


def extract_kernels(word: dict) -> list[frozenset[int]]:
    """Validate source D and return helper-register supports in target order.

    A repeated D destination (including a duplicate whole gate), duplicate
    control, nonhelper control, nonzero frame, or aliased control is rejected.
    This helper checks the R420 shape but does not require the pinned digest.
    """
    _require(isinstance(word, dict), "word must be a dictionary")
    _require(type(word.get("v")) is int and word["v"] == TARGET_COUNT,
             "expected v=120")
    _require(type(word.get("R")) is int and word["R"] == HELPER_COUNT,
             "expected R=420")
    frames = word.get("frames")
    _require(isinstance(frames, list) and bool(frames) and frames[0] == [],
             "frame zero must be the empty frame")
    start = word.get("start")
    _require(isinstance(start, list) and len(start) == REGISTER_COUNT,
             "expected 660 starting frames")
    _require(all(type(f) is int and f == 0 for f in start[TARGET_COUNT:]),
             "all targets and helpers must start at frame zero")
    _validate_gates(word.get("D"), "D", len(frames))
    _require(len(word["D"]) == TARGET_COUNT, "D must contain exactly 120 gates")
    kernels: list[frozenset[int] | None] = [None] * TARGET_COUNT
    for frame, target, sources in word["D"]:
        _require(frame == 0, "D must use only frame zero")
        _require(TARGET_COUNT <= target < 2 * TARGET_COUNT, "D must write only targets")
        vertex = target - TARGET_COUNT
        _require(kernels[vertex] is None, "D has a duplicate target gate")
        _require(all(2 * TARGET_COUNT <= s < REGISTER_COUNT for s in sources),
                 "source D must read only helpers")
        kernels[vertex] = frozenset(sources)
    _require(all(k is not None for k in kernels), "D omits a target")
    return [kernel for kernel in kernels if kernel is not None]


def load_source(path: str | Path = SOURCE_PATH) -> dict:
    """Read a gzip JSON source and require its pinned canonical payload hash."""
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        word = json.load(stream)
    extract_kernels(word)
    _require(hashlib.sha256(canonical_payload(word)).hexdigest() == SOURCE_CANONICAL_SHA256,
             "source does not match the pinned R420 canonical payload")
    return word


def minimum_spanning_tree(kernels: list[frozenset[int]], seed: int = 6) -> list[dict]:
    """Return selected complete-graph edges in deterministic Kruskal order.

    Vertices 0..119 denote target rows; 120 denotes the zero kernel. Equal
    weights use SHA256(ASCII '<seed>:<u>:<v>'), then u,v, so runtime PRNG
    implementation details do not influence the result.
    """
    _require(type(seed) is int, "seed must be an integer")
    _require(len(kernels) == TARGET_COUNT, "expected 120 kernels")
    _require(all(isinstance(k, frozenset) and
                 all(_integer(s, 2 * TARGET_COUNT, REGISTER_COUNT) for s in k)
                 for k in kernels), "invalid helper kernel support")
    edges = []
    for u in range(TARGET_COUNT):
        for v in range(u + 1, TARGET_COUNT + 1):
            weight = len(kernels[u]) if v == DUMMY_VERTEX else len(kernels[u] ^ kernels[v]) + 2
            tie = hashlib.sha256(f"{seed}:{u}:{v}".encode("ascii")).digest()
            edges.append((weight, tie, u, v))
    edges.sort()
    components = list(range(TARGET_COUNT + 1))

    def representative(vertex: int) -> int:
        # At most 120 links: each union reduces the component count by one.
        for _ in range(TARGET_COUNT + 1):
            if components[vertex] == vertex:
                return vertex
            vertex = components[vertex]
        raise ValueError("internal union-find cycle")

    selected = []
    for weight, _, u, v in edges:
        ru, rv = representative(u), representative(v)
        if ru == rv:
            continue
        components[rv] = ru
        selected.append({"u": u, "v": v, "weight": weight})
        if len(selected) == TARGET_COUNT:
            break
    _require(len(selected) == TARGET_COUNT, "complete graph did not produce a spanning tree")
    return selected


def _orient_tree(edges: list[dict]) -> tuple[list[int], list[int], list[int]]:
    adjacency = [[] for _ in range(TARGET_COUNT + 1)]
    for edge in edges:
        u, v = edge["u"], edge["v"]
        adjacency[u].append(v)
        adjacency[v].append(u)
    parents = [-1] * (TARGET_COUNT + 1)
    levels = [-1] * (TARGET_COUNT + 1)
    parents[DUMMY_VERTEX] = DUMMY_VERTEX
    levels[DUMMY_VERTEX] = 0
    queue = [DUMMY_VERTEX]
    for position in range(TARGET_COUNT + 1):
        _require(position < len(queue), "tree is disconnected")
        vertex = queue[position]
        for child in sorted(adjacency[vertex]):
            if child == parents[vertex]:
                continue
            _require(parents[child] == -1, "tree contains a cycle")
            parents[child] = vertex
            levels[child] = levels[vertex] + 1
            queue.append(child)
    _require(len(queue) == TARGET_COUNT + 1, "invalid tree vertex count")
    order = sorted(range(TARGET_COUNT), key=lambda vertex: (-levels[vertex], vertex))
    return parents[:TARGET_COUNT], levels[:TARGET_COUNT], order


def _emit_forest(kernels: list[frozenset[int]], parents: list[int], order: list[int]) -> tuple[list, dict]:
    prepare = [[0, TARGET_COUNT + i, [TARGET_COUNT + parents[i]]]
               for i in order if parents[i] != DUMMY_VERTEX]
    injection = []
    injection_order = []
    for vertex, kernel in enumerate(kernels):
        parent = parents[vertex]
        difference = kernel if parent == DUMMY_VERTEX else kernel ^ kernels[parent]
        # Equal kernels require no injection. Empty-source gates are omitted.
        if difference:
            injection.append([0, TARGET_COUNT + vertex, sorted(difference)])
            injection_order.append(vertex)
    unprepare = copy.deepcopy(prepare[::-1])
    first, second = len(prepare), len(prepare) + len(injection)
    return prepare + injection + unprepare, {
        "prepare": [0, first], "inject": [first, second],
        "unprepare": [second, second + len(unprepare)],
        "injection_order": injection_order,
    }


def _gate_stream(word: dict) -> list:
    scatter = [[word["final"][TARGET_COUNT + i], TARGET_COUNT + i,
                [word["ret"][j] for j in indices]]
               for i, indices in enumerate(word["scatter"]) if indices]
    return word["D"] + word["A"] + scatter + word["B"] + word["C"]


def _gate_metrics(gates: list) -> dict:
    data_ready = [0] * REGISTER_COUNT
    wire_ready = [0] * REGISTER_COUNT
    count = 0
    for _, destination, sources in gates:
        for source in sources:
            count += 1
            data_ready[destination] = 1 + max(data_ready[destination], data_ready[source])
            depth = 1 + max(wire_ready[destination], wire_ready[source])
            wire_ready[destination] = wire_ready[source] = depth
    return {"xor_count": count, "gate_records": len(gates),
            "ordered_data_dependency_depth": max(data_ready),
            "ordered_wire_disjoint_depth": max(wire_ready)}


def xor_metrics(word: dict) -> dict:
    """XOR cost and two explicitly ordered depth models, for D and full word.

    Each multisource record expands in listed source order into dst ^= src.
    Data-dependency depth updates only the destination's ready time (free
    fanout); wire-disjoint depth updates both wires, forbidding simultaneous
    reuse. Neither metric is an optimized schedule or an unsigned prefix bound.
    Full order is D,A,scatter,B,C; climbs have zero XOR cost here.
    """
    return {"D": _gate_metrics(word["D"]), "full": _gate_metrics(_gate_stream(word))}


def construct(word: dict, seed: int = 6, cuts: tuple[int, ...] | list[int] = ()) -> tuple[dict, dict]:
    """Return candidate/recipe without mutation; optionally re-root subtrees.

    Each cut is a distinct nonroot child in the original MST orientation. Its
    parent edge is replaced by an edge to the dummy, increasing XOR cost but
    potentially reducing unsigned growth. A cut candidate is not claimed to
    be a minimum-cost forest satisfying any prefix bound.
    """
    kernels = extract_kernels(word)
    for phase in ("A", "B", "C"):
        _validate_gates(word.get(phase), phase, len(word["frames"]))
    source_digest = hashlib.sha256(canonical_payload(word)).hexdigest()
    _require(source_digest == SOURCE_CANONICAL_SHA256,
             "source does not match the pinned R420 canonical payload")
    mst_edges = minimum_spanning_tree(kernels, seed)
    mst_parents, _, _ = _orient_tree(mst_edges)
    _require(isinstance(cuts, (tuple, list)) and
             all(_integer(vertex, 0, TARGET_COUNT) for vertex in cuts),
             "cuts must be a tuple or list of target vertex IDs")
    _require(len(set(cuts)) == len(cuts), "duplicate cut vertex")
    _require(all(mst_parents[vertex] != DUMMY_VERTEX for vertex in cuts),
             "cannot cut a vertex that is already a root")
    cut_vertices = sorted(cuts)
    removed_edges = {frozenset((vertex, mst_parents[vertex])) for vertex in cut_vertices}
    edges = [dict(edge) for edge in mst_edges
             if frozenset((edge["u"], edge["v"])) not in removed_edges]
    edges.extend({"u": vertex, "v": DUMMY_VERTEX, "weight": len(kernels[vertex])}
                 for vertex in cut_vertices)
    parents, levels, order = _orient_tree(edges)
    gates, boundaries = _emit_forest(kernels, parents, order)
    _validate_gates(gates, "candidate D", len(word["frames"]))
    candidate = copy.deepcopy(word)
    candidate["D"] = gates
    roots = [i for i, parent in enumerate(parents) if parent == DUMMY_VERTEX]
    source_metrics, candidate_metrics = xor_metrics(word), xor_metrics(candidate)
    tree_cost = sum(edge["weight"] for edge in edges)
    _require(tree_cost == candidate_metrics["D"]["xor_count"], "tree and emitted XOR costs differ")
    recipe = {
        "format": "r420-target-forest/1",
        "source": {"path": SOURCE_RELATIVE_PATH, "base_commit": BASE_COMMIT,
                   "canonical_sha256": source_digest, "file_sha256": SOURCE_FILE_SHA256},
        "candidate_canonical_sha256": hashlib.sha256(canonical_payload(candidate)).hexdigest(),
        "seed": seed,
        "algorithm": "Kruskal, ascending (weight, SHA256(ASCII seed:u:v), u, v)",
        "optimality_scope": "The uncut MST minimizes XOR count within the rooted target-forest "
                            "construction; cut variants have no unrestricted optimality claim.",
        "dummy_vertex": DUMMY_VERTEX,
        "vertices": [{"vertex": i, "target_register": TARGET_COUNT + i,
                      "kernel_weight": len(k)}
                     for i, k in enumerate(kernels)] +
                    [{"vertex": DUMMY_VERTEX, "target_register": None,
                      "kernel_weight": 0}],
        "mst_edges": mst_edges,
        "mst_parents": mst_parents,
        "tree_edges": edges,
        "cuts": cut_vertices,
        "parents": parents,
        "roots": roots,
        "levels_from_dummy": levels,
        "forest_height_edges": max(levels) - 1,
        "child_before_parent_order": order,
        "D_boundaries": boundaries,
        "metrics": {"source": source_metrics, "candidate": candidate_metrics,
                    "mst_weight": sum(edge["weight"] for edge in mst_edges),
                    "tree_weight": tree_cost,
                    "xor_saved": source_metrics["D"]["xor_count"] - tree_cost},
        "depth_model": "Listed-order binary XOR expansion; data dependency updates destination only; "
                       "wire-disjoint updates both wires. Neither is a prefix-coefficient bound.",
    }
    return candidate, recipe
