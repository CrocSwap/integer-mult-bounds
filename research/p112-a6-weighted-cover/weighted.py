"""A6 weighted frame/six-flat/four-flat cover certificate.

The rank-three support is relaxed to four arbitrary coordinates. Frame
traversal is adapted from Nick Petalas's PR3180; all weighted bounds here
are new. Apache-2.0.
"""

import hashlib
import json
from collections import Counter
from itertools import combinations, product

from vendor.geometry import SIMPLE, canonical, dot, require

ALL = (1 << 120) - 1


def full_labels(coordinates):
    labels = tuple(1 | sum((int(x) % 2) << (i + 1) for i, x in enumerate(row))
                   for row in coordinates)
    require(len(labels) == len(set(labels)) == 120, "full120 labels")
    require(all(0 < x < 512 and x & 1 for x in labels), "odd full120 labels")
    return labels


def label_reflections(roots, labels):
    index = {r: i for i, r in enumerate(roots)}
    for r, label in zip(roots, labels, strict=True):
        for j, simple in enumerate(SIMPLE):
            factor = dot(r, simple) // 4
            reflected = canonical(tuple(x - factor * y
                                        for x, y in zip(r, simple, strict=True)))
            require(labels[index[reflected]] == label ^ ((factor & 1) << (j + 1)),
                    "Weyl label-linear relation")
    return 960


def cost_layers(costs):
    require(len(costs) == 120 and Counter(costs) == {0: 1, 1: 21, 2: 63, 3: 35},
            "A6 cost inventory")
    return tuple(sum(1 << i for i, c in enumerate(costs) if c >= level)
                 for level in (1, 2, 3))


def weight(mask, layers):
    return sum((mask & layer).bit_count() for layer in layers)


def frame_inventory(roots):
    require(len(roots) == 120, "frame root count")
    adjacency = tuple(sum(1 << j for j, s in enumerate(roots) if dot(r, s) == 0)
                      for r in roots)
    stack, frames = [((), ALL)], []
    for _ in range(2_000_000):
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
        require(len(stack) <= 961, "frame stack capacity")
    require(not stack and len(frames) == len(set(frames)) == 2025,
            "complete orthogonal-frame inventory")
    return tuple(frames)


def selected_six_flats(labels, layers):
    require(len(labels) == 120 and len(layers) == 3, "six-flat input dimensions")
    kernels = tuple(ALL ^ sum(1 << i for i, label in enumerate(labels)
                             if (label & x).bit_count() & 1) for x in range(512))
    selected, histogram = set(), Counter()
    for pivots in combinations(range(9), 3):
        choices = []
        for pivot in pivots:
            free = tuple(c for c in range(pivot) if c not in pivots)
            rows = tuple((1 << pivot) | sum(((code >> i) & 1) << c
                                           for i, c in enumerate(free))
                         for code in range(1 << len(free)))
            choices.append(tuple(kernels[row] for row in rows))
        for chosen in product(*choices):
            mask = chosen[0] & chosen[1] & chosen[2]
            cost = weight(mask, layers)
            histogram[cost] += 1
            if cost >= 55:
                selected.add(mask)
    require(sum(histogram.values()) == 788035 and max(histogram) == 60,
            "complete weighted six-flat census")
    require(len(selected) == 63
            and Counter(weight(m, layers) for m in selected) == {57: 35, 60: 28},
            "high-weight six-flat inventory")
    return tuple(sorted(selected)), dict(sorted(histogram.items()))


def high_four_flats(labels, layers):
    high = tuple(label for i, label in enumerate(labels) if layers[2] >> i & 1)
    require(len(high) == 35, "cost-three labels")
    index = {label: i for i, label in enumerate(labels)}
    masks = set()
    for basis in combinations(high, 4):
        span = {0}
        for label in basis:
            span.update(tuple(x ^ label for x in tuple(span)))
        if len(span) != 16:
            continue
        mask = sum(1 << index[x] for x in span if x in index)
        if (mask & layers[2]).bit_count() >= 7:
            masks.add(mask)
    require(len(masks) == 135
            and Counter((m & layers[2]).bit_count() for m in masks) == {7: 30, 8: 105},
            "high-cost four-flat inventory")
    return tuple(sorted(masks))


def arbitrary_extra(prefix, layers, removed):
    require(type(removed) is int and 0 <= removed <= 120, "arbitrary-cut budget")
    extra = 0
    for level in (3, 2, 1):
        exact = layers[level - 1] ^ (layers[level] if level < 3 else 0)
        taken = min(removed, (exact & ~prefix).bit_count())
        extra += level * taken
        removed -= taken
    return extra


def cover_pairs(frames, six_flats, four_flats, layers):
    require(len(frames) == 2025 and len(six_flats) == 63 and len(four_flats) == 135,
            "cover inventory sizes")
    frame_histogram, prefix_histogram, quad_maxima = Counter(), Counter(), Counter()
    maximum_prefix, tested, losing_maximum = 0, 0, 0
    losing_witness = None
    for frame in frames:
        frame_mask = sum(1 << i for i in frame)
        frame_histogram[weight(frame_mask, layers)] += 1
        for six in six_flats:
            prefix = frame_mask | six
            cost = weight(prefix, layers)
            maximum_prefix = max(maximum_prefix, cost)
            relaxed = cost + arbitrary_extra(prefix, layers, 12)
            if relaxed > losing_maximum:
                losing_maximum = relaxed
                losing_witness = {"frame": frame, "six_mask": six}
            if cost < 76:
                continue
            prefix_histogram[cost] += 1
            required = 100 - cost  # 112 total, allowing 12 for four arbitrary roots.
            residual_maximum = 0
            for four in four_flats:
                tested += 1
                residual = weight(four & ~prefix, layers)
                residual_maximum = max(residual_maximum, residual)
                require(residual < required, "weighted cover reaches 112")
            quad_maxima[(cost, residual_maximum)] += 1
    require(frame_histogram == {14: 210, 16: 735, 17: 630, 19: 420, 21: 30},
            "A6 frame cost spectrum")
    require(maximum_prefix == 77 and prefix_histogram == {76: 4620, 77: 2520},
            "frame/six-flat prefix boundary")
    require(tested == 963900, "four-flat check coverage")
    require(losing_maximum == 113, "arbitrary-twelve-cut losing control")
    return {"frame_costs": dict(sorted(frame_histogram.items())),
            "prefix_costs": dict(sorted(prefix_histogram.items())),
            "maximum_prefix": maximum_prefix, "four_flat_tests": tested,
            "residual_maxima": [[a, b, n] for (a, b), n in sorted(quad_maxima.items())],
            "removed_upper": 111, "surviving_lower": 141,
            "losing_arbitrary12_lower": 139, "losing_witness": losing_witness}


def weighted_cover(roots, coordinates, star):
    costs = tuple(7 - max(Counter((0, *(dot(r, v) for v in star))).values())
                  for r in roots)
    labels = full_labels(coordinates)
    layers = cost_layers(costs)
    six, histogram = selected_six_flats(labels, layers)
    four = high_four_flats(labels, layers)
    raw = json.dumps({"six": six, "four": four}, separators=(",", ":")).encode()
    return {"six_flat_histogram": histogram, "selected_six_flats": len(six),
            "high_four_flats": len(four), "mask_sha256": hashlib.sha256(raw).hexdigest(),
            "label_reflection_checks": label_reflections(roots, labels),
            "cover": cover_pairs(frame_inventory(roots), six, four, layers)}
