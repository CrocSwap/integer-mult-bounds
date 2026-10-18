#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""First-principles verifier for p104-pooled-onehop-and-physical-consumer-bill.

Addresses priority card `p104-side-correction` (track `complex-mechanisms`, weight 20)
by proving four unified pillars and six behavioral negative controls from pinned
upstream inputs only:

  1. Universal 2,309-Edge Pooled Intralayer-Transitivity Obstruction:
     Even when all 2,309 compatible (a, b) pairs of PR #2981's cover are active
     simultaneously (containing every possible 208-edge perfect matching at once),
     replacing PR #2996's transitive connected-component closure with 1-hop-per-dimension
     equal-frame transitivity (F_{u,d} = F_{w,d}) leaves 1 required nonzero entry of
     I - G/2 unreachable: 0-based (Y71, X102) (1-based (72, 103)), where
     C[71, 102] = -1/2. The forward reachability cone of X102 through Dim 5
     (1,725 edges) and the backward reachability cone of Y71's 12 Dim-8 cap writers
     through Dim 6 (37 edges) have empty intersection (1,725 cap 37 = 0).

  2. Direct Refutation of Open PR #3124's Cycle Matchings on Their Own Moved Cycle Vertices:
     Open PR #3124 (external comparator, not read at runtime) modifies PR #3013's
     matching via a 4-cycle [13, 203, 191, 63] (or [39, 154, 139, 134]) so that fixed
     helper 91 obtains 33/9,765 passing flags in isolation. Running the exact 9,765-flag
     single-helper consistency census on the moved cycle vertices themselves proves:
       * On cycle A [13, 203, 191, 63]: moved cycle vertex 13 (edge 13 -> 180) has
         0/9,765 passing flags (min_missing = 1,002; histogram {1002: 225, 1020: 477,
         1023: 477, 1025: 117, 1026: 8469}) and moved cycle vertex 63 (edge 63 -> 185)
         has 0/9,765 passing flags (min_missing = 481; histogram {481: 27, 913: 54,
         950: 66, 968: 360, 972: 132, 992: 9126}). For helper 13, all 12/12 ordered
         distinct intermediate neighbor pairs (u, w) from {63, 91, 118, 185} violate
         A_u subseteq B_{b(w)}.
       * On cycle B [39, 154, 139, 134]: helper 91 and all 4 moved cycle vertices
         39, 154, 139, 134 have 0/9,765 passing flags (min_missing = 91).

  3. Cross-Dimension Subspace-Memory Propagation Obstruction Across All Five Matchings:
     Tracking the minimal subspace A_u subseteq F_{h,d1} subseteq F_{h,d2} subseteq B_{b(w)}
     carried across dimensions d1 <= d2 shows that 116 to 145 of the 208 helpers have
     zero valid intermediate relay pairs, leaving 4,781 of 4,992 pairs missing on PR #2981
     and 4,783 of 4,992 pairs missing on PR #3013, PR #3019, PR #3124_A, and PR #3124_B.

  4. Complete 9-Stage Physical Consumer Bill & Dual-Endpoint Boundary Untangling Frontier:
     Combines the 9-stage consumer (m = 73, W = 832, N = 9, w = 832/9, R = 51, base local
     mass 2,368/call, base idle mass 4,344/call, paid mass 6,712/call) with dual-endpoint
     boundary conversions (4 reverse-adjoint calls per 9-stage consumer) and flag-coarsening
     profiles across kappa_selected = 0.001672660197076918, b_selected = 0.001675460322,
     conservative_complex_lower = 0.0016754626739466284, a_complex = 0.0016754626768081035,
     and c_bit = 0.0017334270395898442 under both Mode A (uncredited non-persistent dual
     accounting) and Mode B (favorable persistent-credit relaxation).

Usage:
  python3 -B verify.py [--write]
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = (
    HERE.parents[1]
    if (HERE.parents[1] / "certificates" / "selected-result.json").is_file()
    else HERE.parents[1] / "imb-repo"
)
sys.path.insert(0, str(ROOT / "research" / "complex-local-word-ceiling"))
import ceiling as ceiling_mod  # noqa: E402

LIMIT = 5_000_000
FULL = (1 << 104) - 1

PINNED_PATHS = (
    "certificates/selected-result.json",
    "docs/research/agent-task-catalog.json",
    "research/complex-local-word-ceiling/ceiling.py",
    "research/p104-all-pair-consumer-budget/RESULT.json",
    "research/p104-coherent-support-witness/CONTROL.json",
    "research/p104-coherent-support-witness/WITNESS.json",
    "research/p104-consumer-budget-audit/RESULT.json",
    "research/p104-endpoint-geometric-budget/RESULT.json",
    "research/p104-endpoint-geometric-budget/geometry.py",
    "research/p104-fixed-matching-flag-consistency/RESULT.json",
    "research/p104-fixed-matching-flag-consistency/verify.py",
    "research/p104-joint-endpoint-obstruction/RESULT.json",
    "research/p104-joint-unit-flags/CERTIFICATE.json",
    "research/p104-joint-unit-flags/verify.py",
    "research/p104-native-channel/inputs/LOWRANK-WITNESS.json",
    "research/p104-native-channel/inputs/P104-FIXTURE.json",
    "research/p104-native-channel/verify.py",
    "research/p104-two-history-lifetime-floor/RESULT.json",
)


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def unique_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = dict(pairs)
    require(len(result) == len(pairs), "duplicate JSON key")
    return result


def read_json(path: Path) -> object:
    with path.open("rb") as stream:
        raw = stream.read(LIMIT + 1)
    require(len(raw) <= LIMIT, f"JSON size bound exceeded: {path}")
    return json.loads(raw, object_pairs_hook=unique_pairs)


def authenticate_sources() -> dict[str, str]:
    sources = read_json(HERE / "SOURCES.json")
    require(isinstance(sources, dict), "SOURCES.json must be object")
    files = sources.get("files")
    require(isinstance(files, list) and len(files) == len(PINNED_PATHS), "pinned file count")
    pins: dict[str, str] = {}
    for entry in files:
        rel = entry["path"]
        sha = entry["sha256"]
        target = ROOT / rel
        require(target.is_file(), f"missing pinned upstream file: {rel}")
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        require(actual == sha, f"SHA-256 mismatch for {rel}: {actual} != {sha}")
        pins[rel] = sha
    require(tuple(sorted(pins)) == tuple(sorted(PINNED_PATHS)), "exact pinned path inventory")
    return pins


def span(basis: list[int]) -> int:
    require(isinstance(basis, list) and len(basis) <= 9, "basis size")
    points = [0]
    for vector in basis:
        require(isinstance(vector, int) and 0 < vector < 512, "binary vector")
        require(vector not in points, "independent basis")
        points += [point ^ vector for point in points]
    return sum(1 << point for point in points)


def bits(mask: int, width: int):
    require(isinstance(mask, int) and 0 <= mask < (1 << width), "mask domain")
    for _ in range(width):
        if not mask:
            break
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def dim(frame: int) -> int:
    count = frame.bit_count()
    require(count > 0 and (count & (count - 1)) == 0, "subspace size")
    return count.bit_length() - 1


def frame_basis(frame: int) -> list[int]:
    points, basis = [0], []
    for vector in range(1, 512):
        if (frame >> vector) & 1 and vector not in points:
            basis.append(vector)
            points += [p ^ vector for p in points]
    require(len(points) == frame.bit_count(), "complete frame basis")
    return basis


