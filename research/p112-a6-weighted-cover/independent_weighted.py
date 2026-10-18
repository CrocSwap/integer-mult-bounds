"""Separate forward-echelon flat and Weyl-orbit frame cover replay.

The primary code uses reverse-echelon annihilators, root-generated four-flats
and an orthogonality-clique frame traversal. This program imports none of
those algorithms. Root/label reconstruction and source binding are shared.
"""

import hashlib
import json
from collections import Counter
from itertools import combinations, product

from independent import inner
from vendor.geometry import SIMPLE, canonical, frame_lines, require, root_data
from verify import PACKAGE, bind_sources, read_bytes

ALL = (1 << 120) - 1


def flat_masks(labels, dimension):
    require(len(labels) == 120 and dimension in (4, 6), "forward-flat domain")
    kernels = [sum(1 << i for i, label in enumerate(labels)
                   if not ((label & vector).bit_count() % 2)) for vector in range(512)]
    dual_dimension = 9 - dimension
    count = 0
    for pivots in combinations(range(9), dual_dimension):
        rows = []
        for pivot in pivots:
            free = [i for i in range(pivot + 1, 9) if i not in pivots]
            rows.append([kernels[(1 << pivot) + sum(((code >> j) & 1) << i
                                                  for j, i in enumerate(free))]
                         for code in range(1 << len(free))])
        for chosen in product(*rows):
            mask = ALL
            for kernel in chosen:
                mask &= kernel
            count += 1
            yield mask
    require(count == {4: 3309747, 6: 788035}[dimension], "forward-flat coverage")


def frame_orbit(roots):
    index = {r: i for i, r in enumerate(roots)}
    permutations = []
    for simple in SIMPLE:
        permutation = []
        for root in roots:
            factor = inner(root, simple) // 4
            image = canonical(tuple(root[i] - factor * simple[i] for i in range(8)))
            permutation.append(index[image])
        require(len(set(permutation)) == 120, "frame reflection permutation")
        permutations.append(tuple(permutation))
    first = tuple(sorted(index[r] for r in frame_lines()))
    queue, seen = [first], {first}
    for i in range(2025):
        require(i < len(queue), "frame orbit stopped early")
        for permutation in permutations:
            image = tuple(sorted(permutation[j] for j in queue[i]))
            if image not in seen:
                seen.add(image)
                queue.append(image)
        require(len(queue) <= 2025, "frame orbit capacity")
    require(len(queue) == len(seen) == 2025, "complete frame orbit")
    require(all(all(inner(roots[i], roots[j]) == 0 for i, j in combinations(frame, 2))
                for frame in queue), "nonorthogonal orbit frame")
    return tuple(sorted(seen))


def inventories(labels, costs):
    exact = tuple(sum(1 << i for i, c in enumerate(costs) if c == j) for j in range(4))
    six, four, histogram = set(), set(), Counter()
    for mask in flat_masks(labels, 6):
        cost = sum(j * (mask & exact[j]).bit_count() for j in range(1, 4))
        histogram[cost] += 1
        if cost >= 55:
            six.add(mask)
    for mask in flat_masks(labels, 4):
        if (mask & exact[3]).bit_count() >= 7:
            four.add(mask)
    require(len(six) == 63 and len(four) == 135, "independent weighted inventories")
    return tuple(sorted(six)), tuple(sorted(four)), dict(sorted(histogram.items())), exact


def cover(frames, six, four, exact):
    def cost(mask):
        return sum(j * (mask & exact[j]).bit_count() for j in range(1, 4))

    frame_histogram, prefix_histogram, maxima = Counter(), Counter(), Counter()
    maximum_prefix = 0
    for frame in frames:
        frame_mask = sum(1 << i for i in frame)
        frame_histogram[cost(frame_mask)] += 1
        for flat in six:
            removed = frame_mask | flat
            prefix = cost(removed)
            maximum_prefix = max(maximum_prefix, prefix)
            if prefix >= 76:
                prefix_histogram[prefix] += 1
                maximum = max(cost(candidate & ~removed) for candidate in four)
                require(prefix + max(22, maximum) + 12 < 112,
                        "independent cover reaches threshold")
                maxima[prefix, maximum] += 1
    require(maximum_prefix == 77, "independent prefix maximum")
    return {"frame_costs": dict(sorted(frame_histogram.items())),
            "prefix_costs": dict(sorted(prefix_histogram.items())),
            "residual_maxima": [[a, b, n] for (a, b), n in sorted(maxima.items())]}


def main():
    bind_sources()
    expected = json.loads(read_bytes(PACKAGE / "RESULT.json"))["weighted"]
    roots, _, _, coordinates = root_data()
    # Match the canonical A6 star using an explicit fixture, not a stabilizer traversal.
    star = tuple(tuple(-2 * (j == 0) - 2 * (j == i) for j in range(8))
                 for i in range(1, 7))
    costs = []
    for root in roots:
        values = [0] + [inner(root, v) for v in star]
        costs.append(7 - max(values.count(value) for value in values))
    labels = tuple(1 + sum((int(x) & 1) << (j + 1) for j, x in enumerate(row))
                   for row in coordinates)
    require(Counter(costs) == {0: 1, 1: 21, 2: 63, 3: 35}, "independent A6 costs")
    six, four, histogram, exact = inventories(labels, costs)
    raw = json.dumps({"six": six, "four": four}, separators=(",", ":")).encode()
    require(hashlib.sha256(raw).hexdigest() == expected["mask_sha256"],
            "independent flat masks differ")
    require({str(k): v for k, v in histogram.items()} == expected["six_flat_histogram"],
            "independent full weighted census differs")
    actual = cover(frame_orbit(roots), six, four, exact)
    for key, value in actual.items():
        require(json.dumps(value, sort_keys=True) == json.dumps(expected["cover"][key], sort_keys=True),
                "independent weighted cover differs: " + key)
    print("PASS_INDEPENDENT_A6_WEIGHTED six_flats=788035 four_flats=3309747 frames=2025 lower=141")


if __name__ == "__main__":
    main()
