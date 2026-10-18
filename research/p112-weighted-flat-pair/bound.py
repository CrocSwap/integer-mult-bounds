"""Eight-endpoint P112 bounds, including the exceptional root-A7 branch."""

import hashlib
import json
from collections import Counter
from itertools import combinations, combinations_with_replacement, product

from vendor.geometry import canonical, dot, require
from vendor.mixed import ANCHOR, CAP, cliques, rational_rank, root_extensions

PROFILE = (4, 5, 5) + (6,) * 8
ALL = (1 << 120) - 1


def mixed_seven(vertices, adjacency, points):
    anchor = tuple(2 * x for x in ANCHOR)
    evaluations = tuple(
        (0, dot(p, anchor), *(dot(p, v) for v in vertices)) for p in points
    )
    ranks, bounds = Counter(), Counter()
    witness = None
    for chosen in cliques(adjacency, 6):
        rank = rational_rank((anchor, *(vertices[i] for i in chosen)))
        ranks[rank] += 1
        if rank != 7:
            continue
        costs = [
            8 - max(Counter(row[:2] + tuple(row[i + 2] for i in chosen)).values())
            for row in evaluations
        ]
        lower = sum(sorted(costs)[:80])
        bounds[lower] += 1
        if lower == 162 and witness is None:
            witness = {
                "indices": chosen,
                "spectrum": dict(sorted(Counter(costs).items())),
            }
    require(ranks == {4: 105, 5: 2520, 6: 5096, 7: 2016}, "six-clique rank census")
    require(bounds == {162: 784, 163: 112, 170: 784, 175: 336}, "mixed support census")
    require(witness is not None, "missing mixed minimum witness")
    return {
        "ranks": dict(sorted(ranks.items())),
        "bounds": dict(sorted(bounds.items())),
        "minimum": min(bounds),
        "witness": witness,
    }


def root_types(roots):
    level, steps = [()], []
    for rank in range(7):
        following = []
        for prefix in level:
            representatives, sizes = root_extensions(prefix, roots)
            steps.append({"rank": rank, "orbit_sizes": sizes})
            following.extend((*prefix, v) for v in representatives)
        level = following
    require(len(level) == 2, "root A7 branch count")
    spectra, costs = [], []
    for prefix in level:
        values = tuple(
            8 - max(Counter((0, *(dot(r, v) for v in prefix))).values()) for r in roots
        )
        costs.append(values)
        spectra.append(dict(sorted(Counter(values).items())))
    require(spectra == [{1: 8, 2: 56, 3: 56}, {0: 1, 2: 84, 4: 35}], "A7 spectra")
    require(sum(sorted(costs[0])[:80]) == 168, "ordinary A7 lower bound")
    require(sum(sorted(costs[1])[:80]) == 158, "arbitrary-cut losing control")
    return level, costs, steps


def frame_inventory(roots):
    require(len(roots) == 120, "frame root count")
    adjacency = tuple(
        sum(1 << j for j, s in enumerate(roots) if dot(r, s) == 0) for r in roots
    )
    stack, frames, visits = [((), ALL)], [], 0
    for _ in range(2_000_000):
        visits += 1
        if not stack:
            break
        chosen, candidates = stack.pop()
        if len(chosen) == 8:
            frames.append(chosen)
            continue
        for _ in range(120):
            if not candidates:
                break
            bit = candidates & -candidates
            candidates ^= bit
            i = bit.bit_length() - 1
            stack.append(((*chosen, i), candidates & adjacency[i]))
        require(len(stack) <= 961, "frame work-stack capacity")
    require(not stack and len(frames) == 2025, "complete orthogonal-frame census")
    require(len(set(frames)) == 2025, "duplicate orthogonal frame")
    return tuple(frames), visits


