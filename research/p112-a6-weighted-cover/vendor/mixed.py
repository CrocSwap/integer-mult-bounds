"""Exact 72-support direction alphabet and anchored P112 simplex census.

Root-star stabilizer coverage follows Nick Petalas's PR3175. The mixed-edge
alphabet, rational two-ray intersections and application are new here.
"""

from collections import Counter
from fractions import Fraction
from itertools import combinations, combinations_with_replacement, product

from vendor.geometry import SIMPLE, canonical, dot, primitive, require, solve

ANCHOR = (1, 0, 1, 0, 1, 0, 1, 0)
CAP = {2: 2, 3: 4, 4: 8, 5: 12, 6: 20, 7: 36}
PROFILE = (4, 5, 5) + (6,) * 9


def projective(row):
    require(len(row) == 8 and any(row), "invalid projective vector")
    return primitive(tuple(map(Fraction, row)))


def alphabet(roots, points):
    require(len(roots) == 120 and len(points) == 112, "incomplete root inventory")
    norm_four = {
        canonical(tuple(x + sign * y for x, y in zip(a, b, strict=True)))
        for a, b in combinations(roots, 2)
        if dot(a, b) == 0
        for sign in (-1, 1)
    }
    require(
        len(norm_four) == 1080 and all(dot(v, v) == 16 for v in norm_four),
        "norm-four projective inventory",
    )
    for normal in norm_four:
        for simple in SIMPLE:
            pairing = dot(normal, simple)
            require(pairing % 4 == 0, "nonintegral norm-four reflection")
            reflected = canonical(
                tuple(x - pairing // 4 * y for x, y in zip(normal, simple, strict=True))
            )
            require(reflected in norm_four, "norm-four inventory not Weyl closed")
    ray = projective(solve(SIMPLE, [1] + [0] * 7))
    require(ray in {projective(v) for v in norm_four}, "missing D7 chamber ray")
    histogram = Counter(sum(dot(v, p) != 0 for p in points) for v in norm_four)
    require(histogram == {70: 128, 73: 896, 76: 56}, "D7 support spectrum")
    short = {
        projective(v) for v in norm_four if sum(dot(v, p) != 0 for p in points) <= 72
    }
    expected = {
        canonical(
            tuple(signs[i // 2] if i % 2 == choices[i // 2] else 0 for i in range(8))
        )
        for choices in product(range(2), repeat=4)
        for signs in product((-1, 1), repeat=4)
    }
    require(short == expected and len(short) == 128, "non-root anchor orbit")
    directions = tuple(sorted({projective(v) for v in roots} | short))
    require(len(directions) == 248 and ANCHOR in short, "72-support alphabet")
    return directions, tuple(sorted(short)), dict(sorted(histogram.items()))


def anchor_orbit(roots, frame, normals):
    """An even signed permutation maps every short D7 normal to ANCHOR."""
    require(len(normals) == 128 and len(frame) == 8, "anchor-orbit input")
    for normal in normals:
        permutation = [0] * 8
        signs = [1] * 8
        for pair in range(4):
            positions = (2 * pair, 2 * pair + 1)
            live = next(i for i in positions if normal[i])
            permutation[2 * pair], permutation[2 * pair + 1] = (
                live,
                sum(positions) - live,
            )
            signs[2 * pair] = normal[live]
        if signs.count(-1) % 2:
            signs[1] = -1  # This position has zero anchor value.
        image = tuple(signs[i] * normal[permutation[i]] for i in range(8))
        require(image == ANCHOR and signs.count(-1) % 2 == 0, "anchor normalization")
        transformed = {
            canonical(tuple(signs[i] * r[permutation[i]] for i in range(8)))
            for r in roots
        }
        moved_frame = {
            canonical(tuple(signs[i] * r[permutation[i]] for i in range(8)))
            for r in frame
        }
        require(
            transformed == set(roots) and moved_frame == set(frame),
            "anchor symmetry changes P112",
        )
    return len(normals)


def intersections(directions):
    """Solve a=s*u+t*v for each pair of distinct projective directions."""
    require(len(directions) == len(set(directions)) == 248, "incomplete alphabet")
    vertices = set()
    for u, v in combinations(directions, 2):
        i, j = next(
            (i, j) for i, j in combinations(range(8), 2) if u[i] * v[j] != u[j] * v[i]
        )
        determinant = u[i] * v[j] - u[j] * v[i]
        s = Fraction(ANCHOR[i] * v[j] - ANCHOR[j] * v[i], determinant)
        t = Fraction(u[i] * ANCHOR[j] - u[j] * ANCHOR[i], determinant)
        if s and t and all(s * u[k] + t * v[k] == ANCHOR[k] for k in range(8)):
            vertices.add(tuple(s * x for x in u))
            vertices.add(tuple(t * x for x in v))
    require(len(vertices) == 58, "anchored vertex inventory changed")
    require(
        all((2 * x).denominator == 1 for v in vertices for x in v),
        "non-half-integral anchored vertex",
    )
    return tuple(sorted(tuple(int(2 * x) for x in v) for v in vertices))


def compatibility(vertices, directions):
    require(len(vertices) == len(set(vertices)) == 58, "invalid vertex inventory")
    allowed = set(directions)
    adjacency = [0] * 58
    for i, j in combinations(range(58), 2):
        difference = tuple(x - y for x, y in zip(vertices[i], vertices[j], strict=True))
        if projective(difference) in allowed:
            adjacency[i] |= 1 << j
            adjacency[j] |= 1 << i
    require(
        sum(row.bit_count() for row in adjacency) == 1190, "compatibility graph changed"
    )
    return tuple(adjacency)


def cliques(adjacency, size):
    """Unique increasing cliques; at most 34,834 states for size seven."""
    require(len(adjacency) == 58 and 0 <= size <= 7, "unsupported clique domain")
    require(
        all(type(row) is int and 0 <= row < 1 << 58 for row in adjacency),
        "invalid adjacency bits",
    )
    stack = [((), (1 << 58) - 1)]
    for _ in range(40_000):
        if not stack:
            return
        chosen, candidates = stack.pop()
        if len(chosen) == size:
            yield chosen
            continue
        for _ in range(58):
            if not candidates:
                break
            bit = candidates & -candidates
            candidates ^= bit
            index = bit.bit_length() - 1
            stack.append(((*chosen, index), candidates & adjacency[index]))
        require(len(stack) <= 407, "clique work-stack capacity")
    require(not stack, "clique state budget exhausted")


def rational_rank(rows):
    require(
        1 <= len(rows) <= 8 and all(len(row) == 8 for row in rows),
        "rank input dimension",
    )
    matrix = [list(map(Fraction, row)) for row in rows]
    pivot = 0
    for col in range(8):
        selected = next((i for i in range(pivot, len(matrix)) if matrix[i][col]), None)
        if selected is None:
            continue
        matrix[pivot], matrix[selected] = matrix[selected], matrix[pivot]
        scale = matrix[pivot][col]
        matrix[pivot] = [x / scale for x in matrix[pivot]]
        for i in range(pivot + 1, len(matrix)):
            scale = matrix[i][col]
            matrix[i] = [
                x - scale * y for x, y in zip(matrix[i], matrix[pivot], strict=True)
            ]
        pivot += 1
    return pivot


def surviving_support(values, removed):
    require(
        len(values) == 112 and type(removed) is int and 0 <= removed <= 112,
        "invalid support/deletion domain",
    )
    require(all(len(row) == 9 for row in values), "nine vertex values required")
    costs = [9 - max(Counter(row).values()) for row in values]
    return sum(sorted(costs)[: 112 - removed]), dict(sorted(Counter(costs).items()))


def mixed_census(vertices, adjacency, points):
    anchor = tuple(2 * x for x in ANCHOR)
    evaluations = tuple(
        (0, dot(p, anchor), *(dot(p, v) for v in vertices)) for p in points
    )
    ranks, bounds = Counter(), Counter()
    witness, minimum, count = None, 1000, 0
    for chosen in cliques(adjacency, 7):
        count += 1
        rank = rational_rank((anchor, *(vertices[i] for i in chosen)))
        ranks[rank] += 1
        if rank != 8:
            continue
        values = tuple(
            row[:2] + tuple(row[i + 2] for i in chosen) for row in evaluations
        )
        lower, spectrum = surviving_support(values, 32)
        bounds[lower] += 1
        if lower < minimum:
            minimum, witness = (
                lower,
                {
                    "indices": chosen,
                    "spectrum": spectrum,
                    "vertices_doubled": [anchor] + [vertices[i] for i in chosen],
                },
            )
    require(
        count == 10520 and ranks == {5: 840, 6: 5040, 7: 4032, 8: 608},
        "incomplete mixed-simplex rank census",
    )
    require(
        minimum == 182
        and bounds == {182: 112, 184: 16, 190: 112, 191: 128, 194: 128, 199: 112},
        "mixed-simplex support bound changed",
    )
    return {
        "cliques": count,
        "rank_histogram": dict(sorted(ranks.items())),
        "support_histogram": dict(sorted(bounds.items())),
        "minimum_after_32_cuts": minimum,
        "witness": witness,
    }


def root_extensions(prefix, roots):
    signed = tuple(v for r in roots for v in (r, tuple(-x for x in r)))
    candidates = {r for r in signed if all(dot(r, p) == 4 for p in prefix)}
    normals = tuple(r for r in roots if all(dot(r, p) == 0 for p in prefix))
    unseen, representatives, sizes = set(candidates), [], []
    for _ in range(240):
        if not unseen:
            break
        first = min(unseen)
        queue, seen = [first], {first}
        for index in range(240):
            if index >= len(queue):
                break
            for normal in normals:
                pairing = dot(queue[index], normal)
                require(pairing % 4 == 0, "nonintegral root-star reflection")
                image = tuple(
                    x - pairing // 4 * y
                    for x, y in zip(queue[index], normal, strict=True)
                )
                require(image in candidates, "root-star reflection leaves candidates")
                if image not in seen:
                    seen.add(image)
                    queue.append(image)
            require(len(queue) <= 240, "root-star orbit capacity")
        require(seen <= unseen, "overlapping root-star orbits")
        unseen.difference_update(seen)
        representatives.append(first)
        sizes.append(len(seen))
    require(not unseen, "incomplete root-star partition")
    return representatives, sizes


def all_root_census(roots):
    level, steps = [()], []
    for rank in range(8):
        following = []
        for prefix in level:
            representatives, sizes = root_extensions(prefix, roots)
            steps.append({"rank": rank, "orbit_sizes": sizes})
            following.extend((*prefix, v) for v in representatives)
        level = following
    require(len(level) == 1, "rank-eight root-star orbit inventory")
    costs = [
        9 - max(Counter([0] + [dot(r, v) for v in level[0]]).values()) for r in roots
    ]
    require(Counter(costs) == {2: 36, 3: 84}, "A8 evaluation spectrum")
    lower = sum(sorted(costs)[:80])  # Relax frame + small support to any 40 root lines.
    require(lower == 204, "all-root support budget")
    return {"steps": steps, "spectrum": {2: 36, 3: 84}, "minimum_after_40_cuts": lower}


def original_survivors():
    distance = (0, 53, 78, 92, 100, 106, 109, 111, 112)
    rows = []
    for size in range(8, 13):
        for weights in combinations_with_replacement(range(2, 8), size):
            if sum(w - 2 for w in weights) >= 48:
                continue
            feasible = True
            for level in range(1, 9):
                prefix = weights[: size - 8 + level]
                total = sum(CAP[w] for w in prefix)
                target = sum(32 if w == 7 else CAP[w] for w in prefix)
                if (
                    (level == 1 and target < 53 and total < 73)
                    or (level == 2 and target < 78 and total < 82)
                    or (level >= 3 and total < distance[level])
                ):
                    feasible = False
                    break
            basis = weights[: size - 8]
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
    require(len(rows) == 251 and PROFILE in rows, "original (8,4) residue changed")
    return rows


def application():
    original = original_survivors()
    bases = sorted(
        {basis for basis in combinations(PROFILE, 4) if sum(CAP[w] for w in basis) < 53}
    )
    require(bases == [PROFILE[:4]], "weight-certified quotient bases changed")
    basis = bases[0]
    cuts = [
        sum(CAP[w] for w, g in zip(basis, assignment, strict=True) if g == 2)
        for assignment in product(range(3), repeat=4)
        if all(
            sum(w for w, g in zip(basis, assignment, strict=True) if g == group) <= 6
            for group in (0, 1)
        )
    ]
    require(min(cuts) == 20, "old weight-cover boundary changed")
    return {
        "b": 8,
        "t": 4,
        "weights": PROFILE,
        "original_survivors": len(original),
        "small_support_cap": 32,
        "quotient_basis_cap": 52,
        "edge_support_cap": 72,
        "endpoint_support_cap": 180,
        "mixed_lower": 182,
        "all_root_lower": 204,
        "margin": 2,
        "weight_only_two_six_flat_cut_allowance": min(cuts),
    }