def data_paths(word: dict) -> dict[str, list[int]]:
    paths = {
        f"{kind}{i}": [span(word["initial_frames"][f"{kind}{i}"])]
        for kind in "XY"
        for i in range(104)
    }
    require(isinstance(word["program"], list) and len(word["program"]) == 4058, "word size")
    for event in word["program"]:
        op, name = event[:2]
        if op != "transport":
            require(op in {"add", "copy", "zero", "erase"}, "opcode")
            require(not name.startswith("X"), "immutable X")
            if op in {"add", "copy"}:
                require(not event[2].startswith("Y"), "unread Y")
            continue
        if name not in paths:
            continue
        old, new = span(event[2]), span(event[3])
        require(paths[name][-1] == old and old != new and (old & new) == old, "path")
        rank = event[4]
        require(isinstance(rank, int) and rank == dim(new) - dim(old), "transport rank")
        paths[name].append(new)
    for name, chain in paths.items():
        require(
            len(chain) <= 10 and chain[-1] == span(word["final_frames"][name]),
            "exit",
        )
        require(
            (dim(chain[0]), dim(chain[-1])) == ((1, 9) if name[0] == "X" else (0, 8)),
            "data endpoints",
        )
    return paths


def cover_frames(certificate: dict, paths: dict[str, list[int]]) -> tuple:
    forms = certificate["forms"]
    require(set(forms) == {"departure", "arrival"}, "cover orientations")
    lines = [paths[f"X{s}"][0] for s in range(104)]
    caps = [paths[f"Y{t}"][-1] for t in range(104)]
    require(len(set(lines)) == len(set(caps)) == 104, "distinct data endpoints")
    departures, arrivals = [], []
    for kind in ("departure", "arrival"):
        require(isinstance(forms[kind], list) and len(forms[kind]) == 104, "cover count")
        for index, pair in enumerate(forms[kind]):
            require(isinstance(pair, list) and len(pair) == 2, "two cover slots")
            for form in pair:
                require(isinstance(form, int) and 0 < form < 512, "cover functional")
                if kind == "departure":
                    basis = [lines[index].bit_length() - 1, form]
                    departures.append(span(basis))
                else:
                    frame = sum(
                        1 << p
                        for p in bits(caps[index], 512)
                        if (p & form).bit_count() % 2 == 0
                    )
                    require(dim(frame) == 7, "arrival dimension")
                    arrivals.append(frame)
    graph = [[j for j, b in enumerate(arrivals) if (a & b) == a] for a in departures]
    require(sum(map(len, graph)) == 2309, "compatibility edges")
    return lines, departures, arrivals, caps, graph


def check_pairing(pairing: list[int], graph: list[list[int]]) -> None:
    size = len(graph)
    require(isinstance(pairing, list) and len(pairing) == size, "pairing size")
    require(all(isinstance(j, int) and 0 <= j < size for j in pairing), "pairing integers")
    require(len(set(pairing)) == size, "pairing bijection")
    require(all(j in graph[i] for i, j in enumerate(pairing)), "compatible pairing")


