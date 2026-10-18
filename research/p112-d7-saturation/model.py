"""Exact finite ingredients for the P112 D7 saturation obstruction.

Root geometry follows Nick Petalas's PR3164/3175.
TWOSIDE filters follow DreamingOfClouds's PR3154 and PR3174's transcription.
New D7 frame and saturated-support packing checks: Nick Petalas. Apache-2.0.
"""

from itertools import combinations, combinations_with_replacement, product

from vendor.geometry import SIMPLE, canonical, dot, require

CAP = {2: 2, 3: 4, 4: 8, 5: 12, 6: 20, 7: 36}
PROFILE = (2, 4) + (5,) * 9


def bits(mask, size):
    require(type(mask) is int and 0 <= mask < (1 << size), "invalid bit mask")
    return tuple(i for i in range(size) if mask >> i & 1)


def binary_rank(rows):
    require(len(rows) <= 120 and all(0 <= x < 512 for x in rows), "rank input")
    pivots = [0] * 9
    for row in rows:
        for pivot in range(8, -1, -1):
            if row >> pivot & 1:
                if pivots[pivot]:
                    row ^= pivots[pivot]
                else:
                    pivots[pivot] = row
                    break
    return sum(bool(x) for x in pivots)


def reflect(root, normal):
    pairing = dot(root, normal)
    require(dot(normal, normal) == 8 and pairing % 4 == 0, "reflection input")
    return tuple(x - pairing // 4 * y for x, y in zip(root, normal, strict=True))


def orbit(seed, permutations, allowed):
    require(seed in allowed and len(allowed) <= 240, "orbit domain")
    seen, queue = {seed}, [seed]
    for index in range(240):
        if index == len(queue):
            break
        for permutation in permutations:
            moved = sum(1 << permutation[i] for i in bits(queue[index], 120))
            require(moved in allowed, "reflection leaves frame domain")
            if moved not in seen:
                seen.add(moved)
                queue.append(moved)
        require(len(queue) <= 240, "frame orbit capacity")
    return seen


def orthogonal_frames(roots, support):
    require(len(roots) == 120 and support.bit_count() == 78, "D7 root domain")
    later = tuple(
        sum(1 << j for j in range(i + 1, 120) if dot(r, roots[j]) == 0)
        for i, r in enumerate(roots)
    )
    stack, frames, nodes = [((), support)], set(), 0
    for _ in range(100_000):
        if not stack:
            break
        prefix, candidates = stack.pop()
        nodes += 1
        if len(prefix) == 8:
            frames.add(sum(1 << i for i in prefix))
        elif candidates.bit_count() >= 8 - len(prefix):
            stack.extend(
                ((*prefix, i), candidates & later[i]) for i in bits(candidates, 120)
            )
        require(len(stack) <= 10_000 and len(frames) <= 240, "frame capacity")
    require(not stack and len(frames) == 240, "incomplete orthogonal-frame census")
    return frames, nodes


def frame_receipt(roots, coordinates):
    normal = (0, 0, 0, 0, 0, 0, 0, 1)
    require([dot(s, normal) for s in SIMPLE] == [1] + [0] * 7, "D7 chamber ray")
    support = sum(1 << i for i, r in enumerate(roots) if dot(r, normal))
    frames, nodes = orthogonal_frames(roots, support)
    index = {r: i for i, r in enumerate(roots)}
    labels = tuple(
        1 | sum((int(x) & 1) << (j + 1) for j, x in enumerate(c)) for c in coordinates
    )
    require(len(set(labels)) == 120, "full root labels")
    permutations = []
    for n in roots:
        if dot(n, normal):
            continue
        permutation = tuple(index[canonical(reflect(r, n))] for r in roots)
        require(len(set(permutation)) == 120, "reflection is not a permutation")
        # The integral Cartan action is linear on simple coordinates modulo two.
        ncoords = coordinates[index[n]]
        columns = tuple(
            tuple(
                int(i == j) - dot(SIMPLE[j], n) // 4 * int(ncoords[i]) for i in range(8)
            )
            for j in range(8)
        )
        for i, c in enumerate(coordinates):
            moved = tuple(
                sum(columns[j][k] * int(c[j]) for j in range(8)) & 1 for k in range(8)
            )
            require(
                labels[permutation[i]]
                == 1 | sum(x << (j + 1) for j, x in enumerate(moved)),
                "binary label covariance",
            )
        permutations.append(permutation)
    require(len(permutations) == 42, "D7 reflection inventory")
    seed = min(frames)
    require(orbit(seed, permutations, frames) == frames, "D7 frame orbit incomplete")
    return (
        support,
        seed,
        labels,
        {
            "frames": len(frames),
            "search_nodes": nodes,
            "reflections": 42,
            "orbit_sizes": [240],
            "representative_frame": bits(seed, 120),
        },
    )


def saturated_flats(labels, d7_support):
    require(
        len(set(labels)) == 120 and all(0 < x < 512 and x & 1 for x in labels),
        "invalid full120 labels",
    )
    all_lines = (1 << 120) - 1
    kernels = tuple(
        sum(
            1 << i
            for i, label in enumerate(labels)
            if (label & row).bit_count() % 2 == 0
        )
        for row in range(512)
    )
    histogram, retained = [0] * 121, set()
    for pivots in combinations(range(9), 4):
        choices = []
        for pivot in pivots:
            free = tuple(c for c in range(pivot) if c not in pivots)
            choices.append(
                tuple(
                    kernels[
                        (1 << pivot)
                        | sum(((code >> i) & 1) << c for i, c in enumerate(free))
                    ]
                    for code in range(1 << len(free))
                )
            )
        for chosen in product(*choices):
            mask = all_lines
            for row in chosen:
                mask &= row
            count = mask.bit_count()
            histogram[count] += 1
            if count == 12 and mask & d7_support == mask:
                retained.add(mask)
            require(len(retained) <= 5040, "saturated flat capacity")
    require(
        sum(histogram) == 3_309_747
        and max(i for i, n in enumerate(histogram) if n) == 12,
        "full120 five-flat census changed",
    )
    require(len(retained) == 5040, "D7 saturated-flat inventory changed")
    return tuple(sorted(retained)), {
        "subspaces": sum(histogram),
        "maximum": 12,
        "histogram": {i: n for i, n in enumerate(histogram) if n},
        "saturated_D7_intersections": len(retained),
    }


def packing_receipt(candidates):
    require(
        1 <= len(candidates) <= 756 and len(set(candidates)) == len(candidates),
        "packing inventory size",
    )
    require(
        all(
            type(x) is int and 0 <= x < 1 << 120 and x.bit_count() == 12
            for x in candidates
        ),
        "packing supports must have twelve coordinates",
    )
    size = len(candidates)
    later = tuple(
        sum(1 << j for j in range(i + 1, size) if not mask & candidates[j])
        for i, mask in enumerate(candidates)
    )
    triangles, witness = 0, None
    for i in range(size):
        for j in bits(later[i], size):
            common = later[i] & later[j]
            for k in bits(common, size):
                require(not later[k] & common, "four disjoint saturated supports exist")
                triangles += 1
                if witness is None:
                    witness = (i, j, k)
    require(witness is not None, "no sharp three-support witness")
    return {
        "vertices": size,
        "edges": sum(x.bit_count() for x in later),
        "triangles": triangles,
        "four_cliques": 0,
        "maximum_disjoint": 3,
        "witness": [bits(candidates[i], 120) for i in witness],
    }


def survives(weights):
    require(
        5 <= len(weights) <= 11
        and tuple(sorted(weights)) == weights
        and all(type(w) is int and 2 <= w <= 7 for w in weights),
        "profile domain",
    )
    if sum(w - 2 for w in weights) >= 30:
        return False
    for level in range(1, 6):
        prefix = weights[: len(weights) - 5 + level]
        total = sum(CAP[w] for w in prefix)
        target = sum(32 if w == 7 else CAP[w] for w in prefix)
        if level == 1 and not (target >= 53 or total >= 73):
            return False
        if level == 2 and not (target >= 78 or total >= 82):
            return False
        if level >= 3 and total < (0, 53, 78, 92, 100, 106)[level]:
            return False
    basis = weights[: len(weights) - 5]
    if sum(CAP[w] for w in basis) >= 53:
        return True
    if sum(basis) <= 7:
        return False
    return not any(
        all(
            sum(w for w, side in zip(basis, assignment, strict=True) if side == group)
            <= 6
            for group in (0, 1)
        )
        for assignment in product((0, 1), repeat=len(basis))
    )


def application_receipt():
    survivors = [
        w
        for n in range(5, 12)
        for w in combinations_with_replacement(range(2, 8), n)
        if survives(w)
    ]
    require(len(survivors) == 77 and PROFILE in survivors, "original TWOSIDE binding")
    small = sum(CAP[w] for w in PROFILE[:4])
    endpoint = max(CAP[w] for w in PROFILE[4:])
    return {
        "weights": PROFILE,
        "cell": [5, 6],
        "deficit": 30 - sum(w - 2 for w in PROFILE),
        "original_survivors": len(survivors),
        **boundary_budget(small, endpoint),
        "forced_partition": [CAP[w] for w in PROFILE[:5]] + [endpoint] * 2,
        "required_disjoint_saturated_five_flat_supports": 5,
        "maximum_disjoint_saturated_five_flat_supports": 3,
    }


def boundary_budget(small, endpoint):
    require(
        type(small) is int
        and type(endpoint) is int
        and 0 < small <= 112
        and endpoint == 12,
        "support-budget domain",
    )
    require(
        small + endpoint < 53 and small + 3 * endpoint < 76,
        "quotient-selection support thresholds fail",
    )
    edge = small + 3 * endpoint
    require(edge == 70, "this obstruction requires the exact D7 boundary")
    return {
        "four_small_support": small,
        "three_class_support": edge,
        "two_dimensional_minimum": 76,
        "selected_five_support": small + endpoint,
        "edge_support": edge,
    }
