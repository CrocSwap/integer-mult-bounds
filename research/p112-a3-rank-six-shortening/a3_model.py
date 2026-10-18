"""A3 equality obstruction with binary-rank-six endpoints, over fixed E8 labels.

Root-star orbit method follows Nick Petalas/PR3175 and PR3211.
The extremal-frame binary-closure test is new here. Apache-2.0.
"""

from collections import Counter
from itertools import combinations, combinations_with_replacement, product

from a3_geometry import SIMPLE, canonical, dot, require

CAP = (0, 1, 2, 4, 8, 12, 20, 36)
PROFILE = (2,) + (6,) * 5 + (7,) * 3


def star_orbit(prefix, roots):
    """Exhaust a subgroup orbit under reflections fixing the prefix pointwise."""
    require(len(prefix) <= 2 and len(roots) == 120, "star input capacity")
    signed = {v for r in roots for v in (r, tuple(-x for x in r))}
    require(all(r in signed for r in prefix), "invalid star root")
    require(all(dot(a, b) == 4 for a, b in combinations(prefix, 2)), "not a star")
    candidates = {r for r in signed if all(dot(r, a) == 4 for a in prefix)}
    normals = [r for r in roots if all(dot(r, a) == 0 for a in prefix)]
    require(candidates, "no star extension")
    first = min(candidates)
    queue, seen = [first], {first}
    for index in range(240):
        if index >= len(queue):
            break
        for normal in normals:
            pairing = dot(queue[index], normal)
            require(pairing % 4 == 0, "nonintegral reflection")
            image = tuple(
                x - pairing // 4 * y for x, y in zip(queue[index], normal, strict=True)
            )
            require(image in candidates, "reflection leaves candidate inventory")
            if image not in seen:
                queue.append(image)
                seen.add(image)
    require(seen == candidates and len(queue) <= 240, "incomplete extension orbit")
    return first, {"normal_lines": len(normals), "orbit_size": len(seen)}


def star(roots):
    prefix, steps = (), []
    for expected in (240, 56, 27):
        vertex, step = star_orbit(prefix, roots)
        require(step["orbit_size"] == expected, "A3 orbit changed")
        prefix += (vertex,)
        steps.append(step)
    values = tuple((0,) + tuple(dot(r, a) for a in prefix) for r in roots)
    costs = tuple(4 - max(Counter(v).values()) for v in values)
    require(Counter(costs) == {0: 20, 1: 64, 2: 36}, "A3 spectrum changed")
    return prefix, values, costs, steps


def orthogonal_frames(roots):
    """Enumerate increasing eight-cliques, with bounded iterative DFS."""
    require(len(roots) == len(set(roots)) == 120, "root inventory changed")
    adjacency = tuple(
        sum(1 << j for j in range(i + 1, 120) if dot(r, roots[j]) == 0)
        for i, r in enumerate(roots)
    )
    stack, frames = [((), (1 << 120) - 1)], []
    for visited in range(1_000_000):
        if not stack:
            require(len(frames) == 2025, "incomplete orthogonal-frame inventory")
            return frames, visited
        prefix, candidates = stack.pop()
        if len(prefix) == 8:
            frames.append(prefix)
            require(len(frames) <= 2025, "frame capacity exceeded")
            continue
        for j in range(120):
            if candidates >> j & 1:
                stack.append((prefix + (j,), candidates & adjacency[j]))
        require(len(stack) <= 961, "DFS stack capacity exceeded")
    raise ValueError("orthogonal-frame traversal budget exhausted")


def binary_span(labels):
    """Explicit closure, at most 512 elements. Independent of elimination."""
    require(len(labels) <= 120 and all(0 < x < 512 for x in labels), "label range")
    result = {0}
    for x in labels:
        result |= {y ^ x for y in result}
    require(len(result) <= 512, "binary closure capacity")
    return result


def extremal_frame(frame, values, costs, labels):
    require(len(frame) == len(set(frame)) == 8, "invalid frame")
    require(all(type(i) is int and 0 <= i < 120 for i in frame), "frame index")
    require(len(values) == len(costs) == len(labels) == 120, "coordinate inventory")
    require(sum(costs[i] for i in frame) == 12, "not an extremal frame")
    require(Counter(costs[i] for i in frame) == {0: 2, 2: 6}, "frame cost shape")
    live = tuple(i for i in range(120) if i not in frame)
    mandatory = [[] for _ in range(4)]
    for i in live:
        if costs[i] != 1:
            continue
        common, count = Counter(values[i]).most_common(1)[0]
        require(count == 3, "singleton coordinate shape")
        for endpoint in range(4):
            if values[i][endpoint] != common:
                mandatory[endpoint].append(i)
    rows = []
    for support in mandatory:
        closure = binary_span([labels[i] for i in support])
        live_closure = [i for i in live if labels[i] in closure]
        require(len(support) == 16 and len(closure) == 64, "mandatory rank-six span")
        require(live_closure == support, "binary flat has additional live coordinates")
        rows.append(
            {
                "mandatory_mask": format(sum(1 << i for i in support), "030x"),
                "span_size": len(closure),
                "live_closure_mask": format(sum(1 << i for i in live_closure), "030x"),
            }
        )
    return {"frame": frame, "endpoints": rows}


