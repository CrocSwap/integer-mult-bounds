"""Weighted support unions for the two P112 root A7 branches.

Nick Petalas. Apache-2.0. Retained root reconstruction is in vendor/geometry.py.
"""

from collections import Counter
from itertools import combinations, combinations_with_replacement, product

from vendor import mixed
from vendor.geometry import SIMPLE, canonical, dot, require


def indices(mask, size):
    require(type(mask) is int and 0 <= mask < 1 << size, "invalid support mask")
    return tuple(i for i in range(size) if mask >> i & 1)


def cost_masks(costs):
    require(len(costs) == 120 and set(costs) == {0, 2, 4}, "A7 cost spectrum")
    return tuple(sum(1 << i for i, c in enumerate(costs) if c == k) for k in (2, 4))


def score(mask, masks):
    return 2 * (mask & masks[0]).bit_count() + 4 * (mask & masks[1]).bit_count()


def orthogonal_frames(roots):
    require(len(roots) == 120 and len(set(roots)) == 120, "root inventory")
    later = tuple(
        sum(1 << j for j in range(i + 1, 120) if not dot(r, roots[j]))
        for i, r in enumerate(roots)
    )
    stack, frames, nodes = [((), (1 << 120) - 1)], set(), 0
    for _ in range(30_000):
        if not stack:
            break
        chosen, candidates = stack.pop()
        nodes += 1
        if len(chosen) == 8:
            frames.add(sum(1 << i for i in chosen))
            continue
        for _ in range(120):
            if not candidates:
                break
            bit = candidates & -candidates
            candidates ^= bit
            i = bit.bit_length() - 1
            following = candidates & later[i]
            if following.bit_count() >= 7 - len(chosen):
                stack.append(((*chosen, i), following))
        require(len(stack) <= 1000 and len(frames) <= 2025, "frame work capacity")
    require(not stack and len(frames) == 2025, "incomplete frame census")
    return frames, nodes


def reflection_permutations(roots, coordinates, normals):
    require(len(normals) <= 120, "reflection inventory capacity")
    index, permutations = {r: i for i, r in enumerate(roots)}, []
    labels = tuple(
        1 | sum((int(x) & 1) << (j + 1) for j, x in enumerate(c)) for c in coordinates
    )
    for normal in sorted(normals):
        ncoords = coordinates[index[normal]]
        columns = tuple(
            tuple(
                int(i == j) - dot(SIMPLE[j], normal) // 4 * int(ncoords[i])
                for i in range(8)
            )
            for j in range(8)
        )
        permutation = tuple(
            index[
                canonical(
                    tuple(
                        x - dot(r, normal) // 4 * y
                        for x, y in zip(r, normal, strict=True)
                    )
                )
            ]
            for r in roots
        )
        require(len(set(permutation)) == 120, "reflection is not a root permutation")
        for i, label in enumerate(labels):
            image = 1
            for col in range(8):
                if label >> (col + 1) & 1:
                    image ^= sum((x & 1) << (j + 1) for j, x in enumerate(columns[col]))
            require(image == labels[permutation[i]], "reflection changes binary ranks")
        permutations.append(permutation)
    return tuple(permutations)


def frame_orbits(frames, permutations, costs):
    require(len(frames) == 2025 and len(permutations) <= 120, "frame orbit domain")
    require(
        all(costs[i] == costs[p[i]] for p in permutations for i in range(120)),
        "frame generator changes vertex costs",
    )
    unseen, representatives, sizes = set(frames), [], []
    for _ in range(2025):
        if not unseen:
            break
        first = min(unseen)
        queue, seen = [first], {first}
        for pos in range(2025):
            if pos == len(queue):
                break
            members = indices(queue[pos], 120)
            for permutation in permutations:
                moved = sum(1 << permutation[i] for i in members)
                require(moved in frames, "orbit leaves orthogonal-frame inventory")
                if moved not in seen:
                    seen.add(moved)
                    queue.append(moved)
            require(len(queue) <= 2025, "frame orbit capacity")
        require(seen <= unseen, "frame orbits overlap")
        unseen.difference_update(seen)
        representatives.append(first)
        sizes.append(len(seen))
    require(not unseen and sizes == [30, 420, 1260, 105, 210], "frame orbit coverage")
    return tuple(representatives), sizes


def flat_masks(labels, dimension):
    """All binary flats via unique reverse-echelon annihilators."""
    require(
        len(labels) == len(set(labels)) == 120 and dimension in (4, 5),
        "full-root flat domain",
    )
    require(
        all(type(x) is int and 0 < x < 512 and x & 1 for x in labels),
        "invalid full-root labels",
    )
    all_lines = (1 << 120) - 1
    kernels = tuple(
        all_lines
        ^ sum(1 << i for i, label in enumerate(labels) if (label & x).bit_count() & 1)
        for x in range(512)
    )
    for pivots in combinations(range(9), 9 - dimension):
        choices = []
        for pivot in pivots:
            free = tuple(i for i in range(pivot) if i not in pivots)
            choices.append(
                tuple(
                    kernels[
                        (1 << pivot)
                        | sum(((v >> j) & 1) << i for j, i in enumerate(free))
                    ]
                    for v in range(1 << len(free))
                )
            )
        for rows in product(*choices):
            mask = all_lines
            for row in rows:
                mask &= row
            yield mask