def intervals(frames: tuple, edges: list[tuple[int, int]], dimension: int) -> list[tuple[int, int]]:
    lines, departures, arrivals, caps, _ = frames
    if dimension == 1:
        return [(lines[a // 2],) * 2 for a, _ in edges]
    if dimension == 2:
        return [(departures[a],) * 2 for a, _ in edges]
    if dimension == 7:
        return [(arrivals[b],) * 2 for _, b in edges]
    if dimension == 8:
        return [(caps[b // 2],) * 2 for _, b in edges]
    require(3 <= dimension <= 6, "intermediate dimension")
    return [(departures[a], arrivals[b]) for a, b in edges]


def fits(bounds: tuple[int, int], dimension: int, frame: int) -> bool:
    low, high = bounds
    return dim(frame) == dimension and (low & frame) == low and (frame & high) == frame


def contact(left: tuple[int, int], right: tuple[int, int], dimension: int) -> bool:
    a, b = left
    c, e = right
    if (a & e) != a or (c & b) != c:
        return False
    minimum = a.bit_count() * c.bit_count() // (a & c).bit_count()
    return minimum <= (1 << dimension) <= (b & e).bit_count()


def build_general_interval_layers(
    frames: tuple, edges: list[tuple[int, int]], paths: dict[str, list[int]]
) -> list[tuple[list[int], list[int], list[int]]]:
    n = len(edges)
    layers = []
    for d in range(1, 9):
        bounds = intervals(frames, edges, d)
        adjacency = [1 << i for i in range(n)]
        reads, writes = [], []
        for i, left in enumerate(bounds):
            reads.append(
                sum(
                    1 << s
                    for s in range(104)
                    if any(fits(left, d, f) for f in paths[f"X{s}"])
                )
            )
            writes.append(
                sum(
                    1 << t
                    for t in range(104)
                    if any(fits(left, d, f) for f in paths[f"Y{t}"])
                )
            )
            for j in range(i):
                if contact(left, bounds[j], d):
                    adjacency[i] |= 1 << j
                    adjacency[j] |= 1 << i
        layers.append((adjacency, reads, writes))
    return layers


def general_components(adjacency: list[int]) -> list[list[int]]:
    count = len(adjacency)
    unvisited = (1 << count) - 1
    groups = []
    for start in range(count):
        if not ((unvisited >> start) & 1):
            continue
        queue = [start]
        unvisited ^= 1 << start
        for cursor in range(count):
            if cursor == len(queue):
                break
            new = adjacency[queue[cursor]] & unvisited
            queue.extend(bits(new, count))
            unvisited ^= new
        groups.append(queue)
    return groups


def layer_plan(layer: tuple[list[int], list[int], list[int]]) -> tuple:
    adjacency, reads, writes = layer
    return general_components(adjacency), reads, [list(bits(w, 104)) for w in writes]


def propagate(plans: list[tuple], direct: list[int]) -> list[int]:
    count = len(plans[0][1])
    support = [0] * count
    outputs = list(direct)
    for groups, reads, write_targets in plans:
        for i, mask in enumerate(reads):
            support[i] |= mask
        for group in groups:
            joined = 0
            for i in group:
                joined |= support[i]
            for i in group:
                support[i] = joined
        for i, targets in enumerate(write_targets):
            for target in targets:
                outputs[target] |= support[i]
    return outputs


def propagate_one_hop_equal_frame(layers: list, direct: list[int]) -> list[int]:
    count = len(layers[0][0])
    support = [0] * count
    outputs = list(direct)
    for adjacency, reads, writes in layers:
        next_support = list(support)
        for i in range(count):
            m = support[i] | reads[i]
            for j in bits(adjacency[i], count):
                m |= support[j]
            next_support[i] = m
        support = next_support
        for i in range(count):
            for t in bits(writes[i], 104):
                outputs[t] |= support[i]
    return outputs


def propagate_with_subspace_memory_bitmap(
    frames: tuple,
    edges: list[tuple[int, int]],
    layers: list,
    paths: dict[str, list[int]],
    direct: list[int],
    full_memory: bool = False,
) -> list[int]:
    count = len(edges)
    state: list[dict[int, list[int]]] = [{} for _ in range(count)]
    outputs = list(direct)

    def add_subspace(sub_list: list[int], cand: int) -> None:
        for existing in sub_list:
            if (existing & cand) == existing:
                return
        sub_list[:] = [m for m in sub_list if not ((cand & m) == cand and cand != m)]
        sub_list.append(cand)

    for d, (adjacency, reads, writes) in enumerate(layers, 1):
        bounds = intervals(frames, edges, d)
        next_state = [{s: list(subs) for s, subs in st.items()} for st in state]

        for h in range(count):
            low_h, _ = bounds[h]
            for s in bits(reads[h], 104):
                for f_x in paths[f"X{s}"]:
                    if fits(bounds[h], d, f_x):
                        sub_mem = f_x if full_memory else low_h
                        add_subspace(next_state[h].setdefault(s, []), sub_mem)

        for h in range(count):
            low_h, high_h = bounds[h]
            for w in bits(adjacency[h], count):
                if w == h:
                    continue
                low_w, high_w = bounds[w]
                inter_high = high_h & high_w
                for s, subs in state[h].items():
                    for S in subs:
                        if (
                            (S & inter_high) == S
                            and (low_h & inter_high) == low_h
                            and (low_w & inter_high) == low_w
                        ):
                            span_pts = S
                            for sub in (low_h, low_w):
                                if (sub & span_pts) != sub:
                                    for pt in bits(sub, 512):
                                        if pt and not ((span_pts >> pt) & 1):
                                            span_pts |= sum(
                                                1 << (p ^ pt)
                                                for p in bits(span_pts, 512)
                                            )
                            if span_pts.bit_count() <= (1 << d) <= inter_high.bit_count():
                                if full_memory:
                                    sub_mem = span_pts
                                else:
                                    span_hw = low_h
                                    for pt in bits(low_w, 512):
                                        if pt and not ((span_hw >> pt) & 1):
                                            span_hw |= sum(
                                                1 << (p ^ pt)
                                                for p in bits(span_hw, 512)
                                            )
                                    sub_mem = span_hw
                                add_subspace(next_state[w].setdefault(s, []), sub_mem)

        state = next_state

        for h in range(count):
            for t in bits(writes[h], 104):
                for f_y in paths[f"Y{t}"]:
                    if fits(bounds[h], d, f_y):
                        for s, subs in state[h].items():
                            if any((S & f_y) == S for S in subs):
                                outputs[t] |= 1 << s
                                break
    return outputs


def correction(fixture: dict) -> list[list[Fraction]]:
    roots = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.append(tuple(row))
    roots += [(1, *s) for s in product((-1, 1), repeat=7) if s.count(-1) % 2 == 0]
    removed = fixture["section4_explicit_P104"]
    ports = sorted(set(roots) - {tuple(v) for v in removed["F0"] + removed["C"]})
    require(len(roots) == 120 and len(ports) == 104, "ordered P104 roots")
    return [
        [
            Fraction(
                8 * int(t == s)
                - sum(a * b for a, b in zip(ports[t], ports[s], strict=True)),
                8,
            )
            for s in range(104)
        ]
        for t in range(104)
    ]


def quotient_spaces() -> list[list[list[int]]]:
    result = []
    for size in range(6):
        spaces = []
        for pivots in combinations(range(5), size):
            free = [
                (i, j)
                for i, p in enumerate(pivots)
                for j in range(p + 1, 5)
                if j not in pivots
            ]
            for entries in range(1 << len(free)):
                rows = [1 << p for p in pivots]
                for index, (i, j) in enumerate(free):
                    if (entries >> index) & 1:
                        rows[i] |= 1 << j
                points = [0]
                for row in rows:
                    points += [p ^ row for p in points]
                spaces.append(sorted(points))
        require(len({tuple(s) for s in spaces}) == len(spaces), "duplicate quotient subspace")
        result.append(spaces)
    require(list(map(len, result)) == [1, 31, 155, 155, 31, 1], "quotient census")
    return result


def coset_masks(low: int, high: int) -> list[int]:
    points, basis = [0], []
    for frame, target in ((low, 2), (high, 7)):
        for vector in range(1, 512):
            if len(basis) == target:
                break
            if ((frame >> vector) & 1) and vector not in points:
                basis.append(vector)
                points += [p ^ vector for p in points]
        require(len(basis) == target, "endpoint basis dimension")
    a_points = [0, basis[0], basis[1], basis[0] ^ basis[1]]
    masks = []
    for q in range(32):
        lift = 0
        for j in range(5):
            if (q >> j) & 1:
                lift ^= basis[2 + j]
        masks.append(sum(1 << (a ^ lift) for a in a_points))
    require(len(set(masks)) == 32, "distinct quotient cosets")
    return masks


def allowed_frames(
    frames: tuple,
    edge: tuple[int, int],
    dimension: int,
    cosets: list[int],
    quotients: list[list[list[int]]],
) -> list[int]:
    lines, departures, arrivals, caps, _ = frames
    a, b = edge
    if dimension == 1:
        return [lines[a // 2]]
    if dimension == 2:
        return [departures[a]]
    if dimension == 7:
        return [arrivals[b]]
    if dimension == 8:
        return [caps[b // 2]]
    require(3 <= dimension <= 6, "literal dimension")
    result = []
    for points in quotients[dimension - 2]:
        mask = 0
        for point in points:
            mask |= cosets[point]
        result.append(mask)
    return result


def full_flags(choices: dict[int, list[int]]):
    for i3, f3 in enumerate(choices[3]):
        for i4, f4 in enumerate(choices[4]):
            if (f3 & f4) != f3:
                continue
            for i5, f5 in enumerate(choices[5]):
                if (f4 & f5) != f4:
                    continue
                for i6, f6 in enumerate(choices[6]):
                    if (f5 & f6) == f5:
                        yield (i3, i4, i5, i6)


def count_missing(outputs: list[int], required: list[int]) -> tuple[int, list[list[int]]]:
    missing_list: list[list[int]] = []
    for t in range(104):
        miss_mask = required[t] & ~outputs[t]
        for s in bits(miss_mask, 104):
            missing_list.append([t, s])
    return len(missing_list), missing_list


def apply_cycle_to_pairing(pairing: list[int], cycle: list[int]) -> list[int]:
    changed = list(pairing)
    k = len(cycle)
    for i, a in enumerate(cycle):
        changed[a] = pairing[cycle[(i + 1) % k]]
    return changed


def load_all_data() -> dict:
    pins = authenticate_sources()
    cert = read_json(ROOT / "research/p104-joint-unit-flags/CERTIFICATE.json")
    word = read_json(ROOT / "research/p104-native-channel/inputs/LOWRANK-WITNESS.json")
    fixture = read_json(ROOT / "research/p104-native-channel/inputs/P104-FIXTURE.json")
    witness_3019 = read_json(ROOT / "research/p104-coherent-support-witness/WITNESS.json")
    control_3013 = read_json(ROOT / "research/p104-coherent-support-witness/CONTROL.json")
    res_2920 = read_json(ROOT / "research/p104-endpoint-geometric-budget/RESULT.json")
    res_2924 = read_json(ROOT / "research/p104-two-history-lifetime-floor/RESULT.json")
    res_2953 = read_json(ROOT / "research/p104-joint-endpoint-obstruction/RESULT.json")
    res_2741 = read_json(ROOT / "research/p104-consumer-budget-audit/RESULT.json")
    res_2819 = read_json(ROOT / "research/p104-all-pair-consumer-budget/RESULT.json")
    res_3038 = read_json(ROOT / "research/p104-fixed-matching-flag-consistency/RESULT.json")
    selected = read_json(ROOT / "certificates/selected-result.json")

    require("geometry" in res_2920 and "price" in res_2920, "PR2920 receipt")
    require(res_2924["pr2920_curve_checked"] is True, "PR2924 two-history receipt")
    require("geometry" in res_2953 and "profile" in res_2953, "PR2953 joint endpoint receipt")
    require(res_2741["status"] == "PASS_P104_CONSUMER_BUDGET_AUDIT", "PR2741 receipt")
    require(res_2819["forgiven_dual_rank_units"] == 416, "PR2819 receipt")
    require(res_3038["census"]["minimum_missing_required_pairs"] == 45, "PR3038 min missing")

    paths = data_paths(word)
    frames = cover_frames(cert, paths)
    matrix = correction(fixture)
    required = [sum(1 << s for s in range(104) if matrix[t][s]) for t in range(104)]
    require(sum(mask.bit_count() for mask in required) == 4992, "4,992 required pairs")
    direct = [
        sum(1 << s for s in range(104) if set(paths[f"X{s}"]) & set(paths[f"Y{t}"]))
        for t in range(104)
    ]

    pairing_2981 = [-1] * 208
    for row in cert["helpers"]:
        s, a, t, b = [row[k] for k in ("source", "departure_choice", "target", "arrival_choice")]
        pairing_2981[2 * s + a] = 2 * t + b
    pairing_3013 = control_3013["pairing"] if isinstance(control_3013, dict) else control_3013
    pairing_3019 = witness_3019["pairing"]
    check_pairing(pairing_2981, frames[-1])
    check_pairing(pairing_3013, frames[-1])
    check_pairing(pairing_3019, frames[-1])

    return {
        "pins": pins,
        "selected": selected,
        "cert": cert,
        "word": word,
        "fixture": fixture,
        "paths": paths,
        "frames": frames,
        "matrix": matrix,
        "required": required,
        "direct": direct,
        "pairing_2981": pairing_2981,
        "pairing_3013": pairing_3013,
        "pairing_3019": pairing_3019,
    }


def analyze_pillar1_pooled_2309(data: dict) -> dict:
    frames = data["frames"]
    paths = data["paths"]
    required = data["required"]
    direct = data["direct"]
    matrix = data["matrix"]
    graph = frames[-1]

    all_edges = [(a, b) for a in range(208) for b in graph[a]]
    require(len(all_edges) == 2309, "2,309 compatibility edges")

    layers_2309 = build_general_interval_layers(frames, all_edges, paths)
    out_comp = propagate([layer_plan(layer) for layer in layers_2309], direct)
    comp_miss_cnt, _ = count_missing(out_comp, required)

    out_adj = propagate_one_hop_equal_frame(layers_2309, direct)
    adj_miss_cnt, adj_miss_list = count_missing(out_adj, required)

    require(comp_miss_cnt == 0, "pooled components missing count must be 0")
    require(adj_miss_cnt == 1, "pooled 1-hop equal-frame missing count must be 1")
    require(adj_miss_list == [[71, 102]], "unreachable pair must be 0-based [71, 102]")

    s_idx = 102
    t_idx = 71
    x_readers_by_dim: dict[str, list[list[int]]] = {}
    y_writers_by_dim: dict[str, list[list[int]]] = {}
    reached = 0
    forward_counts: dict[str, int] = {}
    y_hits_by_dim: dict[str, int] = {}

    for d, (adjacency, reads, writes) in enumerate(layers_2309, 1):
        r_edges = [list(all_edges[i]) for i in range(2309) if (reads[i] >> s_idx) & 1]
        w_edges = [list(all_edges[i]) for i in range(2309) if (writes[i] >> t_idx) & 1]
        if r_edges:
            x_readers_by_dim[str(d)] = r_edges
        if w_edges:
            y_writers_by_dim[str(d)] = w_edges

        nxt_reached = reached
        for i in range(2309):
            if (reads[i] >> s_idx) & 1:
                nxt_reached |= 1 << i
            if (reached >> i) & 1:
                nxt_reached |= adjacency[i]
        reached = nxt_reached
        forward_counts[str(d)] = reached.bit_count()
        if w_edges:
            hits = sum(
                1
                for i in range(2309)
                if ((writes[i] >> t_idx) & 1) and ((reached >> i) & 1)
            )
            y_hits_by_dim[str(d)] = hits

    adj_d8 = layers_2309[7][0]
    adj_d7 = layers_2309[6][0]
    adj_d6 = layers_2309[5][0]
    writes_d8 = layers_2309[7][2]
    y71_d8_mask = sum(1 << i for i in range(2309) if (writes_d8[i] >> t_idx) & 1)
    require(y71_d8_mask.bit_count() == 12, "12 Dim-8 cap writers for Y71")

    back_after_d8 = y71_d8_mask
    for i in bits(y71_d8_mask, 2309):
        back_after_d8 |= adj_d8[i]

    back_after_d7 = back_after_d8
    for i in bits(back_after_d8, 2309):
        back_after_d7 |= adj_d7[i]

    back_after_d6 = back_after_d7
    for i in bits(back_after_d7, 2309):
        back_after_d6 |= adj_d6[i]

    reached_d5 = 0
    for d in range(1, 6):
        adjacency, reads, _ = layers_2309[d - 1]
        nxt = reached_d5
        for i in range(2309):
            if (reads[i] >> s_idx) & 1:
                nxt |= 1 << i
            if (reached_d5 >> i) & 1:
                nxt |= adjacency[i]
        reached_d5 = nxt

    require(reached_d5.bit_count() == 1725, "X102 forward cone at dim 5 must be 1,725 edges")
    require(back_after_d6.bit_count() == 37, "Y71 backward cone at dim 6 must be 37 edges")
    require((reached_d5 & back_after_d6) == 0, "forward dim 5 and backward dim 6 cones must be disjoint")

    return {
        "total_compatibility_edges": len(all_edges),
        "components_missing_count": comp_miss_cnt,
        "one_hop_equal_frame_missing_count": adj_miss_cnt,
        "one_hop_missing_pairs_0based": adj_miss_list,
        "one_hop_missing_pairs_1based": [[y + 1, x + 1] for y, x in adj_miss_list],
        "unreachable_coefficient": str(matrix[t_idx][s_idx]),
        "x102_readers_by_dim": x_readers_by_dim,
        "y71_writers_by_dim": y_writers_by_dim,
        "x102_forward_reached_edge_counts_by_dim": forward_counts,
        "y71_writer_hits_by_dim": y_hits_by_dim,
        "y71_dim8_writer_count": y71_d8_mask.bit_count(),
        "y71_backward_cone_after_dim8_size": back_after_d8.bit_count(),
        "y71_backward_cone_after_dim7_size": back_after_d7.bit_count(),
        "y71_backward_cone_after_dim6_size": back_after_d6.bit_count(),
        "x102_forward_dim5_size": reached_d5.bit_count(),
        "forward_dim5_intersect_backward_dim6_8_size": (reached_d5 & back_after_d6).bit_count(),
    }


def single_helper_flag_census_for_slot(
    slot: int,
    paths: dict[str, list[int]],
    frames: tuple,
    edges: list[tuple[int, int]],
    layers: list,
    required: list[int],
    direct: list[int],
    quotients: list[list[list[int]]],
) -> dict:
    cosets = coset_masks(frames[1][slot], frames[2][edges[slot][1]])
    choices = {
        d: allowed_frames(frames, edges[slot], d, cosets, quotients)
        for d in range(3, 7)
    }
    plans = [layer_plan(layer) for layer in layers]

    def freeze_slot(layer, dimension: int, chosen: int):
        adjacency, reads, writes = [part.copy() for part in layer]
        helper_bit = 1 << slot
        bounds = intervals(frames, edges, dimension)
        adjacency[slot] = helper_bit
        for other in range(208):
            adjacency[other] &= ~helper_bit
            if fits(bounds[other], dimension, chosen):
                adjacency[other] |= helper_bit
                adjacency[slot] |= 1 << other
        reads[slot] = sum(1 << s for s in range(104) if chosen in paths[f"X{s}"])
        writes[slot] = sum(1 << t for t in range(104) if chosen in paths[f"Y{t}"])
        return adjacency, reads, writes

    key_by_dim_idx: dict[int, list[tuple]] = {}
    plan_by_key: dict[tuple, tuple] = {}
    for d in range(3, 7):
        key_list = []
        for f in choices[d]:
            frozen = freeze_slot(layers[d - 1], d, f)
            k = (d, frozen[0][slot], frozen[1][slot], frozen[2][slot])
            if k not in plan_by_key:
                plan_by_key[k] = layer_plan(frozen)
            key_list.append(k)
        key_by_dim_idx[d] = key_list

    census: Counter[int] = Counter()
    y40_missing_hist: Counter[int] = Counter()
    eval_cache: dict[tuple, tuple[int, int]] = {}
    total = 0
    for indices in full_flags(choices):
        prof_key = tuple(key_by_dim_idx[d][i] for d, i in zip(range(3, 7), indices, strict=True))
        if prof_key not in eval_cache:
            trial = plans.copy()
            for d, k in zip(range(3, 7), prof_key, strict=True):
                trial[d - 1] = plan_by_key[k]
            outputs = propagate(trial, direct)
            missing = [r & ~o for r, o in zip(required, outputs, strict=True)]
            count = sum(mask.bit_count() for mask in missing)
            eval_cache[prof_key] = (count, missing[40].bit_count())
        count, y40_miss = eval_cache[prof_key]
        census[count] += 1
        y40_missing_hist[y40_miss] += 1
        total += 1

    require(total == 9765, "complete 9,765-flag census")
    return {
        "slot": slot,
        "edge": list(edges[slot]),
        "total_flags": total,
        "distinct_contact_profiles": len(eval_cache),
        "passing_flag_count": census.get(0, 0),
        "min_missing_pairs": min(census.keys()),
        "max_missing_pairs": max(census.keys()),
        "missing_pairs_histogram": {str(k): v for k, v in sorted(census.items())},
        "y40_missing_histogram": {str(k): v for k, v in sorted(y40_missing_hist.items())},
    }


def analyze_pillar2_and_pillar3(data: dict) -> dict:
    frames = data["frames"]
    paths = data["paths"]
    required = data["required"]
    direct = data["direct"]

    p_2981 = data["pairing_2981"]
    p_3013 = data["pairing_3013"]
    p_3019 = data["pairing_3019"]
    p_3124_a = apply_cycle_to_pairing(p_3013, [13, 203, 191, 63])
    p_3124_b = apply_cycle_to_pairing(p_3013, [39, 154, 139, 134])
    check_pairing(p_3124_a, frames[-1])

    pairings = {
        "PR2981_baseline": p_2981,
        "PR3013_rematched": p_3013,
        "PR3019_witness_swap_91_189": p_3019,
        "PR3124_cycle_A_13_203_191_63": p_3124_a,
        "PR3124_cycle_B_39_154_139_134": p_3124_b,
    }

    matching_summary: dict[str, dict] = {}
    departures = frames[1]
    arrivals = frames[2]

    for name, pairing in pairings.items():
        edges = list(enumerate(pairing))
        layers = build_general_interval_layers(frames, edges, paths)
        out_comp = propagate([layer_plan(layer) for layer in layers], direct)
        m_comp, _ = count_missing(out_comp, required)

        out_adj = propagate_one_hop_equal_frame(layers, direct)
        m_adj, _ = count_missing(out_adj, required)

        out_mem1 = propagate_with_subspace_memory_bitmap(
            frames, edges, layers, paths, direct, full_memory=False
        )
        m_mem1, _ = count_missing(out_mem1, required)

        out_mem_full = propagate_with_subspace_memory_bitmap(
            frames, edges, layers, paths, direct, full_memory=True
        )
        m_mem_full, _ = count_missing(out_mem_full, required)

        zero_relay_helpers = []
        for h in range(208):
            nbrs_by_dim = [
                set(bits(layers[d - 1][0][h] & ~(1 << h), 208))
                for d in range(3, 7)
            ]
            all_nbrs = sorted(set().union(*nbrs_by_dim))
            has_valid_pair = False
            for u in all_nbrs:
                for w in all_nbrs:
                    if u == w:
                        continue
                    if (departures[u] & arrivals[pairing[w]]) == departures[u]:
                        for d1 in range(3, 7):
                            if u in nbrs_by_dim[d1 - 3]:
                                for d2 in range(d1, 7):
                                    if w in nbrs_by_dim[d2 - 3]:
                                        has_valid_pair = True
                                        break
                            if has_valid_pair:
                                break
                    if has_valid_pair:
                        break
                if has_valid_pair:
                    break
            if not has_valid_pair:
                zero_relay_helpers.append(h)

        matching_summary[name] = {
            "PR2996_components_missing": m_comp,
            "one_hop_equal_frame_missing": m_adj,
            "one_step_subspace_memory_missing": m_mem1,
            "full_subspace_memory_missing": m_mem_full,
            "zero_intermediate_relay_helper_count": len(zero_relay_helpers),
        }

    edges_3124_a = list(enumerate(p_3124_a))
    layers_3124_a = build_general_interval_layers(frames, edges_3124_a, paths)
    quotients = quotient_spaces()

    census_3124_a = {}
    for slot in (91, 13, 203, 191, 63):
        census_3124_a[str(slot)] = single_helper_flag_census_for_slot(
            slot, paths, frames, edges_3124_a, layers_3124_a, required, direct, quotients
        )

    require(census_3124_a["91"]["passing_flag_count"] == 33, "PR3124_A helper 91 passing = 33")
    require(census_3124_a["13"]["passing_flag_count"] == 0, "PR3124_A vertex 13 passing = 0")
    require(census_3124_a["13"]["min_missing_pairs"] == 1002, "PR3124_A vertex 13 min_missing = 1002")
    require(census_3124_a["203"]["passing_flag_count"] == 477, "PR3124_A vertex 203 passing = 477")
    require(census_3124_a["191"]["passing_flag_count"] == 225, "PR3124_A vertex 191 passing = 225")
    require(census_3124_a["63"]["passing_flag_count"] == 0, "PR3124_A vertex 63 passing = 0")
    require(census_3124_a["63"]["min_missing_pairs"] == 481, "PR3124_A vertex 63 min_missing = 481")

    edges_3124_b = list(enumerate(p_3124_b))
    layers_3124_b = build_general_interval_layers(frames, edges_3124_b, paths)
    census_3124_b = {}
    for slot in (91, 39, 154, 139, 134):
        census_3124_b[str(slot)] = single_helper_flag_census_for_slot(
            slot, paths, frames, edges_3124_b, layers_3124_b, required, direct, quotients
        )

    require(census_3124_b["91"]["passing_flag_count"] == 0, "PR3124_B helper 91 passing = 0")
    require(census_3124_b["91"]["min_missing_pairs"] == 91, "PR3124_B helper 91 min_missing = 91")
    require(census_3124_b["39"]["passing_flag_count"] == 0, "PR3124_B vertex 39 passing = 0")
    require(census_3124_b["39"]["min_missing_pairs"] == 91, "PR3124_B vertex 39 min_missing = 91")
    require(census_3124_b["154"]["passing_flag_count"] == 0, "PR3124_B vertex 154 passing = 0")
    require(census_3124_b["154"]["min_missing_pairs"] == 91, "PR3124_B vertex 154 min_missing = 91")
    require(census_3124_b["139"]["passing_flag_count"] == 0, "PR3124_B vertex 139 passing = 0")
    require(census_3124_b["139"]["min_missing_pairs"] == 91, "PR3124_B vertex 139 min_missing = 91")
    require(census_3124_b["134"]["passing_flag_count"] == 0, "PR3124_B vertex 134 passing = 0")
    require(census_3124_b["134"]["min_missing_pairs"] == 91, "PR3124_B vertex 134 min_missing = 91")

    h13_neighbors = sorted(
        {
            u
            for d in range(3, 7)
            for u in bits(layers_3124_a[d - 1][0][13] & ~(1 << 13), 208)
        }
    )
    require(h13_neighbors == [63, 91, 118, 185], "helper 13 intermediate neighbors")
    h13_pair_obstructions = []
    for u in h13_neighbors:
        for w in h13_neighbors:
            if u == w:
                continue
            basis_u = frame_basis(departures[u])
            arr_w_mask = arrivals[p_3124_a[w]]
            sep_vecs = [v for v in basis_u if not ((arr_w_mask >> v) & 1)]
            require(len(sep_vecs) > 0, "every ordered neighbor pair of helper 13 must have separating vector")
            h13_pair_obstructions.append(
                {
                    "from_neighbor": u,
                    "to_neighbor": w,
                    "A_from_basis": basis_u,
                    "arrival_slot_to": p_3124_a[w],
                    "separating_basis_vectors_not_in_B_to": sep_vecs,
                }
            )
    require(len(h13_pair_obstructions) == 12, "all 12 ordered neighbor pairs of helper 13 incompatible")

    return {
        "matching_propagation_summary": matching_summary,
        "PR3124_cycle_A_single_helper_census": census_3124_a,
        "PR3124_cycle_B_single_helper_census": census_3124_b,
        "helper_13_intermediate_neighbors": h13_neighbors,
        "helper_13_all_12_ordered_pairs_incompatible": h13_pair_obstructions,
    }


def analyze_pillar4_full_physical_consumer_bill(selected: dict) -> dict:
    exponents = {
        "kappa_selected": float(selected["decimal"]),
        "b_selected_prompt": 0.001675460322,
        "conservative_complex_lower": 0.0016754626739466284,
        "a_complex": 0.0016754626768081035,
        "c_bit": 0.0017334270395898442,
    }

    BASE = {1: 1074, 2: 58, 3: 86, 4: 104, 5: 48, 6: 24, 7: 8, 8: 8}
    m = 73.0
    families = 832.0
    stages = 9.0
    w = families / stages
    R = 51.0

    # Cross-check against pinned ceiling.py exact rational interval enclosure on PR2981 (208 units)
    a_b_sel = Fraction("0.001675460322")
    local_208_ideal = dict(BASE)
    local_208_ideal[1] += 9 * 208
    lo_id, hi_id = ceiling_mod.relax(local_208_ideal, 73, 832, 9, Fraction(56), a_b_sel, 51)
    require(lo_id < 1 and hi_id < 1, "208-unit idealized 0-dual passes at b_selected")

    local_208_fused = dict(BASE)
    local_208_fused[1] += 9 * 208 + Fraction(4, 9) * 260
    local_208_fused[7] += Fraction(4, 9) * 8
    centre_fused_mode_a = Fraction(56) + Fraction(4, 9) * (260 + 7 * 8)
    lo_fa, _ = ceiling_mod.relax(local_208_fused, 73, 832, 9, centre_fused_mode_a, a_b_sel, 51)
    _, hi_fb = ceiling_mod.relax(local_208_fused, 73, 832, 9, Fraction(56), a_b_sel, 51)
    require(lo_fa > 1 and hi_fb < 1, "208-unit 5-boundary fused dual fails in Mode A (> 1) vs Mode B (< 1)")

    def ceiling_moment(
        a: float,
        H_unit_h9: int,
        extra_dirty_jumps: list[tuple[int, int]] | None = None,
        dual_extra_h1_per_dual: float = 0.0,
        dual_extra_h7_per_dual: float = 0.0,
        credit_dual_as_persistent: bool = False,
    ) -> float:
        extra_dirty_jumps = extra_dirty_jumps or []
        profile: dict[int, float] = {r: float(cnt) for r, cnt in BASE.items()}
        profile[1] += 9.0 * H_unit_h9 + (4.0 / 9.0) * dual_extra_h1_per_dual
        profile[7] += (4.0 / 9.0) * dual_extra_h7_per_dual
        for cnt, r_jump in extra_dirty_jumps:
            profile[r_jump] = profile.get(r_jump, 0.0) + float(cnt)

        dirty_mass = 9.0 * H_unit_h9 + sum(cnt * r_jump for cnt, r_jump in extra_dirty_jumps)
        dual_mass_per_call = (4.0 / 9.0) * (dual_extra_h1_per_dual + 7.0 * dual_extra_h7_per_dual)

        if credit_dual_as_persistent:
            idle_mass = 6712.0 - 2368.0 - dirty_mass - dual_mass_per_call
        else:
            idle_mass = 6712.0 - 2368.0 - dirty_mass

        local_cost = sum(
            cnt * ((float(r) / m) ** (1.0 - a))
            for r, cnt in profile.items()
        )
        idle_cost = (idle_mass / R) * ((R / m) ** (1.0 - a))
        return (local_cost + idle_cost) / w

    def max_tolerable_dual_h1(
        a: float,
        H_unit_h9: int,
        extra_dirty_jumps: list[tuple[int, int]] | None = None,
        credit_dual_as_persistent: bool = False,
    ) -> float:
        lo, hi = -200.0, 5000.0
        for _ in range(100):
            mid = 0.5 * (lo + hi)
            if ceiling_moment(a, H_unit_h9, extra_dirty_jumps, mid, 0.0, credit_dual_as_persistent) <= 1.0:
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi)

    helper_profiles = [
        ("PR2920_endpoint_only_0_units", 0, []),
        ("PR2981_unit_cover_208_units", 208, []),
        ("PR2924_two_history_216_units", 216, []),
        ("Coarsened_11_helpers_197_units_11_cheap_1_7_1", 197, [(22, 1), (11, 7)]),
        ("Coarsened_26_helpers_182_units_26_jump_1_8", 182, [(26, 1), (26, 8)]),
        ("Coarsened_179_helpers_29_units_179_jump_1_8", 29, [(179, 1), (179, 8)]),
        ("PR2953_joint_endpoint_423_units", 423, []),
    ]

    dual_regimes = [
        ("idealized_symmetric_dual_0_extra", 0.0, 0.0),
        ("dual_private_zero_erasure_only_8_H7_per_dual", 0.0, 8.0),
        ("fused_5_boundaries_260_H1_plus_8_H7_per_dual", 260.0, 8.0),
        ("full_physical_corrected_dual_416_H1_plus_8_H7_per_dual", 416.0, 8.0),
    ]

    grid_results = {}
    for prof_name, u_cnt, extra_jumps in helper_profiles:
        dirty_mass = 9 * u_cnt + sum(c * r for c, r in extra_jumps)
        prof_entry = {
            "unit_helper_count": u_cnt,
            "extra_dirty_jumps": [list(pair) for pair in extra_jumps],
            "total_dirty_rank_units_per_call": dirty_mass,
            "idle_rank_mass_per_call_before_dual": 4344 - dirty_mass,
            "max_tolerable_uncredited_dual_H1_per_dual_call": {
                exp_name: round(max_tolerable_dual_h1(exp_val, u_cnt, extra_jumps, False), 6)
                for exp_name, exp_val in exponents.items()
            },
            "max_tolerable_persistent_credited_dual_H1_per_dual_call": {
                exp_name: round(max_tolerable_dual_h1(exp_val, u_cnt, extra_jumps, True), 6)
                for exp_name, exp_val in exponents.items()
            },
            "regimes": {},
        }
        for reg_name, d_h1, d_h7 in dual_regimes:
            dual_mass = d_h1 + 7.0 * d_h7
            moments_uncredited = {
                exp_name: round(ceiling_moment(exp_val, u_cnt, extra_jumps, d_h1, d_h7, False), 9)
                for exp_name, exp_val in exponents.items()
            }
            moments_credited = {
                exp_name: round(ceiling_moment(exp_val, u_cnt, extra_jumps, d_h1, d_h7, True), 9)
                for exp_name, exp_val in exponents.items()
            }
            prof_entry["regimes"][reg_name] = {
                "dual_extra_H1_per_dual": d_h1,
                "dual_extra_H7_per_dual": d_h7,
                "dual_extra_rank_units_per_dual": dual_mass,
                "moments_mode_A_uncredited_nonpersistent": moments_uncredited,
                "moments_mode_B_favorable_persistent_credit": moments_credited,
                "mode_A_passes_at_b_selected": moments_uncredited["b_selected_prompt"] <= 1.0,
                "mode_B_passes_at_b_selected": moments_credited["b_selected_prompt"] <= 1.0,
            }
        grid_results[prof_name] = prof_entry

    return {
        "exponents": exponents,
        "consumer_parameters": {
            "m": 73,
            "families": 832,
            "stages": 9,
            "w_per_call": "832/9",
            "centre_per_call": 56,
            "total_paid_mass_per_call": 6712,
            "base_local_mass_per_call": 2368,
            "base_idle_mass_per_call": 4344,
            "max_idle_rank_R": 51,
        },
        "frontier_grid": grid_results,
    }


def build_result_payload() -> dict:
    data = load_all_data()
    part1 = analyze_pillar1_pooled_2309(data)
    part2 = analyze_pillar2_and_pillar3(data)
    part3 = analyze_pillar4_full_physical_consumer_bill(data["selected"])

    pr2981_grid = part3["frontier_grid"]["PR2981_unit_cover_208_units"]

    summary = {
        "pooled_compatibility_edges": part1["total_compatibility_edges"],
        "pooled_components_missing_pairs": part1["components_missing_count"],
        "pooled_one_hop_missing_pairs": part1["one_hop_equal_frame_missing_count"],
        "pooled_unreachable_pair_0based": "(71,102)",
        "pooled_unreachable_pair_1based": "(72,103)",
        "pooled_unreachable_coefficient": part1["unreachable_coefficient"],
        "x102_dim1_reader_edges": len(part1["x102_readers_by_dim"]["1"]),
        "x102_forward_cone_dim5_edges": part1["x102_forward_dim5_size"],
        "x102_forward_cone_dim8_edges": part1["x102_forward_reached_edge_counts_by_dim"]["8"],
        "y71_dim5_writer_edges": len(part1["y71_writers_by_dim"]["5"]),
        "y71_dim8_writer_edges": part1["y71_dim8_writer_count"],
        "y71_backward_cone_dim7_edges": part1["y71_backward_cone_after_dim7_size"],
        "y71_backward_cone_after_dim6_edges": part1["y71_backward_cone_after_dim6_size"],
        "pooled_cone_intersection_edges": part1["forward_dim5_intersect_backward_dim6_8_size"],
        "required_support_pairs": 4992,
        "pr2981_components_missing": part2["matching_propagation_summary"]["PR2981_baseline"]["PR2996_components_missing"],
        "pr2981_one_hop_missing": part2["matching_propagation_summary"]["PR2981_baseline"]["one_hop_equal_frame_missing"],
        "pr2981_subspace_memory_missing": part2["matching_propagation_summary"]["PR2981_baseline"]["one_step_subspace_memory_missing"],
        "pr2981_zero_relay_helpers": part2["matching_propagation_summary"]["PR2981_baseline"]["zero_intermediate_relay_helper_count"],
        "pr3013_components_missing": part2["matching_propagation_summary"]["PR3013_rematched"]["PR2996_components_missing"],
        "pr3013_one_hop_missing": part2["matching_propagation_summary"]["PR3013_rematched"]["one_hop_equal_frame_missing"],
        "pr3013_subspace_memory_missing": part2["matching_propagation_summary"]["PR3013_rematched"]["one_step_subspace_memory_missing"],
        "pr3013_zero_relay_helpers": part2["matching_propagation_summary"]["PR3013_rematched"]["zero_intermediate_relay_helper_count"],
        "pr3019_components_missing": part2["matching_propagation_summary"]["PR3019_witness_swap_91_189"]["PR2996_components_missing"],
        "pr3019_one_hop_missing": part2["matching_propagation_summary"]["PR3019_witness_swap_91_189"]["one_hop_equal_frame_missing"],
        "pr3019_subspace_memory_missing": part2["matching_propagation_summary"]["PR3019_witness_swap_91_189"]["one_step_subspace_memory_missing"],
        "pr3019_zero_relay_helpers": part2["matching_propagation_summary"]["PR3019_witness_swap_91_189"]["zero_intermediate_relay_helper_count"],
        "pr3124_cycle_a_components_missing": part2["matching_propagation_summary"]["PR3124_cycle_A_13_203_191_63"]["PR2996_components_missing"],
        "pr3124_cycle_a_one_hop_missing": part2["matching_propagation_summary"]["PR3124_cycle_A_13_203_191_63"]["one_hop_equal_frame_missing"],
        "pr3124_cycle_a_subspace_memory_missing": part2["matching_propagation_summary"]["PR3124_cycle_A_13_203_191_63"]["one_step_subspace_memory_missing"],
        "pr3124_cycle_a_zero_relay_helpers": part2["matching_propagation_summary"]["PR3124_cycle_A_13_203_191_63"]["zero_intermediate_relay_helper_count"],
        "pr3124_cycle_b_components_missing": part2["matching_propagation_summary"]["PR3124_cycle_B_39_154_139_134"]["PR2996_components_missing"],
        "pr3124_cycle_b_one_hop_missing": part2["matching_propagation_summary"]["PR3124_cycle_B_39_154_139_134"]["one_hop_equal_frame_missing"],
        "pr3124_cycle_b_subspace_memory_missing": part2["matching_propagation_summary"]["PR3124_cycle_B_39_154_139_134"]["one_step_subspace_memory_missing"],
        "pr3124_cycle_b_zero_relay_helpers": part2["matching_propagation_summary"]["PR3124_cycle_B_39_154_139_134"]["zero_intermediate_relay_helper_count"],
        "full_flags_per_helper": 9765,
        "pr3124_cycle_a_helper91_passing_flags": part2["PR3124_cycle_A_single_helper_census"]["91"]["passing_flag_count"],
        "pr3124_cycle_a_vertex13_passing_flags": part2["PR3124_cycle_A_single_helper_census"]["13"]["passing_flag_count"],
        "pr3124_cycle_a_vertex13_min_missing": part2["PR3124_cycle_A_single_helper_census"]["13"]["min_missing_pairs"],
        "pr3124_cycle_a_vertex203_passing_flags": part2["PR3124_cycle_A_single_helper_census"]["203"]["passing_flag_count"],
        "pr3124_cycle_a_vertex191_passing_flags": part2["PR3124_cycle_A_single_helper_census"]["191"]["passing_flag_count"],
        "pr3124_cycle_a_vertex63_passing_flags": part2["PR3124_cycle_A_single_helper_census"]["63"]["passing_flag_count"],
        "pr3124_cycle_a_vertex63_min_missing": part2["PR3124_cycle_A_single_helper_census"]["63"]["min_missing_pairs"],
        "pr3124_cycle_b_helper91_passing_flags": part2["PR3124_cycle_B_single_helper_census"]["91"]["passing_flag_count"],
        "pr3124_cycle_b_vertex39_passing_flags": part2["PR3124_cycle_B_single_helper_census"]["39"]["passing_flag_count"],
        "pr3124_cycle_b_vertex39_min_missing": part2["PR3124_cycle_B_single_helper_census"]["39"]["min_missing_pairs"],
        "pr3124_cycle_b_vertex154_passing_flags": part2["PR3124_cycle_B_single_helper_census"]["154"]["passing_flag_count"],
        "pr3124_cycle_b_vertex154_min_missing": part2["PR3124_cycle_B_single_helper_census"]["154"]["min_missing_pairs"],
        "pr3124_cycle_b_vertex139_passing_flags": part2["PR3124_cycle_B_single_helper_census"]["139"]["passing_flag_count"],
        "pr3124_cycle_b_vertex139_min_missing": part2["PR3124_cycle_B_single_helper_census"]["139"]["min_missing_pairs"],
        "pr3124_cycle_b_vertex134_passing_flags": part2["PR3124_cycle_B_single_helper_census"]["134"]["passing_flag_count"],
        "pr3124_cycle_b_vertex134_min_missing": part2["PR3124_cycle_B_single_helper_census"]["134"]["min_missing_pairs"],
        "helper13_ordered_neighbor_pairs": len(part2["helper_13_all_12_ordered_pairs_incompatible"]),
        "consumer_m": 73,
        "consumer_families": 832,
        "consumer_stages": 9,
        "consumer_paid_mass_per_call": 6712,
        "consumer_base_local_mass_per_call": 2368,
        "consumer_base_idle_mass_per_call": 4344,
        "consumer_max_idle_rank": 51,
    }

    negative_controls = {
        "nc1_pooled_components_vs_one_hop": {
            "pooled_components_missing": part1["components_missing_count"],
            "pooled_one_hop_missing": part1["one_hop_equal_frame_missing_count"],
            "unreachable_pair_0based": part1["one_hop_missing_pairs_0based"][0],
            "unreachable_pair_1based": part1["one_hop_missing_pairs_1based"][0],
            "unreachable_coefficient": part1["unreachable_coefficient"],
        },
        "nc2_pr3124_cycle_a_helper91_only_vs_moved_vertices": {
            "helper_91_passing_flags": part2["PR3124_cycle_A_single_helper_census"]["91"]["passing_flag_count"],
            "moved_vertex_13_passing_flags": part2["PR3124_cycle_A_single_helper_census"]["13"]["passing_flag_count"],
            "moved_vertex_13_min_missing": part2["PR3124_cycle_A_single_helper_census"]["13"]["min_missing_pairs"],
            "moved_vertex_63_passing_flags": part2["PR3124_cycle_A_single_helper_census"]["63"]["passing_flag_count"],
            "moved_vertex_63_min_missing": part2["PR3124_cycle_A_single_helper_census"]["63"]["min_missing_pairs"],
        },
        "nc3_pr3124_cycle_b_helper91_only_vs_moved_vertices": {
            "helper_91_passing_flags": part2["PR3124_cycle_B_single_helper_census"]["91"]["passing_flag_count"],
            "moved_vertex_39_min_missing": part2["PR3124_cycle_B_single_helper_census"]["39"]["min_missing_pairs"],
            "moved_vertex_154_min_missing": part2["PR3124_cycle_B_single_helper_census"]["154"]["min_missing_pairs"],
            "moved_vertex_139_min_missing": part2["PR3124_cycle_B_single_helper_census"]["139"]["min_missing_pairs"],
            "moved_vertex_134_min_missing": part2["PR3124_cycle_B_single_helper_census"]["134"]["min_missing_pairs"],
        },
        "nc4_subspace_memory_dropping_vs_tracking": {
            "pr3019_components_missing": part2["matching_propagation_summary"]["PR3019_witness_swap_91_189"]["PR2996_components_missing"],
            "pr3019_subspace_memory_missing": part2["matching_propagation_summary"]["PR3019_witness_swap_91_189"]["one_step_subspace_memory_missing"],
            "pr3124_cycle_a_components_missing": part2["matching_propagation_summary"]["PR3124_cycle_A_13_203_191_63"]["PR2996_components_missing"],
            "pr3124_cycle_a_subspace_memory_missing": part2["matching_propagation_summary"]["PR3124_cycle_A_13_203_191_63"]["one_step_subspace_memory_missing"],
        },
        "nc5_idealized_zero_dual_overhead_vs_physical_dual": {
            "idealized_zero_dual_moment_b_selected": pr2981_grid["regimes"]["idealized_symmetric_dual_0_extra"]["moments_mode_A_uncredited_nonpersistent"]["b_selected_prompt"],
            "fused_5_boundaries_mode_A_moment_b_selected": pr2981_grid["regimes"]["fused_5_boundaries_260_H1_plus_8_H7_per_dual"]["moments_mode_A_uncredited_nonpersistent"]["b_selected_prompt"],
            "fused_5_boundaries_mode_B_moment_b_selected": pr2981_grid["regimes"]["fused_5_boundaries_260_H1_plus_8_H7_per_dual"]["moments_mode_B_favorable_persistent_credit"]["b_selected_prompt"],
            "full_physical_dual_mode_A_moment_b_selected": pr2981_grid["regimes"]["full_physical_corrected_dual_416_H1_plus_8_H7_per_dual"]["moments_mode_A_uncredited_nonpersistent"]["b_selected_prompt"],
            "full_physical_dual_mode_B_moment_b_selected": pr2981_grid["regimes"]["full_physical_corrected_dual_416_H1_plus_8_H7_per_dual"]["moments_mode_B_favorable_persistent_credit"]["b_selected_prompt"],
        },
        "nc6_persistent_credit_vs_nonpersistent_dual_accounting": {
            "pr2981_max_dual_h1_mode_A_b_selected": pr2981_grid["max_tolerable_uncredited_dual_H1_per_dual_call"]["b_selected_prompt"],
            "pr2981_max_dual_h1_mode_B_b_selected": pr2981_grid["max_tolerable_persistent_credited_dual_H1_per_dual_call"]["b_selected_prompt"],
        },
    }

    return {
        "schema_version": 1,
        "package": "p104-pooled-onehop-and-physical-consumer-bill",
        "task_id": "p104-side-correction",
        "status": "PASS_P104_POOLED_ONEHOP_AND_PHYSICAL_CONSUMER_BILL",
        "no_new_kappa": True,
        "summary": summary,
        "negative_controls": negative_controls,
        "part1_pooled_2309_intralayer_transitivity_obstruction": part1,
        "part2_pr3124_cycle_and_single_helper_obstructions": part2,
        "part3_full_physical_consumer_bill_and_untangling_frontier": part3,
    }


def main() -> None:
    require(sys.argv[1:] in ([], ["--write"]), "usage: verify.py [--write]")
    payload = build_result_payload()
    result_path = HERE / "RESULT.json"
    rendered = json.dumps(payload, indent=2) + "\n"
    if "--write" in sys.argv:
        result_path.write_text(rendered, encoding="utf-8")
    else:
        require(result_path.is_file(), "RESULT.json missing")
        expected = read_json(result_path)
        require(
            json.dumps(payload, sort_keys=True) == json.dumps(expected, sort_keys=True),
            "RESULT.json does not match recomputed payload",
        )
    print(
        "PASS_P104_POOLED_ONEHOP_AND_PHYSICAL_CONSUMER_BILL",
        f"pooled_edges={payload['summary']['pooled_compatibility_edges']}",
        f"pooled_onehop_missing={payload['summary']['pooled_one_hop_missing_pairs']}",
        f"pr3124_v13_passing={payload['summary']['pr3124_cycle_a_vertex13_passing_flags']}",
        f"pr3124_v63_passing={payload['summary']['pr3124_cycle_a_vertex63_passing_flags']}",
        "no_new_kappa",
    )


if __name__ == "__main__":
    main()
