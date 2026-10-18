"""Separate ambient-annihilator and puncture check. Apache-2.0."""

import json
from collections import Counter
from itertools import combinations, product

import verify


def binary_rank(values):
    pivots = [0] * 9
    for original in values:
        if type(original) is not int or not 0 <= original < 512:
            raise ValueError("invalid label")
        value = original
        for bit in range(8, -1, -1):
            if value >> bit & 1:
                if pivots[bit]:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    break
    return sum(v != 0 for v in pivots)


def maximal_axis_subsets(labels):
    """Enumerate all 788035 ambient six-spaces without local coordinates."""
    if len(labels) != 33 or binary_rank(labels) != 8:
        raise ValueError("expected full D6 axis")
    kernels = [
        sum(
            1 << i
            for i, label in enumerate(labels)
            if (label & functional).bit_count() % 2 == 0
        )
        for functional in range(512)
    ]
    counts, maximizers = Counter(), set()
    for pivots in combinations(range(9), 3):
        choices = []
        for pivot in pivots:
            free = [i for i in range(pivot) if i not in pivots]
            choices.append(
                [
                    (1 << pivot) | sum(((v >> j) & 1) << i for j, i in enumerate(free))
                    for v in range(1 << len(free))
                ]
            )
        for a, b, c in product(*choices):
            mask = kernels[a] & kernels[b] & kernels[c]
            counts[mask.bit_count()] += 1
            if mask.bit_count() == 20:
                maximizers.add(mask)
    if sum(counts.values()) != 788035 or max(counts) != 20 or len(maximizers) != 16:
        raise ValueError("full-axis rank-six census differs")
    return maximizers


def orthogonal_frames(roots):
    if len(roots) != 33:
        raise ValueError("expected 33 axis roots")
    gram = [
        [sum(x * y for x, y in zip(a, b, strict=True)) for b in roots] for a in roots
    ]
    frames = []
    for chosen in combinations(range(33), 4):
        if all(gram[a][b] == 0 for a, b in combinations(chosen, 2)):
            frames.append(sum(1 << i for i in chosen))
    if not frames:
        raise ValueError("missing frame controls")
    return frames


def orthogonal_orbit(g, roots):
    index = {r: i for i, r in enumerate(roots)}
    perms = []
    for simple in g.SIMPLE:
        perm = []
        for r in roots:
            reflected = g.canonical(
                tuple(
                    x - g.dot(r, simple) // 4 * y
                    for x, y in zip(r, simple, strict=True)
                )
            )
            perm.append(index[reflected])
        perms.append(perm)
    start = next(
        (i, j) for i, j in combinations(range(120), 2) if g.dot(roots[i], roots[j]) == 0
    )
    seen, queue = {start}, [start]
    for cursor in range(3780):
        if cursor >= len(queue):
            raise ValueError("orthogonal orbit ended early")
        for perm in perms:
            pair = tuple(sorted(perm[i] for i in queue[cursor]))
            if g.dot(*(roots[i] for i in pair)):
                raise ValueError("reflection left orthogonal pairs")
            if pair not in seen:
                seen.add(pair)
                queue.append(pair)
    if len(seen) != 3780 or len(queue) != 3780:
        raise ValueError("orthogonal-pair transitivity failed")
    return len(seen)


def check():
    g = verify.geometry()
    roots, points, _labels, coordinates = g.root_data()
    full_labels = [
        1 | sum((int(x) & 1) << (i + 1) for i, x in enumerate(c)) for c in coordinates
    ]
    a = (0, 0, 0, 0, 0, 2, -2, 0)
    b = (0, 2, -2, 0, 0, 0, 0, 0)
    axis = [i for i, r in enumerate(roots) if g.dot(a, r) and not g.dot(b, r)]
    maxima = maximal_axis_subsets([full_labels[i] for i in axis])
    frames = orthogonal_frames([roots[i] for i in axis])
    intersections = Counter((m & f).bit_count() for m in maxima for f in frames)
    if min(intersections) < 2:
        raise ValueError("a full support20 survives a four-frame puncture")
    # Every actual minimum-union plane removes four orthogonal roots per axis.
    gram = [[g.dot(x, y) for y in roots] for x in roots]
    frame = [i for i, r in enumerate(roots) if r not in points]
    live = [i for i, r in enumerate(roots) if r in points]
    checked = 0
    for x, y in combinations(range(120), 2):
        if gram[x][y] or sum(bool(gram[x][t] or gram[y][t]) for t in live) != 82:
            continue
        for j, k in ((x, y), (y, x)):
            removed = [t for t in frame if gram[j][t] and not gram[k][t]]
            if len(removed) != 4 or any(
                gram[u][v] for u, v in combinations(removed, 2)
            ):
                raise ValueError("actual axis puncture is not an orthogonal four-frame")
            checked += 1
    if checked != 896:
        raise ValueError("minimum-plane coverage differs")
    return {
        "ambient_six_spaces": 788035,
        "full_axis_maximum": 20,
        "twenty_label_sets": 16,
        "orthogonal_four_frames": len(frames),
        "intersection_histogram": dict(sorted(intersections.items())),
        "actual_axis_punctures": checked,
        "orthogonal_pair_orbit": orthogonal_orbit(g, roots),
    }


if __name__ == "__main__":
    result = check()
    print("PASS_INDEPENDENT_D6_PUNCTURE", json.dumps(result, sort_keys=True))