def flat_inventory(labels, frames, masks):
    require(len(frames) == 5 and len(masks) == 2, "flat inventory domain")
    candidates = {d: {j: set() for j in (1, 2, 3)} for d in (4, 5)}
    maxima, receipts = {}, []
    for dimension in (4, 5):
        histogram, best = Counter(), [0] * 5
        for mask in flat_masks(labels, dimension):
            histogram[mask.bit_count()] += 1
            for j, frame in enumerate(frames):
                live = mask & ~frame
                value = score(live, masks)
                best[j] = max(best[j], value)
                threshold = (
                    {4: 28, 5: 44}[dimension] if j == 1 else {4: 32, 5: 48}[dimension]
                )
                if j in (1, 2, 3) and value >= threshold:
                    candidates[dimension][j].add(live)
                    require(
                        len(candidates[dimension][j]) <= 150, "flat candidate capacity"
                    )
        require(sum(histogram.values()) == 3_309_747, "incomplete flat census")
        require(max(histogram) == {4: 8, 5: 12}[dimension], "support capacity changed")
        require(
            best == ({4: [28, 32, 32, 32, 32], 5: [40, 48, 48, 48, 48]}[dimension]),
            "weighted flat maxima changed",
        )
        maxima[dimension] = best
        receipts.append(
            {
                "dimension": dimension,
                "subspaces": sum(histogram.values()),
                "support_histogram": dict(sorted(histogram.items())),
                "weighted_maxima": best,
            }
        )
    return candidates, maxima, receipts


def union_maximum(fours, fives, masks):
    require(
        1 <= len(fours) <= 150 and 1 <= len(fives) <= 150, "union inventory capacity"
    )
    best, count, witness = -1, 0, None
    for a in sorted(fours):
        for b, c in combinations_with_replacement(sorted(fives), 2):
            count += 1
            value = score(a | b | c, masks)
            if value > best:
                best, witness = value, (a, b, c)
    require(witness is not None and count <= 1_698_750, "union work capacity")
    return {
        "triples": count,
        "maximum_union_score": best,
        "witness": [indices(x, 120) for x in witness],
    }


def union_certificate(frames, costs, candidates, maxima):
    masks, rows = cost_masks(costs), []
    for j, frame in enumerate(frames):
        total = sum(c for i, c in enumerate(costs) if not frame >> i & 1)
        independent_cap = maxima[4][j] + 2 * maxima[5][j]
        row = {
            "frame": indices(frame, 120),
            "live_cost": total,
            "independent_flat_sum_cap": independent_cap,
        }
        if j in (1, 2, 3):
            fours, fives = candidates[4][j], candidates[5][j]
            target = total - 160
            high = union_maximum(fours, fives, masks)
            require(
                high["maximum_union_score"] < target, "endpoint allowance can be met"
            )
            # Every score is even. A discarded triple cannot reach target.
            cap = max(target - 2, high["maximum_union_score"])
            row.update(
                {
                    "candidate_counts": [len(fours), len(fives)],
                    "failure_threshold": target,
                    "high_score_triples": high,
                    "union_cap": cap,
                    "outside_lower": total - cap,
                }
            )
        else:
            row.update(
                {"union_cap": independent_cap, "outside_lower": total - independent_cap}
            )
        require(row["outside_lower"] > 160, "all-root support contradiction failed")
        rows.append(row)
    return rows


def root_receipt(roots, coordinates):
    level, steps = [()], []
    for rank in range(7):
        following = []
        for prefix in level:
            representatives, sizes = mixed.root_extensions(prefix, roots)
            steps.append({"rank": rank, "orbit_sizes": sizes})
            following.extend((*prefix, r) for r in representatives)
        level = following
    require(len(level) == 2, "root A7 branches changed")
    spectra = [
        Counter(
            8 - max(Counter([0] + [dot(r, v) for v in star]).values()) for r in roots
        )
        for star in level
    ]
    require(spectra == [{1: 8, 2: 56, 3: 56}, {0: 1, 2: 84, 4: 35}], "A7 spectra")
    first_lower = sum(sorted(k for k, n in spectra[0].items() for _ in range(n))[:80])
    costs = tuple(
        8 - max(Counter([0] + [dot(r, v) for v in level[1]]).values()) for r in roots
    )
    vertices = ((0,) * 8, *level[1])
    normals = {
        canonical(tuple(a - b for a, b in zip(x, y, strict=True)))
        for x, y in combinations(vertices, 2)
    }
    normals.update(r for r in roots if all(dot(r, v) == 0 for v in level[1]))
    frames, nodes = orthogonal_frames(roots)
    permutations = reflection_permutations(roots, coordinates, normals)
    representatives, sizes = frame_orbits(frames, permutations, costs)
    labels = tuple(
        1 | sum((int(x) & 1) << (j + 1) for j, x in enumerate(c)) for c in coordinates
    )
    candidates, maxima, flats = flat_inventory(
        labels, representatives, cost_masks(costs)
    )
    rows = union_certificate(representatives, costs, candidates, maxima)
    require(first_lower == 168, "first root branch bound changed")
    return (
        {
            "star_steps": steps,
            "stars": level,
            "spectra": spectra,
            "first_branch_after_40_cuts": first_lower,
            "frames": len(frames),
            "frame_search_nodes": nodes,
            "frame_orbit_sizes": sizes,
            "rank_preserving_generators": len(permutations),
            "flat_censuses": flats,
            "frame_bounds": rows,
            "minimum_lower": min(row["outside_lower"] for row in rows),
        },
        candidates,
        costs,
    )