def reflection_permutations(roots, prefix, costs):
    indices = {r: i for i, r in enumerate(roots)}
    permutations = []
    for v in prefix:
        permutation = []
        for r in roots:
            pairing = dot(r, v)
            require(pairing % 4 == 0, "root reflection integrality")
            image = canonical(
                tuple(x - pairing // 4 * y for x, y in zip(r, v, strict=True))
            )
            require(image in indices, "root reflection leaves E8")
            permutation.append(indices[image])
        require(sorted(permutation) == list(range(120)), "reflection not bijective")
        require(
            all(costs[i] == costs[permutation[i]] for i in range(120)),
            "reflection changes endpoint equality costs",
        )
        permutations.append(tuple(permutation))
    require(len(permutations) == 7, "A7 generators")
    return tuple(permutations)


def frame_orbits(frames, permutations):
    require(len(frames) == 2025 and len(permutations) == 7, "frame-orbit inputs")
    frame_set = frozenset(frames)
    unseen, result = set(frames), []
    for _ in range(2025):
        if not unseen:
            break
        first = min(unseen)
        queue, seen = [first], {first}
        for index in range(2025):
            if index >= len(queue):
                break
            for permutation in permutations:
                image = tuple(sorted(permutation[i] for i in queue[index]))
                require(image in frame_set, "reflection changes frame")
                if image not in seen:
                    seen.add(image)
                    queue.append(image)
            require(len(queue) <= 2025, "frame orbit queue capacity")
        require(seen <= unseen, "overlapping frame orbits")
        unseen.difference_update(seen)
        result.append((first, len(seen)))
    require(
        not unseen
        and sorted(n for _, n in result) == [30, 105, 105, 105, 210, 210, 1260],
        "incomplete frame orbit partition",
    )
    return tuple(result)


def weight(mask, high, zero):
    return 2 * ((mask & ~zero).bit_count() + (mask & high).bit_count())


def selected_flats(labels, costs):
    require(len(labels) == len(set(labels)) == 120, "full label inventory")
    require(all(type(x) is int and 0 < x < 512 and x & 1 for x in labels), "odd labels")
    require(Counter(costs) == {0: 1, 2: 84, 4: 35}, "exceptional cost inventory")
    high = sum(1 << i for i, c in enumerate(costs) if c == 4)
    zero = sum(1 << i for i, c in enumerate(costs) if c == 0)
    kernels = tuple(
        ALL
        ^ sum(1 << i for i, label in enumerate(labels) if (label & x).bit_count() & 1)
        for x in range(512)
    )
    selected, histogram = set(), Counter()
    for pivots in combinations(range(9), 4):
        row_kernels = []
        for pivot in pivots:
            free = tuple(c for c in range(pivot) if c not in pivots)
            rows = tuple(
                (1 << pivot)
                | sum(((code >> i) & 1) << col for i, col in enumerate(free))
                for code in range(1 << len(free))
            )
            row_kernels.append(tuple(kernels[row] for row in rows))
        for chosen in product(*row_kernels):
            mask = ALL
            for row in chosen:
                mask &= row
            histogram[mask.bit_count()] += 1
            if weight(mask, high, zero) >= 40:
                selected.add(mask)
    require(
        sum(histogram.values()) == 3_309_747 and max(histogram) == 12,
        "five-flat enumeration or capacity",
    )
    require(len(selected) == 3248, "high-cost five-flat inventory")
    return tuple(sorted(selected)), high, zero, dict(sorted(histogram.items()))


def pair_bound(frame, selected, high, zero):
    frame_mask = sum(1 << i for i in frame)
    frame_cost = weight(frame_mask, high, zero)
    if frame_cost == 16:
        return {"frame_cost": 16, "upper_without_pairs": 144, "candidates": 0}
    threshold = 148 - frame_cost - 80  # Other five-flat <=48, rank-four support <=32.
    require(threshold in (40, 44, 48), "unexpected frame threshold")
    candidates = tuple(
        sorted(
            {
                m & ~frame_mask
                for m in selected
                if weight(m & ~frame_mask, high, zero) >= threshold
            }
        )
    )
    maximum, winner = -1, None
    for i, a in enumerate(candidates):
        for b in candidates[i:]:
            value = weight(a | b, high, zero)
            if value > maximum:
                maximum, winner = value, (a, b)
    require(
        winner is not None and frame_cost + maximum + 32 < 148,
        "weighted pair does not exclude loss 148",
    )
    return {
        "frame_cost": frame_cost,
        "threshold": threshold,
        "candidates": len(candidates),
        "candidate_costs": dict(
            sorted(Counter(weight(m, high, zero) for m in candidates).items())
        ),
        "pair_maximum": maximum,
        "pair_witness": winner,
        "high_case_loss_upper": frame_cost + maximum + 32,
        "low_case_loss_upper": 146,
    }


def exceptional_bound(roots, labels, prefix, costs):
    frames, visits = frame_inventory(roots)
    permutations = reflection_permutations(roots, prefix, costs)
    orbits = frame_orbits(frames, permutations)
    selected, high, zero, histogram = selected_flats(labels, costs)
    result = []
    for frame, size in orbits:
        result.append(
            {
                "representative": frame,
                "orbit_size": size,
                **pair_bound(frame, selected, high, zero),
            }
        )
    require(sum(costs) == 308, "exceptional total cost")
    return {
        "frames": len(frames),
        "frame_states": visits,
        "five_flat_histogram": histogram,
        "selected_flats": len(selected),
        "selected_masks_sha256": hashlib.sha256(
            json.dumps(selected, separators=(",", ":")).encode()
        ).hexdigest(),
        "frame_orbits": result,
        "excluded_loss_threshold": 148,
        "loss_upper": 146,
        "surviving_lower": 162,
    }


def original_survivors():
    distance = (0, 53, 78, 92, 100, 106, 109, 111, 112)
    rows = []
    for size in range(7, 12):
        for weights in combinations_with_replacement(range(2, 8), size):
            if sum(w - 2 for w in weights) >= 42:
                continue
            feasible = True
            for level in range(1, 8):
                prefix = weights[: size - 7 + level]
                total = sum(CAP[w] for w in prefix)
                target = sum(32 if w == 7 else CAP[w] for w in prefix)
                if (
                    (level == 1 and target < 53 and total < 73)
                    or (level == 2 and target < 78 and total < 82)
                    or (level >= 3 and total < distance[level])
                ):
                    feasible = False
                    break
            basis = weights[: size - 7]
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
                    for assignment in product(range(2), repeat=len(basis))
                )
            if feasible and not killed:
                rows.append(weights)
    require(len(rows) == 154 and PROFILE in rows, "original (7,4) residue")
    return rows


def application():
    original = original_survivors()
    require(sum(CAP[w] for w in PROFILE[:4]) == 52, "quotient basis support")
    return {
        "b": 7,
        "t": 4,
        "profile": PROFILE,
        "original_survivors": len(original),
        "small_support": 32,
        "quotient_cap": 52,
        "code_distance": 53,
        "edge_cap": 72,
        "endpoints": 8,
        "allowance": 160,
        "mixed_lower": 162,
        "ordinary_root_lower": 168,
        "exceptional_root_lower": 162,
        "margin": 2,
    }