def frame_receipt(roots, labels):
    require(len(labels) == len(set(labels)) == 120, "full label inventory")
    prefix, values, costs, steps = star(roots)
    frames, visited = orthogonal_frames(roots)
    histogram = Counter(sum(costs[i] for i in f) for f in frames)
    require(histogram == {8: 1005, 10: 960, 12: 60}, "frame cost histogram")
    extreme = [
        extremal_frame(f, values, costs, labels)
        for f in frames
        if sum(costs[i] for i in f) == 12
    ]
    require(len(extreme) == 60, "extremal coverage")
    return {
        "star": prefix,
        "extension_orbits": steps,
        "spectrum": {0: 20, 1: 64, 2: 36},
        "full_cost": sum(costs),
        "frames": len(frames),
        "visited_nodes": visited,
        "puncture_cost_histogram": dict(sorted(histogram.items())),
        "extremal_frames": extreme,
        "support_only_lower_at_21": 82,
        "support_only_lower_at_22": 80,
        "rank_six_endpoint_obstruction": True,
    }


def label_action_receipt(roots, labels):
    """Bind Weyl transport to an invertible map on the full nine-bit labels."""
    by_root = dict(zip(roots, labels, strict=True))
    checks = 0
    for i, normal in enumerate(SIMPLE):
        cartan = [dot(simple, normal) // 4 for simple in SIMPLE]
        require(all(dot(simple, normal) % 4 == 0 for simple in SIMPLE), "Cartan parity")
        for r, label in zip(roots, labels, strict=True):
            reflected = canonical(
                tuple(
                    x - dot(r, normal) // 4 * y for x, y in zip(r, normal, strict=True)
                )
            )
            parity = sum(c * ((label >> (j + 1)) & 1) for j, c in enumerate(cartan)) % 2
            image = label ^ (parity << (i + 1))
            require(by_root[reflected] == image, "Weyl binary-label action changed")
            back = sum(c * ((image >> (j + 1)) & 1) for j, c in enumerate(cartan)) % 2
            require(image ^ (back << (i + 1)) == label, "label action not involutive")
            checks += 1
    require(checks == 960, "incomplete label action")
    return {
        "simple_reflections": 8,
        "root_label_comparisons": checks,
        "maps_are_linear_involutions": True,
    }


def original_survivors():
    """Own b=6,t=3 transcription, compared with the retained TWOSIDE table."""
    rows = []
    distance = (0, 53, 78, 92, 100, 106, 109)
    for size in range(6, 10):
        for weights in combinations_with_replacement(range(2, 8), size):
            if sum(w - 2 for w in weights) >= 36:
                continue
            feasible = True
            for level in range(1, 7):
                prefix = weights[: size - 6 + level]
                global_cap = sum(CAP[w] for w in prefix)
                target = sum(32 if w == 7 else CAP[w] for w in prefix)
                if (
                    (level == 1 and target < 53 and global_cap < 73)
                    or (level == 2 and target < 78 and global_cap < 82)
                    or (level >= 3 and global_cap < distance[level])
                ):
                    feasible = False
                    break
            if not feasible:
                continue
            basis = weights[: size - 6]
            killed = False
            if sum(CAP[w] for w in basis) < 53:
                killed = sum(basis) <= 7 or any(
                    all(
                        sum(
                            w
                            for w, g in zip(basis, assignment, strict=True)
                            if g == group
                        )
                        <= 6
                        for group in (0, 1)
                    )
                    for assignment in product((0, 1), repeat=len(basis))
                )
            if not killed:
                rows.append(weights)
    require(len(rows) == 17 and PROFILE in rows, "historical survivor inventory")
    return rows


def application(weights=PROFILE, code_dimension=6, deleted=3):
    require(weights == PROFILE, "unsupported historical profile")
    require(type(deleted) is int and 0 <= deleted <= 3, "deletion count")
    require(type(code_dimension) is int and 0 <= code_dimension <= 8, "code dimension")
    retained = weights[: len(weights) - deleted] if deleted else weights
    require(retained == (2,) + (6,) * 5, "wrong retained profile")
    require(code_dimension - deleted >= 3, "three code dimensions do not survive")
    small = sum(CAP[w] for w in retained[:-4])
    require(small == 22 and max(retained[-4:]) <= 6, "shortening hypotheses fail")
    return {
        "weights": weights,
        "deleted_unrestricted_pieces": deleted,
        "retained_weights": retained,
        "retained_code_dimension_lower": code_dimension - deleted,
        "small_support_cap": small,
        "endpoint_binary_rank_cap": 6,
        "endpoint_support_sum_cap": 80,
        "support_only_lower": 80,
        "newly_excluded_profiles": 1,
    }
